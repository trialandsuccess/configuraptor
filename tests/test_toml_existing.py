import datetime as dt
import math
import typing

import pytest

from src import configuraptor

from .constants import _load_toml


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


class ToolWithInit(Tool):
    more_props: str

    def __init__(self, more_properties: str):
        self.more_props = more_properties


def test_new_instances():
    data = _load_toml()

    tool = configuraptor.load_into(ToolWithInit, data, init=dict(more_properties="more kwargs"))
    assert tool.more_props == "more kwargs"
    assert tool.fruits


class SomethingWithInit:
    def __init__(self, arg1, arg2, kwarg1, kwarg2=None):
        assert arg1
        assert arg2
        assert kwarg1
        assert kwarg2


def test_mixed_init():
    configuraptor.load_into(
        SomethingWithInit,
        {},
        init=(
            [1, 2],
            dict(
                kwarg1=1,
                kwarg2=2,
            ),
        ),
    )

    configuraptor.load_into(
        SomethingWithInit,
        {},
        init=dict(
            arg1=1,
            arg2=2,
            kwarg1=1,
            kwarg2=2,
        ),
    )

    configuraptor.load_into(SomethingWithInit, {}, init=[1, 2, 3, 4])

    # invalid init:
    with pytest.raises(ValueError):
        configuraptor.load_into(
            SomethingWithInit,
            {},
            init=33,
        )


def test_existing_instances():
    data = _load_toml()

    inst1 = ToolWithInit("some setup")

    normal_tool = configuraptor.load_into(Tool, data)
    inst1_extended = configuraptor.load_into(inst1, data)
    assert inst1_extended is inst1

    assert inst1.fruits

    assert inst1_extended.first.extra["name"]["first"] == normal_tool.first.extra["name"]["first"]

    with pytest.raises(ValueError):
        configuraptor.load_into(inst1, data, init=dict(more_properties="Should not be allowed!"))
