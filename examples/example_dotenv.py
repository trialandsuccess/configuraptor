import typing

from configuraptor import load_into, asdict


class DotEnv:
    string: str
    with_variable: str
    number: int
    boolean_t: bool
    boolean_y: bool
    boolean_1: bool

    boolean_f: bool
    boolean_n: bool
    boolean_1: bool

    null: typing.Optional[None]


if __name__ == '__main__':
    data = load_into(DotEnv, ".env", lower_keys=True, convert_types=True)

    print(asdict(data))
