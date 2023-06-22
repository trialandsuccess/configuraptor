# Examples

## Basic

For basic usage, see [../README.md](https://github.com/trialandsuccess/configuraptor/blob/master/README.md#usage)
and [./example_from_readme.py](https://github.com/trialandsuccess/configuraptor/blob/master/examples/example_from_readme.py).
Normal classes can be used with `configuraptor` (with `load_into(YourClass, data, ...)`) or you can
inherit `TypedConfig` (and use `YourClass.load(data, ...)`).

In the examples above, `data` can be either

1. a `str` path to a config file;
2. a `pathlib.Path` to a config file;
3. a `dict` of already retrieved data to load.

The following keyword arguments are available for `load`/`load_into`:

### key (`str`)

if the data your class needs exists in a nested data structure (think a `[tool.some-tool.settings]` sort
of structure), `key` can be provided to manually select where `configuraptor` needs to search for its data
(e.g. `key="tool.some-tool"`). If no key is passed, it will be guessed based on some criteria:

- if there is only one top-level key, it will be used automatically (this happens in the case of `OtherConfig` in
  the `README` example);
- otherwise, the name of the class is used to guess the key name (this happens in the case of `Config` in
  the `README` example).

If you pass `key=""` (empty string), all data will be loaded from the top-level. 
This will be done automatically too if something goes wrong with the supplied key.
Example:

```json
// somedata.json
{
  "string": "here",
  "number": 123
}
```

```python
class FromJson:
    string: str
    number: int


load_into(FromJson, "somedata.json", key="")
```

### init (`dict`)

Can be used to pass extra variables to the class initialization, in case its `__init__` method required parameters.
Only keyword arguments are supported at this moment.

```python
class MyClass:
    some_property: str

    def __init__(self, prop: str = "with default"):
        self.some_property = prop


# load with empty data (since `some_property` will be filled by __init__),
# but with custom init value:
load_into(MyClass, {}, init=dict(prop="override"))
```

### strict (`bool`)

By default, `strict` is True.
This means the data in your config file will be checked with the annotated types of your classes.
This is usually recommended, but if for some reason you need to disable this behavior, it is possible.
Note that disabling strict does NOT transform the incorrect types into the desired ones,
it merely suppreses the error that something's wrong!

```toml
# config.toml
[config]
number = "123"
```

```python
class Config:
    number: int


config = load_into(Config, "config.toml", strict=False)  # would throw an error by default
# type(config.number) == str # !!!
```

## Dataclasses

Aside from using normal classes or `TypedConfig` classes, using `dataclasses` is also supported!
A similar library, `attrs` is unfortunately not supported since it turned out to be a hassle to support.

```python
from dataclasses import dataclass, field
from configuraptor import load_into


@dataclass
class Two:
    name: str
    some_str: str
    some_int: int
    include: list[str] = field(default_factory=list)  # <- not required in config file since it has a default value


@dataclass
class Simple:
    name: str
    two: Two


data = {"simple": {"name": "Steve", "two": {"name": "Alex", "some_str": "string", "some_int": 30}}}

# just like always, data can either be a path to a data file or just a dict of data.
simple = load_into(Simple, data)
print(simple)
# Simple(name='Steve', two=Two(name='Alex', some_str='string', some_int=30, include=[])) Two(name='Alex', some_str='string', some_int=30, include=[])
```

See also: [./dataclass.py](https://github.com/trialandsuccess/configuraptor/blob/master/examples/dataclass.py)

## Inheriting from TypedConfig

In addition to the `MyClass.load` shortcut, inheriting from TypedConfig also gives you the ability to `.update` your
config instances. Update will check whether the type you're trying to assign to a property is inline with its
annotation. By default, `None` values will be skipped to preserve the default or previous value.
These two features can be bypassed with `strict=False` and `allow_none=True` respectively.

```python
from configuraptor import TypedConfig


class SomeConfig(TypedConfig):
    string: str
    num_key: int


config = SomeConfig.load("./some/config.toml")

assert config.string != "updated"
config.update(string="updated")
assert config.string == "updated"

# `string` will not be updated:
config.update(string=None)
assert config.string == "updated"

# `string` will be updated:
config.update(string=None, allow_none=True)
assert config.string is None

# will raise a `ConfigErrorInvalidType`:
config.update(string=123)

# will work:
config.update(string=123, strict=False)
assert config.string == 123

# will raise a `ConfigErrorExtraKey`:
config.update(new_key="some value")

# will work:
config.update(new_key="some value", strict=False)
assert config.new_key == "some value"

```

## Existing Instances

If for some reason you have an already instantiated class and you need to fill the rest of the properties,
`load_into_instance` can be used. Note that this does NOT update properties that already have a value;
It only fills missing properties.

```toml
# ages.toml
[steve]
age = 24

[maria]
age = 999
```

```python
from configuraptor import load_into_instance


class Person:
    name: str
    age: int

    def __init__(self, name: str, age: int = None):
        self.name = name
        if age is not None:
            self.age = age
        # else: age is still unknown


maria = Person("Maria", 45)
steve = Person("Steve")

load_into_instance(maria, "ages.toml", key="maria")  # <- will not update Maria's age since this was already defined.
load_into_instance(steve, "ages.toml", key="steve")  # <- will set Steve's age since this is not set yet.

print(maria.age, steve.age)
# 45, 24
```

## Singletons

This module also provides a `Singleton` mixin class to turn any (config) class into a Singleton.
This means all instances of the class contain the same data, and updating one will also automatically update the others.

```python
from configuraptor import Singleton, load_into


class MyConfig(Singleton):
    string: str
    number: int

    def update(self, string: str, number: int):
        self.string = string
        self.number = number

    def __repr__(self):
        return f"{self.string=}, {self.number=}"


config = load_into(MyConfig, {
    "my_config": dict(
        string="initial string",
        number=0
    )
})

second_config = MyConfig()  # note: no arguments required!
print(f"{config=}\n{second_config=}")
# config=self.string='initial string', self.number=0
# second_config=self.string='initial string', self.number=0

# only calling .update on `config` will also update `second_config`:
config.update(string="second string", number=1)
# config=self.string='second string', self.number=1
# second_config=self.string='second string', self.number=1
```

In this example, both `config` and `second_config` contain exactly the same data at any point in time.

## Postponed Fields

In some cases, a config key you want to define does not exist yet when calling `load_into`. When there is no default or
matching value in the config file, which could be the case in cli tools where you NEED the value from the user,
`postponed()` can be used.

```python
from configuraptor import Singleton, TypedConfig, load_into, postpone


class Later(TypedConfig, Singleton):
    field: str  # instant
    other_field: str = postpone()

    def update(self):
        self.other_field = "usable"


config = load_into(
    Later,
    {
        "later": dict(field="instant")
        # no other_field yet!
    },
)

print(config.field)  # will work
# config.other_field  # will give an error if you try to use it here!

config.update()  # fill in other_field some way or another
print(config.other_field)  # works now!

```

## Dumping

Filled config instances can also be dumped to multiple output formats (`asdict`, `asjson`, `asyaml` and `astoml`).
The first argument is the class you want to dump, the other keyword arguments are passed to the respective dump
methods (`json.dumps`, `yaml.dump` and `tomlkit.dump`).

```yaml
# dumping.yml
complex:
  name: "some name"
  dependency:
    name: "dependency 1"
  dependencies:
    - name: "dependency 2.1"
    - name: "dependency 2.2"
  extra:
    first:
      name: "dependency 3.1"
    second:
      name: "dependency 3.2"

```

```python
from configuraptor import TypedConfig, astoml, asjson


class Dependency:
    name: str


class Complex(TypedConfig):
    name: str
    dependency: Dependency
    dependencies: list[Dependency]
    extra: dict[str, Dependency]


config = Complex.load("dumping.yml")

print(
    astoml(config),
    asjson(config, indent=1)
)
```

```toml
[complex]
name = "some name"

[[complex.dependencies]]
name = "dependency 2.1"

[[complex.dependencies]]
name = "dependency 2.2"

[complex.dependency]
name = "dependency 1"

[complex.extra]
[complex.extra.first]
name = "dependency 3.1"

[complex.extra.second]
name = "dependency 3.2"
```

```json
{
  "complex": {
    "name": "some name",
    "dependency": {
      "name": "dependency 1"
    },
    "dependencies": [
      {
        "name": "dependency 2.1"
      },
      {
        "name": "dependency 2.2"
      }
    ],
    "extra": {
      "first": {
        "name": "dependency 3.1"
      },
      "second": {
        "name": "dependency 3.2"
      }
    }
  }
}
```

## Mappings

To make a class unpackable with `**`, you need to inherit `TypedMapping` or `TypedMutableMapping`.
Doing this will break compatibility with `Singleton`, so this unpacking feature is not enabled on the
default `TypedConfig`.
`TypedMapping` also makes updating the data illegal, whereas this is allowed in `TypedConfig` and `TypedMutableMapping`.

```python
# example_mapping.py
import configuraptor


class MyConfig(configuraptor.TypedMapping):
    key: str


my_config = MyConfig.load({"key": "something"})

# not allowed, because it's not a Mutable Mapping:
my_config.update(key="something else")

# this would crash if MyConfig was a TypedConfig:
"key is {key}".format(**my_config)  # == "key is something"
```
