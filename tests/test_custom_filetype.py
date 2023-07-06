import typing
from pathlib import Path
from typing import BinaryIO

import xmltodict

from src import configuraptor

from .constants import PYTEST_EXAMPLES


class MyConfig:
    string: str
    number: float
    boolean: bool
    list: list[str]
    dict: dict[str, str]


@configuraptor.loader("xml")
def load_xml(file_handler: BinaryIO, file_path: Path) -> typing.Any:
    return xmltodict.parse(file_handler)


def test_xml_loader():
    xml_file = PYTEST_EXAMPLES / "example.xml"
    config = configuraptor.load_into(MyConfig, xml_file, convert_types=True)

    assert 2 < config.number < 4
    assert config.boolean is True
    assert len(config.list) == 2
    assert len(config.dict.keys()) == 1
