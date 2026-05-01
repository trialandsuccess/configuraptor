"""
Contains stand-alone helper functions.
"""

import contextlib
import dataclasses as dc
import io
import math
import re
import types
import typing
import warnings
from collections import ChainMap
from pathlib import Path

from expandvars import expand
from typeguard import TypeCheckError
from typeguard import check_type as _check_type

try:
    import annotationlib
except ImportError:  # pragma: no cover
    annotationlib = None


def camel_to_snake(s: str) -> str:
    """
    Convert CamelCase to snake_case.

    Source:
        https://stackoverflow.com/questions/1175208/elegant-python-function-to-convert-camelcase-to-snake-case
    """
    return "".join([f"_{c.lower()}" if c.isupper() else c for c in s]).lstrip("_")


# def find_pyproject_toml() -> typing.Optional[str]:
#     """
#     Find the project's config toml, looks up until it finds the project root (black's logic).
#     """
#     return black.files.find_pyproject_toml((os.getcwd(),))


def find_pyproject_toml(start_dir: typing.Optional[Path | str] = None) -> Path | None:
    """
    Search for pyproject.toml starting from the current working directory \
     and moving upwards in the directory tree.

    Args:
        start_dir: Starting directory to begin the search.
            If not provided, uses the current working directory.

    Returns:
        Path or None: Path object to the found pyproject.toml file, or None if not found.
    """
    start_dir = Path.cwd() if start_dir is None else Path(start_dir).resolve()

    current_dir = start_dir

    while str(current_dir) != str(current_dir.root):
        pyproject_toml = current_dir / "pyproject.toml"
        if pyproject_toml.is_file():
            return pyproject_toml
        current_dir = current_dir.parent

    # If not found anywhere
    return None


Type = typing.Type[typing.Any]


def strip_annotated(_type: type) -> type:
    """
    Unwrap typing.Annotated[T, ...] to T.
    """
    while typing.get_origin(_type) is typing.Annotated:
        args = typing.get_args(_type)
        if not args:  # pragma: no cover
            break
        _type = typing.cast(type, args[0])
    return _type


def _cls_annotations(c: type) -> dict[str, type]:  # pragma: no cover
    """
    Functions to get the annotations of a class (excl inherited, use _all_annotations for that).

    Uses `annotationlib` if available (since 3.14) and if so, resolves forward references immediately.
    """
    if annotationlib:
        return typing.cast(
            dict[str, type],
            annotationlib.get_annotations(c, format=annotationlib.Format.VALUE, eval_str=True),
        )
    else:
        # note: idk why but this is not equivalent (the first doesn't work well):
        # return getattr(c, "__annotations__", {})
        return c.__dict__.get("__annotations__") or {}


def _all_annotations(cls: type) -> ChainMap[str, type]:
    """
    Returns a dictionary-like ChainMap that includes annotations for all \
    attributes defined in cls or inherited from superclasses.
    """
    # chainmap reverses the iterable, so reverse again beforehand to keep order normally:

    return ChainMap(*(_cls_annotations(c) for c in getattr(cls, "__mro__", [])))


def all_annotations(cls: Type, _except: typing.Iterable[str] = None) -> dict[str, type[object]]:
    """
    Wrapper around `_all_annotations` that filters away any keys in _except.

    It also flattens the ChainMap to a regular dict.
    """
    if _except is None:
        _except = set()

    _all = _all_annotations(cls)
    return {k: strip_annotated(v) for k, v in _all.items() if k not in _except}


T = typing.TypeVar("T")


def check_type(value: typing.Any, expected_type: typing.Type[T]) -> typing.TypeGuard[T]:
    """
    Given a variable, check if it matches 'expected_type' (which can be a Union, parameterized generic etc.).

    Based on typeguard but this returns a boolean instead of returning the value or throwing a TypeCheckError
    """
    try:
        _check_type(value, expected_type)
        return True
    except TypeCheckError:
        return False


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


def is_union(sometype: typing.Type[typing.Any] | typing.Any) -> bool:
    """
    Determines if a given type is a Union type.

    A Union type in Python is used to represent a type that can be one of multiple
    types. This function checks whether the provided type object corresponds to a
    Union type as defined in Python's type hints or annotations.

    Returns:
    bool
        True if the provided type is a Union type, False otherwise.
    """
    origin = typing.get_origin(sometype)
    return origin in (typing.Union, types.UnionType)


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

    try:
        return (
            _type is None
            or types.NoneType in typing.get_args(_type)  # union with Nonetype
            or issubclass(types.NoneType, _type)
            or issubclass(types.NoneType, type(_type))  # no type  # Nonetype
        )
    except TypeError:
        # probably some weird input that's not a type
        return False


