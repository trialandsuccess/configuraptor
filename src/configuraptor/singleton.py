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

    def clear(cls, instance: "Singleton | type[Singleton] | None" = None) -> None:
        """
        Use to remove old instances.

        (otherwise e.g. pytest will crash)
        """
        if instance:
            # Singleton.clear(SomeSingleton) or Singleton.clear(some_instance)
            SingletonMeta._instances.pop(instance if isinstance(instance, SingletonMeta) else instance.__class__, None)
        elif isinstance(cls, SingletonMeta) and issubclass(cls, Singleton) and cls is not Singleton:
            # SomeSingleton.clear()
            SingletonMeta._instances.pop(cls, None)
        else:
            # Singleton.clear()
            SingletonMeta._instances.clear()


class Singleton(metaclass=SingletonMeta):
    """
    Mixin to make a class a singleton.
    """
