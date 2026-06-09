from __future__ import annotations


try:
    from bs4 import (  # noqa: TID251 this is the only allowed use
        BeautifulSoup as BeautifulSoup,
    )

    has_bs4 = True
except ImportError as err:
    BeautifulSoup = None  # type: ignore[assignment,misc]
    has_bs4 = False
    import_error = err


def assert_bs4() -> None:
    if not has_bs4:
        msg = (
            "beautifulsoup4 not found; enable the "
            "`marktplaats[scraping]` extra to use this function"
        )
        raise ImportError(msg) from import_error
