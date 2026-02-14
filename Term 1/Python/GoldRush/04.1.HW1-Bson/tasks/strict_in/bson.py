import struct
from typing import Any
import datetime

PROMPT = '>>> '

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

MAX_STRING_SIZE = 2**32 - 1
MAX_BYTES_SIZE = 2**32 - 1
MAX_DOCUMENT_SIZE = 16 * 1024 * 1024
TYPES = (str, int, float, bytes, bytearray, type(None),
         bool, dict, list, tuple, datetime.datetime)
#====================
# ERRORS
#====================
#region
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

#endregion
#====================
# MARSHAL
#====================
#region
def marshal(data: dict[str, Any]) -> bytes:
    visited: set[int] = set()
    return _marshal_document(data, visited)


def _marshal_document(data: dict[str, Any], visited: set[int]) -> bytes:
    if not isinstance(data, dict):
        raise BsonUnsupportedObjectError

    obj_id = id(data)
    if obj_id in visited:
        raise BsonCycleDetectedError
    visited.add(obj_id)

    try:
        if not all(isinstance(k, str) for k in data.keys()):
            raise BsonUnsupportedKeyError("All keys must be str")
        if any("\x00" in k for k in data.keys()):
            raise BsonKeyWithZeroByteError("Key contains NUL")
        if not all(isinstance(x, TYPES) for x in data.values()):
             raise BsonUnsupportedObjectError

        body = bytearray()
        for key in sorted(data.keys()):
            value = data[key]
            body.extend(_marshal_element(key, value, visited))

        body.append(0)
        total_len = 4 + len(body)
        if total_len > MAX_DOCUMENT_SIZE:
            raise BsonDocumentTooBigError
        return struct.pack("<i", total_len) + body
    finally:
        visited.remove(obj_id)


def _marshal_element(key: str, value: Any, visited: set[int]) -> bytes:
    if not isinstance(key, str):
        raise BsonUnsupportedKeyError
    if "\x00" in key:
        raise BsonKeyWithZeroByteError
    if not isinstance(value, TYPES):
        raise BsonUnsupportedObjectError

    if value is None:
        return bytes([TYPE_NULL]) + _cstring(key)

    if isinstance(value, bool):
        return bytes([TYPE_BOOLEAN]) + _cstring(key) + (b"\x01" if value else b"\x00")

    if isinstance(value, int):
        if -2**31 <= value < 2**31:
            return bytes([TYPE_INT32]) + _cstring(key) + struct.pack("<i", value)
        elif -2**63 <= value < 2**63:
            return bytes([TYPE_INT64]) + _cstring(key) + struct.pack("<q", value)
        else:
            raise BsonIntegerTooBigError

    if isinstance(value, float):
        return bytes([TYPE_DOUBLE]) + _cstring(key) + struct.pack("<d", value)

    if isinstance(value, str):
        encoded = value.encode("utf-8")

        if len(encoded)+1 > MAX_STRING_SIZE:
            raise BsonStringTooBigError
        return (
            bytes([TYPE_STRING])
            + _cstring(key)
            + struct.pack("<i", len(encoded) + 1)
            + encoded
            + b"\x00"
        )

    if isinstance(value, (bytes, bytearray)):
        data = bytes(value)
        if len(data)+1 > MAX_BYTES_SIZE:
            raise BsonBinaryTooBigError
        return (
            bytes([TYPE_BINARY])
            + _cstring(key)
            + struct.pack("<i", len(data))
            + b"\x00"
            + data
        )

    if isinstance(value, dict):
        return bytes([TYPE_DOCUMENT]) + _cstring(key) + _marshal_document(value, visited)

    if isinstance(value, (list, tuple)):
        return bytes([TYPE_ARRAY]) + _cstring(key) + _marshal_array(value, visited)

    if isinstance(value, datetime.datetime):
        start = datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc)
        msec = int((value - start).total_seconds() * 1000)
        return bytes([TYPE_DATETIME]) + _cstring(key) + struct.pack("<q", msec)

    raise BsonUnsupportedObjectError


