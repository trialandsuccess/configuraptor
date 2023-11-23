"""
Contains most of the loading logic.
"""

import dataclasses as dc
import io
import os
import typing
import warnings
from pathlib import Path
from typing import Any, Type

import requests

from . import loaders
from .abs import C, T, T_data, Type_C
from .alias import Alias
from .binary_config import BinaryConfig
from .errors import (
    ConfigErrorCouldNotConvert,
    ConfigErrorInvalidType,
    ConfigErrorMissingKey,
)
from .helpers import (
    all_annotations,
    camel_to_snake,
    check_type,
    dataclass_field,
    find_pyproject_toml,
    is_custom_class,
    is_optional,
    is_parameterized,
)
from .postpone import Postponed
from .type_converters import CONVERTERS


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
        key = parts.pop(0)
        if key not in raw:
            return {}

        raw = raw[key]

    return raw


def _guess_key(clsname: str) -> str:
    """
    If no key is manually defined for `load_into`, \
    the class' name is converted to snake_case to use as the default key.
    """
    return camel_to_snake(clsname)


def _from_mock_url(url: str) -> str:
    """
    Pytest only: when starting a url with mock:// it is expected to just be json afterwards.
    """
    return url.removeprefix("mock://")


def guess_filetype_for_url(url: str, response: requests.Response = None) -> str:
    """
    Based on the url (which may have an extension) and the requests response \
        (which may have a content-type), try to guess the right filetype (-> loader, e.g. json or yaml).

    Falls back to JSON if none can be found.
    """
    url = url.split("?")[0]
    if url_extension := os.path.splitext(url)[1].lower():
        return url_extension.strip(".")

    if response and (content_type_header := response.headers.get("content-type", "").split(";")[0].strip()):
        content_type = content_type_header.split("/")[-1]
        if content_type != "plain":
            return content_type

    # If both methods fail, default to JSON
    return "json"


def from_url(url: str, _dummy: bool = False) -> tuple[io.BytesIO, str]:
    """
    Load data as bytes into a file-like object and return the file type.

    This can be used by __load_data:
    > loader = loaders.get(filetype)
    > # dev/null exists but always returns b''
    > data = loader(contents, Path("/dev/null"))
    """
    if url.startswith("mock://"):
        data = _from_mock_url(url)
        resp = None
    elif _dummy:
        resp = None
        data = "{}"
    else:
        resp = requests.get(url, timeout=10)
        data = resp.text

    filetype = guess_filetype_for_url(url, resp)
    return io.BytesIO(data.encode()), filetype


def _load_data(
    data: T_data,
    key: str = None,
    classname: str = None,
    lower_keys: bool = False,
    allow_types: tuple[type, ...] = (dict,),
) -> dict[str, typing.Any]:
    """
    Tries to load the right data from a filename/path or dict, based on a manual key or a classname.

    E.g. class Tool will be mapped to key tool.
    It also deals with nested keys (tool.extra -> {"tool": {"extra": ...}}
    """
    if isinstance(data, bytes):
        # instantly return, don't modify
        # bytes as inputs -> bytes as output
        # but since `T_data` is re-used, that's kind of hard to type for mypy.
        return data  # type: ignore

    if isinstance(data, list):
        if not data:
            raise ValueError("Empty list passed!")

        final_data: dict[str, typing.Any] = {}
        for source in data:
            final_data |= load_data(source, key=key, classname=classname, lower_keys=True, allow_types=allow_types)

        return final_data

    if isinstance(data, str):
        if data.startswith(("http://", "https://", "mock://")):
            contents, filetype = from_url(data)

            loader = loaders.get(filetype)
            # dev/null exists but always returns b''
            data = loader(contents, Path("/dev/null"))
        else:
            data = Path(data)

    if isinstance(data, Path):
        with data.open("rb") as f:
            loader = loaders.get(data.suffix or data.name)
            data = loader(f, data.resolve())

    if not data:
        return {}

    if key is None:
        # try to guess key by grabbing the first one or using the class name
        if len(data) == 1:
            key = next(iter(data.keys()))
        elif classname is not None:
            key = _guess_key(classname)

    if key:
        data = _data_for_nested_key(key, data)

    if not data:
        raise ValueError("No data found!")

    if not isinstance(data, allow_types):
        raise ValueError(f"Data should be one of {allow_types} but it is {type(data)}!")

    if lower_keys and isinstance(data, dict):
        data = {k.lower(): v for k, v in data.items()}

    return typing.cast(dict[str, typing.Any], data)


def load_data(
    data: T_data,
    key: str = None,
    classname: str = None,
    lower_keys: bool = False,
    allow_types: tuple[type, ...] = (dict,),
) -> dict[str, typing.Any]:
    """
    Wrapper around __load_data that retries with key="" if anything goes wrong.
    """
    if data is None:
        # try to load pyproject.toml
        data = find_pyproject_toml()

    try:
        return _load_data(data, key, classname, lower_keys=lower_keys, allow_types=allow_types)
    except Exception as e:
        # sourcery skip: remove-unnecessary-else, simplify-empty-collection-comparison, swap-if-else-branches
        # @sourcery: `key != ""` is NOT the same as `not key`
        if key != "":
            return _load_data(data, "", classname, lower_keys=lower_keys, allow_types=allow_types)
        else:  # pragma: no cover
            warnings.warn(f"Data could not be loaded: {e}", source=e)
            # key already was "", just return data!
            # (will probably not happen but fallback)
            return {}


