from typing import Optional

import pytest

from src.configuraptor import TypedConfig, alias, load_into, postpone
from src.configuraptor.core import check_and_convert_type
from src.configuraptor.errors import ConfigError


class MyConfig:
    key_one: str
    key_two: str = alias("key_one")


class MyConfigInvalid(TypedConfig):
    key_three: str = alias("key_four")
    key_four: str = alias("key_three")


class AliasWithPostponed(TypedConfig):
    first: str = postpone()
    second: str = alias("first")


class MyConfigInvalidTwo(TypedConfig):
    key_five: str = alias("key_five")


class UnresolvedOptionalAlias(TypedConfig):
    fro: Optional[str]
    to: Optional[str] = alias("fro")


def test_it():
    conf1 = load_into(MyConfig, {"key_one": "one"})

    assert conf1.key_one == conf1.key_two == "one"

    conf2 = load_into(MyConfig, {"key_two": "two"})

    assert conf2.key_one == conf2.key_two == "two"

    # normal one should have priority over alias field:
    conf3 = load_into(MyConfig, {"key_one": "ONE", "key_two": "two"})

    assert conf3.key_one == "ONE"

    conf = UnresolvedOptionalAlias.load()

    assert conf.fro is None
    assert conf.to is None

    assert check_and_convert_type(alias("something"), Optional[str], False) is None


def test_with_postpone():
    c = AliasWithPostponed.load({"first": "one"})

    assert c.first == c.second == "one"

    c.update(first="two")

    assert c.first == c.second == "two"

    c.update(second="two2")

    assert c.first == c.second == "two2"

    c = AliasWithPostponed.load({})
    c.first = "three"
    assert c.first == c.second == "three"

    c.second = "three2"
    assert c.first == c.second == "three2"


def test_invalid():
    with pytest.raises(ConfigError):
        load_into(MyConfigInvalid, {})

    assert load_into(MyConfigInvalid, {"key_three": "3"})
    assert load_into(MyConfigInvalid, {"key_four": "4"})

    with pytest.raises(ConfigError):
        load_into(MyConfigInvalidTwo, {})

    assert load_into(MyConfigInvalidTwo, {"key_five": "123"})
