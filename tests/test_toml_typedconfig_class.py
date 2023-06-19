import datetime as dt
import math
import typing

import pytest

from src import configuraptor
from src.configuraptor.errors import ConfigError, ConfigErrorInvalidType, ConfigErrorExtraKey

from .constants import EMPTY_FILE, EXAMPLE_FILE, _load_toml


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


class First(configuraptor.TypedConfig):
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
    # extra: typing.Optional[FirstExtra]
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


class Tool(configuraptor.TypedConfig):
    first: First
    fruits: list[Fruit]
    second_extra: SecondExtra


class Empty(configuraptor.TypedConfig):
    default: str = "allowed"


def test_empty():
    empty = configuraptor.load_into(Empty, {})
    assert empty and empty.default == "allowed"

    with pytest.raises(ConfigError):
        configuraptor.load_into(Tool, {})

    with pytest.raises(ConfigError):
        configuraptor.load_into(First, EMPTY_FILE, key="tool.first")


def test_typedconfig_classes():
    data = _load_toml()

    tool = Tool.load(data)
    first = First.load(EXAMPLE_FILE, key="tool.first")

    assert tool.first.extra["name"]["first"] == first.extra["name"]["first"]


def test_typedconfig_update():
    first = First.load(EXAMPLE_FILE, key="tool.first")

    assert first.string != "updated"
    first.update(string="updated")
    assert first.string == "updated"

    first.update(string=None)
    assert first.string == "updated"

    first.update(string=None, allow_none=True)
    assert first.string is None

    with pytest.raises(ConfigErrorInvalidType):
        first.update(string=123)

    first.update(string=123, strict=False)
    assert first.string == 123

    with pytest.raises(ConfigErrorExtraKey):
        try:
            first.update(new_key="some value")
        except ConfigErrorExtraKey as e:
            assert "new_key" in str(e)
            raise e

    first.update(new_key="some value", strict=False)
    assert first.new_key == "some value"
