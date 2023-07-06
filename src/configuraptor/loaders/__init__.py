"""
Loads loaders based on Python version.
"""

# tomli used for every Python version now.
from .loaders_shared import dotenv, ini, json, toml, yaml
from .register import LOADERS, T_loader, register_loader


def get(extension: str) -> T_loader:
    """
    Get the right loader for a specific extension.
    """
    extension = extension.removeprefix(".")

    if loader := LOADERS.get(extension):
        return loader
    else:
        raise ValueError(f"Invalid extension {extension}")


__all__ = ["get", "toml", "json", "yaml", "dotenv", "ini", "register_loader"]
