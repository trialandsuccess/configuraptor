"""
Contains most of the loading logic.
"""

import tomllib
import types
import typing
from collections import ChainMap
from dataclasses import is_dataclass
from pathlib import Path

from typeguard import TypeCheckError
from typeguard import check_type as _check_type

from .errors import ConfigErrorInvalidType, ConfigErrorMissingKey
from .helpers import camel_to_snake

T = typing.TypeVar("T")
T_typelike: typing.TypeAlias = type | types.UnionType  # | typing.Union
T_data = str | Path | dict[str, typing.Any]


def _data_for_nested_key(key: str, raw: dict[str, typing.Any]) -> dict[str, typing.Any]:
    """
    If a key contains a dot, traverse the raw dict until the right key was found.

    Example:
        key = some.nested.key
        raw = {"some": {"nested": {"key": {"with": "data"}}}}
        -> {"with": "data"}
    """
    parts = key.split(".")
    while parts:
        raw = raw[parts.pop(0)]

    return raw


def _guess_key(clsname: str) -> str:
    """
    If no key is manually defined for `load_into`, \
    the class' name is converted to snake_case to use as the default key.
    """
    return camel_to_snake(clsname)


def _load_data(data: T_data, key: str = None, classname: str = None) -> dict[str, typing.Any]:
    if isinstance(data, str):
        data = Path(data)
    if isinstance(data, Path):
        # todo: more than toml
        with data.open("rb") as f:
            data = tomllib.load(f)

    if not data:
        return {}

    if key is None:
        # try to guess key by grabbing the first one or using the class name
        if len(data) == 1:
            key = list(data.keys())[0]
        elif classname is not None:
            key = _guess_key(classname)

    if key:
        return _data_for_nested_key(key, data)
    else:
        # no key found, just return all data
        return data


def check_type(value: typing.Any, expected_type: T_typelike) -> bool:
    """
    Given a variable, check if it matches 'expected_type' (which can be a Union, parameterized generic etc.).

    Based on typeguard but this returns a boolean instead of returning the value or throwing a TypeCheckError
    """
    try:
        _check_type(value, expected_type)
        return True
    except TypeCheckError:
        return False


def ensure_types(data: dict[str, T], annotations: dict[str, type]) -> dict[str, T | None]:
    """
    Make sure all values in 'data' are in line with the ones stored in 'annotations'.

    If an annotated key in missing from data, it will be filled with None for convenience.
    """
    # custom object to use instead of None, since typing.Optional can be None!
    # cast to T to make mypy happy
    notfound = typing.cast(T, object())

    final: dict[str, T | None] = {}
    for key, _type in annotations.items():
        compare = data.get(key, notfound)
        if compare is notfound:
            # skip!
            continue
        if not check_type(compare, _type):
            raise ConfigErrorInvalidType(key, value=compare, expected_type=_type)

        final[key] = compare
    return final


def convert_config(items: dict[str, T]) -> dict[str, T]:
    """
    Converts the config dict (from toml) or 'overwrites' dict in two ways.

    1. removes any items where the value is None, since in that case the default should be used;
    2. replaces '-' and '.' in keys with '_' so it can be mapped to the Config properties.
    """
    return {k.replace("-", "_").replace(".", "_"): v for k, v in items.items() if v is not None}


Type = typing.Type[typing.Any]
T_Type = typing.TypeVar("T_Type", bound=Type)


def is_builtin_type(_type: Type) -> bool:
    return _type.__module__ in ("__builtin__", "builtins")


def is_builtin_class_instance(obj: typing.Any) -> bool:
    return is_builtin_type(obj.__class__)


def is_from_types_or_typing(_type: Type) -> bool:
    # e.g. types.UnionType or typing.Union
    return _type.__module__ in ("types", "typing")


def is_from_other_toml_supported_module(_type: Type) -> bool:
    return _type.__module__ in ("datetime", "math")


def is_parameterized(_type: Type) -> bool:
    return typing.get_origin(_type) is not None


def is_custom_class(_type: Type) -> bool:
    return (
        type(_type) is type
        and not is_builtin_type(_type)
        and not is_from_other_toml_supported_module(_type)
        and not is_from_types_or_typing(_type)
    )


def is_optional(_type: Type | None) -> bool:
    return (
        _type is None
        or issubclass(types.NoneType, _type)
        or issubclass(types.NoneType, type(_type))  # no type  # Nonetype
        or type(None) in typing.get_args(_type)  # union with Nonetype
    )


def load_recursive(cls: Type, data: dict[str, T], annotations: dict[str, Type]) -> dict[str, T]:
    updated = {}
    for _key, _type in annotations.items():
        if _key in data:
            value: typing.Any = data[_key]  # value can change so define it as any instead of T
            if is_parameterized(_type):
                origin = typing.get_origin(_type)
                arguments = typing.get_args(_type)
                if origin is list and arguments and is_custom_class(arguments[0]):
                    subtype = arguments[0]
                    value = [load_into_recurse(subtype, subvalue) for subvalue in value]

                elif origin is dict and arguments and is_custom_class(arguments[1]):
                    subkey, subtype = arguments
                    value = {subkey: load_into_recurse(subtype, subvalue) for subvalue in value.values()}
                # elif origin is dict:
                # keep data the same
                elif origin is typing.Union and arguments:
                    for arg in arguments:
                        if is_custom_class(arg):
                            value = load_into_recurse(arg, value)
                        else:
                            print(_type, arg, value)

                # todo: other parameterized/unions/typing.Optional

            elif is_custom_class(_type):
                value = load_into_recurse(_type, value)

        elif _key in cls.__dict__:
            # property has default, use that instead.
            value = cls.__dict__[_key]
        elif is_optional(_type):
            # type is optional and not found in __dict__ -> default is None
            value = None
        else:
            # todo: exception group?
            raise ConfigErrorMissingKey(_key, cls, _type)

        updated[_key] = value

    return updated


def _all_annotations(cls: Type) -> ChainMap[str, Type]:
    """Returns a dictionary-like ChainMap that includes annotations for all
    attributes defined in cls or inherited from superclasses."""
    return ChainMap(*(c.__annotations__ for c in getattr(cls, "__mro__", []) if "__annotations__" in c.__dict__))


def all_annotations(cls: Type) -> dict[str, Type]:
    return dict(_all_annotations(cls))


C = typing.TypeVar("C")


def load_into_recurse(cls: typing.Type[C], data: dict[str, typing.Any]) -> C:
    annotations = all_annotations(cls)
    to_load = convert_config(data)
    to_load = load_recursive(cls, to_load, annotations)
    to_load = ensure_types(to_load, annotations)

    if is_dataclass(cls):
        # ensure mypy inst is an instance of the cls type (and not a fictuous `DataclassInstance`)
        inst = typing.cast(C, cls(**to_load))
    else:
        inst = cls()
        inst.__dict__.update(**to_load)

    return inst


def load_into(cls: typing.Type[C], data: T_data, key: str = None) -> C:
    to_load = _load_data(data, key, cls.__name__)

    return load_into_recurse(cls, to_load)
