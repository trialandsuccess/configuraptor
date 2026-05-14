from typing import Optional

import configuraptor


class ConfigWithNones(configuraptor.TypedConfig):
    required: str
    optional: str | None


def test_required():
    config = configuraptor.load_into(ConfigWithNones, {"required": "value", "optional": "value"})

    config.update(required=None)

    assert config.required == "value"

    config.update(required=None, _allow_none=True)
    assert config.required is None


def test_optional():
    config = configuraptor.load_into(ConfigWithNones, {"required": "value", "optional": "value"})

    assert config.optional == "value"

    config.update(optional=None)
    assert config.optional is None

    config.update(optional="new")
    assert config.optional == "new"

    config.update(optional=None, _skip_none=True)
    assert config.optional == "new"


def test_falsey_into_none():
    # toml doesn't support none so sometimes you want a falsey value to indicate missing
    class Maybe:
        value: int

    class ContainsNone:
        maybe_none: Optional[Maybe]


    happy = {
        "contains_none": {
            "maybe_none": {
                "value": 123
            }
        }
    }

    sad = {
        "contains_none": {
            "maybe_none": False
        }
    }


    assert configuraptor.load_into(ContainsNone, happy, convert_types=True).maybe_none
    assert configuraptor.load_into(ContainsNone, sad, convert_types=True).maybe_none is None
