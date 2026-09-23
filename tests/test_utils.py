from __future__ import annotations

import pytest
import responses

from marktplaats import BadStatusCodeError, JSONDecodeError
from marktplaats.utils import REQUEST_HEADERS, get_request


"""Tests for the shared request helper and exceptions."""


@pytest.mark.parametrize(
    ("params", "expected"),
    [
        (None, {}),
        ({}, {}),
        ({"a": "1"}, {"a": "1"}),
        ({"sellerId": 42, "flag": "true"}, {"sellerId": "42", "flag": "true"}),
        ({"list[]": ["1", "2"]}, {"list[]": ["1", "2"]}),
    ],
)
def test_get_request(
    params: dict[str, object] | None, expected: dict[str, object]
) -> None:
    with responses.RequestsMock() as rsps:
        rsps.get(
            "https://www.marktplaats.nl/test",
            body="ok",
            match=[
                responses.matchers.header_matcher(REQUEST_HEADERS),
                responses.matchers.request_kwargs_matcher({"timeout": 15}),
                responses.matchers.query_param_matcher(expected),
            ],
        )
        assert get_request("https://www.marktplaats.nl/test", params).text == "ok"


@pytest.mark.parametrize("status", [200, 404, 500])
def test_get_request_does_not_raise(status: int) -> None:
    # Callers decide what to do with the status code
    with responses.RequestsMock() as rsps:
        rsps.get("https://www.marktplaats.nl/test", status=status)
        assert get_request("https://www.marktplaats.nl/test").status_code == status


@pytest.mark.parametrize("exc_type", [BadStatusCodeError, JSONDecodeError])
@pytest.mark.parametrize(
    ("msg", "obj", "expected"),
    [
        ("Received non-200 status code:", 204, "Received non-200 status code: 204"),
        (
            "Received invalid (non-json) response:",
            "oops",
            "Received invalid (non-json) response: oops",
        ),
        ("msg", None, "msg None"),
    ],
)
def test_message_object_exception(
    exc_type: type[BadStatusCodeError | JSONDecodeError],
    msg: str,
    obj: object,
    expected: str,
) -> None:
    exc = exc_type(msg, obj)
    assert exc.msg == msg
    assert exc.obj == obj
    assert str(exc) == expected
    assert exc.args == (msg, obj)
