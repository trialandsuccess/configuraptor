import json
import typing

import tomli_w
import yaml

from src.configuraptor import TypedConfig
from src.configuraptor.dump import asdict, asjson, astoml, asyaml


class Simple(TypedConfig):
    key: str
    num: int


data = {
    "simple": {
        "key": "abc",
        "num": 123,
    }
}

simple = Simple.load(data)


def test_asdict_simple():
    assert asdict(simple) == data


def test_asjson():
    assert asjson(simple) == json.dumps(data)


def test_asyaml():
    assert asyaml(simple) == yaml.dump(data)


def test_astoml():
    assert astoml(simple) == tomli_w.dumps(data)


class Dependency:
    name: str


class Complex(TypedConfig):
    name: str
    dependency: Dependency
    dependencies: list[Dependency]
    extra: dict[str, Dependency]


data_complex = {
    "complex": {
        "name": "hi",
        "dependency": {"name": "hey"},
        "dependencies": [{"name": "he"}, {"name": "ha"}],
        "extra": {"first": {"name": "1"}, "second": {"name": "2"}},
        "ignored": "should not exist in asdict",
    }
}

complex = Complex.load(data_complex)


def test_asdict_complex():
    data_complex["complex"].pop("ignored")
    json_complex = json.dumps(data_complex)

    assert asjson(complex) == json_complex


def test_asdict_dataclass():
    ...
