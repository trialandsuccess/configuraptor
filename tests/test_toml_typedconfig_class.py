import datetime as dt
import math
import os
import typing

import pytest

from src import configuraptor
from src.configuraptor import all_annotations, asdict
from src.configuraptor.errors import (
    ConfigError,
    ConfigErrorExtraKey,
    ConfigErrorImmutable,
    ConfigErrorInvalidType,
)

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


class Tool(configuraptor.TypedMutableMapping):
    first: First
    fruits: list[Fruit]
    second_extra: SecondExtra
    third: str = "-"


class Empty(configuraptor.TypedMapping):
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

    configuraptor.update(first, string=None)
    assert first.string == "updated"

    first.update(string=None, _allow_none=True)
    assert first.string is None

    with pytest.raises(ConfigErrorInvalidType):
        first.update(string=123)

    first.update(string=123, _strict=False)
    assert first.string == 123

    with pytest.raises(ConfigErrorExtraKey):
        try:
            first.update(new_key="some value")
        except ConfigErrorExtraKey as e:
            assert "new_key" in str(e)
            raise e

    first.update(new_key="some value", _strict=False)
    assert first.new_key == "some value"

    assert not first.some_boolean
    second = first | {"some_boolean": True}

    assert not first.some_boolean
    assert second.some_boolean

    with pytest.raises(ConfigErrorExtraKey):
        first.update(some_boolean=True, other="extra")

    with pytest.raises(ConfigErrorInvalidType):
        first.update(some_boolean=123, other="extra")

    first.update(some_boolean=False, other="extra", _ignore_extra=True)

    assert not first.some_boolean

    os.environ["SOME-BOOLEAN"] = "1"

    first.update_from_env()

    assert first.some_boolean


class VeryOptional(configuraptor.TypedConfig):
    value1: str | None
    value2: str | None = None
    value3: int = 0


def test_typedconfig_fill():
    config1 = VeryOptional.load(dict(value1="one"))

    # will overwrite existing values:
    config1.update(
        value1="1",
        value2="2",
        value3=3,
    )

    assert config1.value1 == "1"
    assert config1.value2 == "2"
    assert config1.value3 == 3

    config2 = VeryOptional.load(dict(value1="one"))

    # will only update missing values:
    config2.fill(
        value1="1",
        value2="2",
        value3=3,
    )

    assert config2.value1 == "one"  # already had a value
    assert config2.value2 == "2"  # updated
    assert config2.value3 == 0  # 0 is falsey but not missing, since it's not None

    config2._fill(
        value1="NO",
        value2="NO",
        value3=-3,
    )

    # nothing should've changed now:

    assert config2.value1 == "one"
    assert config2.value2 == "2"
    assert config2.value3 == 0


class MyConfig(configuraptor.TypedConfig):
    update: bool = False


def test_typedconfig_update_name_collision():
    config = MyConfig.load({"update": True})

    assert config.update == True
    config._update(update=False)
    assert config.update == False

    configuraptor.update(config, update=True)
    assert config.update == True


def test_annotations():
    conf = MyConfig.load({})

    assert conf._all_annotations() == all_annotations(MyConfig)


def test_mapping():
    tool = Tool.load(EXAMPLE_FILE, key="tool")

    assert tool._format("{first.string}") == "src"

    first = tool.first

    # tool is a MutableMapping so this should work:
    assert tool["first"] == first
    with pytest.raises(TypeError):
        # first is not a mutable  mapping, so this should not work:
        assert first["string"]

    tool_d = dict(**tool)

    assert tool_d["third"] == asdict(tool)["tool"]["third"] == tool.third
    assert tool_d["first"].string == asdict(tool)["tool"]["first"]["string"]

    tool.third = "!"
    tool.first.string = "!"
    with pytest.raises(TypeError):
        tool.first["string"] = "123"
    tool["third"] = "123"

    with pytest.raises(ConfigErrorInvalidType):
        tool.third = 123

    with pytest.raises(ConfigErrorInvalidType):
        tool["third"] = 123

    tool2 = tool | {"third": "after update"}

    assert tool["third"] != "after update"
    assert tool2["third"] == "after update"

    del tool["third"]

    with pytest.raises(KeyError):
        assert not tool["third"]

    non_mut = Empty.load({})

    assert non_mut.default == non_mut["default"] == "allowed"
    assert "{default}".format(**non_mut) == "allowed"

    with pytest.raises(TypeError):
        non_mut["default"] = "overwrite"

    with pytest.raises(ConfigErrorImmutable):
        try:
            non_mut.update(default="overwrite")
        except ConfigErrorImmutable as e:
            assert "Empty is Immutable" in str(e)
            raise e

    with pytest.raises(ConfigErrorImmutable):
        non_mut.default = "overwrite"


def test_allow_setting_internals():
    conf = MyConfig.load({})

    # internal keys should NOT be type checked!

    conf._new_key = "allowed"
    conf._new_key = 123
