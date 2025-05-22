import json

import pytest

from src.configuraptor import load_into
from src.configuraptor.core import from_url, load_data
from src.configuraptor.errors import FailedToLoad


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
    url0 = "https://my-api.dev/styles.json?secret=any"

    _, filetype = from_url(url0, _dummy=True)

    # from url
    assert filetype == "json"

    class Dummy: ...

    with pytest.raises(FailedToLoad):
        load_into(Dummy, url0, strict=True)

    with pytest.warns(UserWarning):
        assert load_into(Dummy, url0, strict=False)

    url1 = "https://jsonplaceholder.typicode.com/posts/1"

    _, filetype = from_url(url1)

    # from content-type
    assert filetype == "json"

    class JsonPlaceholder:
        userId: int
        id: int
        title: str
        body: str
        other: str | None

    json_placeholder = load_into(JsonPlaceholder, url1)
    assert json_placeholder.id == 1

    # two urls:
    with pytest.raises(FailedToLoad):
        load_data([url0, url1], strict=True)


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
