<div align="center">
    <img 
        align="center" 
        src="https://raw.githubusercontent.com/trialandsuccess/configuraptor/master/_static/configuraptor_circle.png" 
        alt="Classy Configuraptor"
        width="400px"
        />
    <h1 align="center">Configuraptor</h1>
</div>

<div align="center">
    Load config files into Python classes for a typed config (for type hinting etc.).
    Supported file types are toml/yaml/json, and .env/.ini to a lesser degree 
        (see <a href="#supported-config-file-types">Supported Config File Types</a>).
</div>

<br>

<div align="center">
    <a href="https://pypi.org/project/configuraptor"><img alt="PyPI - Version" src="https://img.shields.io/pypi/v/configuraptor.svg"/></a>
    <a href="https://pypi.org/project/configuraptor"><img alt="PyPI - Python Version" src="https://img.shields.io/pypi/pyversions/configuraptor.svg"/></a>
    <br/>
    <a href="https://github.com/psf/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"/></a>
    <a href="https://opensource.org/licenses/MIT"><img alt="License: MIT" src="https://img.shields.io/badge/License-MIT-yellow.svg"/></a>
    <br/>
    <a href="https://github.com/trialandsuccess/configuraptor/actions"><img alt="su6 checks" src="https://github.com/trialandsuccess/configuraptor/actions/workflows/su6.yml/badge.svg?branch=development"/></a>
    <a href="https://github.com/trialandsuccess/configuraptor/actions"><img alt="Coverage" src="coverage.svg"/></a>
</div> 

---

**Table of Contents**

- [Installation](#installation)
- [Usage](#usage)
- [Supported Config File Types](#supported-config-file-types)
- [License](#license)
- [Changelog](#changelog)

## Installation

```console
pip install configuraptor
```

## Usage

Configuraptor can be used to load your config files into structured Python classes.

```toml
# examples/example_from_readme.toml
[config]
name = "Hello World!"

[config.reference]
number = 42
numbers = [41, 43]
string = "42"
```

Could be loaded into Python classes using the following code:

```python
# examples/example_from_readme.py
from configuraptor import load_into, TypedConfig


######################
# with basic classes #
######################

class SomeRegularClass:
    number: int
    numbers: list[int]
    string: str


class Config:
    name: str
    reference: SomeRegularClass


if __name__ == '__main__':
    my_config = load_into(Config, "example_from_readme.toml")  # or .json, .yaml, ...

    print(my_config.name)
    # Hello World!
    print(my_config.reference.numbers)
    # [41, 43]


########################
# alternative notation #
########################

class SomeOtherRegularClass:
    number: int
    numbers: list[int]
    string: str


class OtherConfig(TypedConfig):
    name: str
    reference: SomeRegularClass


if __name__ == '__main__':
    my_config = OtherConfig.load("https://api.my-server.dev/v1/config.json?secret=token")  # or .toml, .yaml, ...

    print(my_config.name)
    # Hello World!
    print(my_config.reference.numbers)
    # [41, 43]

    # TypedConfig has an extra benefit of allowing .update:
    my_config.update(numbers=[68, 70])
```

The second argument of `.load_into` and the first argument of `.load` (which is `"example_from_readme.toml"` in the
examples above), can be either a string or a Path to a file, a raw dictionary with data, a URL or empty.
You can also use a list of these options to combine data sources.
If it is left empty, the `pyproject.toml` will be used. You can supply a `key='tool.mytool.myconf'` to specify which
section of the file should be read. For HTTP authentication, currently you can use http basic
auth (`https://user:pass@host` or query parameters (like `?token=...`)). 
Other authentication methods are not currently supported.

More examples can be found in [examples](https://github.com/trialandsuccess/configuraptor/blob/master/examples).

## Supported Config File Types

- [`.toml`](https://docs.fileformat.com/programming/toml/): supports the most types (strings, numbers, booleans,
  datetime, lists/arrays, dicts/tables);
- [`.json`](https://www.w3schools.com/js/js_json_datatypes.asp): supports roughly the same types as toml (except
  datetime);
- [`.yaml`](https://docs.fileformat.com/programming/yaml): supports roughly the same types as toml, backwards compatible
  with JSON;
- [`.env`](https://pypi.org/project/python-dotenv/): only supports strings. You can use `convert_types=True` to try to
  convert to your annotated types;
- [`.ini`](https://docs.python.org/3/library/configparser.html): only supports strings. You can use `convert_types=True`
  to try to convert to your annotated types;

For other file types, a custom Loader can be written.
See [examples/readme.md#Custom File Types](https://github.com/trialandsuccess/configuraptor/blob/master/examples/readme.md#custom-file-types)

### Binary Config

You can also parse a [`struct`-packed](https://docs.python.org/3/library/struct.html) bytestring into a config class.
For this, you have to use `BinaryConfig` with
`BinaryField`s. Annotations are not supported in this case, because the order of properties is important for this type
of config.

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

## License

`configuraptor` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.

## Changelog

[See CHANGELOG.md](https://github.com/trialandsuccess/configuraptor/blob/master/CHANGELOG.md)
