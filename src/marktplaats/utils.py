from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING, Any

import requests  # noqa: TID251 This is the only allowed use
from requests import Response  # noqa: TID251 Not doing any requests


if TYPE_CHECKING:
    from collections.abc import Mapping


REQUEST_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/101.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
}


def get_request(  # type: ignore[explicit-any] # This is Any to avoid replicating the actual type of the `params` parameter
    url: str,
    params: Mapping[str, Any] | None = None,
) -> Response:
    return requests.get(
        url,
        params=params,
        # Some headers to make the request look legit
        headers=REQUEST_HEADERS,
        timeout=15,
    )


class MessageObjectException(Exception, ABC):  # noqa: N818 this is a base class, not an error itself
    def __init__(self, msg: str, obj: object) -> None:
        super().__init__(msg, obj)
        self.msg = msg
        self.obj = obj

    def __str__(self) -> str:
        return f"{self.msg} {self.obj}"
