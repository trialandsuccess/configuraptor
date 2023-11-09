"""
Logic for the TypedConfig inheritable class.
"""
import copy
import os
import typing
from collections.abc import Mapping, MutableMapping
from typing import Any, Iterator

from typing_extensions import Never, Self

from . import Alias
from .abs import AbstractTypedConfig
from .core import check_and_convert_type, has_aliases
from .errors import ConfigErrorExtraKey, ConfigErrorImmutable
from .helpers import all_annotations
from .loaders.loaders_shared import _convert_key

C = typing.TypeVar("C", bound=Any)


class TypedConfig(AbstractTypedConfig):
    """
    Can be used instead of load_into.
    """

    def _update(
        self,
        _strict: bool = True,
        _allow_none: bool = False,
        _overwrite: bool = True,
        _ignore_extra: bool = False,
        _lower_keys: bool = False,
        _normalize_keys: bool = True,
        _convert_types: bool = False,
        _update_aliases: bool = True,
        **values: Any,
    ) -> Self:
        """
        Underscore version can be used if .update is overwritten with another value in the config.
        """
        annotations = all_annotations(self.__class__)

        for key, value in values.items():
            if _lower_keys:
                key = key.lower()

            if _normalize_keys:
                # replace - with _
                key = _convert_key(key)

            if value is None and not _allow_none:
                continue

            existing_value = self.__dict__.get(key)
            if existing_value is not None and not _overwrite:
                # fill mode, don't overwrite
                continue

            if _strict and key not in annotations:
                if _ignore_extra:
                    continue
                else:
                    raise ConfigErrorExtraKey(cls=self.__class__, key=key, value=value)

            # check_and_convert_type
            if _strict and not (value is None and _allow_none):
                value = check_and_convert_type(value, annotations[key], convert_types=_convert_types, key=key)

            self.__dict__[key] = value
            # setattr(self, key, value)

            if _update_aliases:
                cls = self.__class__
                prop = cls.__dict__.get(key)
                if isinstance(prop, Alias):
                    self.__dict__[prop.to] = value
                else:
                    for alias in has_aliases(cls, key):
                        self.__dict__[alias] = value

        return self

    def update(
        self,
        _strict: bool = True,
        _allow_none: bool = False,
        _overwrite: bool = True,
        _ignore_extra: bool = False,
        _lower_keys: bool = False,
        _normalize_keys: bool = True,
        _convert_types: bool = False,
        _update_aliases: bool = True,
        **values: Any,
    ) -> Self:
        """
        Update values on this config.

        Args:
            _strict: allow wrong types?
            _allow_none: allow None or skip those entries?
            _overwrite: also update not-None values?
            _ignore_extra: skip additional keys that aren't in the object.
            _lower_keys: set the keys to lowercase (useful for env)
            _normalize_keys: change - to _
            _convert_types: try to convert variables to the right type if they aren't yet
            _update_aliases: also update related fields?

            **values: key: value pairs in the right types to update.
        """
        return self._update(
            _strict=_strict,
            _allow_none=_allow_none,
            _overwrite=_overwrite,
            _ignore_extra=_ignore_extra,
            _lower_keys=_lower_keys,
            _normalize_keys=_normalize_keys,
            _convert_types=_convert_types,
            _update_aliases=_update_aliases,
            **values,
        )

    def __or__(self, other: dict[str, Any]) -> Self:
        """
        Allows config |= {}.

        Where {} is a dict of new data and optionally settings (starting with _)

        Returns an updated clone of the original object, so this works too:
        new_config = config | {...}
        """
        to_update = self._clone()
        return to_update._update(**other)

    def update_from_env(self) -> Self:
        """
        Update (in place) using the current environment variables, lowered etc.

        Ignores extra env vars.
        """
        return self._update(_ignore_extra=True, _lower_keys=True, _convert_types=True, **os.environ)

    def _fill(self, _strict: bool = True, **values: typing.Any) -> Self:
        """
        Alias for update without overwrite.

        Underscore version can be used if .fill is overwritten with another value in the config.
        """
        return self._update(_strict, _allow_none=False, _overwrite=False, **values)

    def fill(self, _strict: bool = True, **values: typing.Any) -> Self:
        """
        Alias for update without overwrite.
        """
        return self._update(_strict, _allow_none=False, _overwrite=False, **values)

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

    def _clone(self) -> Self:
        return copy.deepcopy(self)


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

    def _update(self, *_: Any, **__: Any) -> Never:
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

    def update(self, *args: Any, **kwargs: V) -> Self:  # type: ignore
        """
        Ensure TypedConfig.update is used en not MutableMapping.update.
        """
        return TypedConfig._update(self, *args, **kwargs)


T = typing.TypeVar("T", bound=TypedConfig)


# also expose as separate function:
def update(self: T, _strict: bool = True, _allow_none: bool = False, **values: Any) -> T:
    """
    Update values on a config.

    Args:
        self: config instance to update
        _strict: allow wrong types?
        _allow_none: allow None or skip those entries?
        **values: key: value pairs in the right types to update.
    """
    return TypedConfig._update(self, _strict, _allow_none, **values)
