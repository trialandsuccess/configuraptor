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
