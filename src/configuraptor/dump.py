"""
Method to dump classes to other formats.
"""

import json
import typing

import tomli_w
import yaml

from .core import instance_of_custom_class, is_custom_class
from .helpers import camel_to_snake


def asdict(inst: typing.Any, _level: int = 0, /, with_top_level_key: bool = True) -> dict[str, typing.Any]:
    """
    Dump a config instance to a dictionary (recursively).
    """
    data = {}

    for key, value in inst.__dict__.items():
        cls = value.__class__
        if is_custom_class(cls):
            value = asdict(value, _level + 1)
        elif isinstance(value, list):
            value = [asdict(_, _level + 1) if instance_of_custom_class(_) else _ for _ in value]
        elif isinstance(value, dict):
            value = {k: asdict(v, _level + 1) if instance_of_custom_class(v) else v for k, v in value.items()}

        data[key] = value

    if _level == 0 and with_top_level_key:
        # top-level: add an extra key indicating the class' name
        cls_name = camel_to_snake(inst.__class__.__name__)
        return {cls_name: data}

    return data


def astoml(inst: typing.Any, multiline_strings: bool = False) -> str:
    """
    Dump a config instance to toml (recursively).
    """
    data = asdict(inst)
    return tomli_w.dumps(data, multiline_strings=multiline_strings)


def asjson(inst: typing.Any, **kw: typing.Any) -> str:
    """
    Dump a config instance to json (recursively).
    """
    data = asdict(inst)
    return json.dumps(data, **kw)


def asyaml(inst: typing.Any, **kw: typing.Any) -> str:
    """
    Dump a config instance to yaml (recursively).
    """
    data = asdict(inst)
    output = yaml.dump(data, encoding=None, **kw)
    # output is already a str but mypy doesn't know that
    return typing.cast(str, output)
