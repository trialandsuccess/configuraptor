"""
Contains module-specific custom errors.
"""
import typing
from dataclasses import dataclass


class ConfigError(Exception):
    """
    Base exception class for this module.
    """


# class ConfigErrorGroup(ConfigError, ExceptionGroup):
#     """
#     Base Exception class for this module, but for exception groups (3.11+)
#     """
#     def __init__(self, _type: str, errors: list[Exception]):
#         more = len(errors) > 1
#         cnt = "Multiple" if more else "One"
#         s = "s" if more else ""
#         message = f"{cnt} {_type}{s} in config!"
#         super().__init__(message, errors)
#         if not errors:
#             raise ValueError("Error group raised without any errors?")


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
        self._annotated_type = getattr(self.annotated_type, "__name__", str(self.annotated_type))
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
class ConfigErrorExtraKey(ConfigError):
    """
    Exception for when the config file is missing a required key.
    """

    key: str
    value: str
    cls: type

    def __post_init__(self) -> None:
        """
        Automatically filles in the names of annotated type and cls for printing from __str__.
        """
        self._cls = self.cls.__name__
        self._type = type(self.value)

    def __str__(self) -> str:
        """
        Custom error message based on dataclass values and calculated actual type.
        """
        return (
            f"Config key '{self.key}' (value: `{self.value}` type `{self._type}`) "
            f"does not exist on class `{self._cls}`, but was attempted to be updated. "
            f"Use strict = False to allow this behavior."
        )


@dataclass
class ConfigErrorCouldNotConvert(ConfigError):
    """
    Raised by `convert_between` if something funky is going on (incompatible types etc.).
    """

    from_t: type
    to_t: type
    value: typing.Any

    def __str__(self) -> str:
        """
        Custom error message based on dataclass values and calculated actual type.
        """
        return f"Could not convert `{self.value}` from `{self.from_t}` to `{self.to_t}`"


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
class ConfigErrorImmutable(ConfigError):
    """
    Raised when an immutable Mapping is attempted to be updated.
    """

    cls: type

    def __post_init__(self) -> None:
        """
        Store the class name.
        """
        self._cls = self.cls.__name__

    def __str__(self) -> str:
        """
        Custom error message.
        """
        return f"{self._cls} is Immutable!"


@dataclass
class IsPostponedError(ConfigError):
    """
    Error thrown when you try to access a 'postponed' property without filling its value first.
    """

    message: str = "This postponed property has not been filled yet!"
