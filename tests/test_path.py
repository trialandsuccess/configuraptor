from pathlib import Path
from typing import Optional

from src.configuraptor import load_into, postpone


class PathConfig:
    required: Path
    optional: Optional[Path]


class PathConfigPostponed:
    required: Path = postpone()
    optional: Optional[Path] = postpone()


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

    conf.required = Path.home()

    assert conf.required == Path.home()
