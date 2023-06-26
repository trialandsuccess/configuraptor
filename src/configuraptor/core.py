"""
Contains most of the loading logic.
"""

import dataclasses as dc
import math
import types
import typing
import warnings
from collections import ChainMap
from pathlib import Path

from typeguard import TypeCheckError
from typeguard import check_type as _check_type

from . import loaders
from .errors import ConfigErrorInvalidType, ConfigErrorMissingKey
from .helpers import camel_to_snake
from .postpone import Postponed

# T is a reusable typevar
T = typing.TypeVar("T")
# t_typelike is anything that can be type hinted
T_typelike: typing.TypeAlias = type | types.UnionType  # | typing.Union
# t_data is anything that can be fed to _load_data
T_data = str | Path | dict[str, typing.Any]
# c = a config class instance, can be any (user-defined) class
C = typing.TypeVar("C")
# type c is a config class
Type_C = typing.Type[C]


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


def __load_data(data: T_data, key: str = None, classname: str = None) -> dict[str, typing.Any]:
    """
    Tries to load the right data from a filename/path or dict, based on a manual key or a classname.

    E.g. class Tool will be mapped to key tool.
    It also deals with nested keys (tool.extra -> {"tool": {"extra": ...}}
    """
    if isinstance(data, str):
        data = Path(data)
    if isinstance(data, Path):
        with data.open("rb") as f:
            loader = loaders.get(data.suffix)
            data = loader(f)

    if not data:
        return {}

    if key is None:
        # try to guess key by grabbing the first one or using the class name
        if len(data) == 1:
            key = list(data.keys())[0]
        elif classname is not None:
            key = _guess_key(classname)

    if key:
        data = _data_for_nested_key(key, data)

    if not data:
        raise ValueError("No data found!")

    if not isinstance(data, dict):
        raise ValueError("Data is not a dict!")

    return data


