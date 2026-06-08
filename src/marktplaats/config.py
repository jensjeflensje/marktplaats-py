from __future__ import annotations

from dataclasses import dataclass


ISSUE_LINK = "https://github.com/jensjeflensje/marktplaats-py/issues"


@dataclass
class HttpOptions:
    user_agent: str
    timeout: int
