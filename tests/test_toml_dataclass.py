import datetime as dt
import math
import typing
from dataclasses import dataclass

import pytest

from src.typedconfig.helpers import ConfigError
from .constants import _load_toml, EMPTY_FILE, EXAMPLE_FILE

import src.typedconfig as typedconfig


def test_example_is_valid_toml():
    data = _load_toml()

    assert data


# @dataclass
# class FirstExtraName:
#     first: str
#     last: str
#
#
# @dataclass
# class FirstExtraPoint:
#     x: int
#     y: int
#
#
# @dataclass
# class FirstExtraAnimalType:
#     name: str
#
#
# @dataclass
# class FirstExtraAnimal:
#     type: FirstExtraAnimalType
#
#
# @dataclass
# class FirstExtra:
#     name: FirstExtraName
#     point: FirstExtraPoint
#     animal: FirstExtraAnimal


@dataclass
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
    # extra: typing.Optional[FirstExtra]
    extra: typing.Optional[dict[str, typing.Any]]


@dataclass
class FruitDetails:
    color: str
    shape: str


@dataclass
class FruitVariety:
    name: str


@dataclass
class Fruit:
    name: str
    varieties: list[FruitVariety]
    physical: typing.Optional[FruitDetails]


@dataclass
class SecondExtra:
    allowed: bool


@dataclass
class Tool:
    first: First
    fruits: list[Fruit]
    second_extra: SecondExtra


@dataclass
class Empty:
    default: str = "allowed"


def test_empty():
    empty = typedconfig.load_into(Empty, {})
    assert empty and empty.default == "allowed"

    with pytest.raises(ConfigError):
        typedconfig.load_into(Tool, {})

    with pytest.raises(ConfigError):
        typedconfig.load_into(First, EMPTY_FILE, key="tool.first")


def test_dataclasses():
    data = _load_toml()

    tool = typedconfig.load_into(Tool, data)
    first = typedconfig.load_into(First, EXAMPLE_FILE, key="tool.first")

    assert tool.first.extra['name']['first'] == first.extra['name']['first']
