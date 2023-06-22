import configuraptor
import contextlib
from configuraptor.errors import ConfigErrorImmutable


class MyConfig(configuraptor.TypedMapping):
    key: str


my_config = MyConfig.load({"key": "something"})

# not allowed, because it's not a Mutable Mapping:
with contextlib.suppress(ConfigErrorImmutable):
    my_config.update(key="something else")

# this would crash if MyConfig was a TypedConfig:
print("key is {key}".format(**my_config))  # == "key is something"
