import os
import tempfile
import typing
from contextlib import chdir
from pathlib import Path

import pytest
from dotenv import dotenv_values

from src import configuraptor
from src.configuraptor import asjson
from src.configuraptor.errors import ConfigErrorCouldNotConvert
from tests.constants import PYTEST_EXAMPLES

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
    my_config = configuraptor.load_into(MyConfig, dotenv_values(ENV_FILE), lower_keys=True, convert_types=True)

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
        ),
    )

    with pytest.raises(ConfigErrorCouldNotConvert):
        try:
            configuraptor.load_into(InvalidConfig, ENV_FILE, lower_keys=True, convert_types=True)
        except ConfigErrorCouldNotConvert as e:
            assert "from `<class 'str'>`" in str(e)
            assert "to `<class 'bool'>`" in str(e)
            raise e


class EnvConfig(configuraptor.TypedConfig):
    from_my_env: str
    second: str | None


def test_from_env():
    os.environ["FROM_MY_ENV"] = "Example"

    conf = EnvConfig.from_env()

    assert conf.from_my_env == "Example"

    del os.environ["FROM_MY_ENV"]

    with tempfile.NamedTemporaryFile() as f:
        f.write(b"FROM_MY_ENV=SECOND")
        f.seek(0)

        conf = EnvConfig.from_env(f.name)

        assert conf.from_my_env == "SECOND"
        assert not conf.second


def test_env_interpolation():
    config_toml = """
    [env-config]
    from_my_env = '${OTHER_ENV_VAR:-nothing}'
    second = "$SECOND"
    """

    dot_env = """
    OTHER_ENV_VAR=from_dotenv
    SECOND=from_dotenv
    """

    with tempfile.TemporaryDirectory() as d, chdir(d):
        d_path = Path(d)
        f = d_path / "config.toml"
        e = d_path / ".env"

        f.write_text(config_toml)
        e.write_text(dot_env)

        os.environ["OTHER_ENV_VAR"] = "from_env"
        os.environ["SECOND"] = "from_env"

        interpolated_yes = EnvConfig.load(f)
        interpolated_inverse = EnvConfig.load(f, use_env="inverse")
        interpolated_dotenv = EnvConfig.load(f, use_env="dotenv")
        interpolated_environ = EnvConfig.load(f, use_env="environ")
        interpolated_no = EnvConfig.load(f, use_env="no")

        del os.environ["OTHER_ENV_VAR"]
        del os.environ["SECOND"]

        e.write_text("SECOND=from_dotenv_again\n")
        os.environ["SECOND"] = "from_env_again"

        interpolated_fallback = EnvConfig.load(f)

        del os.environ["SECOND"]

    assert interpolated_yes.from_my_env == "from_env"
    assert interpolated_yes.second == "from_env"

    assert interpolated_inverse.from_my_env == "from_dotenv"
    assert interpolated_inverse.second == "from_dotenv"

    assert interpolated_dotenv.from_my_env == "from_dotenv"
    assert interpolated_dotenv.second == "from_dotenv"

    assert interpolated_environ.from_my_env == "from_env"
    assert interpolated_environ.second == "from_env"

    assert interpolated_no.from_my_env == "${OTHER_ENV_VAR:-nothing}"
    assert interpolated_no.second == "$SECOND"

    assert interpolated_fallback.from_my_env == "nothing"
    assert interpolated_fallback.second == "from_env_again"
