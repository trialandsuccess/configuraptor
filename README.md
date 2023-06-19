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
    Load toml/yaml/json config files into classes for a typed config (type hinting etc.).
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
    my_config = load_into(Config, "example_from_readme.toml")  # or .json, .yaml

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
    my_config = OtherConfig.load("example_from_readme.toml")  # or .json, .yaml

    print(my_config.name)
    # Hello World!
    print(my_config.reference.numbers)
    # [41, 43]

    # TypedConfig has an extra benefit of allowing .update:
    my_config.update(numbers=[68, 70])
```

More examples can be found in [examples](https://github.com/trialandsuccess/configuraptor/blob/master/examples).

## License

`configuraptor` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.

## Changelog

[See CHANGELOG.md](https://github.com/trialandsuccess/configuraptor/blob/master/CHANGELOG.md)
