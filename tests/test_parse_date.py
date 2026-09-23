from __future__ import annotations

from datetime import date, datetime

import pytest

from marktplaats import query
from marktplaats.query import get_price_cents, parse_date, replace_dutch_months


"""Tests for the helpers that turn Marktplaats' values into Python values."""


class _FixedDatetime(datetime):
    @classmethod
    def now(cls, tz: object = None) -> _FixedDatetime:  # ruff: ignore[unused-class-method-argument]
        return cls(2026, 3, 1, 12, 0, 0)


@pytest.fixture
def fixed_now(monkeypatch: pytest.MonkeyPatch) -> None:
    # 2026-03-01 is right after a (non-leap) February, so this also checks
    #  that going back in time crosses month boundaries correctly.
    monkeypatch.setattr(query, "datetime", _FixedDatetime)


@pytest.mark.usefixtures("fixed_now")
@pytest.mark.parametrize(
    ("date_str", "expected"),
    [
        ("Vandaag", date(2026, 3, 1)),
        ("Gisteren", date(2026, 2, 28)),
        ("Eergisteren", date(2026, 2, 27)),
    ],
)
def test_relative_dates(date_str: str, expected: date) -> None:
    assert parse_date(date_str) == expected


@pytest.mark.parametrize(
    ("date_str", "expected"),
    [
        ("10 jan 24", date(2024, 1, 10)),
        ("29 feb 24", date(2024, 2, 29)),
        ("10 mrt 24", date(2024, 3, 10)),
        ("1 apr 25", date(2025, 4, 1)),
        ("15 mei 25", date(2025, 5, 15)),
        ("30 jun 25", date(2025, 6, 30)),
        ("4 jul 26", date(2026, 7, 4)),
        ("29 aug 26", date(2026, 8, 29)),
        ("09 sep 26", date(2026, 9, 9)),
        ("31 okt 26", date(2026, 10, 31)),
        ("11 nov 23", date(2023, 11, 11)),
        ("25 dec 23", date(2023, 12, 25)),
    ],
)
def test_absolute_dates(date_str: str, expected: date) -> None:
    assert parse_date(date_str) == expected


@pytest.mark.parametrize(
    "date_str",
    [
        "",
        "Morgen",
        "vandaag",  # Relative words are case-sensitive
        "10 march 24",
        "32 jan 24",
        "29 feb 25",  # Not a leap year
        "2024-03-10",
    ],
)
def test_invalid_dates(date_str: str) -> None:
    with pytest.raises(ValueError):  # ruff:ignore[pytest-raises-too-broad]
        parse_date(date_str)


@pytest.mark.parametrize(
    ("dutch", "english"),
    [
        ("10 mrt 24", "10 Mar 24"),
        ("15 mei 25", "15 May 25"),
        ("31 okt 26", "31 Oct 26"),
        ("1 jan 24", "1 Jan 24"),
        ("Vandaag", "Vandaag"),  # Nothing to replace
    ],
)
def test_replace_dutch_months(dutch: str, english: str) -> None:
    assert replace_dutch_months(dutch) == english


@pytest.mark.parametrize(
    ("price", "expected"),
    [
        (None, "null"),
        (0, "0"),
        (1, "100"),
        (10, "1000"),
        (200, "20000"),
        (123456, "12345600"),
    ],
)
def test_get_price_cents(price: int | None, expected: str) -> None:
    assert get_price_cents(price) == expected
