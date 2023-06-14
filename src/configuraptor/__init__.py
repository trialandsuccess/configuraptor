"""
Exposes TypedConfig and load_into for this library.
"""

# SPDX-FileCopyrightText: 2023-present Robin van der Noord <robinvandernoord@gmail.com>
#
# SPDX-License-Identifier: MIT
from .cls import TypedConfig  # noqa: F401 imported for library reasons
from .core import (  # noqa: F401 imported for library reasons
    all_annotations,
    check_type,
    ensure_types,
    load_into,
)
from .singleton import (  # noqa: F401 imported for library reasons
    Singleton,
    SingletonMeta,
)
