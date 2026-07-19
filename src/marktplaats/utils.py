from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING, Any


if TYPE_CHECKING:
    from collections.abc import Mapping

    from requests import Response, Session  # noqa: TID251 - Only used for type hinting.


def get_request(  # type: ignore[explicit-any] # This is Any to avoid replicating the actual type of the `params` parameter
    url: str,
    session: Session,
    params: Mapping[str, Any] | None = None,
) -> Response:
    return session.get(
        url,
        params=params,
        timeout=15,
    )


class MessageObjectException(Exception, ABC):  # noqa: N818 this is a base class, not an error itself
    def __init__(self, msg: str, obj: object) -> None:
        super().__init__(msg, obj)
        self.msg = msg
        self.obj = obj

    def __str__(self) -> str:
        return f"{self.msg} {self.obj}"
