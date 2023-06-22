"""
Logic for the TypedConfig inheritable class.
"""

import typing
from collections.abc import Mapping, MutableMapping
from typing import Any, Iterator

from .core import T_data, all_annotations, check_type, load_into
from .errors import ConfigErrorExtraKey, ConfigErrorImmutable, ConfigErrorInvalidType

C = typing.TypeVar("C", bound=Any)


class TypedConfig:
    """
    Can be used instead of load_into.
    """

    @classmethod
    def load(cls: typing.Type[C], data: T_data, key: str = None, init: dict[str, Any] = None, strict: bool = True) -> C:
        """
        Load a class' config values from the config file.

        SomeClass.load(data, ...) = load_into(SomeClass, data, ...).
        """
        return load_into(cls, data, key=key, init=init, strict=strict)

    def _update(self, _strict: bool = True, _allow_none: bool = False, **values: Any) -> None:
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

            self.__dict__[key] = value
            # setattr(self, key, value)

    def update(self, _strict: bool = True, _allow_none: bool = False, **values: Any) -> None:
        """
        Update values on this config.

        Args:
            _strict: allow wrong types?
            _allow_none: allow None or skip those entries?
            **values: key: value pairs in the right types to update.
        """
        return self._update(_strict, _allow_none, **values)

    @classmethod
    def _all_annotations(cls) -> dict[str, type]:
        """
        Shortcut to get all annotations.
        """
        return all_annotations(cls)

    def _format(self, string: str) -> str:
        """
        Format the config data into a string template.

        Replacement for string.format(**config), which is only possible for MutableMappings.
        MutableMapping does not work well with our Singleton Metaclass.
        """
        return string.format(**self.__dict__)

    def __setattr__(self, key: str, value: typing.Any) -> None:
        """
        Updates should have the right type.

        If you want a non-strict option, use _update(strict=False).
        """
        if key.startswith("_"):
            return super().__setattr__(key, value)
        self._update(**{key: value})


K = typing.TypeVar("K", bound=str)
V = typing.TypeVar("V", bound=Any)


class TypedMappingAbstract(TypedConfig, Mapping[K, V]):
    """
    Note: this can't be used as a singleton!

    Don't use directly, choose either TypedMapping (immutable) or TypedMutableMapping (mutable).
    """

    def __getitem__(self, key: K) -> V:
        """
        Dict-notation to get attribute.

        Example:
            my_config[key]
        """
        return typing.cast(V, self.__dict__[key])

    def __len__(self) -> int:
        """
        Required for Mapping.
        """
        return len(self.__dict__)

    def __iter__(self) -> Iterator[K]:
        """
        Required for Mapping.
        """
        # keys is actually a `dict_keys` but mypy doesn't need to know that
        keys = typing.cast(list[K], self.__dict__.keys())
        return iter(keys)


class TypedMapping(TypedMappingAbstract[K, V]):
    """
    Note: this can't be used as a singleton!
    """

    def _update(self, *_: Any, **__: Any) -> None:
        raise ConfigErrorImmutable(self.__class__)


class TypedMutableMapping(TypedMappingAbstract[K, V], MutableMapping[K, V]):
    """
    Note: this can't be used as a singleton!
    """

    def __setitem__(self, key: str, value: V) -> None:
        """
        Dict notation to set attribute.

        Example:
            my_config[key] = value
        """
        self.update(**{key: value})

    def __delitem__(self, key: K) -> None:
        """
        Dict notation to delete attribute.

        Example:
            del my_config[key]
        """
        del self.__dict__[key]

    def update(self, *args: Any, **kwargs: V) -> None:  # type: ignore
        """
        Ensure TypedConfig.update is used en not MutableMapping.update.
        """
        return TypedConfig._update(self, *args, **kwargs)


# also expose as separate function:
def update(self: Any, _strict: bool = True, _allow_none: bool = False, **values: Any) -> None:
    """
    Update values on a config.

    Args:
        self: config instance to update
        _strict: allow wrong types?
        _allow_none: allow None or skip those entries?
        **values: key: value pairs in the right types to update.
    """
    return TypedConfig._update(self, _strict, _allow_none, **values)
