# not directly testable
import sys

import pytest

if sys.version_info > (3, 11):
    def test_loader_310_fails():
        with pytest.raises(EnvironmentError):
            from src.typedconfig.loaders.loaders_310 import toml
            toml()
else:
    def test_loader_311_fails():
        with pytest.raises(EnvironmentError):
            from src.typedconfig.loaders.loaders_311 import toml
            toml()
