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

    def _update(self, _strict: bool = True, _allow_none: bool = False, **values: typing.Any) -> None:
        """
        Can be used if .update is overwritten with another value in the config.
        """
        annotations = all_annotations(self.__class__)

        for key, value in values.items():
            if value is None and not _allow_none:
                continue

            if _strict and key not in annotations:
                raise ConfigErrorExtraKey(cls=self.__class__, key=key, value=value)

            if _strict and not check_type(value, annotations[key]) and not (value is None and _allow_none):
                raise ConfigErrorInvalidType(expected_type=annotations[key], key=key, value=value)

            setattr(self, key, value)

    def update(self, _strict: bool = True, _allow_none: bool = False, **values: typing.Any) -> None:
        """
        Update values on this config.

        Args:
            _strict: allow wrong types?
            _allow_none: allow None or skip those entries?
            **values: key: value pairs in the right types to update.
        """
        return self._update(_strict, _allow_none, **values)


# also expose as separate function:
def update(instance: typing.Any, _strict: bool = True, _allow_none: bool = False, **values: typing.Any) -> None:
    """
    Update values on a config.

    Args:
        instance: config instance to update
        _strict: allow wrong types?
        _allow_none: allow None or skip those entries?
        **values: key: value pairs in the right types to update.
    """
    return TypedConfig._update(instance, _strict, _allow_none, **values)
