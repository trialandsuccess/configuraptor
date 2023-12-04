import pytest

from src.configuraptor import Singleton, TypedConfig, postpone
from src.configuraptor.errors import IsPostponedError


class Later(TypedConfig, Singleton):
    field: str  # instant
    other_field: str = postpone()

    def update(self):
        self.other_field = "usable"


later = Later.load({"field": "instant"})


def test_postponed_can_be_filled_later():
    # later should be able to exist
    assert later
    assert later.field
    print(later, later.field)

    # later.other_field should throw an error
    with pytest.raises(IsPostponedError):
        try:
            print(later.other_field)
        except IsPostponedError as e:
            assert "Later.other_field" in str(e)
            raise e

    later.update()

    # now later.other_field should work
    print(later.other_field)
