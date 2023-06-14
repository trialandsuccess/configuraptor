"""
Loaders for Python 3.10.
"""

import sys
from typing import BinaryIO

from ._types import T_config, as_tconfig

if sys.version_info > (3, 11):
    raise EnvironmentError("Wrong Python version!")
else:  # pragma: no cover
    import tomlkit

    def toml(f: BinaryIO) -> T_config:
        """
        Load a toml file.
        """
        data = tomlkit.load(f)
        return as_tconfig(data)
