from configuraptor import Singleton, load_into


class MyConfig(Singleton):
    string: str
    number: int

    def update(self, string: str, number: int):
        self.string = string
        self.number = number

    def __repr__(self):
        return f"{self.string=}, {self.number=}"


config = load_into(MyConfig, {"my_config": dict(string="initial string", number=0)})

second_config = MyConfig()  # note: no arguments required!
print(f"{config=}\n{second_config=}")
# config=self.string='initial string', self.number=0
# second_config=self.string='initial string', self.number=0

config.update(string="second string", number=1)
# config=self.string='second string', self.number=1
# second_config=self.string='second string', self.number=1
