"""
This module contains an example of both methods of adding commands to su6.
"""
import typing

from su6.plugins import PluginConfig, print, register, run_tool

from typer import Typer


@register
class DemoConfig(PluginConfig):
    """
    Config without state, loads [tool.su6.demo] from pyproject.toml into self.
    """

    required_arg: str
    # etc.


config = DemoConfig()


# method 1: adding top-level commands

@register
def first() -> int:
    """
    Register a top-level command.

    @register works without ()
    """
    print("This is a demo command!")
    return 0


# etc.

# method 2: adding a namespace (based on the plugin package name)

app = Typer()


@app.command()
def subcommand() -> None:
    """
    Register a plugin-level command.

    Can be used as `su6 demo subcommand` (in this case, the plugin name is demo)
    """
    print("this lives in a namespace")

# etc.