def _load_data(data: T_data, key: str = None, classname: str = None) -> dict[str, typing.Any]:
    """
    Wrapper around __load_data that retries with key="" if anything goes wrong.
    """
    try:
        return __load_data(data, key, classname)
    except Exception as e:
        if key != "":
            return __load_data(data, "", classname)
        else:  # pragma: no cover
            warnings.warn(f"Data could not be loaded: {e}", source=e)
            # key already was "", just return data!
            # (will probably not happen but fallback)
            return {}


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

    TODO: python 3.11 exception groups to throw multiple errors at once!
    """
    # custom object to use instead of None, since typing.Optional can be None!
    # cast to T to make mypy happy
    notfound = typing.cast(T, object())
    postponed = Postponed()

    final: dict[str, T | None] = {}
    for key, _type in annotations.items():
        compare = data.get(key, notfound)
        if compare is notfound:  # pragma: nocover
            warnings.warn(
                "This should not happen since " "`load_recursive` already fills `data` " "based on `annotations`"
            )
            # skip!
            continue

        if compare is postponed:
            # don't do anything with this item!
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
    """
    Returns whether _type is one of the builtin types.
    """
    return _type.__module__ in ("__builtin__", "builtins")


# def is_builtin_class_instance(obj: typing.Any) -> bool:
#     return is_builtin_type(obj.__class__)


def is_from_types_or_typing(_type: Type) -> bool:
    """
    Returns whether _type is one of the stlib typing/types types.

    e.g. types.UnionType or typing.Union
    """
    return _type.__module__ in ("types", "typing")


def is_from_other_toml_supported_module(_type: Type) -> bool:
    """
    Besides builtins, toml also supports 'datetime' and 'math' types, \
    so this returns whether _type is a type from these stdlib modules.
    """
    return _type.__module__ in ("datetime", "math")


def is_parameterized(_type: Type) -> bool:
    """
    Returns whether _type is a parameterized type.

    Examples:
        list[str] -> True
        str -> False
    """
    return typing.get_origin(_type) is not None


def is_custom_class(_type: Type) -> bool:
    """
    Tries to guess if _type is a builtin or a custom (user-defined) class.

    Other logic in this module depends on knowing that.
    """
    return (
        type(_type) is type
        and not is_builtin_type(_type)
        and not is_from_other_toml_supported_module(_type)
        and not is_from_types_or_typing(_type)
    )


def instance_of_custom_class(var: typing.Any) -> bool:
    """
    Calls `is_custom_class` on an instance of a (possibly custom) class.
    """
    return is_custom_class(var.__class__)


def is_optional(_type: Type | typing.Any) -> bool:
    """
    Tries to guess if _type could be optional.

    Examples:
        None -> True
        NoneType -> True
        typing.Union[str, None] -> True
        str | None -> True
        list[str | None] -> False
        list[str] -> False
    """
    if _type and (is_parameterized(_type) and typing.get_origin(_type) in (dict, list)) or (_type is math.nan):
        # e.g. list[str]
        # will crash issubclass to test it first here
        return False

    return (
        _type is None
        or types.NoneType in typing.get_args(_type)  # union with Nonetype
        or issubclass(types.NoneType, _type)
        or issubclass(types.NoneType, type(_type))  # no type  # Nonetype
    )


def dataclass_field(cls: Type, key: str) -> typing.Optional[dc.Field[typing.Any]]:
    """
    Get Field info for a dataclass cls.
    """
    fields = getattr(cls, "__dataclass_fields__", {})
    return fields.get(key)


def load_recursive(cls: Type, data: dict[str, T], annotations: dict[str, Type]) -> dict[str, T]:
    """
    For all annotations (recursively gathered from parents with `all_annotations`), \
    try to resolve the tree of annotations.

    Uses `load_into_recurse`, not itself directly.

    Example:
        class First:
            key: str

        class Second:
            other: First

        # step 1
        cls = Second
        data = {"second": {"other": {"key": "anything"}}}
        annotations: {"other": First}

        # step 1.5
        data = {"other": {"key": "anything"}
        annotations: {"other": First}

        # step 2
        cls = First
        data = {"key": "anything"}
        annotations: {"key": str}


    TODO: python 3.11 exception groups to throw multiple errors at once!
    """
    updated = {}

    for _key, _type in annotations.items():
        if _key in data:
            value: typing.Any = data[_key]  # value can change so define it as any instead of T
            if is_parameterized(_type):
                origin = typing.get_origin(_type)
                arguments = typing.get_args(_type)
                if origin is list and arguments and is_custom_class(arguments[0]):
                    subtype = arguments[0]
                    value = [_load_into_recurse(subtype, subvalue) for subvalue in value]

                elif origin is dict and arguments and is_custom_class(arguments[1]):
                    # e.g. dict[str, Point]
                    subkeytype, subvaluetype = arguments
                    # subkey(type) is not a custom class, so don't try to convert it:
                    value = {subkey: _load_into_recurse(subvaluetype, subvalue) for subkey, subvalue in value.items()}
                # elif origin is dict:
                # keep data the same
                elif origin is typing.Union and arguments:
                    for arg in arguments:
                        if is_custom_class(arg):
                            value = _load_into_recurse(arg, value)
                        else:
                            # print(_type, arg, value)
                            ...

                # todo: other parameterized/unions/typing.Optional

            elif is_custom_class(_type):
                # type must be C (custom class) at this point
                value = _load_into_recurse(
                    # make mypy and pycharm happy by telling it _type is of type C...
                    # actually just passing _type as first arg!
                    typing.cast(Type_C[typing.Any], _type),
                    value,
                )

        elif _key in cls.__dict__:
            # property has default, use that instead.
            value = cls.__dict__[_key]
        elif is_optional(_type):
            # type is optional and not found in __dict__ -> default is None
            value = None
        elif dc.is_dataclass(cls) and (field := dataclass_field(cls, _key)) and field.default_factory is not dc.MISSING:
            # could have a default factory
            # todo: do something with field.default?
            value = field.default_factory()
        else:
            raise ConfigErrorMissingKey(_key, cls, _type)

        updated[_key] = value

    return updated


def _all_annotations(cls: Type) -> ChainMap[str, Type]:
    """
    Returns a dictionary-like ChainMap that includes annotations for all \
    attributes defined in cls or inherited from superclasses.
    """
    return ChainMap(*(c.__annotations__ for c in getattr(cls, "__mro__", []) if "__annotations__" in c.__dict__))


def all_annotations(cls: Type, _except: typing.Iterable[str] = None) -> dict[str, Type]:
    """
    Wrapper around `_all_annotations` that filters away any keys in _except.

    It also flattens the ChainMap to a regular dict.
    """
    if _except is None:
        _except = set()

    _all = _all_annotations(cls)
    return {k: v for k, v in _all.items() if k not in _except}


def check_and_convert_data(
    cls: typing.Type[C],
    data: dict[str, typing.Any],
    _except: typing.Iterable[str],
    strict: bool = True,
) -> dict[str, typing.Any]:
    """
    Based on class annotations, this prepares the data for `load_into_recurse`.

    1. convert config-keys to python compatible config_keys
    2. loads custom class type annotations with the same logic (see also `load_recursive`)
    3. ensures the annotated types match the actual types after loading the config file.
    """
    annotations = all_annotations(cls, _except=_except)

    to_load = convert_config(data)
    to_load = load_recursive(cls, to_load, annotations)
    if strict:
        to_load = ensure_types(to_load, annotations)

    return to_load


T_init_list = list[typing.Any]
T_init_dict = dict[str, typing.Any]
T_init = tuple[T_init_list, T_init_dict] | T_init_list | T_init_dict | None


@typing.no_type_check  # (mypy doesn't understand 'match' fully yet)
def _split_init(init: T_init) -> tuple[T_init_list, T_init_dict]:
    """
    Accept a tuple, a dict or a list of (arg, kwarg), {kwargs: ...}, [args] respectively and turn them all into a tuple.
    """
    if not init:
        return [], {}

    args: T_init_list = []
    kwargs: T_init_dict = {}
    match init:
        case (args, kwargs):
            return args, kwargs
        case [*args]:
            return args, {}
        case {**kwargs}:
            return [], kwargs
        case _:
            raise ValueError("Init must be either a tuple of list and dict, a list or a dict.")


def _load_into_recurse(
    cls: typing.Type[C],
    data: dict[str, typing.Any],
    init: T_init = None,
    strict: bool = True,
) -> C:
    """
    Loads an instance of `cls` filled with `data`.

    Uses `load_recursive` to load any fillable annotated properties (see that method for an example).
    `init` can be used to optionally pass extra __init__ arguments. \
        NOTE: This will overwrite a config key with the same name!
    """
    init_args, init_kwargs = _split_init(init)

    if dc.is_dataclass(cls):
        to_load = check_and_convert_data(cls, data, init_kwargs.keys(), strict=strict)
        if init:
            raise ValueError("Init is not allowed for dataclasses!")

        # ensure mypy inst is an instance of the cls type (and not a fictuous `DataclassInstance`)
        inst = typing.cast(C, cls(**to_load))
    else:
        inst = cls(*init_args, **init_kwargs)
        to_load = check_and_convert_data(cls, data, inst.__dict__.keys(), strict=strict)
        inst.__dict__.update(**to_load)

    return inst


def _load_into_instance(
    inst: C,
    cls: typing.Type[C],
    data: dict[str, typing.Any],
    init: T_init = None,
    strict: bool = True,
) -> C:
    """
    Similar to `load_into_recurse` but uses an existing instance of a class (so after __init__) \
    and thus does not support init.

    """
    if init is not None:
        raise ValueError("Can not init an existing instance!")

    existing_data = inst.__dict__

    to_load = check_and_convert_data(cls, data, _except=existing_data.keys(), strict=strict)

    inst.__dict__.update(**to_load)

    return inst


def load_into_class(
    cls: typing.Type[C],
    data: T_data,
    /,
    key: str = None,
    init: T_init = None,
    strict: bool = True,
) -> C:
    """
    Shortcut for _load_data + load_into_recurse.
    """
    to_load = _load_data(data, key, cls.__name__)
    return _load_into_recurse(cls, to_load, init=init, strict=strict)


def load_into_instance(
    inst: C,
    data: T_data,
    /,
    key: str = None,
    init: T_init = None,
    strict: bool = True,
) -> C:
    """
    Shortcut for _load_data + load_into_existing.
    """
    cls = inst.__class__
    to_load = _load_data(data, key, cls.__name__)
    return _load_into_instance(inst, cls, to_load, init=init, strict=strict)


def load_into(
    cls: typing.Type[C],
    data: T_data,
    /,
    key: str = None,
    init: T_init = None,
    strict: bool = True,
) -> C:
    """
    Load your config into a class (instance).

    Supports both a class or an instance as first argument, but that's hard to explain to mypy, so officially only
    classes are supported, and if you want to `load_into` an instance, you should use `load_into_instance`.

    Args:
        cls: either a class or an existing instance of that class.
        data: can be a dictionary or a path to a file to load (as pathlib.Path or str)
        key: optional (nested) dictionary key to load data from (e.g. 'tool.su6.specific')
        init: optional data to pass to your cls' __init__ method (only if cls is not an instance already)
        strict: enable type checks or allow anything?

    """
    if not isinstance(cls, type):
        # would not be supported according to mypy, but you can still load_into(instance)
        return load_into_instance(cls, data, key=key, init=init, strict=strict)

    # make mypy and pycharm happy by telling it cls is of type C and not just 'type'
    # _cls = typing.cast(typing.Type[C], cls)
    return load_into_class(cls, data, key=key, init=init, strict=strict)