F = typing.TypeVar("F")


def convert_between(from_value: F, from_type: Type[F], to_type: Type[T]) -> T:
    """
    Convert a value between types.
    """
    if converter := CONVERTERS.get((from_type, to_type)):
        return typing.cast(T, converter(from_value))

    # default: just convert type:
    return to_type(from_value)  # type: ignore


def check_and_convert_type(value: Any, _type: Type[T], convert_types: bool, key: str = "variable") -> T:
    """
    Checks if the given value matches the specified type. If it does, the value is returned as is.

    Args:
        value (Any): The value to be checked and potentially converted.
        _type (Type[T]): The expected type for the value.
        convert_types (bool): If True, allows type conversion if the types do not match.
        key (str, optional): The name or key associated with the variable (used in error messages).
                             Defaults to "variable".

    Returns:
        T: The value, potentially converted to the expected type.

    Raises:
        ConfigErrorInvalidType: If the type does not match, and type conversion is not allowed.
        ConfigErrorCouldNotConvert: If type conversion fails.
    """
    if check_type(value, _type):
        # type matches
        return value

    if isinstance(value, Alias):
        if is_optional(_type):
            return typing.cast(T, None)
        else:
            # unresolved alias, error should've already been thrown for parent but lets do it again:
            raise ConfigErrorInvalidType(value.to, value=value, expected_type=_type)

    if not convert_types:
        # type does not match and should not be converted
        raise ConfigErrorInvalidType(key, value=value, expected_type=_type)

    # else: type does not match, try to convert it
    try:
        return convert_between(value, type(value), _type)
    except (TypeError, ValueError) as e:
        raise ConfigErrorCouldNotConvert(type(value), _type, value) from e


def ensure_types(
    data: dict[str, T], annotations: dict[str, type[T]], convert_types: bool = False
) -> dict[str, T | None]:
    """
    Make sure all values in 'data' are in line with the ones stored in 'annotations'.

    If an annotated key in missing from data, it will be filled with None for convenience.

    TODO: python 3.11 exception groups to throw multiple errors at once!
    """
    # custom object to use instead of None, since typing.Optional can be None!
    # cast to T to make mypy happy
    notfound = typing.cast(T, object())

    final: dict[str, T | None] = {}
    for key, _type in annotations.items():
        compare = data.get(key, notfound)
        if compare is notfound:  # pragma: nocover
            warnings.warn(
                "This should not happen since " "`load_recursive` already fills `data` " "based on `annotations`"
            )
            # skip!
            continue

        if isinstance(compare, Postponed):
            # don't do anything with this item!
            continue

        if isinstance(compare, Alias):
            related_data = data.get(compare.to, notfound)
            if related_data is not notfound:
                if isinstance(related_data, Postponed):
                    # also continue alias for postponed items
                    continue

                # original key set, update alias
                compare = related_data

        compare = check_and_convert_type(compare, _type, convert_types, key)

        final[key] = compare

    return final


def convert_config(items: dict[str, T]) -> dict[str, T]:
    """
    Converts the config dict (from toml) or 'overwrites' dict in two ways.

    1. removes any items where the value is None, since in that case the default should be used;
    2. replaces '-' and '.' in keys with '_' so it can be mapped to the Config properties.
    """
    return {k.replace("-", "_").replace(".", "_"): v for k, v in items.items() if v is not None}


AnyType: typing.TypeAlias = typing.Type[typing.Any]
T_Type = typing.TypeVar("T_Type", bound=AnyType)


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


def load_recursive(
    cls: AnyType, data: dict[str, T], annotations: dict[str, AnyType], convert_types: bool = False
) -> dict[str, T]:
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
                    value = [_load_into_recurse(subtype, subvalue, convert_types=convert_types) for subvalue in value]

                elif origin is dict and arguments and is_custom_class(arguments[1]):
                    # e.g. dict[str, Point]
                    subkeytype, subvaluetype = arguments
                    # subkey(type) is not a custom class, so don't try to convert it:
                    value = {
                        subkey: _load_into_recurse(subvaluetype, subvalue, convert_types=convert_types)
                        for subkey, subvalue in value.items()
                    }
                # elif origin is dict:
                # keep data the same
                elif origin is typing.Union and arguments:
                    for arg in arguments:
                        if is_custom_class(arg):
                            value = _load_into_recurse(arg, value, convert_types=convert_types)

                # todo: other parameterized/unions/typing.Optional

            elif is_custom_class(_type):
                # type must be C (custom class) at this point
                value = _load_into_recurse(
                    # make mypy and pycharm happy by telling it _type is of type C...
                    # actually just passing _type as first arg!
                    typing.cast(Type_C[typing.Any], _type),
                    value,
                    convert_types=convert_types,
                )
        elif value := has_alias(cls, _key, data):
            # value updated by alias
            ...
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


