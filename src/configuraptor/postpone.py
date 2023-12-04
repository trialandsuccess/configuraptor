"""
File contains logic to do with the 'postpone' feature.
"""

from typing import Any, Optional

from typing_extensions import Never

from .errors import IsPostponedError
from .singleton import Singleton


class Postponed(Singleton):
    """
    Class returned by `postpone` below.
    """

    def __get_property_name__(self, instance: type[Any], owner: type[Any]) -> Optional[str]:
        """
        Internal method to get the property name of the class this descriptor is being used on.
        """
        if not instance:  # pragma: no cover
            return None

        # instance: the instance the descriptor is accessed from
        # owner: the class that owns the descriptor
        property_name = None
        for attr_name, attr_value in owner.__dict__.items():
            if attr_value is self:
                property_name = attr_name
                break
        # return instance.__dict__.get(property_name, None)
        return property_name

    def __get__(self, instance: type[Any], owner: type[Any]) -> Never:
        """
        This magic method is called when a property is accessed.

        Example:
             someclass.someprop will trigger the __get__ of `someprop`

        Args:
            instance: the class on which the postponed property is defined,
            owner: `SingletonMeta`
        """
        msg = f"Err: Using postponed property on {owner.__name__}"

        if name := self.__get_property_name__(instance, owner):
            msg += f".{name}"

        raise IsPostponedError(msg)


def postpone() -> Any:
    """
    Can be used to mark a property as postponed, meaning the user will fill it in later (they promose).

    If they don't fill it in and still try to use it, they will be met with a IsPostponedError.
    """
    return Postponed()
