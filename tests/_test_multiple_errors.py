import pytest

from src.configuraptor import load_into
from src.configuraptor.errors import ConfigErrorGroup, ConfigErrorMissingKey, ConfigErrorInvalidType


class MultipleRequired:
    first: str
    second: int
    third: list[str]
    fourth: list[list[int]]


def test_exception_group_missing():
    with pytest.raises(ConfigErrorGroup):
        load_into(MultipleRequired, {})

    # or with star except:
    try:
        load_into(MultipleRequired, {})
        assert False
    except* ConfigErrorMissingKey:
        pass

def test_exception_group_wrong():
    data = {
        "first": 0,
        "second": "",
        "third": [1],
        "fourth": [None],
    }

    with pytest.raises(ConfigErrorGroup):
        load_into(MultipleRequired, data, key="")

    # or with star except:
    try:
        load_into(MultipleRequired, data, key="")
        assert False
    except* ConfigErrorInvalidType:
        pass
