"""
Logic for the TypedConfig inheritable class.
"""

import typing

from .core import T_data, load_into

C = typing.TypeVar("C", bound=typing.Any)


class TypedConfig:
    """
    Can be used instead of load_into.
    """

    @classmethod
    def load(
        cls: typing.Type[C], data: T_data, key: str = None, init: dict[str, typing.Any] = None, strict: bool = True
    ) -> C:
        """
        Load a class' config values from the config file.

        SomeClass.load(data, ...) = load_into(SomeClass, data, ...).
        """
        return load_into(cls, data, key=key, init=init, strict=strict)
