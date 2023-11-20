"""
Alias functionality so config keys can have multiple names.
"""

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class Alias:
    """
    Internal class used to relate keys.
    """

    to: str


def alias(to: str) -> Any:
    """
    Function to create an alias to a different key in the same class.
    """
    return Alias(to)
