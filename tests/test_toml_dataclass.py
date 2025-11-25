import datetime as dt
import math
import typing
from dataclasses import dataclass, field

import pytest

from src import configuraptor
from src.configuraptor.dump import asdict
from src.configuraptor.errors import ConfigError
from src.configuraptor.helpers import is_union

from .constants import EMPTY_FILE, EXAMPLE_FILE, _load_toml


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
    include: list[int] = field(default_factory=list)
    # ^ not required in config file since it has a default value


def test_empty():
    empty = configuraptor.load_into(Empty, {})
    assert empty and empty.default == "allowed"

    with pytest.raises(ConfigError):
        configuraptor.load_into(Tool, {})

    with pytest.raises(ConfigError):
        configuraptor.load_into(First, EMPTY_FILE, key="tool.first")


def test_dataclasses():
    data = _load_toml()

    tool = configuraptor.load_into(Tool, data)
    first = configuraptor.load_into(First, EXAMPLE_FILE, key="tool.first")

    assert tool.first.extra["name"]["first"] == first.extra["name"]["first"]


def test_init_not_allowed():
    data = _load_toml()

    with pytest.raises(ValueError):
        tool = configuraptor.load_into(Tool, data, init={"extra": "data"})


def test_optional_dataclass():
    @dataclass
    class Inner:
        value: str

    @dataclass
    class Outer:
        inner: Inner | None
        second: typing.Optional[Inner]

    filled_data = Outer(inner=Inner(value="some"), second=None)
    empty_data = Outer(inner=None, second=Inner(value="second"))

    filled_dict = asdict(filled_data)
    empty_dict = asdict(empty_data)

    filled_reloaded = configuraptor.load_into(Outer, filled_dict)
    empty_reloaded = configuraptor.load_into(Outer, empty_dict)

    assert filled_reloaded == filled_data
    assert empty_reloaded == empty_data


def test_is_union():
    assert is_union(typing.Optional[dict[str, typing.Any]])
    assert is_union(str | None)

    assert not is_union(str)
    assert not is_union(None)
    assert not is_union(dict[str, None])
