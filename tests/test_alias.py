import pytest

from src.configuraptor import TypedConfig, alias, load_into
from src.configuraptor.errors import ConfigError


class MyConfig:
    key_one: str
    key_two: str = alias("key_one")


class MyConfigInvalid(TypedConfig):
    key_three: str = alias("key_four")
    key_four: str = alias("key_three")


class MyConfigInvalidTwo(TypedConfig):
    key_five: str = alias("key_five")


def test_it():
    conf1 = load_into(MyConfig, {"key_one": "one"})

    assert conf1.key_one == conf1.key_two == "one"

    conf2 = load_into(MyConfig, {"key_two": "two"})

    assert conf2.key_one == conf2.key_two == "two"


def test_invalid():
    with pytest.raises(ConfigError):
        load_into(MyConfigInvalid, {})

    assert load_into(MyConfigInvalid, {"key_three": "3"})
    assert load_into(MyConfigInvalid, {"key_four": "4"})

    with pytest.raises(ConfigError):
        load_into(MyConfigInvalidTwo, {})

    assert load_into(MyConfigInvalidTwo, {"key_five": "123"})
