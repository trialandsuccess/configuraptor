import re

from src.su6_plugin_demo.__about__ import __version__


def test_version():
    version_re = re.compile(r"\d+\.\d+\.\d+.*")
    assert version_re.findall(__version__)
