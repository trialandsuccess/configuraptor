import typing

from .core import T_data, load_into


class TypedConfig:
    @classmethod
    def load(cls, data: T_data, key: str = None) -> typing.Self:
        return load_into(cls, data, key=key)
