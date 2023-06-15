from configuraptor import TypedConfig, astoml, asjson


class Dependency:
    name: str


class Complex(TypedConfig):
    name: str
    dependency: Dependency
    dependencies: list[Dependency]
    extra: dict[str, Dependency]


config = Complex.load("dumping.yml")

print(astoml(config))
"""
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

"""

print(asjson(config, indent=1))
"""
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
"""
