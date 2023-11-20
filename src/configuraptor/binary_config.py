"""
Logic to do with parsing bytestrings as configuration (using struct).
"""

import collections
import struct
import typing
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path

from typing_extensions import Self

from . import loaders
from .abs import AbstractTypedConfig
from .helpers import is_custom_class
from .loaders.register import DUMPERS

BINARY_TYPES = typing.Union[str, float, int, bool]


class BinaryConfig(AbstractTypedConfig):
    """
    Inherit this class if you want your config or a section of it to be parsed using struct.
    """

    _fields: collections.OrderedDict[str, "_BinaryField"]

    def __init__(self) -> None:
        """
        Before filling the class with data, we store the fields (BinaryField) for later use.
        """
        fields, elements = self._collect_fields()
        self._fields = collections.OrderedDict(zip(fields, elements))
        super().__init__()

    @classmethod
    def _collect_fields(cls) -> tuple[list[str], list["_BinaryField"]]:
        """
        Get the class' field names and dataclass instances.
        """
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
        """
        Parse a bytestring or a dict of bytestrings (in the right order).
        """
        from .core import load_into

        # NOTE: annotations not used!
        fields, elements = cls._collect_fields()

        if isinstance(data, dict):
            # create one long bytestring of data in the right order:
            data = b"".join(data[field] for field in fields)

        unpacked = struct.unpack(" ".join(str(_) for _ in elements), data)
        final_data: dict[str, BINARY_TYPES] = {}

        zipped: typing.Iterable[tuple[str, typing.Any, _BinaryField]] = zip(fields, unpacked, elements)
        for field, value, meta in zipped:
            if isinstance(value, bytes) and not issubclass(meta.klass, BinaryConfig):
                value = value.strip(b"\x00").decode()

            if meta.special:
                # e.g. load from JSON
                value = meta.special(value)

            # ensure it's the right class (e.g. bool):
            value = load_into(meta.klass, value) if is_custom_class(meta.klass) else meta.klass(value)

            final_data[field] = value

        return final_data

    @classmethod
    def _parse_into(cls, data: bytes | dict[str, bytes]) -> Self:
        """
        Create a new instance based on data.
        """
        converted = cls._parse(data)
        inst = cls()
        inst.__dict__.update(**converted)
        return inst

    def _pack(self) -> bytes:
        """
        Pack an instance back into a bytestring.
        """
        fmt = " ".join(str(_) for _ in self._fields.values())

        values = [self._fields[k].pack(v) for k, v in self.__dict__.items() if not k.startswith("_")]

        return struct.pack(fmt, *values)

    @classmethod
    def _format(cls) -> str:
        _, fields = cls._collect_fields()

        return " ".join(str(_) for _ in fields)

    @classmethod
    def _get_length(cls) -> int:
        """
        How many bytes do the fields of this class have?
        """
        fmt = cls._format()

        return struct.calcsize(fmt)

    def __setattr__(self, key: str, value: typing.Any) -> None:
        """
        When setting a new field for this config, update the _fields property to have the correct new type + size.
        """
        if not key.startswith("_") and isinstance(value, BinaryConfig):
            field = self._fields[key]
            field.klass = value.__class__
            field.length = value.__class__._get_length()

        return super().__setattr__(key, value)


@dataclass(slots=True)
class _BinaryField:
    """
    Class that stores info to parse the value from a bytestring.

    Returned by BinaryField, but overwritten on instances with the actual value of type klass.
    """

    klass: typing.Type[typing.Any]
    length: int
    fmt: str
    special: typing.Callable[[typing.Any], dict[str, typing.Any]] | None
    packer: typing.Callable[[typing.Any], typing.Any] | None

    def __str__(self) -> str:
        return f"{self.length}{self.fmt}"

    def pack(self, value: typing.Any) -> typing.Any:
        if self.packer:
            value = self.packer(value)
        if isinstance(value, str):
            return value.encode()
        if isinstance(value, BinaryConfig):
            return value._pack()
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
    bool: "?",  # b
}


def BinaryField(klass: typing.Type[T], **kw: typing.Any) -> T:
    """
    Fields for BinaryConfig can not be annotated like a regular typed config, \
    because more info is required (such as struct format/type and length).

    This actually returns a _BinaryField but when using load/load_into, the value will be replaced with type 'klass'.

    Args:
        klass (type): the final type the value will have
        format (str): either one of the formats of struct (e.g. 10s) or a loadable format (json, toml, yaml etc.)
        length (int): how many bytes of data to store? (required for str, unless you enter it in format already)

    Usage:
        class MyConfig(BinaryConfig):
            string = BinaryField(str, length=5) # string of 5 characters
            integer = BinaryField(int)
            complex = BinaryField(OtherClass, format='json', length=64)
                        # will extract 64 bytes of string and try to convert to the linked class
                        # (using regular typeconfig logic)
    """
    special = None
    packer = None

    if issubclass(klass, BinaryConfig):
        fmt = "s"  # temporarily group as one string
        length = kw.get("length", klass._get_length())
    else:
        fmt = kw.get("format") or DEFAULT_FORMATS[klass]
        if loader := loaders.get(fmt, None):
            special = lambda data: loader(  # noqa: E731
                BytesIO(data if isinstance(data, bytes) else data.encode()), Path()
            )
            if _packer := DUMPERS.get(fmt, None):
                packer = lambda data: _packer(data, with_top_level_key=False)  # noqa: E731
            length = kw["length"]
            fmt = "s"
        elif len(fmt) > 1:
            # length in format: 10s
            length, fmt = int(fmt[:-1]), fmt[-1]
        else:
            length = kw.get("length", 1)

    field = _BinaryField(
        klass,
        fmt=fmt,
        length=length,
        special=special,
        packer=packer,
    )

    return typing.cast(T, field)
