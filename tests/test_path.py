from pathlib import Path
from typing import Optional

from src.configuraptor import load_into, postpone


class PathConfig:
    required: Path
    optional: Optional[Path]


class PathConfigPostponed:
    required: Path = postpone()
    optional: Optional[Path] = postpone()
    instant: str = postpone()

    def __post_init__(self):
        self.instant = "set"


def test_regular():
    conf = load_into(
        PathConfig,
        {
            "required": Path.home(),
        },
    )

    assert conf.required == Path.home()
    assert isinstance(conf.required, Path)


def test_postponed():
    conf = load_into(PathConfigPostponed, {})

    assert conf
    assert conf.instant == "set"

    conf.required = Path.home()

    assert conf.required == Path.home()
