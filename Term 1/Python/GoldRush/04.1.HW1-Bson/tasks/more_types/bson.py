import struct
import datetime
from typing import Any
from dataclasses import fields as dataclass_fields
from collections import namedtuple  # <-- добавлено для восстановления namedtuple при unmarshal

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

        # --- additions: registry for namedtuple classes during marshal ---
        # Словарь: { class_object : "nt-X" }
        self._nt_class_to_id: dict[type, str] = {}
        # Словарь метаданных типов по id: { "nt-X": {"name": ..., "fields": [...], "defaults": [...]} }
        self._nt_metadata_by_id: dict[str, dict] = {}
        # Счётчик для генерации nt-идентификаторов
        self._nt_next_index = 0

        # --- temporary storage used during unmarshal to hold parsed 'types' metadata ---
        self._parsed_types: dict | None = None

        # --- temporary storage used to indicate root namedtuple id during marshal ---
        self._current_root_nt_id: str | None = None

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

    def _get_type_hint(self, value: Any) -> str:
        # Изменено: поддержка именованных кортежей — возвращаем их идентификатор (nt-X)
        if self._is_namedtuple(value):
            # регистрируем класс (если ещё не зарегистрирован) и возвращаем id
            return self._register_namedtuple_for_instance(value)
        if isinstance(value, tuple):
            return "tuple"
        if isinstance(value, bytearray):
            return "bytearray"
        if isinstance(value, bytes):
            return ""
        return ""

    def _apply_type_hint(self, value: Any, hint: str) -> Any:
        # Изменено: поддержка восстановления именованных кортежей (hint формата 'nt-X')
        if hint == "tuple" and isinstance(value, list):
            return tuple(value)
        if hint == "bytearray" and isinstance(value, bytes):
            return bytearray(value)

        # namedtuple hint (nt-0, nt-1, ...)
        if hint.startswith("nt-") and isinstance(value, dict):
            # попытка восстановить из только что распарсенных типов (если есть)
            types = getattr(self, "_parsed_types", None)
            if types and hint in types:
                type_info = types[hint]
                # fields order:
                fields = type_info.get("fields", [])
                name = type_info.get("name", "NT")
                defaults = type_info.get("defaults", [])
                # создаём класс namedtuple и инстанцируем
                try:
                    NT = namedtuple(name, fields)
                    # build args from dict in fields order
                    args = [value.get(f) for f in fields]
                    return NT(*args)
                except Exception:
                    # если не получилось — оставляем dict
                    return value
        return value

    # --- helper to register namedtuple classes during marshal ---
    def _register_namedtuple_for_instance(self, inst: Any) -> str:
        cls = inst.__class__
        if cls in self._nt_class_to_id:
            return self._nt_class_to_id[cls]

        # новый id
        nt_id = f"nt-{self._nt_next_index}"
        self._nt_next_index += 1
        self._nt_class_to_id[cls] = nt_id

        # Собираем metadata: name, fields, defaults (только простые значения)
        # defaults: сначала пробуем стандартный атрибут _field_defaults (collections.namedtuple)
        defaults_map = getattr(cls, "_field_defaults", None)
        if defaults_map is None:
            # fallback: иногда у typing.NamedTuple есть __dict__-based defaults; пытаемся словарь
            defaults_map = getattr(cls, "__dict__", {}).get("_field_defaults", {}) or {}

        # fields:
        fields_list = list(getattr(cls, "_fields", []))

        # defaults aligned to fields_list
        defaults_list = []
        for f in fields_list:
            val = None
            if defaults_map and isinstance(defaults_map, dict) and f in defaults_map:
                candidate = defaults_map[f]
                # сохраняем только простые значения
                if isinstance(candidate, (str, int, float, bool)) or candidate is None:
                    val = candidate
                else:
                    val = None
            else:
                val = None
            defaults_list.append(val)

        meta = {
            "name": getattr(cls, "__name__", "NT"),
            "fields": fields_list,
            "defaults": defaults_list
        }
        self._nt_metadata_by_id[nt_id] = meta
        return nt_id

    # --- HELPER METHODS FOR TASK 6 ---

    def _is_namedtuple(self, obj: Any) -> bool:
        """Проверяет, является ли объект именованным кортежем."""
        return isinstance(obj, tuple) and hasattr(obj, '_fields') and hasattr(obj, '_asdict')

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
        """Точка входа. Обрабатывает все типы, которые сериализуются как Document."""
        visited: set[int] = set()
        # Reset registry before each top-level marshal
        self._nt_class_to_id = {}
        self._nt_metadata_by_id = {}
        self._nt_next_index = 0
        self._current_root_nt_id = None
        return self._marshal_document(data, visited, root=True)  # pass root flag

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

            # Перед сериализацией элемента — если это именованный кортеж и это корень, нужно зарегистрировать self
            # (но регистрация в _get_type_hint уже сделана)
            elements.append(self._marshal_element(key, value, visited))

        # Добавление метаданных
        # Изменено: поддержка новых типов метаданных (types dict) + совместимость со старым форматом (children)
        if self.keep_types:
            meta_container = None
            # 'children' - старый формат (colon-separated type_hints)
            if has_significant_hints:
                # формируем старую строку
                metadata_str = ":".join(type_hints)
            else:
                metadata_str = None

            # если есть зарегистрированные namedtuple классы, готовим их метаданные
            if self._nt_metadata_by_id:
                types_meta = {}
                for nt_id, info in self._nt_metadata_by_id.items():
                    # сохраняем только простые defaults (мы уже обеспечили это при регистрации)
                    types_meta[nt_id] = {
                        "name": info["name"],
                        "fields": list(info["fields"]),
                        "defaults": list(info["defaults"])
                    }
                meta_container = {}
                meta_container["types"] = types_meta

                # если root и текущ root id установлен — добавляем self
                if getattr(self, "_current_root_nt_id", None):
                    meta_container["self"] = self._current_root_nt_id

                # если есть старые метаданные, кладём их в child (compat)
                if metadata_str is not None:
                    meta_container["children"] = metadata_str

            else:
                # нет новых types — если есть только старые метаданные, ведём как прежде, но запакуем в бинарный payload
                if metadata_str is not None:
                    # старый поведение: добавление бинарного USER_METADATA со строкой
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
                    # продолжаем формирование документа; возвращаем раннее
                    body = bytearray()
                    for el_bytes in elements:
                        body.extend(el_bytes)
                    body.append(0)
                    total_len = 4 + len(body)
                    if total_len > MAX_DOCUMENT_SIZE:
                        raise BsonDocumentTooBigError
                    return struct.pack("<i", total_len) + body

            # если есть meta_container (новый формат), сериализуем его как вложенный BSON и добавим префикс \x00
            if meta_container is not None:
                # сериализуем meta_container в BSON — но при этом временно отключаем keep_types,
                # чтобы не рекурсивно добавлять метаданные само к себе
                old_keep = self._config["keep_types"]
                self._config["keep_types"] = False
                try:
                    # создаём BSON для meta_container (используем новый чистый visited для метаданных)
                    meta_bson = self._marshal_document(meta_container, set(), root=False)
                finally:
                    self._config["keep_types"] = old_keep

                # добавляем нулевой байт как маркер формата + BSON
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

        # Поддержка указания текущего корневого namedtuple id для включения self в метаданные:
        previous_root_nt = getattr(self, "_current_root_nt_id", None)
        try:
            # 1. СТАНДАРТНЫЙ СЛОВАРЬ (dict)
            if isinstance(data, dict):
                if not all(isinstance(k, str) for k in data.keys()):
                    raise BsonUnsupportedKeyError("All keys must be str")
                keys_order = sorted(data.keys())
                return self._marshal_dict_like(data, keys_order, visited, root=root)

            # 2. ИМЕНОВАННЫЙ КОРТЕЖ (Named Tuple)
            if self._is_namedtuple(data):
                # регистрируем класс (чтобы получить nt-id) — регистрация также заполнит self._nt_metadata_by_id
                nt_id = self._register_namedtuple_for_instance(data)
                # если это корень, отметим текущий root id, чтобы при создании __metadata__ добавить "self"
                if root:
                    self._current_root_nt_id = nt_id

                keys_order = list(data._fields)
                data_dict = data._asdict()
                return self._marshal_dict_like(data_dict, keys_order, visited, root=root)

            # 3. ЭКЗЕМПЛЯР ДАТА-КЛАССА (Data Class Instance)
            if self._is_dataclass_instance(data):
                keys_order = [f.name for f in dataclass_fields(data)]
                data_dict = {name: getattr(data, name) for name in keys_order}

                return self._marshal_dict_like(data_dict, keys_order, visited, root=root)

            # 4. ОБЪЕКТ С PROPERTY (Property Object)
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
            # восстанавливаем предыдущий root nt id (если был)
            self._current_root_nt_id = previous_root_nt

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
            return bytes([TYPE_DOCUMENT]) + self._cstring(key) + self._marshal_document(value, visited)

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
                # Здесь добавляем старый формат (colon-separated hints) или новый формат,
                # но поскольку массивы не могут содержать top-level namedtuple types без
                # общего "types" dict, мы добавляем только children (старый формат).
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

        # Reset parsed_types before parsing top-level doc
        self._parsed_types = None

        _, result, _ = self._parse_document(data, 0, size)
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

        # --- additions: to hold parsed 'types' metadata and possible 'self' id ---
        metadata_types: dict | None = None
        metadata_self_id: str | None = None

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

            if element_type == TYPE_BINARY:
                pos, value, subtype = self._parse_binary(buf, pos, end, is_metadata_key)

                # Изменено: если это бинарный SUBTYPE_USER_METADATA и ключ __metadata__ — обрабатываем
                if subtype == SUBTYPE_USER_METADATA and is_metadata_key:
                    # value - это байтовая нагрузка
                    if value is None:
                        # ничего не делать
                        continue

                    # Новая форма: если первый байт == 0, далее идет сериализованный BSON-словарь метаданных
                    if len(value) > 0 and value[0] == 0:
                        # парсим payload[1:] как BSON-документ
                        payload = value[1:]
                        # Создаём временную парсерную копию: вызывать _parse_document на payload
                        try:
                            # Сохраним текущее parsed_types, чтобы вложенный вызов не потерялся
                            prev_parsed_types = getattr(self, "_parsed_types", None)
                            # При парсинге метаданных используем отдельный вызов: pos0=0, limit=len(payload)
                            _, meta_dict, _ = self._parse_document(payload, 0, len(payload))
                        finally:
                            # _parse_document мог бы изменить self._parsed_types; но мы ждём, что meta_dict —
                            # это чистый dict
                            pass

                        # теперь meta_dict может содержать keys: types (dict), children (str), self (id)
                        if isinstance(meta_dict, dict):
                            if "children" in meta_dict and isinstance(meta_dict["children"], str):
                                metadata_hints = meta_dict["children"].split(":") if meta_dict["children"] else []
                            if "types" in meta_dict and isinstance(meta_dict["types"], dict):
                                # meta types: копируем прямо
                                metadata_types = meta_dict["types"]
                            if "self" in meta_dict and isinstance(meta_dict["self"], str):
                                metadata_self_id = meta_dict["self"]
                        # не сохраняем в result — это служебная информация
                        continue

                    else:
                        # Старый формат: строка типа colon-separated hints
                        try:
                            metadata_str = value.decode("utf-8")
                        except UnicodeDecodeError:
                            raise BsonBadStringDataError("Invalid UTF-8 in metadata")
                        metadata_hints = metadata_str.split(":")
                        continue

                # если это не метаданные, обрабатываем как обычное бинарное поле
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
                    pos, value = self._parse_supported_value(element_type, buf, pos, end)
                    result[key] = value
                else:
                    pos = self._skip_known_type(element_type, buf, pos, end)

            if pos > end:
                raise BsonBrokenDataError("Element overshoots document")

        if pos != end - 1:
            raise BsonBrokenDataError("Invalid document length or alignment")
        if buf[pos] != 0:
            raise BsonBrokenDataError("Missing final zero byte")

        # Если были метаданные типа children (старые hints), применяем их
        if self.keep_types and metadata_hints:
            keys = list(result.keys())
            count = min(len(keys), len(metadata_hints))
            # подготовим self._parsed_types = metadata_types (если были)
            prev_parsed_types = getattr(self, "_parsed_types", None)
            if metadata_types:
                self._parsed_types = metadata_types
            try:
                for i in range(count):
                    k = keys[i]
                    hint = metadata_hints[i]
                    if hint:
                        result[k] = self._apply_type_hint(result[k], hint)
            finally:
                # не очищаем parsed_types до выхода, потому что можем понадобиться ниже для восстановления root
                pass

        # Если есть types metadata и есть self (т.е. корневой документ был namedtuple), восстанавливаем
        if metadata_types:
            # Временно установим parsed_types (если ещё не установлено)
            prev_parsed_types2 = getattr(self, "_parsed_types", None)
            self._parsed_types = metadata_types
            try:
                if metadata_self_id:
                    # Восстанавливаем весь корневой документ как namedtuple
                    if metadata_self_id in metadata_types:
                        type_info = metadata_types[metadata_self_id]
                        fields = list(type_info.get("fields", []))
                        name = type_info.get("name", "NT")
                        try:
                            NT = namedtuple(name, fields)
                            args = [result.get(f) for f in fields]
                            return end, NT(*args), end
                        except Exception:
                            # если не смогли восстановить — оставим dict
                            pass
            finally:
                # очищаем parsed_types (внешние уровни будут восстановлены предыдущим значением)
                self._parsed_types = prev_parsed_types2

        # Очистим parsed_types, если мы его устанавливали ранее и оно больше не нужно
        # (если parsed_types было установлено в области применения этого вызова, оно уже сброшено)
        # Просто убеждаемся, что не оставим мусор в self._parsed_types
        if metadata_types is None:
            # если parsed_types было временно установлено при применении children, сбрасываем
            self._parsed_types = None

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
