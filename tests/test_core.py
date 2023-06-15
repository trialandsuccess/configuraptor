# not directly testable
import math
import sys
import typing

import pytest

from src.configuraptor import all_annotations
from src.configuraptor.core import is_optional
from tests.constants import EXAMPLE_FILE

if sys.version_info > (3, 11):

    def test_loader_310_fails():
        with pytest.raises(EnvironmentError):
            from src.configuraptor.loaders.loaders_310 import toml

            toml()

    def test_loader_311_works():
        from src.configuraptor.loaders.loaders_311 import toml

        with open(EXAMPLE_FILE, "rb") as f:
            assert toml(f)

else:

    def test_loader_311_fails():
        with pytest.raises(EnvironmentError):
            from src.configuraptor.loaders.loaders_311 import toml

            toml()


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
