"""
Add @beautify behavior to enhance configuraptor/TypedConfig classes automagically!
"""

import functools
import typing

from .dump import asdict, asjson

T = typing.TypeVar("T")


def is_default(obj: typing.Any, prop: str) -> bool:
    """
    Check if the property of an object is set to its default value.

    Args:
        obj (typing.Any): The object to check.
        prop (str): The property to check.

    Returns:
        bool: True if the property is set to its default value, False otherwise.
    """
    return getattr(obj, prop) is getattr(object, prop)


def patch(cls: typing.Type[T], patch_repr: bool, patch_str: bool) -> None:
    """
    Patch the __str__ and __repr__ methods of a class if they are set to their default values.

    Args:
        cls (typing.Type[typing.Any]): The class to patch.
        patch_repr: patch __repr__? (if no custom one set yet)
        patch_str: patch __str__? (if no custom one set yet)
    """

    def _repr(self: T) -> str:
        """
        Custom __repr__ by configuraptor @beautify.
        """
        clsname = type(self).__name__
        data = asdict(self, with_top_level_key=False, exclude_internals=2)
        return f"<{clsname} {data}>"

    def _str(self: T) -> str:
        """
        Custom __str__ by configuraptor @beautify.
        """
        return asjson(self, with_top_level_key=False, exclude_internals=2)

    # if magic method is already set, don't overwrite it!
    if patch_str and is_default(cls, "__str__"):
        cls.__str__ = _str  # type: ignore

    if patch_repr and is_default(cls, "__repr__"):
        cls.__repr__ = _repr  # type: ignore


@typing.overload
def beautify(
    maybe_cls: typing.Type[T],
    repr: bool = True,  # noqa A002
    str: bool = True,  # noqa A002
) -> typing.Type[T]:
    """
    Overload function for the beautify decorator when used without parentheses.
    """


@typing.overload
def beautify(
    maybe_cls: None = None,
    repr: bool = True,  # noqa A002
    str: bool = True,  # noqa A002
) -> typing.Callable[[typing.Type[T]], typing.Type[T]]:
    """
    Overload function for the beautify decorator when used with parentheses.
    """


def beautify(
    maybe_cls: typing.Type[T] | None = None,
    repr: bool = True,  # noqa A002
    str: bool = True,  # noqa A002
) -> typing.Type[T] | typing.Callable[[typing.Type[T]], typing.Type[T]]:
    """
    The beautify decorator. Enhances a class by patching its __str__ and __repr__ methods.

    Args:
        maybe_cls (typing.Type[T] | None, optional): The class to beautify. None when used with parentheses.
        repr: patch __repr__? (if no custom one set yet)
        str: patch __str__? (if no custom one set yet)

    Returns:
        The beautified class or the beautify decorator.
    """
    if maybe_cls:
        patch(maybe_cls, patch_repr=repr, patch_str=str)
        return maybe_cls
    else:
        return functools.partial(beautify, repr=repr, str=str)
