import struct
import math
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


def run_calc(context: dict[str, Any] | None = None) -> None:
    """Run interactive calculator session in specified namespace"""


if __name__ == '__main__':
    context = {'math': math}
    run_calc(context)

def marshal(data: dict[str, Any]) -> bytes:
    return _marshal_document(data)


def _marshal_document(data: dict[str, Any]) -> bytes:
    """Serialize dict into BSON document."""
    body = bytearray()
    for key in sorted(data.keys()):
        value = data[key]
        body.extend(_marshal_element(key, value))

    body.append(0)
    total_len = 4 + len(body)
    return struct.pack("<i", total_len) + body


def _marshal_element(key: str, value: Any) -> bytes:
    if value is None:
        return bytes([TYPE_NULL]) + _cstring(key)

    if isinstance(value, bool):
        return bytes([TYPE_BOOLEAN]) + _cstring(key) + (b"\x01" if value else b"\x00")

    if isinstance(value, int):
        if -2**31 <= value < 2**31:
            return bytes([TYPE_INT32]) + _cstring(key) + struct.pack("<i", value)
        else:
            return bytes([TYPE_INT64]) + _cstring(key) + struct.pack("<q", value)

    if isinstance(value, float):
        return bytes([TYPE_DOUBLE]) + _cstring(key) + struct.pack("<d", value)

    if isinstance(value, str):
        encoded = value.encode("utf-8")
        return (
            bytes([TYPE_STRING])
            + _cstring(key)
            + struct.pack("<i", len(encoded) + 1)
            + encoded
            + b"\x00"
        )

    if isinstance(value, (bytes, bytearray)):
        data = bytes(value)
        return (
            bytes([TYPE_BINARY])
            + _cstring(key)
            + struct.pack("<i", len(data))
            + b"\x00"
            + data
        )

    if isinstance(value, dict):
        return bytes([TYPE_DOCUMENT]) + _cstring(key) + _marshal_document(value)

    if isinstance(value, (list, tuple)):
        return bytes([TYPE_ARRAY]) + _cstring(key) + _marshal_array(value)

    if isinstance(value, datetime.datetime):
        start = datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc)
        msec = int((value - start).total_seconds() * 1000)
        return bytes([TYPE_DATETIME]) + _cstring(key) + struct.pack("<q", msec)

    raise TypeError(f"Unsupported type {type(value)}")


def _marshal_array(arr: list[Any] | tuple[Any]) -> bytes:
    body = bytearray()
    for i, val in enumerate(arr):
        body.extend(_marshal_element(str(i), val))

    body.append(0)
    total_len = 4 + len(body)
    return struct.pack("<i", total_len) + body


def _cstring(s: str) -> bytes:
    return s.encode("utf-8") + b"\x00"


def unmarshal(data: bytes) -> dict[str, Any]:
    _, obj, _ = _parse_document(data, 0)
    return obj


def _parse_document(buf: bytes, pos: int):
    total_len = struct.unpack_from("<i", buf, pos)[0]
    end = pos + total_len
    pos += 4
    res = {}

    while pos < end - 1:
        typ = buf[pos]
        pos = int(pos)
        pos += 1
        key, pos = _read_cstring(buf, pos)
        value, pos = _parse_value(typ, buf, pos)
        res[key] = value

    return end, res, end


def _parse_value(typ: int, buf: bytes, pos: int):
    if typ == TYPE_NULL:
        return None, pos

    if typ == TYPE_BOOLEAN:
        b = buf[pos]
        pos += 1
        return bool(b), pos

    if typ == TYPE_INT32:
        v = struct.unpack_from("<i", buf, pos)[0]
        return v, pos + 4

    if typ == TYPE_INT64:
        v = struct.unpack_from("<q", buf, pos)[0]
        return v, pos + 8

    if typ == TYPE_DOUBLE:
        v = struct.unpack_from("<d", buf, pos)[0]
        return v, pos + 8

    if typ == TYPE_STRING:
        size = struct.unpack_from("<i", buf, pos)[0]
        pos += 4
        s = buf[pos:pos+size-1].decode("utf-8")
        pos += size
        return s, pos

    if typ == TYPE_BINARY:
        size = struct.unpack_from("<i", buf, pos)[0]
        pos += 5
        data = buf[pos:pos+size]
        pos += size
        return bytes(data), pos

    if typ == TYPE_DOCUMENT:
        _, doc, new_pos = _parse_document(buf, pos)
        return doc, new_pos

    if typ == TYPE_ARRAY:
        _, doc, new_pos = _parse_document(buf, pos)
        arr = [doc[str(i)] for i in range(len(doc))]
        return arr, new_pos

    if typ == TYPE_DATETIME:
        ms = struct.unpack_from("<q", buf, pos)[0]
        pos += 8
        dt = datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc) + datetime.timedelta(milliseconds=ms)
        return dt, pos

    raise ValueError("Unknown BSON type")


def _read_cstring(buf: bytes, pos: int):
    start = pos
    while buf[pos] != 0:
        pos += 1
    return buf[start:pos].decode("utf-8"), pos + 1
