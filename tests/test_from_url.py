import json

from src.configuraptor import load_into
from src.configuraptor.core import from_url


class Configuration:
    color: str
    width: int


def mock_request_one():
    return {"color": "green", "width": 15}


def mock_request_two():
    return {"color": "green"}


def mock_request_three():
    return {"width": 15}


def mock_url(callback):
    data = json.dumps(callback())
    return f"mock://{data}"


def test_from_url():
    _, filetype = from_url("https://my-api.dev/styles.json?secret=any", _dummy=True)

    # from url
    assert filetype == "json"

    _, filetype = from_url("https://jsonplaceholder.typicode.com/posts/1")

    # from content-type
    assert filetype == "json"


def test_one_url():
    inst = load_into(Configuration, mock_url(mock_request_one))

    assert inst.color == "green"
    assert inst.width == 15


def test_multiple_urls():
    inst = load_into(Configuration, [mock_url(mock_request_two), mock_url(mock_request_three)])

    assert inst.color == "green"
    assert inst.width == 15


def test_mixed():
    inst = load_into(Configuration, [mock_url(mock_request_two), {"width": 15}])

    assert inst.color == "green"
    assert inst.width == 15
