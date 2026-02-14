import base64
import struct
import datetime
from typing import Any
from dataclasses import fields as dataclass_fields

TYPE_DOUBLE = 1
TYPE_STRING = 2
TYPE_DOCUMENT = 3
TYPE_ARRAY = 4
TYPE_BINARY = 5
TYPE_OBJECT_ID = 7
TYPE_BOOLEAN = 8
TYPE_DATETIME = 9
TYPE_NULL = 10
TYPE_INT32 = 16
TYPE_INT64 = 18

SUBTYPE_USER_METADATA = 128
MAX_STRING_SIZE = 2 ** 32 - 1
MAX_BYTES_SIZE = 2 ** 32 - 1
MAX_DOCUMENT_SIZE = 16 * 1024 * 1024
TYPES = (str, int, float, bytes, bytearray, type(None),
         bool, dict, list, tuple, datetime.datetime)


# ====================
# ERRORS
# ====================
# region
class BsonError(ValueError):
    pass
class BsonMarshalError(BsonError):
    pass
class BsonUnsupportedObjectError(BsonMarshalError):
    pass
class BsonUnsupportedKeyError(BsonMarshalError):
    pass
class BsonKeyWithZeroByteError(BsonUnsupportedKeyError):
    pass
class BsonInputTooBigError(BsonMarshalError):
    pass
class BsonBinaryTooBigError(BsonInputTooBigError):
    pass
class BsonIntegerTooBigError(BsonInputTooBigError):
    pass
class BsonStringTooBigError(BsonInputTooBigError):
    pass
class BsonDocumentTooBigError(BsonInputTooBigError):
    pass
class BsonCycleDetectedError(BsonMarshalError):
    pass
class BsonUnmarshalError(BsonError):
    pass
class BsonBrokenDataError(BsonUnmarshalError):
    pass
class BsonIncorrectSizeError(BsonBrokenDataError):
    pass
class BsonTooManyDataError(BsonBrokenDataError):
    pass
class BsonNotEnoughDataError(BsonBrokenDataError):
    pass
class BsonInvalidElementTypeError(BsonBrokenDataError):
    pass
class BsonInvalidStringError(BsonBrokenDataError):
    pass
class BsonStringSizeError(BsonBrokenDataError):
    pass
class BsonInconsistentStringSizeError(BsonBrokenDataError):
    pass
class BsonBadStringDataError(BsonBrokenDataError):
    pass
class BsonBadKeyDataError(BsonBrokenDataError):
    pass
class BsonRepeatedKeyDataError(BsonBrokenDataError):
    pass
class BsonBadArrayIndexError(BsonBrokenDataError):
    pass
class BsonInvalidBinarySubtypeError(BsonBrokenDataError):
    pass
class MapperConfigError(ValueError):
    pass
class BsonInvalidArrayError(Exception):
    pass
# endregion


