import datetime as dt
import math
import typing

import pytest

import src.typedconfig as typedconfig
from src.typedconfig.errors import ConfigError, ConfigErrorInvalidType, ConfigErrorMissingKey
from .constants import _load_toml, EMPTY_FILE, EXAMPLE_FILE, PYTEST_EXAMPLES


def test_example_is_valid_toml():
    data = _load_toml()

    assert data


class AbsHasName:
    # can be inherited by other classes with a 'name' attribute.
    name: str


# class FirstExtraName:
#     first: str
#     last: str
#
#
# class FirstExtraPoint:
#     x: int
#     y: int
#
#
# class FirstExtraAnimalType(AbsHasName):
#     ...
#
#
# class FirstExtraAnimal:
#     type: FirstExtraAnimalType
#
#
# class FirstExtra:
#     name: FirstExtraName
#     point: FirstExtraPoint
#     animal: FirstExtraAnimal


class First:
    string: str
    list_of_string: list[str]
    list_of_int: list[int]
    list_of_float: list[float]
    list_of_numbers: list[float | int]
    some_boolean: bool
    number: float | int
    not_a_number: math.nan
    datetime: dt.datetime
    datetimes: list[dt.datetime]
    extra: typing.Optional[dict[str, typing.Any]]


class FruitDetails:
    color: str
    shape: str


class FruitVariety(AbsHasName):
    ...


class Fruit(AbsHasName):
    varieties: list[FruitVariety]
    physical: typing.Optional[FruitDetails]


class SecondExtra:
    allowed: bool


class Tool:
    first: First
    fruits: list[Fruit]
    second_extra: SecondExtra


class Empty:
    default: str = "allowed"


def test_empty():
    empty = typedconfig.load_into(Empty, {})
    assert empty and empty.default == "allowed"

    with pytest.raises(ConfigError):
        typedconfig.load_into(Tool, {})

    with pytest.raises(ConfigError):
        typedconfig.load_into(First, EMPTY_FILE, key="tool.first")


def test_basic_classes():
    data = _load_toml()

    tool = typedconfig.load_into(Tool, data)
    first = typedconfig.load_into(First, EXAMPLE_FILE, key="tool.first")

    assert tool.first.extra["name"]["first"] == first.extra["name"]["first"]


class Relevant:
    key: str


class OptionalRelevant:
    key: typing.Optional[str]


class Irrelevant:
    key: dict


def test_guess_key_from_multiple_keys():
    file = str(PYTEST_EXAMPLES / "with_multiple_toplevel_keys.toml")
    relevant = typedconfig.load_into(Relevant, file)
    assert relevant and relevant.key == "this one!"


def test_guess_key_no_match():
    file = str(PYTEST_EXAMPLES / "with_multiple_toplevel_keys.toml")
    # no key and no match by class name:
    relevant = typedconfig.load_into(Irrelevant, file, key="")
    assert relevant and relevant.key["value"] == "fallback"


class TooLong:
    type: str


def test_invalid_type():
    file = str(PYTEST_EXAMPLES / "with_multiple_toplevel_keys.toml")
    with pytest.raises(ConfigErrorInvalidType):
        # tool.key contains an int instead of a str
        typedconfig.load_into(Relevant, file, key="tool")

    with pytest.raises(ConfigErrorInvalidType):
        # complex.type is a long dict but is typed as string.
        # it will be truncated in the error message
        try:
            typedconfig.load_into(TooLong, file, key="complex")
        except ConfigErrorInvalidType as e:
            assert "..." in str(e)
            raise e


def test_missing_key():
    file = str(PYTEST_EXAMPLES / "with_multiple_toplevel_keys.toml")
    with pytest.raises(ConfigErrorMissingKey):
        # key.key does not exist
        try:
            typedconfig.load_into(Relevant, file, key="key")
        except ConfigErrorMissingKey as e:
            assert "Config key 'key'" in str(e)
            raise e

    # allowed here since 'key' is optional:
    inst = typedconfig.load_into(OptionalRelevant, file, key="key")
    assert inst.key is None


class Point:
    x: int
    y: int


class Structure:
    # contents: dict[str, Point]
    contents: dict[str, Point]


def test_dict_of_custom():
    file = PYTEST_EXAMPLES / "with_dict_of_custom.toml"

    structure = typedconfig.load_into(Structure, file)
    for key, value in structure.contents.items():
        assert isinstance(key, str)
        assert isinstance(value, Point)
