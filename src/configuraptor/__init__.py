"""
Exposes TypedConfig and load_into for this library.
"""

# SPDX-FileCopyrightText: 2023-present Robin van der Noord <robinvandernoord@gmail.com>
#
# SPDX-License-Identifier: MIT
from .cls import TypedConfig
from .core import (
    all_annotations,
    check_and_convert_data,
    convert_config,
    ensure_types,
    load_into,
    load_into_class,
    load_into_instance,
)
from .postpone import postpone
from .singleton import Singleton, SingletonMeta

__all__ = [
    # cls
    "TypedConfig",
    # singleton
    "Singleton",
    "SingletonMeta",
    # core
    "all_annotations",
    "check_and_convert_data",
    "convert_config",
    "ensure_types",
    "load_into",
    "load_into_class",
    "load_into_instance",
    # postpone
    "postpone",
]
