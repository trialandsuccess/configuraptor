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

load_into_instance(maria, "ages.toml", key="maria")
load_into_instance(steve, "ages.toml", key="steve")

print(maria.age, steve.age)
# 45, 24
