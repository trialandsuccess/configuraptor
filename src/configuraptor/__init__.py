"""
Exposes TypedConfig and load_into for this library.
"""

# SPDX-FileCopyrightText: 2023-present Robin van der Noord <robinvandernoord@gmail.com>
#
# SPDX-License-Identifier: MIT
from .alias import Alias, alias
from .binary_config import BinaryConfig, BinaryField
from .cls import TypedConfig, TypedMapping, TypedMutableMapping, update
from .core import (
    check_and_convert_data,
    convert_config,
    ensure_types,
    load_data,
    load_into,
    load_into_class,
    load_into_instance,
)
from .dump import asbytes, asdict, asjson, astoml, asyaml
from .helpers import all_annotations, check_type
from .loaders import register_loader as loader
from .postpone import postpone
from .singleton import Singleton, SingletonMeta
from .type_converters import register_converter as converter

__all__ = [
    # binary
    "BinaryConfig",
    "BinaryField",
    # cls
    "TypedConfig",
    "TypedMapping",
    "TypedMutableMapping",
    "update",
    # singleton
    "Singleton",
    "SingletonMeta",
    # core
    "check_and_convert_data",
    "convert_config",
    "ensure_types",
    "load_data",
    "load_into",
    "load_into_class",
    "load_into_instance",
    # helpers
    "all_annotations",
    "check_type",
    # postpone
    "postpone",
    # dump
    "asbytes",
    "asdict",
    "astoml",
    "asyaml",
    "asjson",
    # register
    "loader",
    "converter",
    # alias
    "alias",
    "Alias",
]
