"""
Contains stand-alone helper functions.
"""

import os
import typing

import black.files


def camel_to_snake(s: str) -> str:
    """
    Convert CamelCase to snake_case.

    Source:
        https://stackoverflow.com/questions/1175208/elegant-python-function-to-convert-camelcase-to-snake-case
    """
    return "".join([f"_{c.lower()}" if c.isupper() else c for c in s]).lstrip("_")


def find_pyproject_toml() -> typing.Optional[str]:
    """
    Find the project's config toml, looks up until it finds the project root (black's logic).
    """
    return black.files.find_pyproject_toml((os.getcwd(),))
