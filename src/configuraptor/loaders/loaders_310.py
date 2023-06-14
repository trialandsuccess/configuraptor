"""
Loaders for Python 3.10.
"""

import sys
import typing
from typing import BinaryIO

if sys.version_info > (3, 11):
    raise EnvironmentError("Wrong Python version!")
else:  # pragma: no cover
    import tomlkit

    T_toml = dict[str, typing.Any]

    def toml(f: BinaryIO) -> T_toml:
        """
        Load a toml file.
        """
        return typing.cast(T_toml, tomlkit.load(f))
