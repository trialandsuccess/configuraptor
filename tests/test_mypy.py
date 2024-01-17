import typing

import pytest

from src.configuraptor import load_into, asjson, asdict


class Test:
    ...


@pytest.mark.mypy_testing
def mypy_test_invalid_assignment() -> None:
    test = load_into(Test, {})

    typing.reveal_type(test)  # R: tests.test_mypy.Test


@pytest.mark.mypy_testing
def mypy_test_asjson() -> None:
    jsonified = asjson("-")

    typing.reveal_type(jsonified)  # R: builtins.str


@pytest.mark.mypy_testing
def mypy_test_asdict() -> None:
    dictified = asdict(Test)

    typing.reveal_type(dictified)  # R: builtins.dict[builtins.str, Any]
