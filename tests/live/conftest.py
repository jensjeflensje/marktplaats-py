from __future__ import annotations

import time
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    import pytest


def pytest_runtest_setup(item: pytest.Item) -> None:  # ruff: ignore[unused-function-argument]
    # Marktplaats rate limits listing pages (HTTP 403 from CloudFront),
    #  so leave a little room between tests.
    time.sleep(0.5)
