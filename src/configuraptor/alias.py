"""
Alias functionality so config keys can have multiple names.
"""

import typing
from dataclasses import dataclass
from typing import Any

from .abs import AnyType, T


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


def has_aliases(cls: AnyType, key: str) -> typing.Generator[str, None, None]:
    """
    Generate all aliases that point to 'key' in 'cls'.
    """
    for field, value in cls.__dict__.items():
        if isinstance(value, Alias) and value.to == key:
            yield field


def has_alias(cls: AnyType, key: str, data: dict[str, T]) -> typing.Optional[T]:
    """
    Get the value of any alias in the same config class that references `key`.

    Example:
        class Config:
            key1: str
            key2: str = alias('key1')

    load_into(Config, {'key2': 'something'})
    # -> key1 will look up the value of key2 because it's configured as an alias for it.

    If multiple aliases point to the same base, they are all iterated until a valid value was found.
    """
    # for field, value in cls.__dict__.items():
    #     if isinstance(value, Alias) and value.to == key:
    #         # yay!
    #         return data.get(field)
    #
    # return None

    return next(
        (value for field in has_aliases(cls, key) if (value := data.get(field))),
        None,
    )


def is_alias(cls: AnyType, prop: str) -> bool:
    """
    Returns whether 'prop' is an alias to something else on cls.
    """
    return isinstance(cls.__dict__.get(prop), Alias)
