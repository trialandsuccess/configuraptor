import json
import typing

import pytest

from src.configuraptor import load_into
from src.configuraptor.beautify import beautify


@beautify
class MyClass:
    string: str
    number: int


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

    assert "MyOtherClass" in repr(test2)
    assert "number" in repr(test2)
    assert "True" in repr(test2)

    assert repr(test3) == "dont-touch-me"