def dataclass_field(cls: Type, key: str) -> typing.Optional[dc.Field[typing.Any]]:
    """
    Get Field info for a dataclass cls.
    """
    fields = getattr(cls, "__dataclass_fields__", {})
    return fields.get(key)


@contextlib.contextmanager
def uncloseable(fd: typing.BinaryIO) -> typing.Generator[typing.BinaryIO, typing.Any, None]:
    """
    Context manager which turns the fd's close operation to no-op for the duration of the context.
    """
    close = fd.close
    fd.close = lambda: None  # type: ignore
    yield fd
    fd.close = close  # type: ignore


def as_binaryio(file: str | Path | typing.BinaryIO | None, mode: typing.Literal["rb", "wb"] = "rb") -> typing.BinaryIO:
    """
    Convert a number of possible 'file' descriptions into a single BinaryIO interface.
    """
    if isinstance(file, str):
        file = Path(file)
    if isinstance(file, Path):
        file = file.open(mode)
    if file is None:
        file = io.BytesIO()
    if isinstance(file, io.BytesIO):
        # so .read() works after .write():
        file.seek(0)
        # so the with-statement doesn't close the in-memory file:
        file = uncloseable(file)  # type: ignore

    return file


_LEGACY_ENV_DEFAULTS_RE = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*):([^\-?=+][^}]*)}")


def _normalize_legacy_env_defaults(value: str) -> str:
    """
    Rewrite legacy ${VAR:default} to ${VAR:-default} and warn once.
    """
    if not _LEGACY_ENV_DEFAULTS_RE.search(value):
        return value

    warnings.warn(
        "Legacy ${VAR:default} syntax is deprecated; use ${VAR:-default}. "
        "Support for the legacy form may be removed in a future release.",
        DeprecationWarning,
        stacklevel=3,
    )

    return _LEGACY_ENV_DEFAULTS_RE.sub(r"${\1:-\2}", value)


def expand_posix_vars(posix_expr: str, context: dict[str, str]) -> str:
    """
    Replace case-insensitive POSIX and Docker Compose-like environment variables in a string with their values.

    Args:
        posix_expr (str): The input string containing case-insensitive POSIX or Docker Compose-like variables.
        context (dict): A dictionary containing variable names and their respective values.

    Returns:
        str: The string with replaced variable values.
    """
    posix_expr = _normalize_legacy_env_defaults(posix_expr)
    return typing.cast(str, expand(posix_expr, environ=context))


def expand_env_vars_into_toml_values(
    toml: dict[str, typing.Any],
    env: dict[str, typing.Any],
    *,
    case_insensitive: bool = True,
) -> None:
    """
    Recursively expands POSIX/Docker Compose-like environment variables in a TOML dictionary.

    This function traverses a TOML dictionary and expands POSIX/Docker Compose-like
    environment variables (${VAR:default}) using values provided in the 'env' dictionary.
    It performs in-place modification of the 'toml' dictionary.

    Args:
        toml (dict): A TOML dictionary with string values possibly containing environment variables.
        env (dict): A dictionary containing environment variable names and their respective values.
        case_insensitive (bool): If True, treat environment keys as case-insensitive by adding
            upper/lower variants for lookup. Defaults to True.

    Returns:
        None: The function modifies the 'toml' dictionary in place.

    Notes:
        The function recursively traverses the 'toml' dictionary. If a value is a string or a list of strings,
        it attempts to substitute any environment variables found within those strings using the 'env' dictionary.

    Example:
        toml_data = {
            'key1': 'This has ${ENV_VAR:default}',
            'key2': ['String with ${ANOTHER_VAR}', 'Another ${YET_ANOTHER_VAR}']
        }
        environment = {
            'ENV_VAR': 'replaced_value',
            'ANOTHER_VAR': 'value_1',
            'YET_ANOTHER_VAR': 'value_2'
        }

        expand_env_vars_into_toml_values(toml_data, environment)
        # 'toml_data' will be modified in place:
        # {
        #     'key1': 'This has replaced_value',
        #     'key2': ['String with value_1', 'Another value_2']
        # }
    """
    if not toml or not env:  # pragma: no cover
        return

    if case_insensitive:
        env_case: dict[str, typing.Any] = dict(env)
        for key, value in env.items():
            upper = key.upper()
            lower = key.lower()
            if upper not in env_case:
                env_case[upper] = value
            if lower not in env_case:
                env_case[lower] = value
        env = env_case

    for key, var in toml.items():
        if isinstance(var, dict):
            expand_env_vars_into_toml_values(var, env, case_insensitive=case_insensitive)
        elif isinstance(var, list):
            toml[key] = [expand_posix_vars(value, env) if isinstance(value, str) else value for value in var]
        elif isinstance(var, str):
            toml[key] = expand_posix_vars(var, env)
        else:
            # nothing to substitute
            continue
