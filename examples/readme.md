# Examples

## Basic

For basic usage, see [../README.md](https://github.com/trialandsuccess/configuraptor/blob/master/README.md#usage)
and [./example_from_readme.py](https://github.com/trialandsuccess/configuraptor/blob/master/examples/example_from_readme.py).
Normal classes can be used with `configuraptor` (with `load_into(YourClass, data, ...)`) or you can
inherit `TypedConfig` (and
use `YourClass.load(data, ...)`).

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

## Inheriting from TypedConfig

## Classes with `init`

## Existing Instances

## Singletons
