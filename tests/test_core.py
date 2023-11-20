# not directly testable
import io
import math
import typing
from pathlib import Path

import pytest

from src.configuraptor import all_annotations
from src.configuraptor.core import is_optional
from src.configuraptor.helpers import as_binaryio
from src.configuraptor.type_converters import str_to_none


def test_invalid_extension():
    from src.configuraptor.loaders import get

    with pytest.raises(ValueError):
        get(".doesntexist")


def test_is_optional_with_weird_inputs():
    assert is_optional(math.nan) is False
    assert is_optional(typing.Optional[dict[str, typing.Optional[str]]]) is True


def test_as_binaryio():
    path = Path("/tmp/pytest_asbinary_file")
    path.touch()

    with as_binaryio(str(path)) as f:
        assert hasattr(f, "read")

    with as_binaryio(path) as f:
        assert hasattr(f, "read")

    with as_binaryio(open(str(path), "rb")) as f:
        assert hasattr(f, "read")

    with as_binaryio(io.BytesIO()) as f:
        assert hasattr(f, "read")

    with as_binaryio(None) as f:
        assert hasattr(f, "read")


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
        configuraptor.core.load_data(42, key=None)
    with pytest.raises(ValueError):
        configuraptor.core.load_data([], key=None)

    # but other than that, it should be fine:
    configuraptor.core.load_data({}, key="")
    configuraptor.core.load_data({}, key=None)
    configuraptor.core.load_data({"-": 0, "+": None}, key="joe", classname="-.+")
    configuraptor.core.load_data({"-": 0, "+": None}, key="+", classname="-.+")
    configuraptor.core.load_data({"-": 0, "+": None}, key="", classname="-.+")
    configuraptor.core.load_data({"-": 0, "+": None}, key=None, classname="-.+")


def test_str_to_none():
    assert str_to_none("null") == str_to_none("none") == str_to_none("None") == str_to_none("") == None

    assert str_to_none("yeet") != None
