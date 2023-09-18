"""
Loads loaders based on Python version.
"""
import typing

# tomli used for every Python version now.
from .loaders_shared import dotenv, ini, json, toml, yaml
from .register import LOADERS, T_loader, register_loader


def get(extension: str, default: T_loader | None | typing.Type[Exception] = ValueError) -> T_loader | None:
    """
    Get the right loader for a specific extension.
    """
    extension = extension.removeprefix(".")

    if loader := LOADERS.get(extension):
        return loader
    elif default and issubclass(default, Exception):
        raise default(f"Invalid extension {extension}")
    else:
        return default


__all__ = ["get", "toml", "json", "yaml", "dotenv", "ini", "register_loader"]
