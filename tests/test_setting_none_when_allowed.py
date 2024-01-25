from src.configuraptor import beautify, TypedConfig


@beautify
class MyClass(TypedConfig):
    required: str
    optional: str | None


config = MyClass.load({'required': "there"})


def test_required():
    assert config.required == "there"
    config.required = None
    assert config.required == "there"


def test_optional():
    assert config.optional is None
    config.optional = "not none"
    assert config.optional == "not none"
    config.optional = None  # should be allowed according to the annotation
    assert config.optional is None
