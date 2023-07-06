"""
File loaders that work regardless of Python version.
"""
import configparser
import json as json_lib
import typing
from collections import defaultdict
from pathlib import Path
from typing import BinaryIO

import tomli
import yaml as yaml_lib
from dotenv import dotenv_values

from ._types import T_config, as_tconfig
from .register import register_loader


@register_loader
def json(f: BinaryIO, _: typing.Optional[Path]) -> T_config:
    """
    Load a JSON file.
    """
    data = json_lib.load(f)
    return as_tconfig(data)


@register_loader(".yaml", ".yml")
def yaml(f: BinaryIO, _: typing.Optional[Path]) -> typing.Any:
    """
    Load a YAML file.
    """
    return yaml_lib.load(f, yaml_lib.SafeLoader)


@register_loader
def toml(f: BinaryIO, _: typing.Optional[Path]) -> typing.Any:
    """
    Load a toml file.
    """
    return tomli.load(f)


@register_loader(".env")
def dotenv(_: typing.Optional[BinaryIO], fullpath: Path) -> typing.Any:
    """
    Load a toml file.
    """
    return dotenv_values(fullpath)


def _convert_key(key: str) -> str:
    return key.replace(" ", "_").replace("-", "_")


def _convert_value(value: str) -> str:
    if value.startswith('"') and value.endswith('"'):
        value = value.removeprefix('"').removesuffix('"')
    return value


RecursiveDict = dict[str, typing.Union[str, "RecursiveDict"]]


@register_loader
def ini(_: typing.Optional[BinaryIO], fullpath: Path) -> typing.Any:
    """
    Load an ini file.
    """
    config = configparser.ConfigParser()
    config.read(fullpath)

    final_data: defaultdict[str, RecursiveDict] = defaultdict(dict)
    for section in config.sections():
        data: RecursiveDict = {_convert_key(k): _convert_value(v) for k, v in dict(config[section]).items()}
        section = _convert_key(section)
        if "." in section:
            _section = _current = {}  # type: ignore
            for part in section.split("."):
                _current[part] = _current.get(part) or {}
                _current = _current[part]

            # nested structure is set up, now load the right data into it:
            _current |= data
            final_data |= _section
        else:
            final_data[section] = data

    return dict(final_data)
