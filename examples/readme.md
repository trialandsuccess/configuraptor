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

## DotEnv

Although env files are much more limited than the other supported file types, it can be useful to parse (dot)envs.
Because by default, only strings are really supported and the convention is to write env keys in CAPITAL LETTERS,
`load_into` has two options to make working with env files easier:

- `lower_keys` will lower the keys in an env file to match your class properties.
- `convert_types` will try to convert the values from string to the annotated type. Note that this is pretty limited,
  and
  should only be used to compare to simple types such as `int`s. Relationships to other config instances is not
  supported with env files.
    - Converting to `bool` has some special rules, which will convert "True", "Yes" and "1" (any capitalization) into
      True; "False", "No" and "0" to False and any other values will raise an exception.
    - Complex types such as `dict[str, int]` will not be converted!
    - Advanced: Custom converters can be defined with `@configuraptor.converter(from_type: type, to_type: type)`.
      See [tests/test_custom_converter.py](../tests/test_custom_converter.py).

```env
# examples/.env
STRING=string
WITH_VARIABLE="${STRING}"
NUMBER=123
BOOLEAN_T=True
BOOLEAN_Y=Yes
BOOLEAN_F=False
BOOLEAN_N=No
BOOLEAN_1=1
BOOLEAN_0=0

NULL
```

```python
# examples/example_dotenv.py
import typing

from configuraptor import load_into, asdict


class DotEnv:
    string: str
    with_variable: str
    number: int
    boolean_t: bool
    boolean_y: bool
    boolean_1: bool

    boolean_f: bool
    boolean_n: bool
    boolean_1: bool

    null: typing.Optional[None]


if __name__ == '__main__':
    data = load_into(DotEnv, ".env", lower_keys=True, convert_types=True)

    print(asdict(data))

```

## Multiple data sources

Sometimes, you need to combine different sources of configuration.
This can be done by providing a list of filenames as the first argument (`data`) of `configuraptor.load_into`.
A dictionary of data can also be used to extend the config files. The files are loaded in order and overwrite any keys
that were already defined in previous files, so be careful with in which order you load them.

```toml
# config.toml
[my_config]
public_key = "some key"
private_key = "<overwrite me>"
```

```env
# secrets.env
PRIVATE_KEY="some private key"
```

```python
from configuraptor import load_into


class MyConfig:
    public_key: str
    private_key: str
    extra: int


data = load_into(MyConfig, ["config.toml", "secrets.env", {"extra": 3}],
                 # lower_keys=True,  # <- automatically set to True when loading a list.
                 # other settings such as `convert_types` and `key` are still available.
                 )

data.private_key == "some private key"  # because secrets.env was after config.toml in the list, it has overwritten the private_key setting.
data.public_key == "some key"  # because secrets.env did not have a public_key setting, the one from config.toml is used.
```

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

## Binary Config

To load a bytestring (from struct.pack) into a config class, use `BinaryConfig` with `BinaryField`:

```python
from configuraptor import BinaryConfig, BinaryField


class MyBinaryConfig(BinaryConfig):
    # annotations not supported! (because mixing annotation and __dict__ lookup messes with the order,
    # which is important for struct.(un)pack
    number = BinaryField(int)
    string = BinaryField(str, length=5)
    decimal = BinaryField(float)
    double = BinaryField(float, format="d")
    other_string = BinaryField(str, format="10s")
    boolean = BinaryField(bool)


MyBinaryConfig.load(
    b'*\x00\x00\x00Hello\x00\x00\x00fff@\xab\xaa\xaa\xaa\xaa\xaa\n@Hi\x00\x00\x00\x00\x00\x00\x00\x00\x01')
```

If one of these fields contains complex info (e.g. JSON), you can link another (regular typedconfig) class:

```python
from configuraptor import BinaryConfig, BinaryField
import json, yaml, tomli_w


class JsonField:
    name: str
    age: int


class NestedBinaryConfig(BinaryConfig):
    data1 = BinaryField(JsonField, format="json", length=32)
    data2 = BinaryField(JsonField, format="yaml", length=32)
    data3 = BinaryField(JsonField, format="toml", length=32)
    other_data = "don't touch this"


input_data1 = {"name": "Alex", "age": 42}
input_data2 = {"name": "Sam", "age": 24}
data1 = struct.pack("32s", json.dumps(input_data1).encode())
data2 = struct.pack("32s", yaml.dump(input_data2).encode())
data3 = struct.pack("32s", tomli_w.dumps(input_data2).encode())

inst = NestedBinaryConfig.load({'data2': data2, 'data1': data1, 'data3': data3})
# or:
inst = load_into(NestedBinaryConfig,
                 b'{"name": "Alex", "age": 42}\x00\x00\x00\x00\x00age: 24\nname: Sam\n\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00name = "Sam"\nage = 24\n\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
```

Config can also be split up into multiple binary blocks:

```python
import struct
from configuraptor import BinaryConfig, BinaryField, asbytes


class Version(BinaryConfig):
    major = BinaryField(int)
    minor = BinaryField(int)
    patch = BinaryField(int)


class Versions(BinaryConfig):
    first = BinaryField(Version)
    second = BinaryField(Version, length=12)  # length optional, can be calculated automatically.


v1 = struct.pack("i i i", 1, 12, 5)
v2 = struct.pack("i i i", 0, 4, 2)
obj = Versions.load(v1 + v2)

print(obj.first.patch)  # 5

# and back into bytes:
asbytes(obj)
# -> b'\x01\x00\x00\x00\x0c\x00\x00\x00\x05\x00\x00\x00\x00\x00\x00\x00\x04\x00\x00\x00\x02\x00\x00\x00'
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

## Alias Fields

Alias fields allow you to create alternative names for configuration keys, providing flexibility and the ability to
refer to the same underlying configuration value by different names.

```python
from configuraptor import load_into, alias


class Config:
    key1: str
    key2: str = alias('key1')


conf = load_into(Config, {'key2': 'something'}) # or {key1: ...}
# -> key1 will look up the value of key2 because it's configured as an alias for it.
assert conf.key1 == conf.key2 == "something"
```

### Use Case:

When you're unsure about the exact name a configuration key will have but have a set of possibilities, you can now
create an alias. This enables you to access the same configuration value using different names within your code.

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

## Custom File Types

You can define custom loaders for file types that are not supported by default.

Here follows an example for XML using `xmltodict`:

```xml
<!-- pytest_examples/example.xml -->
<my_config>
    <string>string</string>
    <number>3.14</number>
    <boolean>true</boolean>
    <list>
        list 1
    </list>
    <list>
        list 2
    </list>
    <dict>
        <key>value</key>
    </dict>
</my_config>
```

```python
# tests/test_custom_filetype.py
class MyConfig:
    string: str
    number: float
    boolean: bool
    list: list[str]
    dict: dict[str, str]


@configuraptor.loader("xml")
def load_xml(file_handler: BinaryIO, file_path: Path) -> typing.Any:
    return xmltodict.parse(file_handler)


# loading works just like normal now:
config = configuraptor.load_into(MyConfig, xml_file, convert_types=True)
# {'string': 'string', 'number': 3.14, 'boolean': True, 'list': ['list 1', 'list 2'], 'dict': {'key': 'value'}}
```

### Custom Type Converters

Additionally, you can also define custom converters (used with `convert_types=True`).
See [tests/test_custom_converter.py](../tests/test_custom_converter.py) for an example.
