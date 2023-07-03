from pathlib import Path

from src.configuraptor import loaders

PYTEST_EXAMPLES = Path("./pytest_examples")
EXAMPLE_FILE = PYTEST_EXAMPLES / "some.toml"
EMPTY_FILE = PYTEST_EXAMPLES / "empty.toml"


def _load_toml():
    with EXAMPLE_FILE.open("rb") as f:
        return loaders.toml(f, None)
