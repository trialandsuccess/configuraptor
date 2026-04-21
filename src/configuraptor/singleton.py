"""
Singleton mixin/metaclass.
"""

import typing

T = typing.TypeVar("T")


class SingletonMeta(type):
    """
    Every instance of a singleton shares the same object underneath.

    Can be used as a metaclass:
    Example:
        class AbstractConfig(metaclass=Singleton):

    Source: https://stackoverflow.com/questions/6760685/creating-a-singleton-in-python
    """

    _instances: typing.ClassVar[dict[type[typing.Any], typing.Any]] = {}

    def __call__(self: type[T], *args: typing.Any, **kwargs: typing.Any) -> T:
        """
        When a class is instantiated (e.g. `AbstractConfig()`), __call__ is called. This overrides the default behavior.
        """
        if self not in SingletonMeta._instances:
            SingletonMeta._instances[self] = type.__call__(self, *args, **kwargs)

        return typing.cast(T, SingletonMeta._instances[self])

    @staticmethod
    def clear(instance: "Singleton" = None) -> None:
        """
        Use to remove old instances.

        (otherwise e.g. pytest will crash)
        """
        if instance:
            SingletonMeta._instances.pop(instance.__class__, None)
        else:
            SingletonMeta._instances.clear()


class Singleton(metaclass=SingletonMeta):
    """
    Mixin to make a class a singleton.
    """
