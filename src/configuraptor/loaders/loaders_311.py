"""
Loaders for Python 3.11+.
"""
import sys
from typing import BinaryIO

from ._types import T_config

if sys.version_info < (3, 11):  # pragma: no cover
    raise EnvironmentError("Wrong Python version!")
else:
    import tomllib

    def toml(f: BinaryIO) -> T_config:
        """
        Load a toml file.
        """
        return tomllib.load(f)
