import types

from src import configuraptor


@configuraptor.converter(str, list[str])
def using_csv(data: str) -> list[str]:
    """
    Register a converter that will use values that are `str` but annotated as `list[str]` and convert by splitting.
    """
    return data.split(",")


@configuraptor.converter(str, list[int])
def list_of_numbers(data: str) -> list[int]:
    """
    Another example, will convert data to a list of ints, if the property is annotated as such.
    """
    list_of_string = using_csv(data)
    return [int(_) for _ in list_of_string]


class MyConfig:
    data: list[str]
    boolean: bool
    none: None
    null: types.NoneType
    number: float

    numbers: list[int]
    strings: list[str]


def test_csv_converter():
    config = configuraptor.load_into(
        MyConfig,
        {
            # custom:
            "data": "this,is,csv",
            "numbers": "1,22,3",
            "strings": "1,22,3",  # same data, different annotation -> different output
            # builtin converters:
            "boolean": "false",
            "none": "",
            "null": "",
            # fallback:
            "number": "3.14",
        },
        convert_types=True,
    )

    _this, _is, _csv = config.data

    assert _this == "this"
    assert _is == "is"
    assert _csv == "csv"

    assert config.boolean is False
    assert config.none is None
    assert config.null is None

    assert config.number == 3.14

    assert config.numbers == [1, 22, 3]
    assert config.strings == ["1", "22", "3"]
