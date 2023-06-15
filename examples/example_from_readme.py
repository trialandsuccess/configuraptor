from configuraptor import TypedConfig, load_into

######################
# with basic classes #
######################


class SomeRegularClass:
    number: int
    numbers: list[int]
    string: str


class Config:
    name: str
    reference: SomeRegularClass


if __name__ == "__main__":
    my_config = load_into(Config, "example_from_readme.json")

    print(my_config.name)
    # Hello World!
    print(my_config.reference.numbers)
    # [41, 43]


########################
# alternative notation #
########################


class SomeOtherRegularClass:
    number: int
    numbers: list[int]
    string: str


class OtherConfig(TypedConfig):
    name: str
    reference: SomeRegularClass


if __name__ == "__main__":
    my_config = OtherConfig.load("example_from_readme.json")

    print(my_config.name)
    # Hello World!
    print(my_config.reference.numbers)
    # [41, 43]
