import typing

T_config = dict[str, typing.Any]


def as_tconfig(data: typing.Any) -> T_config:
    """
    Does not actually do anything, but tells mypy the 'data' of type Any (json, pyyaml, tomlkit) \
    is actually a dict of string keys and Any values.
    """
    return typing.cast(T_config, data)
