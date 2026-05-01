import re
from pathlib import Path
from typing import Optional

from configuraptor import asdict
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
        self._internal = re.compile("...")

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

    class ReferenceIt:
        pcp: PathConfigPostponed = postpone()

        def __post_init__(self):
            self.pcp = conf

    ref = load_into(ReferenceIt, {})


    assert "_internal" not in asdict(conf, exclude_internals=2)["path_config_postponed"]
    assert "_internal" not in asdict(ref, exclude_internals=2)["reference_it"]["pcp"]
