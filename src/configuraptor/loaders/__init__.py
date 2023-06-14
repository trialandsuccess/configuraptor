"""
Loads loaders based on Python version.
"""

import sys
import typing

from ._types import T_config
from .loaders_shared import json, yaml

if sys.version_info > (3, 11):
    from .loaders_311 import toml
else:  # pragma: no cover
    from .loaders_310 import toml

__all__ = ["get", "toml", "json", "yaml"]

T_loader = typing.Callable[[typing.BinaryIO], T_config]

LOADERS: dict[str, T_loader] = {
    "toml": toml,
    "json": json,
    "yml": yaml,
    "yaml": yaml,
}


def get(extension: str) -> T_loader:
    """
    Get the right loader for a specific extension.
    """
    extension = extension.removeprefix(".")
    if loader := LOADERS.get(extension):
        return loader
    else:
        raise ValueError(f"Invalid extension {extension}")
