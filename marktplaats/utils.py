from __future__ import annotations


REQUEST_HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
}


class MessageObjectException(Exception):
    def __init__(self, msg: str, obj: object) -> None:
        super().__init__(msg, obj)
        self.msg = msg
        self.obj = obj

    def __str__(self) -> str:
        return f"{self.msg} {self.obj}"
