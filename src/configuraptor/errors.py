"""
Contains module-specific custom errors.
"""
import typing
from dataclasses import dataclass


class ConfigError(Exception):
    """
    Base exception class for this module.
    """


@dataclass
class ConfigErrorMissingKey(ConfigError):
    """
    Exception for when the config file is missing a required key.
    """

    key: str
    cls: type
    annotated_type: type

    def __post_init__(self) -> None:
        """
        Automatically filles in the names of annotated type and cls for printing from __str__.
        """
        self._annotated_type = self.annotated_type.__name__
        self._cls = self.cls.__name__

    def __str__(self) -> str:
        """
        Custom error message based on dataclass values and calculated actual type.
        """
        return (
            f"Config key '{self.key}' (type `{self._annotated_type}`) "
            f"of class `{self._cls}` was not found in the config, "
            f"but is required as a default value is not specified."
        )


@dataclass
class ConfigErrorInvalidType(ConfigError):
    """
    Exception for when the config file contains a key with an unexpected type.
    """

    key: str
    value: typing.Any
    expected_type: type

    def __post_init__(self) -> None:
        """
        Store the actual type of the config variable.
        """
        self.actual_type = type(self.value)

        max_len = 50
        self._value = str(self.value)
        if len(self._value) > max_len:
            self._value = f"{self._value[:max_len]}..."

    def __str__(self) -> str:
        """
        Custom error message based on dataclass values and calculated actual type.
        """
        return (
            f"Config key '{self.key}' had a value (`{self._value}`) with a type (`{self.actual_type}`) "
            f"that was not expected: `{self.expected_type}` is the required type."
        )


@dataclass
class IsPostponedError(ConfigError):
    """
    Error thrown when you try to access a 'postponed' property without filling its value first.
    """

    message: str = "This postponed property has not been filled yet!"
