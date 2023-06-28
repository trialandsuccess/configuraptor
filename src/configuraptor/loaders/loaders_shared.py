"""
File loaders that work regardless of Python version.
"""
import io
import json as json_lib
from typing import BinaryIO

import tomli
import yaml as yaml_lib
from dotenv import dotenv_values

from ._types import T_config, as_tconfig


def json(f: BinaryIO) -> T_config:
    """
    Load a JSON file.
    """
    data = json_lib.load(f)
    return as_tconfig(data)


def yaml(f: BinaryIO) -> T_config:
    """
    Load a YAML file.
    """
    data = yaml_lib.load(f, yaml_lib.SafeLoader)
    return as_tconfig(data)


def toml(f: BinaryIO) -> T_config:
    """
    Load a toml file.
    """
    data = tomli.load(f)
    return as_tconfig(data)


def dotenv(f: BinaryIO) -> T_config:
    """
    Load a toml file.
    """
    _bytes = f.read()
    text = _bytes.decode()
    data = dotenv_values(stream=io.StringIO(text))
    return as_tconfig(data)
