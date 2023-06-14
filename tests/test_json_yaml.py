from src.configuraptor import load_into
from tests.constants import PYTEST_EXAMPLES


class SomeRegularClass:
    number: int
    numbers: list[int]
    string: str


class Config:
    name: str
    reference: SomeRegularClass


def test_basic_json_and_yaml():
    toml = load_into(Config, PYTEST_EXAMPLES / "example.toml")
    json = load_into(Config, PYTEST_EXAMPLES / "example.json")
    yaml = load_into(Config, PYTEST_EXAMPLES / "example.yaml")

    assert toml.reference.numbers and toml.reference.numbers == json.reference.numbers == yaml.reference.numbers
