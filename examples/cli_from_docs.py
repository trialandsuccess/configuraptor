import contextlib

from su6.plugins import register, PluginConfig


@register
class MyConfig(PluginConfig):
    some: str


@register(config_key="demo.extra")
class ExtraConfig(PluginConfig):
    more: list[str]


@register(with_state=True, strict=False, config_key="demo.untyped")
class StateConfig(PluginConfig):
    number: str


my_config = MyConfig()
extra_config = ExtraConfig()
state_config = StateConfig()


# note: config is not set up at this moment yet,
# it is only available in a command since the user can define `--config`
# and those arguments are parsed after importing plugin modules.

@register
def command(optional_argument: str = None):
    # e.g. su6 command --optional-argument something
    assert my_config.some == "config"
    assert extra_config.more == ["config", "here"]
    assert state_config.state

    my_config.update(some="new!")
    assert my_config.some != "config"

    assert MyConfig() is my_config

    # will update 'some' if optional_argument is not None
    my_config.update(some=optional_argument)

    with contextlib.suppress(KeyError):
        # will error since new_key is not defined in MyConfig:
        my_config.update(new_key=optional_argument)

    # will work and create a new (untyped) property:
    my_config.update(new_key=optional_argument, strict=False)

    print(my_config)

    if optional_argument:
        assert my_config.some == optional_argument
        assert my_config.new_key == optional_argument
    else:
        assert my_config.some != optional_argument
        assert not hasattr(my_config, "new_key")
