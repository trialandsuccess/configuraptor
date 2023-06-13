"""
Loaders for Python 3.11+.
"""
import sys
import typing
from typing import BinaryIO

if sys.version_info < (3, 11): # pragma: no cover
    raise EnvironmentError("Wrong Python version!")
else:
    import tomllib

    def toml(f: BinaryIO) -> dict[str, typing.Any]:
        """
        Load a toml file.
        """
        return tomllib.load(f)
