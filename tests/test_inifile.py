import typing

from src import configuraptor

from .constants import PYTEST_EXAMPLES

INI = PYTEST_EXAMPLES / "config.ini"


class Default:
    string: str
    number: int
    boolean: bool
    other_boolean: bool


class Example:
    port: int
    forwardx11: bool
    nothing: None


class Server:
    example: Example


class TopSecret:
    server: Server


class WithSpaces:
    key_with_spaces: str
    empty: str
    with_colon: str


class MyConfig:
    default: Default
    topsecret: TopSecret
    section_with_spaces: WithSpaces


def test_basic_ini():
    my_config = configuraptor.load_into(MyConfig, INI, convert_types=True)

    assert my_config
    assert my_config.default.string == "value"
    assert my_config.default.number == 45
    assert my_config.default.boolean is True
    assert my_config.default.other_boolean is True

    assert my_config.topsecret.server.example.port == 50022
    assert my_config.topsecret.server.example.forwardx11 is False
    assert my_config.topsecret.server.example.nothing is None

    assert isinstance(my_config.section_with_spaces.key_with_spaces, str)
    assert my_config.section_with_spaces.empty == ""
    assert my_config.section_with_spaces.with_colon == "as seperator"
