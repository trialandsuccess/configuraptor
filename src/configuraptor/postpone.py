"""
File contains logic to do with the 'postpone' feature.
"""

from typing import Any

from typing_extensions import Never

from .errors import IsPostponedError
from .singleton import Singleton


class Postponed(Singleton):
    """
    Class returned by `postpone` below.
    """

    def __get__(self, instance: type[Any], owner: type[Any]) -> Never:
        """
        This magic method is called when a property is accessed.

        Example:
             someclass.someprop will trigger the __get__ of `someprop`

        Args:
            instance: the class on which the postponed property is defined,
            owner: `SingletonMeta`
        """
        raise IsPostponedError()


def postpone() -> Any:
    """
    Can be used to mark a property as postponed, meaning the user will fill it in later (they promose).

    If they don't fill it in and still try to use it, they will be met with a IsPostponedError.
    """
    return Postponed()
