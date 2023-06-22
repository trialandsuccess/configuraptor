import typing

import pytest

from src.configuraptor import load_into


class Test:
    ...


@pytest.mark.mypy_testing
def mypy_test_invalid_assignment() -> None:
    test = load_into(Test, {})

    typing.reveal_type(test)  # R: tests.test_mypy.Test
