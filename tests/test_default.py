import typing as t

import pytest

from configuraptor.helpers import strip_annotated
from src.configuraptor import Defaultable, all_annotations, load_into, postpone
from src.configuraptor.errors import ConfigErrorMissingKey

class SomethingWithDefault(Defaultable):
    value: t.Annotated[str, "test"]

    @classmethod
    def default(cls):
        return load_into(cls, {"value": "DEFAULT VALUE"})


class SomethingElse(Defaultable):
    yah: int = postpone()

    def __post_init__(self):
        self.yah = 420


class SomeConfig(Defaultable):
    something: t.Annotated[SomethingWithDefault, "Something"]
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

