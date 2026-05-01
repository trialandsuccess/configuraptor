import pytest

from src.configuraptor import Defaultable, load_into, postpone
from src.configuraptor.errors import ConfigErrorMissingKey


class SomethingWithDefault(Defaultable):
    value: str

    @classmethod
    def default(cls):
        return load_into(cls, {"value": "DEFAULT VALUE"})


class SomethingElse(Defaultable):
    yah: int = postpone()

    def __post_init__(self):
        self.yah = 420


class SomeConfig(Defaultable):
    something: SomethingWithDefault
    other: SomethingElse


def test_default():
    some_config = load_into(SomeConfig, {})

    assert some_config.something.value == "DEFAULT VALUE"
    assert some_config.other.yah == 420


class SomethingWithoutDefault(Defaultable):
    value: str


class SomeConfigWithoutDefault(Defaultable):
    something: SomethingWithoutDefault


def test_default_requires_defaultable_base():
    with pytest.raises(ConfigErrorMissingKey):
        load_into(SomeConfigWithoutDefault, {})
