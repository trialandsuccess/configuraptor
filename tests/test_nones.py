import configuraptor


class ConfigWithNones(configuraptor.TypedConfig):
    required: str
    optional: str | None


def test_required():
    config = configuraptor.load_into(ConfigWithNones, {'required': 'value', 'optional': 'value'})

    config.update(required=None)

    assert config.required == "value"

    config.update(required=None, _allow_none=True)
    assert config.required is None


def test_optional():
    config = configuraptor.load_into(ConfigWithNones, {'required': 'value', 'optional': 'value'})

    assert config.optional == "value"

    config.update(optional=None)
    assert config.optional is None

    config.update(optional="new")
    assert config.optional == "new"

    config.update(optional=None, _skip_none=True)
    assert config.optional == "new"
