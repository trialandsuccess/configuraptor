import collections
import inspect
import json
import struct
import typing
from dataclasses import dataclass
from io import StringIO

from typing_extensions import Self

from . import loaders
from .abs import AbstractTypedConfig
from .helpers import all_annotations, is_custom_class
from .loaders.register import DUMPERS

# def get_class_properties_in_order(cls: type) -> list[str]:
#     properties = []
#     for name, value in inspect.getmembers(cls):
#
#         print(name, value)
#
#         if name.startswith("_"):
#             continue
#         if inspect.ismethod(value):
#             continue
#         properties.append(name)
#
#     return properties

BINARY_TYPES = typing.Union[str, float, int, bool]


class BinaryConfig(AbstractTypedConfig):
    _fields: collections.OrderedDict[str, "_BinaryField"] = {}

    def __init__(self):
        fields, elements = self._collect_fields()
        self._fields = collections.OrderedDict(zip(fields, elements))
        super().__init__()

    @classmethod
    def _collect_fields(cls) -> tuple[list[str], list["_BinaryField"]]:
        elements: list[_BinaryField] = []
        fields: list[str] = []

        for field, value in cls.__dict__.items():
            if field.startswith("_"):
                continue
            if not isinstance(value, _BinaryField):
                # other data, skip
                continue

            fields.append(field)
            elements.append(value)

        return fields, elements

    @classmethod
    def _parse(cls, data: bytes | dict[str, bytes]) -> dict[str, BINARY_TYPES]:
        from .core import load_into

        # NOTE: annotations not used!
        fields, elements = cls._collect_fields()

        if isinstance(data, dict):
            # create one long bytestring of data in the right order:
            data = b"".join(data[field] for field in fields)

        unpacked = struct.unpack(" ".join(str(_) for _ in elements), data)
        data = {}
        for field, value, meta in zip(fields, unpacked, elements):
            meta: _BinaryField
            if isinstance(value, bytes):
                value = value.strip(b"\x00").decode()

            if meta.special:
                value = meta.special(value)

            if is_custom_class(meta.klass):
                value = load_into(meta.klass, value)

            data[field] = value

        return data

    @classmethod
    def _parse_into(cls, data: bytes | dict[str, bytes]) -> Self:
        converted = cls._parse(data)
        inst = cls()
        inst.__dict__.update(**converted)
        return inst

    def _pack(self) -> bytes:
        fmt = " ".join(str(_) for _ in self._fields.values())

        values = [self._fields[k].pack(v) for k, v in self.__dict__.items() if not k.startswith("_")]
        return struct.pack(fmt, *values)


@dataclass
class _BinaryField:
    klass: type
    length: int
    format: str
    special: typing.Callable[[typing.Any], typing.Any] | None
    packer: typing.Callable[[typing.Any], typing.Any] | None

    def __str__(self):
        return f"{self.length}{self.format}"

    def pack(self, value: typing.Any) -> typing.Any:
        if self.packer:
            value = self.packer(value)
        if isinstance(value, str):
            return value.encode()
        return value


T = typing.TypeVar("T")

# https://docs.python.org/3/library/struct.html
# DEFAULT_LENGTHS = {
#     "x": 1,
#     "c": 1,
#     "b": 1,
#     "?": 1,
#     "h": 2,
#     "H": 2,
#     "i": 4,
#     "I": 4,
#     "l": 4,
#     "L": 4,
#     "q": 8,
#     "Q": 8,
#     "n": 8,
#     "N": 8,
#     "e": 2,
#     "f": 4,
#     "d": 8,
#     "s": 1,
#     "p": 1,
#     "P": 8,
# }

DEFAULT_FORMATS = {
    str: "s",
    int: "i",
    float: "f",
    bool: "b",
}


def BinaryField(klass: typing.Type[T], **kw) -> typing.Type[T]:
    fmt = kw.get("format") or DEFAULT_FORMATS[klass]
    special = None
    packer = None
    if loader := loaders.get(fmt, None):
        special = lambda data: loader(StringIO(data), None)
        if _packer := DUMPERS.get(fmt, None):
            packer = lambda data: _packer(data, with_top_level_key=False)
        length = kw["length"]
        fmt = "s"
    elif len(fmt) > 1:
        # length in format: 10s
        length, fmt = int(fmt[:-1]), fmt[-1]
    else:
        length = kw.get("length", 1)

    field = _BinaryField(
        klass,
        format=fmt,
        length=length,
        special=special,
        packer=packer,
    )

    return typing.cast(typing.Type[T], field)
