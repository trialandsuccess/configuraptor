"""
Logic for the TypedConfig inheritable class.
"""

import typing

from .core import T_data, all_annotations, check_type, load_into
from .errors import ConfigErrorExtraKey, ConfigErrorInvalidType

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

    def update(self, strict: bool = True, allow_none: bool = False, **values: typing.Any) -> None:
        """
        Update values on this config.

        Args:
            strict: allow wrong types?
            allow_none: allow None or skip those entries?
            **values: key: value pairs in the right types to update.

        """
        annotations = all_annotations(self.__class__)

        for key, value in values.items():
            if value is None and not allow_none:
                continue

            if strict and key not in annotations:
                raise ConfigErrorExtraKey(cls=self.__class__, key=key, value=value)

            if strict and not check_type(value, annotations[key]) and not (value is None and allow_none):
                raise ConfigErrorInvalidType(expected_type=annotations[key], key=key, value=value)

            setattr(self, key, value)
