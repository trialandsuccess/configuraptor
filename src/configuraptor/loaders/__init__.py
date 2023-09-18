"""
Loads loaders based on Python version.
"""
import typing

# tomli used for every Python version now.
from .loaders_shared import dotenv, ini, json, toml, yaml
from .register import LOADERS, T_loader, register_loader


@typing.overload
def get(extension: str, default: T_loader) -> T_loader:
    """
    When setting a loader function as default, a loader will always be returned.
    """


@typing.overload
def get(extension: str, default: None) -> T_loader | None:
    """
    When setting None as the default, either a loader or none will be returned.
    """


@typing.overload
def get(extension: str, default: typing.Type[Exception] = ValueError) -> T_loader:
    """
    When not setting a default, a loader will be returned or an exception will be thrown.
    """


def get(extension: str, default: T_loader | None | typing.Type[Exception] = ValueError) -> T_loader | None:
    """
    Get the right loader for a specific extension.
    """
    extension = extension.removeprefix(".")

    if loader := LOADERS.get(extension):
        return loader
    elif default and isinstance(default, type) and issubclass(default, Exception):
        raise default(f"Invalid extension {extension}")
    else:
        # can't be an exeption because the above clause makes sure of that. So tell mypy with cast:
        return typing.cast(typing.Optional[T_loader], default)


__all__ = ["get", "toml", "json", "yaml", "dotenv", "ini", "register_loader"]
