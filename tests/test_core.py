# not directly testable
import math
import sys
import typing

import pytest

from src.configuraptor import all_annotations
from src.configuraptor.core import is_optional
from tests.constants import EXAMPLE_FILE


def test_invalid_extension():
    from src.configuraptor.loaders import get

    with pytest.raises(ValueError):
        get(".doesntexist")


def test_is_optional_with_weird_inputs():
    assert is_optional(math.nan) is False
    assert is_optional(typing.Optional[dict[str, typing.Optional[str]]]) is True


class Base:
    has: int


class Sub(Base):
    has_also: int


def test_all_annotations():
    # without except:
    assert set(all_annotations(Sub).keys()) == {"has", "has_also"}
    # with except:
    assert set(all_annotations(Sub, {"has_also"}).keys()) == {"has"}


def test_no_data():
    from src import configuraptor

    # data must be a dict:
    with pytest.raises(ValueError):
        configuraptor.core._load_data(42, key=None)
    with pytest.raises(ValueError):
        configuraptor.core._load_data(["joe"], key=None)

    # but other than that, it should be fine:
    configuraptor.core._load_data({}, key="")
    configuraptor.core._load_data({}, key=None)
    configuraptor.core._load_data({"-": 0, "+": None}, key="joe", classname="-.+")
    configuraptor.core._load_data({"-": 0, "+": None}, key="+", classname="-.+")
    configuraptor.core._load_data({"-": 0, "+": None}, key="", classname="-.+")
    configuraptor.core._load_data({"-": 0, "+": None}, key=None, classname="-.+")
