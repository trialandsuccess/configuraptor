import json
import typing

import pytest

from src.configuraptor import load_into, TypedConfig
from src.configuraptor.beautify import beautify


@beautify
class MyClass:
    string: str
    number: int
    _internal: bool = False


@beautify(repr=True, str=False)
class MyOtherClass:
    number: float
    boolean: bool


@beautify()
class CustomRepr:
    some: str

    def __repr__(self) -> str:
        return "dont-touch-me"

    def __str__(self) -> str:
        return 'dont-touch-me-either'


class FromTypedConfig(TypedConfig):
    # should be auto-beautified
    another: bool


class NoBeautify(TypedConfig, beautify=False):
    # should NOT be auto-beautified
    beautiful: bool


test1 = load_into(MyClass, {'string': '123', 'number': 123})
test2 = load_into(MyOtherClass, {'number': 12.3, 'boolean': True})
test3 = load_into(CustomRepr, {"some": "value"})


@pytest.mark.mypy_testing
def mypy_test_decorated_cls() -> None:
    typing.reveal_type(test1)  # R: tests.test_beautify.MyClass
    typing.reveal_type(test2)  # R: tests.test_beautify.MyOtherClass


def test_str() -> None:
    assert json.loads(str(test1))

    with pytest.raises(json.JSONDecodeError):
        # str=False so it shouldn't be json-able
        assert json.loads(str(test2))

    assert str(test3) == "dont-touch-me-either"


def test_repr() -> None:
    assert "MyClass" in repr(test1)
    assert "string" in repr(test1)
    assert "123" in repr(test1)
    assert "_internal" not in repr(test1)
    assert "_internal" not in str(test1)

    assert "MyOtherClass" in repr(test2)
    assert "number" in repr(test2)
    assert "True" in repr(test2)

    assert repr(test3) == "dont-touch-me"


def test_from_typedconfig() -> None:
    inst = FromTypedConfig.load({"another": True})

    assert "<FromTypedConfig" in repr(inst)
    assert "another" in repr(inst)
    assert "True" in repr(inst)

    assert "<FromTypedConfig" not in str(inst)
    assert "another" in str(inst)
    assert "true" in str(inst)
    assert json.loads(str(inst))


def test_nobeautify() -> None:
    ugly = NoBeautify.load({"beautiful": False})

    assert "<NoBeautify" not in repr(ugly)
    assert "beautiful" not in repr(ugly)
    assert "False" not in repr(ugly)

    assert "<NoBeautify" not in str(ugly)
    assert "beautiful" not in str(ugly)
    assert "false" not in str(ugly)

    with pytest.raises(json.JSONDecodeError):
        assert not json.loads(str(ugly))
