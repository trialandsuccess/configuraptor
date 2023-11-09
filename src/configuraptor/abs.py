"""
Contains the Abstract config class shared by TypedConfig and BinaryConfig.
"""
import os
import types
import typing
from pathlib import Path

import dotenv
from dotenv import find_dotenv

# T is a reusable typevar
T = typing.TypeVar("T")
# t_typelike is anything that can be type hinted
T_typelike: typing.TypeAlias = type | types.UnionType  # | typing.Union
# t_data is anything that can be fed to _load_data
T_data_types = str | Path | bytes | dict[str, typing.Any] | None
T_data = T_data_types | list[T_data_types]

# c = a config class instance, can be any (user-defined) class
C = typing.TypeVar("C")
# type c is a config class
Type_C = typing.Type[C]


class AbstractTypedConfig:
    """
    These functions only exist on the class, not on instances.
    """

    @classmethod
    def load(
        cls: typing.Type[C],
        data: T_data = None,
        key: str = None,
        init: dict[str, typing.Any] = None,
        strict: bool = True,
        lower_keys: bool = False,
        convert_types: bool = False,
    ) -> C:
        """
        Load a class' config values from the config file.

        SomeClass.load(data, ...) = load_into(SomeClass, data, ...).
        """
        from .core import load_into

        return load_into(
            cls, data, key=key, init=init, strict=strict, lower_keys=lower_keys, convert_types=convert_types
        )

    @classmethod
    def from_env(
        cls: typing.Type[C],
        load_dotenv: str | bool = False,
        init: dict[str, typing.Any] = None,
        strict: bool = True,
        convert_types: bool = True,
    ) -> C:
        """
        Create an instance of the typed config class by loading environment variables and initializing \
            object attributes based on those values.

        Args:
            cls (typing.Type[C]): The class to create an instance of.
            init (dict[str, typing.Any], optional): Additional initialization data to be used
                in the object creation. Defaults to None.
            strict (bool, optional): If True, raise an error if any required environment variable
                is missing. Defaults to True.
            convert_types (bool, optional): If True, attempt to convert environment variable values
                to the appropriate Python types. Defaults to False.
            load_dotenv (str | bool, optional): Path to a dotenv file or True to load the default
                dotenv file. If False, no dotenv file will be loaded. Defaults to False.

        Returns:
            C: An instance of the class `C` with attributes initialized based on the environment variables.
        """
        from .core import load_into

        if load_dotenv:
            dotenv_path = load_dotenv if isinstance(load_dotenv, str) else find_dotenv(usecwd=True)
            dotenv.load_dotenv(dotenv_path)

        data = {**os.environ}

        return load_into(cls, data, lower_keys=True, init=init, strict=strict, convert_types=convert_types)
