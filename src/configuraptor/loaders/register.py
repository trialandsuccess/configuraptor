"""
Exposes `register_loader` to define loader for specific file types.
"""

import typing
from pathlib import Path

from ._types import T_config

T_loader = typing.Callable[[typing.BinaryIO, Path], T_config]
T_WrappedLoader = typing.Callable[[T_loader], T_loader]

LOADERS: dict[str, T_loader] = {}


@typing.overload
def register_loader(*extension_args: str) -> T_WrappedLoader:
    """
    Overload for case with parens.

    @register_loader("yaml", ".yml")
    def load_yaml(...):
        ...

    # extension_args is a tuple of strings
    # this will return a wrapper which takes `load_yaml` as input and output.
    """


@typing.overload
def register_loader(*extension_args: T_loader) -> T_loader:
    """
    Overload for case without parens.

    @register_loader
    def json(...):
        ...

    # extension_args is a tuple of 1: `def json`
    # this will simply return the `json` method itself.
    """


def register_loader(*extension_args: str | T_loader) -> T_loader | T_WrappedLoader:
    """
    Register a data loader for a new filetype.

    Used as a decorator on a method that takes two arguments:
    (BinaryIO, Path) - an open binary file stream to the config file and the pathlib.Path to the config file.
    By default, the open file handler can be used.
    However, some loaders (such as .ini) don't support binary file streams.
    These can use the Path to open and read the file themselves however they please.
    """
    f_outer = None
    extension_set = set()

    for extension in extension_args:
        if not isinstance(extension, str):
            f_outer = extension
            extension = extension.__name__

        elif extension.startswith("."):
            extension = extension.removeprefix(".")

        extension_set.add(extension)

    def wrapper(f_inner: T_loader) -> T_loader:
        LOADERS.update({ext: f_inner for ext in extension_set})
        return f_inner

    if f_outer:
        return wrapper(f_outer)  # -> T_Loader
    else:
        return wrapper  # -> T_WrappedLoader


__all__ = ["register_loader", "LOADERS"]
