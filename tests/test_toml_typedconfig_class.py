import datetime as dt
import math
import tomllib
import typing
from pathlib import Path
from pprint import pprint

import pytest

import src.typedconfig as typedconfig
from src.typedconfig.helpers import ConfigError
from .constants import _load_toml, EMPTY_FILE, EXAMPLE_FILE


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


class First(typedconfig.TypedConfig):
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


class Tool(typedconfig.TypedConfig):
    first: First
    fruits: list[Fruit]
    second_extra: SecondExtra


class Empty(typedconfig.TypedConfig):
    default: str = "allowed"


def test_empty():
    empty = typedconfig.load_into(Empty, {})
    assert empty and empty.default == "allowed"

    with pytest.raises(ConfigError):
        typedconfig.load_into(Tool, {})

    with pytest.raises(ConfigError):
        typedconfig.load_into(First, EMPTY_FILE, key="tool.first")


def test_typedconfig_classes():
    data = _load_toml()

    tool = Tool.load(data)
    first = First.load(EXAMPLE_FILE, key="tool.first")

    assert tool.first.extra['name']['first'] == first.extra['name']['first']
