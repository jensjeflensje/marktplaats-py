from __future__ import annotations

import pytest

from marktplaats import PriceType


"""Tests for formatting prices as strings."""


@pytest.mark.parametrize(
    ("price_type", "en", "nl"),
    [
        (PriceType.FREE, "Free", "Gratis"),
        (PriceType.BID, "Bid", "Bieden"),
        (PriceType.RESERVED, "Reserved", "Gereserveerd"),
        (PriceType.SEE_DESCRIPTION, "See description", "Zie omschrijving"),
        (PriceType.TO_BE_AGREED_UPON, "To be agreed upon", "N.o.t.k."),
        (PriceType.ON_REQUEST, "On request", "Op aanvraag"),
        (PriceType.EXCHANGE, "Exchange", "Ruilen"),
        (PriceType.UNKNOWN, "UNKNOWN", "UNKNOWN"),
    ],
)
@pytest.mark.parametrize("euro_sign", [True, False])
def test_non_numeric_price_types(
    price_type: PriceType, en: str, nl: str, euro_sign: bool
) -> None:
    # The price and euro sign are ignored for these price types
    assert price_type._as_string(12.5, euro_sign=euro_sign, lang="en") == en  # ruff:ignore[private-member-access]
    assert price_type._as_string(12.5, euro_sign=euro_sign, lang="nl") == nl  # ruff:ignore[private-member-access]


@pytest.mark.parametrize("price_type", [PriceType.FIXED, PriceType.BID_FROM])
@pytest.mark.parametrize("lang", ["en", "nl"])
@pytest.mark.parametrize(
    ("price", "euro_sign", "expected"),
    [
        (75, True, "€ 75.00"),
        (75, False, "75.00"),
        (0, True, "€ 0.00"),
        (12.5, True, "€ 12.50"),
        (1234.567, False, "1234.57"),
        (0.01, True, "€ 0.01"),
    ],
)
def test_numeric_price_types(
    price_type: PriceType, lang: str, price: float, euro_sign: bool, expected: str
) -> None:
    assert price_type._as_string(price, euro_sign=euro_sign, lang=lang) == expected  # ruff:ignore[private-member-access]


@pytest.mark.parametrize("lang", ["de", "fr", "EN", "NL", ""])
@pytest.mark.parametrize("price_type", list(PriceType))
def test_unsupported_language(price_type: PriceType, lang: str) -> None:
    with pytest.raises(
        ValueError, match=rf"^{lang!r} not in supported languages \(nl, en\)$"
    ):
        price_type._as_string(10, euro_sign=True, lang=lang)  # ruff:ignore[private-member-access]


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("FREE", PriceType.FREE),
        ("FAST_BID", PriceType.BID),
        ("RESERVED", PriceType.RESERVED),
        ("SEE_DESCRIPTION", PriceType.SEE_DESCRIPTION),
        ("NOTK", PriceType.TO_BE_AGREED_UPON),
        ("ON_REQUEST", PriceType.ON_REQUEST),
        ("EXCHANGE", PriceType.EXCHANGE),
        ("FIXED", PriceType.FIXED),
        ("MIN_BID", PriceType.BID_FROM),
    ],
)
def test_api_values(raw: str, expected: PriceType) -> None:
    # These are the raw values the search API returns in priceInfo.priceType
    assert PriceType(raw) is expected
