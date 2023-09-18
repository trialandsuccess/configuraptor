import types
import typing
from pathlib import Path

# T is a reusable typevar
T = typing.TypeVar("T")
# t_typelike is anything that can be type hinted
T_typelike: typing.TypeAlias = type | types.UnionType  # | typing.Union
# t_data is anything that can be fed to _load_data
T_data_types = str | Path | dict[str, typing.Any] | None
T_data = T_data_types | list[T_data_types]
C = typing.TypeVar("C", bound=typing.Any)


class AbstractTypedConfig:
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
