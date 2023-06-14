"""
Loads loaders based on Python version.
"""

import sys

if sys.version_info > (3, 11):
    from .loaders_311 import toml
else:  # pragma: no cover
    from .loaders_310 import toml

__all__ = ["toml"]
