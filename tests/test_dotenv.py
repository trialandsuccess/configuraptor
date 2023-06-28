import typing

import pytest

from src import configuraptor
from src.configuraptor import asjson
from src.configuraptor.errors import ConfigErrorCouldNotConvert
from tests.constants import PYTEST_EXAMPLES
from dotenv import dotenv_values

ENV_FILE = PYTEST_EXAMPLES / ".env"


class MyConfig:
    first_variable: str
    second_variable: int
    third_variable: bool
    fourth_variable: bool

    domain: str
    admin_email: str
    root_url: str

    empty: typing.Optional[str]
    empty_str: str


class MyConfiguraptor(configuraptor.TypedConfig, MyConfig):
    empty_str: bool


class InvalidConfig:
    first_variable: bool


def test_dotenv_basic():
    my_config = configuraptor.load_into(MyConfig,
                                        dotenv_values(ENV_FILE),
                                        lower_keys=True,
                                        convert_types=True
                                        )

    my_configuraptor = MyConfiguraptor.load(ENV_FILE, lower_keys=True, convert_types=True)

    assert my_config.fourth_variable == my_configuraptor.fourth_variable == False
    assert "$" not in my_config.admin_email

    assert my_config.empty_str == ""
    assert my_configuraptor.empty_str is False

    print(
        asjson(
            my_config,
            indent=2,
        ),
        asjson(
            my_configuraptor,
            indent=2,
        )
    )


    with pytest.raises(ConfigErrorCouldNotConvert):
        try:
            configuraptor.load_into(InvalidConfig, ENV_FILE, lower_keys=True, convert_types=True)
        except ConfigErrorCouldNotConvert as e:
            assert "from `<class 'str'>`" in str(e)
            assert "to `<class 'bool'>`" in str(e)
            raise e