def _marshal_array(arr: list[Any] | tuple[Any], visited:set[int]) -> bytes:
    obj_id = id(arr)
    if obj_id in visited:
        raise BsonCycleDetectedError("Cycle detected in array")
    visited.add(obj_id)
    try:
        body = bytearray()
        for i, val in enumerate(arr):
            body.extend(_marshal_element(str(i), val, visited))
        body.append(0)
        total_len = 4 + len(body)
        return struct.pack("<i", total_len) + body
    finally:
        visited.remove(obj_id)



def _cstring(s: str) -> bytes:
    return s.encode("utf-8") + b"\x00"
#endregion

#====================
# UNMARSHAL
#====================
#region

def unmarshal(data: bytes) -> dict[str, Any]:
    if len(data) < 4:
        raise BsonBrokenDataError("Not enough bytes for size")
    size = struct.unpack_from("<i", data)[0]

    if size < 5:
        raise BsonIncorrectSizeError("Document size too small")
    if size > len(data):
        raise BsonNotEnoughDataError("Not enough data for declared document size")
    if size < len(data):
        raise BsonTooManyDataError("Extra data beyond document size")

    _, result, _ = _parse_document(data, 0, size)
    return result

def _parse_document(buf: bytes, pos: int, limit: int) -> tuple[int, dict[str, Any], int]:
    doc_size = struct.unpack_from("<i", buf, pos)[0]
    end = pos + doc_size
    if doc_size < 5:
        raise BsonIncorrectSizeError("Document size too small")
    pos += 4

    result: dict[str, Any] = {}
    seen_keys: set[str] = set()

    while pos < end - 1:
        element_type = buf[pos]
        pos += 1

        key, pos = _read_cstring(buf, pos, end)
        if key in seen_keys:
            raise BsonRepeatedKeyDataError(f"Repeated key: {key}")
        seen_keys.add(key)
        if element_type == TYPE_BINARY:
            pos, value = _parse_binary(buf, pos, end)
            if value is not None:
                result[key] = value
        elif element_type in (TYPE_NULL, TYPE_BOOLEAN, TYPE_INT32, TYPE_INT64,
                             TYPE_DOUBLE, TYPE_STRING, TYPE_DOCUMENT, TYPE_ARRAY, TYPE_DATETIME):
            pos, value = _parse_supported_value(element_type, buf, pos, end)
            result[key] = value
        else:
            pos = _skip_known_type(element_type, buf, pos, end)
        if pos > end:
            raise BsonBrokenDataError("Element overshoots document")

    if pos != end - 1:
        raise BsonBrokenDataError("Invalid document length")
    if buf[pos] != 0:
        raise BsonBrokenDataError("Missing final zero byte")

    return end, result, end

def _read_cstring(buf: bytes, pos: int, limit: int) -> tuple[str, int]:
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

def _parse_binary(buf: bytes, pos: int, limit: int) -> tuple[int, Any]:
    length = struct.unpack_from("<i", buf, pos)[0]
    pos += 4
    if length < 0:
        raise BsonBrokenDataError("Negative binary size")
    if pos + 1 + length > limit:
        raise BsonInconsistentStringSizeError("Binary exceeds bounds")

    subtype = buf[pos]
    pos += 1
    payload = buf[pos:pos + length]
    pos += length

    if subtype == 0:
        return pos, bytes(payload)
    if 1 <= subtype <= 9 or subtype >= 128:
        return pos, None
    raise BsonInvalidBinarySubtypeError(f"Bad subtype {subtype}")

def _parse_supported_value(typ: int, buf: bytes, pos: int, limit: int) -> tuple[int, Any]:
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
        _, value, pos = _parse_document(buf, pos, limit)
        return pos, value

    if typ == TYPE_ARRAY:
        _, doc, pos = _parse_document(buf, pos, limit)
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
        arr = [None] * (max_idx + 1)
        for k, v in doc.items():
            arr[int(k)] = v
        return pos, arr

    if typ == TYPE_DATETIME:
        ms = struct.unpack_from("<q", buf, pos)[0]
        return pos + 8, (datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc) +
                        datetime.timedelta(milliseconds=ms))

    raise BsonInvalidElementTypeError(f"Invalid type {typ}")

def _skip_known_type(typ: int, buf: bytes, pos: int, limit: int) -> int:
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
#endregion