class Mapper:
    _DEFAULTS = {
        "python_only": False,
        "keep_types": False,
    }

    def __init__(self, **kwargs):
        self.__dict__["_config"] = self._DEFAULTS.copy()

        for key, value in kwargs.items():
            if key not in self._DEFAULTS:
                raise MapperConfigError(f"Option '{key}' is not supported")
            self._config[key] = value

        # registry for namedtuple types collected during marshal
        self._nt_counter = 0
        self._nt_type_to_id: dict[type, str] = {}  # type -> "nt-0"
        # metadata: "nt-0" -> {"name": ..., "fields": [...], "defaults": {field: val}}
        self._nt_metadata: dict[str, dict] = {}

        # during unmarshal we may fill this from parsed __metadata__ types
        self._parsed_nt_metadata: dict[str, dict] | None = None

    def __getattr__(self, name):
        if name in self._config:
            return self._config[name]
        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")

    def __setattr__(self, name, value):
        if name in self._config:
            raise AttributeError("Configuration is read-only")
        super().__setattr__(name, value)

    def __delattr__(self, name):
        if name in self._config:
            raise AttributeError("Configuration is read-only")
        super().__delattr__(name)

    # --- HELPER METHODS FOR TYPE HINTS ---
    def _is_namedtuple(self, obj: Any) -> bool:
        return isinstance(obj, tuple) and hasattr(obj, '_fields') and hasattr(obj, '_asdict')

    def _register_namedtuple_type(self, cls: type) -> str:
        """Register namedtuple class and return its id (nt-X)."""
        if cls in self._nt_type_to_id:
            return self._nt_type_to_id[cls]

        nt_id = f"nt-{self._nt_counter}"
        self._nt_counter += 1

        fields_list = list(cls._fields)
        # collect defaults as a dict {field: default} but only simple values
        defaults_dict = {}
        defaults_map = getattr(cls, "_field_defaults", None) or {}
        if isinstance(defaults_map, dict):
            for k, v in defaults_map.items():
                # only simple default values allowed per task
                if isinstance(v, (str, int, float, bool)) or v is None:
                    defaults_dict[k] = v

        self._nt_metadata[nt_id] = {
            "name": cls.__name__,
            "fields": fields_list,
            "defaults": defaults_dict,
        }
        self._nt_type_to_id[cls] = nt_id
        return nt_id

    def _get_type_hint(self, value: Any) -> str:
        # Support namedtuple as a special hint returning its nt-id
        if self._is_namedtuple(value):
            return self._register_namedtuple_type(type(value))
        if isinstance(value, tuple):
            return "tuple"
        if isinstance(value, bytearray):
            return "bytearray"
        if isinstance(value, bytes):
            return ""
        return ""

    def _apply_type_hint(self, value: Any, hint: str) -> Any:
        # tuple -> convert list to tuple
        if hint == "tuple" and isinstance(value, list):
            return tuple(value)
        # bytearray -> convert bytes to bytearray
        if hint == "bytearray" and isinstance(value, bytes):
            return bytearray(value)
        # namedtuple hint: 'nt-X'
        if hint.startswith("nt-"):
            # value must be dict-like (document) to reconstruct, or list/tuple for positional
            if isinstance(value, dict):
                types = self._parsed_nt_metadata or {}
                meta = types.get(hint)
                if not meta:
                    # if metadata not present, leave as dict
                    return value
                # build namedtuple instance using metadata
                from collections import namedtuple
                name = meta.get("name", "NT")
                fields = list(meta.get("fields", []))
                defaults = meta.get("defaults", {}) or {}
                try:
                    NT = namedtuple(name, fields)
                except Exception:
                    return value
                # prepare kwargs for constructor: take from dict or defaults
                kwargs = {}
                for f in fields:
                    if f in value:
                        kwargs[f] = value[f]
                    else:
                        kwargs[f] = defaults.get(f)
                try:
                    return NT(**kwargs)
                except Exception:
                    return value
            # if value is list and fields exist, try mapping by position
            if isinstance(value, list):
                types = self._parsed_nt_metadata or {}
                meta = types.get(hint)
                if not meta:
                    return value
                from collections import namedtuple
                name = meta.get("name", "NT")
                fields = list(meta.get("fields", []))
                defaults = meta.get("defaults", {}) or {}
                try:
                    NT = namedtuple(name, fields)
                except Exception:
                    return value
                args = []
                for idx, f in enumerate(fields):
                    if idx < len(value):
                        args.append(value[idx])
                    else:
                        args.append(defaults.get(f))
                try:
                    return NT(*args)
                except Exception:
                    return value
        return value

    def apply_metadata(self, value: Any, metadata: list[str] | None) -> Any:
        """Применяет список type-hint'ов к значениям документа или массива."""
        if not metadata:
            return value

        # dict → применяем к каждому ключу
        if isinstance(value, dict):
            keys = list(value.keys())
            for i, hint in enumerate(metadata):
                if i >= len(keys):
                    break
                if hint:
                    k = keys[i]
                    value[k] = self._apply_type_hint(value[k], hint)
            return value

        # array/list → применяем по индексам
        if isinstance(value, list):
            for i, hint in enumerate(metadata):
                if i < len(value) and hint:
                    value[i] = self._apply_type_hint(value[i], hint)
            return value

        return value

    def apply_namedtuple_metadata(self, obj: Any, nt_id: str | None) -> Any:
        """
        Если nt_id задан, пытается реконструировать namedtuple
        используя локальные или глобальные типы.
        """
        if not nt_id or not isinstance(obj, dict):
            return obj

        # Источник метаданных
        types = self._parsed_nt_metadata or self._nt_metadata
        if not types or nt_id not in types:
            return obj

        meta = types[nt_id]
        name = meta.get("name", "NT")
        fields = list(meta.get("fields", []))
        defaults = meta.get("defaults", {}) or {}

        from collections import namedtuple
        try:
            NT = namedtuple(name, fields)
        except Exception:
            return obj

        kwargs = {}
        for f in fields:
            if f in obj:
                kwargs[f] = obj[f]
            else:
                kwargs[f] = defaults.get(f)

        try:
            return NT(**kwargs)
        except Exception:
            return obj

    def _is_dataclass_instance(self, obj: Any) -> bool:
        """Проверяет, является ли объект экземпляром дата-класса."""
        # Проверяем, что это экземпляр класса, для которого определены поля дата-класса
        return hasattr(obj.__class__, '__dataclass_fields__') and not isinstance(obj, type)

    def _get_readable_properties(self, obj: Any) -> dict[str, Any] | None:
        readable_props = {}
        found_any = False

        for attr_name in dir(obj.__class__):
            if attr_name.startswith('__'):
                continue

            attr = getattr(obj.__class__, attr_name)

            if isinstance(attr, property) and attr.fget is not None:
                try:
                    value = getattr(obj, attr_name)
                    readable_props[attr_name] = value
                    found_any = True
                except RecursionError:
                    raise
                except Exception:
                    continue

        return readable_props if found_any else None

    # --- MARSHAL METHODS ---
    def marshal(self, data: Any) -> bytes:
        # reset state
        self._nt_counter = 0
        self._nt_type_to_id = {}
        self._nt_metadata = {}

        visited: set[int] = set()
        # pass root flag True for the outermost document
        result = self._marshal_document(data, visited, root=True)
        return result

    def _marshal_dict_like(self, data: dict[str, Any], keys_order: list[str], visited: set[int],
                           root: bool = False) -> bytes:
        """Сериализует словарь или его подобие в байты BSON."""
        for key in keys_order:
            if "\x00" in key:
                raise BsonKeyWithZeroByteError("Key contains NUL")

        elements = []
        type_hints: list[str] = []
        has_significant_hints = False

        for key in keys_order:
            value = data[key]
            hint = self._get_type_hint(value)
            type_hints.append(hint)
            if hint:
                has_significant_hints = True
            elements.append(self._marshal_element(key, value, visited))

        # Добавление метаданных: старые hints (children) для types внутри документа/массива
        if self.keep_types and has_significant_hints:
            metadata_str = ":".join(type_hints)
            encoded_meta = metadata_str.encode("utf-8")

            meta_key = "__metadata__"
            meta_payload = (
                    bytes([TYPE_BINARY]) +
                    self._cstring(meta_key) +
                    struct.pack("<i", len(encoded_meta)) +
                    bytes([SUBTYPE_USER_METADATA]) +
                    encoded_meta
            )
            elements.append(meta_payload)

        # Если есть зарегистрированные namedtuple-типы во всём дереве и это корневой документ,
        # добавляем новый формат метаданных types (с префиксом \x00 + BSON(types_doc))
        if self.keep_types and root and self._nt_metadata:
            # подготовим types doc
            meta_doc = {"types": self._nt_metadata}
            # используем временный mapper без keep_types чтобы не закрутиться рекурсией
            helper = Mapper(keep_types=False)
            meta_bson = helper._marshal_document(meta_doc, set(), root=False)
            payload = b"\x00" + meta_bson
            meta_key = "__metadata__"
            meta_payload = (
                bytes([TYPE_BINARY]) +
                self._cstring(meta_key) +
                struct.pack("<i", len(payload)) +
                bytes([SUBTYPE_USER_METADATA]) +
                payload
            )
            elements.append(meta_payload)

        body = bytearray()
        for el_bytes in elements:
            body.extend(el_bytes)

        body.append(0)
        total_len = 4 + len(body)
        if total_len > MAX_DOCUMENT_SIZE:
            raise BsonDocumentTooBigError
        return struct.pack("<i", total_len) + body

    def _marshal_document(self, data: Any, visited: set[int], root: bool = False) -> bytes:
        """Маршрутизатор для сериализации документа."""
        obj_id = id(data)
        if obj_id in visited:
            raise BsonCycleDetectedError
        visited.add(obj_id)

        try:
            # 1. dict
            if isinstance(data, dict):
                if not all(isinstance(k, str) for k in data.keys()):
                    raise BsonUnsupportedKeyError("All keys must be str")
                keys_order = sorted(data.keys())
                return self._marshal_dict_like(data, keys_order, visited, root=root)

            # 2. namedtuple
            if self._is_namedtuple(data):
                # register class (so its metadata will be present at root)
                self._register_namedtuple_type(type(data))
                # serialize its fields as a dict
                keys_order = list(data._fields)
                data_dict = data._asdict()
                return self._marshal_dict_like(data_dict, keys_order, visited, root=root)

            # 3. dataclass
            if self._is_dataclass_instance(data):
                keys_order = [f.name for f in dataclass_fields(data)]
                data_dict = {name: getattr(data, name) for name in keys_order}
                return self._marshal_dict_like(data_dict, keys_order, visited, root=root)

            # 4. object with properties
            readable_props = self._get_readable_properties(data)
            if readable_props:
                keys_order = sorted(readable_props.keys())
                return self._marshal_dict_like(readable_props, keys_order, visited, root=root)

            raise BsonUnsupportedObjectError(f"Unsupported dict-like object: {type(data)}")

        except (BsonUnsupportedKeyError, BsonKeyWithZeroByteError) as e:
            raise e
        except BsonUnsupportedObjectError as e:
            raise e
        except BsonCycleDetectedError as e:
            raise e
        except RecursionError:
            raise RecursionError("Cycle detected via object properties")
        except BsonKeyWithZeroByteError as e:
            raise e
        except Exception:
            raise BsonMarshalError(f"Error during structured object marshalling: {type(data)}")
        finally:
            visited.remove(obj_id)

    def _marshal_element(self, key: str, value: Any, visited: set[int]) -> bytes:
        """Сериализует пару ключ-значение."""
        if not isinstance(key, str) or "\x00" in key:
            raise BsonUnsupportedKeyError

        if value is None:
            return bytes([TYPE_NULL]) + self._cstring(key)

        if isinstance(value, bool):
            return bytes([TYPE_BOOLEAN]) + self._cstring(key) + (b"\x01" if value else b"\x00")

        if isinstance(value, int):
            if -2 ** 31 <= value < 2 ** 31:
                return bytes([TYPE_INT32]) + self._cstring(key) + struct.pack("<i", value)
            elif -2 ** 63 <= value < 2 ** 63:
                return bytes([TYPE_INT64]) + self._cstring(key) + struct.pack("<q", value)
            else:
                raise BsonIntegerTooBigError

        if isinstance(value, float):
            return bytes([TYPE_DOUBLE]) + self._cstring(key) + struct.pack("<d", value)

        if isinstance(value, str):
            encoded = value.encode("utf-8")
            if len(encoded) + 1 > MAX_STRING_SIZE:
                raise BsonStringTooBigError
            return (
                    bytes([TYPE_STRING])
                    + self._cstring(key)
                    + struct.pack("<i", len(encoded) + 1)
                    + encoded
                    + b"\x00"
            )

        if isinstance(value, (bytes, bytearray)):
            data = bytes(value)
            if len(data) + 1 > MAX_BYTES_SIZE:
                raise BsonBinaryTooBigError
            return (
                    bytes([TYPE_BINARY])
                    + self._cstring(key)
                    + struct.pack("<i", len(data))
                    + b"\x00"
                    + data
            )

        if isinstance(value, datetime.datetime):
            start = datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc)
            msec = int((value - start).total_seconds() * 1000)
            return bytes([TYPE_DATETIME]) + self._cstring(key) + struct.pack("<q", msec)

        is_dict_like = (
                isinstance(value, dict) or
                self._is_namedtuple(value) or
                self._is_dataclass_instance(value) or
                self._get_readable_properties(value) is not None
        )

        if is_dict_like:
            return bytes([TYPE_DOCUMENT]) + self._cstring(key) + self._marshal_document(value, visited, root=False)

        if isinstance(value, (list, tuple)):
            return bytes([TYPE_ARRAY]) + self._cstring(key) + self._marshal_array(value, visited)

        raise BsonUnsupportedObjectError(f"Unsupported object type: {type(value)}")

    def _marshal_array(self, arr: list[Any] | tuple[Any], visited: set[int]) -> bytes:
        obj_id = id(arr)
        if obj_id in visited:
            raise BsonCycleDetectedError("Cycle detected in array")
        visited.add(obj_id)
        try:
            elements = []
            type_hints: list[str] = []
            has_significant_hints = False

            for i, val in enumerate(arr):
                key_str = str(i)
                hint = self._get_type_hint(val)
                type_hints.append(hint)
                if hint:
                    has_significant_hints = True

                elements.append(self._marshal_element(key_str, val, visited))

            if self.keep_types and has_significant_hints:
                metadata_str = ":".join(type_hints)
                encoded_meta = metadata_str.encode("utf-8")

                meta_key = "__metadata__"

                meta_payload = (
                        bytes([TYPE_BINARY]) +
                        self._cstring(meta_key) +
                        struct.pack("<i", len(encoded_meta)) +
                        bytes([SUBTYPE_USER_METADATA]) +
                        encoded_meta
                )
                elements.append(meta_payload)

            body = bytearray()
            for el_bytes in elements:
                body.extend(el_bytes)

            body.append(0)
            total_len = 4 + len(body)
            return struct.pack("<i", total_len) + body
        finally:
            visited.remove(obj_id)

    @staticmethod
    def _cstring(s: str) -> bytes:
        return s.encode("utf-8") + b"\x00"

    # --- UNMARSHAL METHODS ---

    def unmarshal(self, data: bytes) -> dict[str, Any]:
        if len(data) < 4:
            raise BsonBrokenDataError("Not enough bytes for size")

        size = struct.unpack_from("<i", data)[0]

        if size > len(data) or size < 0:
            raise BsonNotEnoughDataError("Not enough data for declared document size")
        if len(data) < 5:
            raise BsonIncorrectSizeError("Document size too small")
        if size < len(data):
            raise BsonTooManyDataError("Extra data beyond document size")
        if size < 5:
            raise BsonIncorrectSizeError("Document size too small")

        # reset parsed types
        self._parsed_nt_metadata = None

        _, result, _ = self._parse_document(data, 0, size)
        return result

    def unmarshal_value(
            self,
            element_type: int,
            key: str,
            buf: bytes,
            pos: int,
            end: int,
            *,
            metadata_hints: list[str] | None,
            nt_id: str | None
    ):
        """
        Унифицированный разбор одного BSON-элемента + применение метаданных.
        Возвращает (new_pos, value).
        """
        # --- Парсинг стандартных типов ---
        pos, value = self._parse_supported_value(element_type, buf, pos, end)

        # --- Применение старого формата metadata_hints ---
        if self.keep_types and metadata_hints:
            # В apply_metadata уже есть логика, dict/list → корректно мапит по ключам/индексам
            value = self.apply_metadata(value, metadata_hints)

        # --- Применение namedtuple metadata ---
        if self.keep_types and nt_id:
            value = self.apply_namedtuple_metadata(value, nt_id)

        return pos, value

    def unmarshal_dict(self, obj, keep_types=False):
        # Если объект содержит метаданные с типом — восстанавливаем оригинальный объект
        if keep_types and "__metadata__" in obj:
            return self.apply_metadata(obj, keep_types)

        result = {}
        for k, v in obj.items():
            if k == "__metadata__":
                continue
            result[k] = self.unmarshal_value(v, keep_types)

        return result

    def _parse_document(self, buf: bytes, pos: int, limit: int) -> tuple[int, dict[str, Any], int]:
        if pos + 4 > limit:
            raise BsonBrokenDataError("Not enough bytes for document size")

        doc_size = struct.unpack_from("<i", buf, pos)[0]
        if doc_size < 0 or pos + doc_size > limit:
            raise BsonBrokenDataError("Nested document size exceeds parent bounds")
        if doc_size < 5:
            raise BsonIncorrectSizeError("Document size too small")

        end = pos + doc_size
        pos += 4

        result: dict[str, Any] = {}
        seen_keys: set[str] = set()
        metadata_hints: list[str] | None = None
        namedtuple_type_id: str | None = None
        local_types: dict[str, dict] | None = None
        root_self_id: str | None = None

        ALLOWED_PYTHON_TYPES = (
            TYPE_DOUBLE, TYPE_STRING, TYPE_DOCUMENT, TYPE_ARRAY,
            TYPE_BINARY, TYPE_BOOLEAN, TYPE_DATETIME, TYPE_NULL,
            TYPE_INT32, TYPE_INT64
        )

        while pos < end - 1:
            if pos >= limit:
                raise BsonBrokenDataError("Unexpected end of data while reading types")

            element_type = buf[pos]
            pos += 1

            if self.python_only and element_type not in ALLOWED_PYTHON_TYPES:
                raise BsonInvalidElementTypeError(f"Type {element_type} invalid for python_only mode")

            key, pos = self._read_cstring(buf, pos, end)

            is_metadata_key = (key == "__metadata__")

            if key == "__type__" and element_type == TYPE_BINARY:
                pos, value, subtype = self._parse_binary(buf, pos, end, allow_128=True)
                if subtype == SUBTYPE_USER_METADATA:
                    try:
                        namedtuple_type_id = value.decode("utf-8")
                    except Exception:
                        namedtuple_type_id = None
                continue

            # special root self marker (string)
            if key == "self" and element_type == TYPE_STRING:
                size = struct.unpack_from("<i", buf, pos)[0]
                pos += 4
                root_self_id = buf[pos:pos + size - 1].decode("utf-8")
                pos += size
                continue

            if element_type == TYPE_BINARY:
                pos, value, subtype = self._parse_binary(buf, pos, end, is_metadata_key)

                # metadata field handling
                if subtype == SUBTYPE_USER_METADATA and is_metadata_key:
                    # if payload starts with 0x00 => new format with embedded BSON doc
                    if len(value) > 0 and value[0] == 0:
                        payload = value[1:]
                        # parse payload as BSON document
                        try:
                            _, meta_doc, _ = self._parse_document(payload, 0, len(payload))
                        except Exception:
                            raise BsonBadStringDataError("Invalid metadata BSON")
                        # meta_doc may contain 'types' (dict), 'children' (str), 'self' (str)
                        if isinstance(meta_doc, dict):
                            if "types" in meta_doc and isinstance(meta_doc["types"], dict):
                                local_types = meta_doc["types"]
                            if "children" in meta_doc and isinstance(meta_doc["children"], str):
                                metadata_hints = meta_doc["children"].split(":") if meta_doc["children"] else []
                            if "self" in meta_doc and isinstance(meta_doc["self"], str):
                                root_self_id = meta_doc["self"]
                        continue
                    else:
                        # old format: colon-separated hints string
                        try:
                            metadata_str = value.decode("utf-8")
                        except UnicodeDecodeError:
                            raise BsonBadStringDataError("Invalid UTF-8 in metadata")
                        metadata_hints = metadata_str.split(":") if metadata_str else []
                        continue

                # if not metadata (or metadata but not processed above), add binary value
                if value is not None:
                    if key in seen_keys:
                        raise BsonRepeatedKeyDataError(f"Repeated key: {key}")
                    seen_keys.add(key)
                    result[key] = value
            else:
                if key in seen_keys:
                    raise BsonRepeatedKeyDataError(f"Repeated key: {key}")
                seen_keys.add(key)

                if element_type in (TYPE_NULL, TYPE_BOOLEAN, TYPE_INT32, TYPE_INT64,
                                    TYPE_DOUBLE, TYPE_STRING, TYPE_DOCUMENT, TYPE_ARRAY, TYPE_DATETIME):
                    pos, value = self.unmarshal_value(
                        element_type,
                        key,
                        buf,
                        pos,
                        end,
                        metadata_hints=metadata_hints,
                        nt_id=namedtuple_type_id,
                    )
                    result[key] = value

                else:
                    pos = self._skip_known_type(element_type, buf, pos, end)

            if pos > end:
                raise BsonBrokenDataError("Element overshoots document")

        if pos != end - 1:
            raise BsonBrokenDataError("Invalid document length or alignment")
        if buf[pos] != 0:
            raise BsonBrokenDataError("Missing final zero byte")

        # If we found local types (new format), save them into parsed metadata for this mapper
        if local_types:
            # local_types should be a mapping nt-id -> {name, fields, defaults}
            self._parsed_nt_metadata = local_types

        # Apply old-style metadata hints (children) to fields of this document
        if self.keep_types and metadata_hints:
            keys = list(result.keys())
            count = min(len(keys), len(metadata_hints))
            for i in range(count):
                k = keys[i]
                hint = metadata_hints[i]
                if hint:
                    result[k] = self._apply_type_hint(result[k], hint)

        # If the document had an internal __type__ marker (namedtuple for this doc), reconstruct it
        if self.keep_types and namedtuple_type_id:
            # try to get metadata from parsed_nt_metadata (local) or previously parsed
            meta_source = self._parsed_nt_metadata or self._nt_metadata
            meta = meta_source.get(namedtuple_type_id) if meta_source else None
            if meta:
                from collections import namedtuple
                name = meta.get("name", "NT")
                fields = list(meta.get("fields", []))
                defaults = meta.get("defaults", {}) or {}
                try:
                    NT = namedtuple(name, fields)
                    # prepare kwargs from result
                    kwargs = {}
                    for f in fields:
                        if f in result:
                            kwargs[f] = result[f]
                        else:
                            kwargs[f] = defaults.get(f)
                    return end, NT(**kwargs), end
                except Exception:
                    pass  # fallback to dict

        # If new-format metadata provided 'types' and 'self' for this document, reconstruct root namedtuple
        if self.keep_types and self._parsed_nt_metadata and root_self_id:
            meta = self._parsed_nt_metadata.get(root_self_id)
            if meta:
                from collections import namedtuple
                name = meta.get("name", "NT")
                fields = list(meta.get("fields", []))
                defaults = meta.get("defaults", {}) or {}
                try:
                    NT = namedtuple(name, fields)
                    kwargs = {}
                    for f in fields:
                        if f in result:
                            kwargs[f] = result[f]
                        else:
                            kwargs[f] = defaults.get(f)
                    # clear parsed metadata after reconstructing root to avoid leaking into siblings
                    parsed_saved = self._parsed_nt_metadata
                    self._parsed_nt_metadata = None
                    return end, NT(**kwargs), end
                except Exception:
                    pass

        # If local_types are present but we didn't reconstruct root, keep parsed metadata (for nested conversion)
        # (Do not clear self._parsed_nt_metadata here — leave to caller to manage lifecycle.)
        # Otherwise, if no types, ensure parsed metadata is None
        if not local_types:
            self._parsed_nt_metadata = None

        return end, result, end

    def _parse_binary(self, buf: bytes, pos: int, limit: int, allow_128: bool) -> tuple[int, Any, int]:
        length = struct.unpack_from("<i", buf, pos)[0]
        pos += 4
        if length < 0:
            raise BsonBrokenDataError("Negative binary size")
        if pos + 1 + length > limit:
            raise BsonInconsistentStringSizeError("Binary exceeds bounds")

        subtype = buf[pos]
        pos += 1

        if self.python_only:
            is_valid = (subtype == 0) or (subtype == SUBTYPE_USER_METADATA and allow_128)
            if not is_valid:
                raise BsonInvalidBinarySubtypeError(f"Binary subtype {subtype} invalid for python_only mode")

        payload = buf[pos:pos + length]
        pos += length

        if subtype == 0:
            return pos, bytes(payload), subtype

        if subtype == SUBTYPE_USER_METADATA and allow_128:
            return pos, bytes(payload), subtype

        if 1 <= subtype <= 9 or subtype >= 128:
            return pos, None, subtype

        raise BsonInvalidBinarySubtypeError(f"Bad subtype {subtype}")

    def _parse_supported_value(self, typ: int, buf: bytes, pos: int, limit: int) -> tuple[int, Any]:
        if typ == TYPE_NULL:
            return pos, None
        if typ == TYPE_BOOLEAN:
            return pos + 1, buf[pos] != 0
        if typ == TYPE_INT32:
            return pos + 4, struct.unpack_from("<i", buf, pos)[0]
        if typ == TYPE_INT64:
            return pos + 8, struct.unpack_from("<q", buf, pos)[0]
        if typ == TYPE_DOUBLE:
            return pos + 8, struct.unpack_from("<d", buf, pos)[0]

        if typ == TYPE_STRING:
            size = struct.unpack_from("<i", buf, pos)[0]
            pos += 4
            if size < 1:
                raise BsonStringSizeError("Invalid string size")
            if pos + size > limit - 1:
                raise BsonInconsistentStringSizeError("String exceeds bounds")
            if buf[pos + size - 1] != 0:
                raise BsonBrokenDataError("Missing string terminator")
            try:
                value = buf[pos:pos + size - 1].decode("utf-8")
            except UnicodeDecodeError:
                raise BsonBadStringDataError("Invalid UTF-8 in string")
            return pos + size, value

        if typ == TYPE_DOCUMENT:
            _, value, pos = self._parse_document(buf, pos, limit)
            return pos, value

        if typ == TYPE_ARRAY:
            _, doc, pos = self._parse_document(buf, pos, limit)
            indices = []
            for k in doc:
                if not k.isdigit():
                    raise BsonBadArrayIndexError(f"Non-numeric array index: {k}")
                i = int(k)
                if str(i) != k:
                    raise BsonBadArrayIndexError(f"Non-canonical array index '{k}'")
                indices.append(i)

            if not indices:
                return pos, []

            max_idx = max(indices)

            if self.python_only:
                if max_idx != len(indices) - 1:
                    raise BsonInvalidArrayError("Array indices have gaps or do not start from 0")

            arr = [None] * (max_idx + 1)
            for k, v in doc.items():
                arr[int(k)] = v

            # If the array document had metadata hints, they were already applied inside nested _parse_document
            # because nested document applies metadata to its own values. So arr elements should already be typed.

            return pos, arr

        if typ == TYPE_DATETIME:
            ms = struct.unpack_from("<q", buf, pos)[0]
            return pos + 8, (datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc) +
                             datetime.timedelta(milliseconds=ms))

        raise BsonInvalidElementTypeError(f"Invalid type {typ}")

    def _read_cstring(self, buf: bytes, pos: int, limit: int) -> tuple[str, int]:
        start = pos
        while pos < limit:
            if buf[pos] == 0:
                raw = buf[start:pos]
                try:
                    return raw.decode("utf-8"), pos + 1
                except UnicodeDecodeError:
                    raise BsonBadKeyDataError("Invalid UTF-8 in key")
            pos += 1
        raise BsonBadKeyDataError("Missing zero terminator in key")

    def _skip_known_type(self, typ: int, buf: bytes, pos: int, limit: int) -> int:
        if typ in (0x06, 0x0A, 0xFF, 0x7F):
            return pos

        if typ == 0x07:
            if pos + 12 > limit:
                raise BsonBrokenDataError("ObjectId truncated")
            return pos + 12

        if typ == 0x11:
            if pos + 8 > limit:
                raise BsonBrokenDataError("Timestamp truncated")
            return pos + 8

        if typ == 0x13:
            if pos + 16 > limit:
                raise BsonBrokenDataError("Decimal128 truncated")
            return pos + 16

        if typ in (0x0D, 0x0E):
            size = struct.unpack_from("<i", buf, pos)[0]
            pos += 4
            if size < 1:
                raise BsonStringSizeError("Invalid string size")
            if pos + size > limit:
                raise BsonInconsistentStringSizeError("String exceeds bounds")
            if buf[pos + size - 1] != 0:
                raise BsonBrokenDataError("Missing string terminator")
            try:
                buf[pos:pos + size - 1].decode("utf-8")
            except UnicodeDecodeError:
                raise BsonBadStringDataError("Invalid UTF-8")
            return pos + size

        if typ == 0x0B:
            for _ in range(2):
                start = pos
                while pos < limit and buf[pos] != 0:
                    pos += 1
                if pos >= limit:
                    raise BsonBadStringDataError("Regex missing terminator")
                try:
                    buf[start:pos].decode("utf-8")
                except UnicodeDecodeError:
                    raise BsonBadStringDataError("Invalid UTF-8 in regex")
                pos += 1
            return pos

        if typ == 0x0C:
            size = struct.unpack_from("<i", buf, pos)[0]
            pos += 4
            if size < 1:
                raise BsonStringSizeError("Invalid DBPointer string size")
            if pos + size > limit:
                raise BsonInconsistentStringSizeError("DBPointer exceeds bounds")
            if buf[pos + size - 1] != 0:
                raise BsonBrokenDataError("Missing DBPointer string terminator")
            try:
                buf[pos:pos + size - 1].decode("utf-8")
            except UnicodeDecodeError:
                raise BsonBadStringDataError("Invalid UTF-8 in DBPointer")
            pos += size
            if pos + 12 > limit:
                raise BsonBrokenDataError("DBPointer OID truncated")
            return pos + 12

        if typ == 0x0F:
            if pos + 4 > limit:
                raise BsonInconsistentStringSizeError("JS code: missing size field")

            first_int = struct.unpack_from("<i", buf, pos)[0]
            has_second_int = (pos + 8 <= limit)
            second_int = None
            if has_second_int:
                second_int = struct.unpack_from("<i", buf, pos + 4)[0]

            if (has_second_int and second_int is not None and second_int >= 1
                    and first_int >= 5 and pos + first_int <= limit):
                pos += 4
                str_size = second_int
                pos += 4
            else:
                str_size = first_int
                pos += 4

            if str_size < 1:
                raise BsonStringSizeError("Invalid JS code string size")
            if pos + str_size > limit - 1:
                raise BsonInconsistentStringSizeError("JS code string exceeds document bounds")
            if buf[pos + str_size - 1] != 0:
                raise BsonBrokenDataError("Missing JS code terminator")
            try:
                buf[pos:pos + str_size - 1].decode("utf-8")
            except UnicodeDecodeError:
                raise BsonBadStringDataError("Invalid UTF-8 in JS code")

            pos += str_size
            if pos + 4 > limit:
                raise BsonInconsistentStringSizeError("JS code: missing scope document size")
            doc_size = struct.unpack_from("<i", buf, pos)[0]
            if doc_size < 5:
                raise BsonIncorrectSizeError("Invalid scope document size")
            if pos + doc_size > limit:
                raise BsonInconsistentStringSizeError("Scope document exceeds bounds")
            return pos + doc_size
        raise BsonInvalidElementTypeError(f"Unsupported BSON type {typ}")
# ====================
# WRAPPERS
# ====================
# region
def marshal(data: dict[str, Any]) -> bytes:
    return Mapper().marshal(data)


def unmarshal(data: bytes) -> dict[str, Any]:
    return Mapper().unmarshal(data)
# endregion
