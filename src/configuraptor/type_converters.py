"""
Register from-to relationship between types, used with load_into(..., convert_types=True).
"""

import types
import typing
from typing import Any

T = typing.TypeVar("T")

Wrapped = typing.Callable[[Any], Any]
Wrapper = typing.Callable[[Wrapped], Wrapped]

CONVERTERS = {}


def register_converter(from_type: type | tuple[type], to_type: type | None | tuple[type | None, ...]) -> Wrapper:
    """
    Register a custom converter that converts from `from_type` to `to_type` using custom logic.

    `from_type` and `to_type` can both be tuples of types,
    but make sure the `to_type`s are compatible with eachother and your method's return value!

    @register_converter(str, bool)
    def str_to_bool(value: str) -> bool:
        ...

    """
    if not isinstance(from_type, tuple):
        from_type = (from_type,)
    if not isinstance(to_type, tuple):
        to_type = (to_type,)

    def wrapper(func: Wrapped) -> Wrapped:
        for _from in from_type:
            for _to in to_type:
                CONVERTERS[(_from, _to)] = func
        return func

    return wrapper


@register_converter(str, bool)
def str_to_bool(value: str) -> bool:
    """
    Used by convert_between, usually for .env loads.

    Example:
        SOME_VALUE=TRUE -> True
        SOME_VALUE=1 -> True
        SOME_VALUE=Yes -> True

        SOME_VALUE  -> None
        SOME_VALUE=NOpe -> False

        SOME_VALUE=Unrelated -> Error
    """
    if not value:
        return False

    first_letter = value[0].lower()
    # yes, true, 1
    if first_letter in {"y", "t", "1"}:
        return True
    elif first_letter in {"n", "f", "0"}:
        return False
    else:
        raise ValueError("Not booly.")


@register_converter(str, (types.NoneType, None))
def str_to_none(value: str) -> typing.Optional[str]:
    """
    Convert a string value of null/none to None, or keep the original string otherwise.
    """
    if value.lower() in {"", "null", "none"}:
        return None
    else:
        return value
