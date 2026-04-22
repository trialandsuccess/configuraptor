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

def test_singleton_clear():

    class SingletonOne(Singleton):
        key: str = ""

    class SingletonTwo(Singleton):
        value: int = 0

    one = SingletonOne()
    one.key = "test-dont-lose-me"

    two = SingletonTwo()
    two.value = 1

    assert SingletonOne().key == "test-dont-lose-me"
    assert SingletonTwo().value == 1

    Singleton.clear(two)

    assert SingletonOne().key == "test-dont-lose-me"
    assert not SingletonTwo().value

    SingletonTwo().value = 2

    Singleton.clear(SingletonTwo)

    assert SingletonOne().key == "test-dont-lose-me"
    assert not SingletonTwo().value

    SingletonTwo().value = 3

    SingletonTwo.clear()

    assert SingletonOne().key == "test-dont-lose-me"
    assert not SingletonTwo().value

    SingletonTwo().value = 4

    Singleton.clear()

    assert not SingletonOne().key
    assert not SingletonTwo().value