def check_and_convert_data(
    cls: typing.Type[C],
    data: dict[str, typing.Any],
    _except: typing.Iterable[str],
    strict: bool = True,
    convert_types: bool = False,
) -> dict[str, typing.Any]:
    """
    Based on class annotations, this prepares the data for `load_into_recurse`.

    1. convert config-keys to python compatible config_keys
    2. loads custom class type annotations with the same logic (see also `load_recursive`)
    3. ensures the annotated types match the actual types after loading the config file.
    """
    annotations = all_annotations(cls, _except=_except)

    to_load = convert_config(data)
    to_load = load_recursive(cls, to_load, annotations, convert_types=convert_types)

    if strict:
        to_load = ensure_types(to_load, annotations, convert_types=convert_types)

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
    data: dict[str, typing.Any] | bytes,
    init: T_init = None,
    strict: bool = True,
    convert_types: bool = False,
) -> C:
    """
    Loads an instance of `cls` filled with `data`.

    Uses `load_recursive` to load any fillable annotated properties (see that method for an example).
    `init` can be used to optionally pass extra __init__ arguments. \
        NOTE: This will overwrite a config key with the same name!
    """
    init_args, init_kwargs = _split_init(init)

    if isinstance(data, bytes) or issubclass(cls, BinaryConfig):
        if not isinstance(data, (bytes, dict)):  # pragma: no cover
            raise NotImplementedError("BinaryConfig can only deal with `bytes` or a dict of bytes as input.")
        elif not issubclass(cls, BinaryConfig):  # pragma: no cover
            raise NotImplementedError("Only BinaryConfig can be used with `bytes` (or a dict of bytes) as input.")

        inst = typing.cast(C, cls._parse_into(data))
    elif dc.is_dataclass(cls):
        to_load = check_and_convert_data(cls, data, init_kwargs.keys(), strict=strict, convert_types=convert_types)
        if init:
            raise ValueError("Init is not allowed for dataclasses!")

        # ensure mypy inst is an instance of the cls type (and not a fictuous `DataclassInstance`)
        inst = typing.cast(C, cls(**to_load))
    else:
        inst = cls(*init_args, **init_kwargs)
        to_load = check_and_convert_data(cls, data, inst.__dict__.keys(), strict=strict, convert_types=convert_types)
        inst.__dict__.update(**to_load)

    return inst


def _load_into_instance(
    inst: C,
    cls: typing.Type[C],
    data: dict[str, typing.Any],
    init: T_init = None,
    strict: bool = True,
    convert_types: bool = False,
) -> C:
    """
    Similar to `load_into_recurse` but uses an existing instance of a class (so after __init__) \
    and thus does not support init.

    """
    if init is not None:
        raise ValueError("Can not init an existing instance!")

    existing_data = inst.__dict__

    to_load = check_and_convert_data(
        cls, data, _except=existing_data.keys(), strict=strict, convert_types=convert_types
    )

    inst.__dict__.update(**to_load)

    return inst


def load_into_class(
    cls: typing.Type[C],
    data: T_data,
    /,
    key: str = None,
    init: T_init = None,
    strict: bool = True,
    lower_keys: bool = False,
    convert_types: bool = False,
) -> C:
    """
    Shortcut for _load_data + load_into_recurse.
    """
    allow_types = (dict, bytes) if issubclass(cls, BinaryConfig) else (dict,)
    to_load = load_data(data, key, cls.__name__, lower_keys=lower_keys, allow_types=allow_types)
    return _load_into_recurse(cls, to_load, init=init, strict=strict, convert_types=convert_types)


def load_into_instance(
    inst: C,
    data: T_data,
    /,
    key: str = None,
    init: T_init = None,
    strict: bool = True,
    lower_keys: bool = False,
    convert_types: bool = False,
) -> C:
    """
    Shortcut for _load_data + load_into_existing.
    """
    cls = inst.__class__
    allow_types = (dict, bytes) if issubclass(cls, BinaryConfig) else (dict,)
    to_load = load_data(data, key, cls.__name__, lower_keys=lower_keys, allow_types=allow_types)
    return _load_into_instance(inst, cls, to_load, init=init, strict=strict, convert_types=convert_types)


def load_into(
    cls: typing.Type[C],
    data: T_data = None,
    /,
    key: str = None,
    init: T_init = None,
    strict: bool = True,
    lower_keys: bool = False,
    convert_types: bool = False,
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
        lower_keys: should the config keys be lowercased? (for .env)
        convert_types: should the types be converted to the annotated type if not yet matching? (for .env)

    """
    if not isinstance(cls, type):
        # would not be supported according to mypy, but you can still load_into(instance)
        return load_into_instance(
            cls, data, key=key, init=init, strict=strict, lower_keys=lower_keys, convert_types=convert_types
        )

    # make mypy and pycharm happy by telling it cls is of type C and not just 'type'
    # _cls = typing.cast(typing.Type[C], cls)
    return load_into_class(
        cls, data, key=key, init=init, strict=strict, lower_keys=lower_keys, convert_types=convert_types
    )
