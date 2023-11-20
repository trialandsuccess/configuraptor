import datetime as dt
import math
import typing

import pytest

from src import configuraptor
from src.configuraptor.errors import (
    ConfigError,
    ConfigErrorInvalidType,
    ConfigErrorMissingKey,
)

from .constants import EMPTY_FILE, EXAMPLE_FILE, PYTEST_EXAMPLES, _load_toml


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
    empty = configuraptor.load_into(Empty, {})
    assert empty and empty.default == "allowed"

    with pytest.raises(ConfigError):
        configuraptor.load_into(Tool, {})

    with pytest.raises(ConfigError):
        configuraptor.load_into(First, EMPTY_FILE, key="tool.first")


class MyConfig:
    public_key: str
    private_key: str
    extra: int


def test_multiple_files():
    public_file = str(PYTEST_EXAMPLES / "my_config.toml")
    private_file = str(PYTEST_EXAMPLES / "my_secrets.env")

    config = configuraptor.load_into(
        MyConfig,
        [public_file, private_file, {"extra": 3}],  # toml  # .env  # raw dict
        key="my_config.custom"  # should work even if only relevant for toml file
        # lower keys is automatically set to True
    )

    assert config.public_key == "this is public"
    assert config.private_key == "THIS IS PRIVATE" != "<overwite me>"


def test_basic_classes():
    data = _load_toml()

    tool = configuraptor.load_into(Tool, data)
    first = configuraptor.load_into(First, EXAMPLE_FILE, key="tool.first")

    assert tool.first.extra["name"]["first"] == first.extra["name"]["first"]


class Relevant:
    key: str


class OptionalRelevant:
    key: typing.Optional[str]


class Irrelevant:
    key: dict


def test_guess_key_from_multiple_keys():
    file = str(PYTEST_EXAMPLES / "with_multiple_toplevel_keys.toml")
    relevant = configuraptor.load_into(Relevant, file)
    assert relevant and relevant.key == "this one!"


def test_guess_key_no_match():
    file = str(PYTEST_EXAMPLES / "with_multiple_toplevel_keys.toml")
    # no key and no match by class name:
    relevant = configuraptor.load_into(Irrelevant, file)
    assert relevant and relevant.key["value"] == "fallback"


class TooLong:
    type: str


def test_invalid_type():
    file = str(PYTEST_EXAMPLES / "with_multiple_toplevel_keys.toml")
    with pytest.raises(ConfigErrorInvalidType):
        # tool.key contains an int instead of a str
        configuraptor.load_into(Relevant, file, key="tool")

    with pytest.raises(ConfigErrorInvalidType):
        # complex.type is a long dict but is typed as string.
        # it will be truncated in the error message
        try:
            configuraptor.load_into(TooLong, file, key="complex")
        except ConfigErrorInvalidType as e:
            assert "..." in str(e)
            raise e


def test_missing_key():
    file = str(PYTEST_EXAMPLES / "with_multiple_toplevel_keys.toml")
    with pytest.raises(ConfigErrorMissingKey):
        # key.key does not exist
        try:
            configuraptor.load_into(Relevant, file, key="key")
        except ConfigErrorMissingKey as e:
            assert "Config key 'key'" in str(e)
            raise e

    # allowed here since 'key' is optional:
    inst = configuraptor.load_into(OptionalRelevant, file, key="key")
    assert inst.key is None


class Point:
    x: int
    y: int


class Structure:
    # contents: dict[str, Point]
    contents: dict[str, Point]


def test_dict_of_custom():
    file = PYTEST_EXAMPLES / "with_dict_of_custom.toml"

    structure = configuraptor.load_into(Structure, file)
    for key, value in structure.contents.items():
        assert isinstance(key, str)
        assert isinstance(value, Point)


try:
    import contextlib

    chdir = contextlib.chdir
except AttributeError:
    from contextlib_chdir import chdir


class ProjectToml:
    my_key: str


def test_pyproject_toml():
    with chdir("pytest_examples/nested"):
        config = configuraptor.load_into(ProjectToml, key="tool.configuraptor.test")

    assert config.my_key == "my_value"


class ShouldHaveListOfString:
    required: list[str]
    not_required: typing.Optional[list[str]]


def test_missing_required_parameterized():
    # should go through is_optional -> is_parameterized -> typing.get_origin(_type) in (dict, list) -> False -> Error
    data = {"not_required": ["list", "of", "string"]}
    with pytest.raises(ConfigErrorMissingKey):
        configuraptor.load_into(ShouldHaveListOfString, data)
