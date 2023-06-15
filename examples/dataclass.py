"""
Example with dataclasses
"""
from dataclasses import dataclass, field

from configuraptor import load_into


@dataclass
class Two:
    name: str
    some_str: str
    some_int: int
    include: list[str] = field(default_factory=list) # <- not required in config file since it has a default value

    def __repr__(self) -> str:
        return f"{self.name=} {self.some_str=} {self.some_int=}"


@dataclass
class Simple:
    name: str
    two: Two

    def __repr__(self) -> str:
        return f"{self.name=} {self.two=}"


def main() -> None:
    data = {"simple": {"name": "Steve", "two": {"name": "Alex", "some_str": "string", "some_int": 30}}}

    simple = load_into(Simple, data)
    two = simple.two
    print(simple, two)


if __name__ == "__main__":
    main()
