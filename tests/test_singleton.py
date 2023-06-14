import pytest

from src.configuraptor import Singleton


def test_singleton():
    Singleton.clear()
    assert not Singleton._instances

    class MySingletonState(Singleton):
        def update(self, **kw):
            for k, v in kw.items():
                setattr(self, k, v)

    inst1 = MySingletonState()
    inst2 = MySingletonState()
    assert inst1 is inst2

    inst1.update(some_new_value="yes")
    assert inst2.some_new_value == "yes"

    Singleton.clear(inst1)
    assert inst2 is not MySingletonState()
