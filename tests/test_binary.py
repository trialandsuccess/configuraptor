import json
import struct

import tomli_w
import yaml

from src import configuraptor
from src.configuraptor import BinaryConfig, BinaryField, asbytes


class MyBinaryConfig(BinaryConfig):
    # annotations not supported! (because mixing annotation and __dict__ lookup messes with the order,
    # which is important for struct.(un)pack
    number = BinaryField(int)
    string = BinaryField(str, length=5)
    decimal = BinaryField(float)
    double = BinaryField(float, format="d")
    other_string = BinaryField(str, format="10s")
    boolean = BinaryField(bool)


class TopLevel:
    binary: MyBinaryConfig


class JsonField:
    name: str
    age: int


class NestedBinaryConfig(BinaryConfig):
    data1 = BinaryField(JsonField, format="json", length=32)
    data2 = BinaryField(JsonField, format="yaml", length=32)
    data3 = BinaryField(JsonField, format="toml", length=32)
    other_data = "don't touch this"


def test_binary_config():
    binary = struct.pack("I 5s f d 10s b", 42, "Hello".encode(), 3.6, 10 / 3, b"Hi", True)
    data = {"binary": binary}

    inst = configuraptor.load_into(TopLevel, data).binary
    assert MyBinaryConfig.load(binary)

    assert inst.string == "Hello"
    assert inst.other_string == "Hi"
    assert inst.boolean is True

    assert inst._pack() == binary == asbytes(inst)


def test_nested_binary_config():
    input_data1 = {"name": "Alex", "age": 42}
    input_data2 = {"name": "Sam", "age": 24}
    data1 = struct.pack("32s", json.dumps(input_data1).encode())
    data2 = struct.pack("32s", yaml.dump(input_data2).encode())
    data3 = struct.pack("32s", tomli_w.dumps(input_data2).encode())

    inst = NestedBinaryConfig.load({"data2": data2, "data1": data1, "data3": data3})

    assert inst.data1.name != inst.data2.name

    assert inst._pack() == data1 + data2 + data3 == asbytes(inst)


class Version(BinaryConfig):
    major = BinaryField(int)
    minor = BinaryField(int)
    patch = BinaryField(int)


class Versions(BinaryConfig):
    first = BinaryField(Version)
    second = BinaryField(Version)


def test_binary_config_with_external_block():
    v1 = struct.pack("i i i", 1, 12, 5)
    v2 = struct.pack("i i i", 0, 4, 2)
    data = Versions.load(v1 + v2)

    assert data.first.patch == 5
    assert data.second.major == 0

    assert data._pack() == v1 + v2 == asbytes(data)


class IsNumber(BinaryConfig):
    value = BinaryField(int, format="h")


class IsBigNumber(BinaryConfig):
    value = BinaryField(int, format="l")


class HasNumber(BinaryConfig):
    contains = BinaryField(IsNumber)


def test_resize_config():
    inst = HasNumber()
    assert inst._get_length() == 2
    inst.contains = 12
    assert inst._get_length() == 2

    big_num = IsBigNumber()
    big_num.value = 420

    inst.contains = big_num
    assert inst._get_length() == 8
