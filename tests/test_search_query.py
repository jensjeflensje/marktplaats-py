from __future__ import annotations

import copy
import json
import logging
from datetime import datetime
from typing import TYPE_CHECKING, Any

import pytest
import responses

from marktplaats import (
    Condition,
    PriceType,
    SearchQuery,
    SortBy,
    SortOrder,
)
from marktplaats.categories import L1Category, L2Category, category_from_name
from tests.utils import get_mock_file


if TYPE_CHECKING:
    from collections.abc import Iterator


"""Tests for the parameters SearchQuery sends and how it parses the response."""

SEARCH_URL = "https://www.marktplaats.nl/lrp/api/search"

DEFAULT_PARAMS = {
    "limit": "1",
    "offset": "0",
    "query": "fiets",
    "searchInTitleAndDescription": "true",
    "viewOptions": "list-view",
    "distanceMeters": "1000000",
    "postcode": "",
    "sortBy": "OPTIMIZED",
    "sortOrder": "INCREASING",
}


def _body() -> dict[str, Any]:
    return json.loads(get_mock_file("query_response.json"))


def _listing(**overrides: object) -> dict[str, Any]:
    listing = copy.deepcopy(_body()["listings"][0])
    listing.update(overrides)
    return listing


@pytest.fixture
def mocked() -> Iterator[responses.RequestsMock]:
    with responses.RequestsMock() as rsps:
        yield rsps


def _expect_params(
    mocked: responses.RequestsMock,
    params: dict[str, str | list[str]],
    body: dict[str, Any] | None = None,
) -> None:
    mocked.get(
        SEARCH_URL,
        body=json.dumps(body if body is not None else _body()),
        match=[
            responses.matchers.request_kwargs_matcher({"timeout": 15}),
            responses.matchers.query_param_matcher(params),
        ],
    )


def _search_with_listings(
    mocked: responses.RequestsMock,
    *listings: dict[str, Any],
    limit: int = 1,
) -> SearchQuery:
    body = _body()
    body["listings"] = list(listings)
    mocked.get(SEARCH_URL, body=json.dumps(body))
    return SearchQuery("fiets", limit=limit)


# Request parameters


def test_default_params(mocked: responses.RequestsMock) -> None:
    _expect_params(mocked, DEFAULT_PARAMS)
    SearchQuery("fiets")


@pytest.mark.parametrize(
    ("kwargs", "expected"),
    [
        ({"limit": 30}, {"limit": "30"}),
        ({"limit": 100, "offset": 200}, {"limit": "100", "offset": "200"}),
        ({"zip_code": "1016LV"}, {"postcode": "1016LV"}),
        ({"distance_km": 25}, {"distanceMeters": "25000"}),
        ({"distance_km": 0}, {"distanceMeters": "0"}),
        (
            {"zip_code": "3011AA", "distance_km": 5},
            {"postcode": "3011AA", "distanceMeters": "5000"},
        ),
    ],
)
def test_simple_params(
    mocked: responses.RequestsMock,
    kwargs: dict[str, Any],
    expected: dict[str, str],
) -> None:
    _expect_params(mocked, DEFAULT_PARAMS | expected)
    SearchQuery("fiets", **kwargs)


@pytest.mark.parametrize("sort_by", list(SortBy))
@pytest.mark.parametrize("sort_order", list(SortOrder))
def test_sorting(
    mocked: responses.RequestsMock, sort_by: SortBy, sort_order: SortOrder
) -> None:
    _expect_params(
        mocked,
        DEFAULT_PARAMS | {"sortBy": sort_by.value, "sortOrder": sort_order.value},
    )
    SearchQuery("fiets", sort_by=sort_by, sort_order=sort_order)


@pytest.mark.parametrize(
    ("price_from", "price_to", "expected"),
    [
        (10, 200, "PriceCents:1000:20000"),
        (10, None, "PriceCents:1000:null"),
        (None, 200, "PriceCents:null:20000"),
        (0, 0, "PriceCents:0:0"),
        (0, None, "PriceCents:0:null"),
    ],
)
def test_price_range(
    mocked: responses.RequestsMock,
    price_from: int | None,
    price_to: int | None,
    expected: str,
) -> None:
    _expect_params(mocked, DEFAULT_PARAMS | {"attributeRanges[]": expected})
    SearchQuery("fiets", price_from=price_from, price_to=price_to)


@pytest.mark.parametrize("condition", list(Condition))
def test_condition(mocked: responses.RequestsMock, condition: Condition) -> None:
    _expect_params(mocked, DEFAULT_PARAMS | {"attributesById[]": str(condition.value)})
    SearchQuery("fiets", condition=condition)


@pytest.mark.parametrize(
    ("condition", "extra_attributes", "expected"),
    [
        # A single value is matched as a plain string
        (None, [1], "1"),
        (None, [1, 2, 3], ["1", "2", "3"]),
        (None, [], None),
        (Condition.NEW, [1], ["30", "1"]),
        (Condition.USED, [5, 6], ["32", "5", "6"]),
    ],
)
def test_attributes_by_id(
    mocked: responses.RequestsMock,
    condition: Condition | None,
    extra_attributes: list[int],
    expected: str | list[str] | None,
) -> None:
    # An empty list means the parameter isn't sent at all
    params: dict[str, str | list[str]] = dict(DEFAULT_PARAMS)
    if expected is not None:
        params["attributesById[]"] = expected
    _expect_params(mocked, params)
    SearchQuery("fiets", condition=condition, extra_attributes=extra_attributes)


@pytest.mark.parametrize(
    "offered_since",
    [
        datetime(2024, 12, 31, 14, 10, 0),
        datetime(2026, 1, 1, 0, 0, 0),
        # Sub-second precision is dropped
        datetime(2026, 9, 22, 8, 30, 15, 999999),
    ],
)
def test_offered_since(mocked: responses.RequestsMock, offered_since: datetime) -> None:
    millis = int(offered_since.timestamp()) * 1000
    _expect_params(
        mocked, DEFAULT_PARAMS | {"attributesByKey[]": f"offeredSince:{millis}"}
    )
    SearchQuery("fiets", offered_since=offered_since)


@pytest.mark.parametrize(
    ("name", "expected"),
    [
        ("Fietsen en Brommers", {"l1CategoryId": "445"}),
        ("Auto's", {"l1CategoryId": "91"}),
        (
            "Fietsen | Mountainbikes en ATB",
            {"l1CategoryId": "445", "l2CategoryIds": "460"},
        ),
        ("Volkswagen", {"l1CategoryId": "91", "l2CategoryIds": "157"}),
        ("Windows Laptops", {"l1CategoryId": "322", "l2CategoryIds": "339"}),
    ],
)
def test_category(
    mocked: responses.RequestsMock, name: str, expected: dict[str, str]
) -> None:
    _expect_params(mocked, DEFAULT_PARAMS | expected)
    SearchQuery("fiets", category=category_from_name(name))


@pytest.mark.parametrize(
    "category",
    [
        L1Category(445, "Fietsen en Brommers"),
        L2Category(460, "Fietsen | Mountainbikes en ATB", L1Category(445, "")),
    ],
)
def test_category_without_query(
    mocked: responses.RequestsMock, category: L1Category | L2Category
) -> None:
    # A category on its own is enough, no search term needed
    expected = {"query": "", "l1CategoryId": "445"}
    if isinstance(category, L2Category):
        expected["l2CategoryIds"] = "460"
    _expect_params(mocked, DEFAULT_PARAMS | expected)
    SearchQuery(category=category)


def test_all_params_combined(mocked: responses.RequestsMock) -> None:
    offered_since = datetime(2026, 9, 1, 12, 0, 0)
    _expect_params(
        mocked,
        {
            "limit": "50",
            "offset": "100",
            "query": "trek",
            "searchInTitleAndDescription": "true",
            "viewOptions": "list-view",
            "distanceMeters": "30000",
            "postcode": "1016LV",
            "sortBy": "PRICE",
            "sortOrder": "DECREASING",
            "attributeRanges[]": "PriceCents:10000:null",
            "attributesById[]": ["31", "7"],
            "attributesByKey[]": f"offeredSince:{int(offered_since.timestamp()) * 1000}",
            "l1CategoryId": "445",
            "l2CategoryIds": "460",
        },
    )
    SearchQuery(
        "trek",
        zip_code="1016LV",
        distance_km=30,
        price_from=100,
        limit=50,
        offset=100,
        sort_by=SortBy.PRICE,
        sort_order=SortOrder.DESC,
        condition=Condition.AS_GOOD_AS_NEW,
        offered_since=offered_since,
        category=category_from_name("Fietsen | Mountainbikes en ATB"),
        extra_attributes=[7],
    )


# Deprecated distance parameter


@pytest.mark.parametrize(
    ("distance", "expected"), [(5000, "5000"), (1500, "1500"), (0, "0")]
)
def test_deprecated_distance(
    mocked: responses.RequestsMock, distance: int, expected: str
) -> None:
    _expect_params(mocked, DEFAULT_PARAMS | {"distanceMeters": expected})
    with pytest.warns(
        DeprecationWarning,
        match=r"^distance is deprecated\. Use distance_km instead\.$",
    ):
        SearchQuery("fiets", distance=distance)


def test_distance_km_wins_over_deprecated_distance(
    mocked: responses.RequestsMock,
) -> None:
    _expect_params(mocked, DEFAULT_PARAMS | {"distanceMeters": "10000"})
    with pytest.warns(DeprecationWarning, match=r"^distance is deprecated"):
        SearchQuery("fiets", distance=5000, distance_km=10)


@pytest.mark.filterwarnings("error::DeprecationWarning")
def test_distance_km_does_not_warn(mocked: responses.RequestsMock) -> None:
    _expect_params(mocked, DEFAULT_PARAMS | {"distanceMeters": "10000"})
    SearchQuery("fiets", distance_km=10)


# Parsing the response


@pytest.mark.parametrize(
    ("total", "expected"), [(100, 100), (0, 0), (123456, 123456), (None, None)]
)
def test_total_result_count(
    mocked: responses.RequestsMock, total: int | None, expected: int | None
) -> None:
    body = _body()
    if total is None:
        del body["totalResultCount"]
    else:
        body["totalResultCount"] = total
    mocked.get(SEARCH_URL, body=json.dumps(body))
    assert SearchQuery("fiets").total_result_count == expected


def test_no_listings(mocked: responses.RequestsMock) -> None:
    query = _search_with_listings(mocked, limit=10)
    assert query.get_listings() == []


@pytest.mark.parametrize(
    ("limit", "returned", "expected"),
    [(1, 1, 1), (5, 20, 5), (10, 3, 3), (30, 30, 30), (100, 0, 0)],
)
def test_limit_variants(
    mocked: responses.RequestsMock, limit: int, returned: int, expected: int
) -> None:
    listings = [_listing(itemId=f"m{i}") for i in range(returned)]
    query = _search_with_listings(mocked, *listings, limit=limit)
    result = query.get_listings()
    assert len(result) == expected
    # The first listings are kept, in order
    assert [listing.id for listing in result] == [f"m{i}" for i in range(expected)]


def test_listing_fields(mocked: responses.RequestsMock) -> None:
    (listing,) = _search_with_listings(mocked, _listing()).get_listings()

    assert listing.id == "m2064554806"
    assert listing.title == "Batavus damesfiets 26 inch"
    assert listing.description.startswith("Degelijke batavus damesfiets")
    assert listing.link == "https://link.marktplaats.nl/m2064554806"
    assert listing.category_id == 447
    assert listing.price == 75.0  # ruff:ignore[float-equality-comparison]
    assert listing.price_as_string() == "€ 75.00"
    assert listing.price_as_string(euro_sign=False, lang="nl") == "75.00"
    assert listing.seller.id == 7405065
    assert listing.seller.name == "Vogel"
    assert [a["key"] for a in listing.attributes] == ["condition", "delivery"]
    assert [a["key"] for a in listing.extended_attributes] == ["condition", "delivery"]


@pytest.mark.parametrize(
    ("price_type", "cents", "expected_type", "expected_en", "expected_nl"),
    [
        ("FIXED", 7500, PriceType.FIXED, "€ 75.00", "€ 75.00"),
        ("FIXED", 1999, PriceType.FIXED, "€ 19.99", "€ 19.99"),
        ("MIN_BID", 25000, PriceType.BID_FROM, "€ 250.00", "€ 250.00"),
        ("FREE", 0, PriceType.FREE, "Free", "Gratis"),
        ("FAST_BID", 0, PriceType.BID, "Bid", "Bieden"),
        ("NOTK", 0, PriceType.TO_BE_AGREED_UPON, "To be agreed upon", "N.o.t.k."),
        ("EXCHANGE", 0, PriceType.EXCHANGE, "Exchange", "Ruilen"),
    ],
)
def test_listing_price_types(  # ruff:ignore[too-many-arguments, too-many-positional-arguments]
    mocked: responses.RequestsMock,
    price_type: str,
    cents: int,
    expected_type: PriceType,
    expected_en: str,
    expected_nl: str,
) -> None:
    raw = _listing(priceInfo={"priceCents": cents, "priceType": price_type})
    (listing,) = _search_with_listings(mocked, raw).get_listings()
    assert listing.price_type is expected_type
    assert listing.price == pytest.approx(cents / 100)
    assert listing.price_as_string(lang="en") == expected_en
    assert listing.price_as_string(lang="nl") == expected_nl


@pytest.mark.parametrize("price_type", ["SOMETHING_NEW", "", "fixed"])
def test_unknown_price_type(
    mocked: responses.RequestsMock, caplog: pytest.LogCaptureFixture, price_type: str
) -> None:
    raw = _listing(priceInfo={"priceCents": 100, "priceType": price_type})
    with caplog.at_level(logging.WARNING, logger="marktplaats.query"):
        (listing,) = _search_with_listings(mocked, raw).get_listings()

    assert listing.price_type is PriceType.UNKNOWN
    assert listing.price_as_string() == "UNKNOWN"
    assert "unknown PriceType" in caplog.text
    assert "m2064554806" in caplog.text


@pytest.mark.parametrize("date_str", ["Morgen", "10 march 24", ""])
def test_unknown_date_format(
    mocked: responses.RequestsMock, caplog: pytest.LogCaptureFixture, date_str: str
) -> None:
    with caplog.at_level(logging.WARNING, logger="marktplaats.query"):
        (listing,) = _search_with_listings(
            mocked, _listing(date=date_str)
        ).get_listings()

    assert listing.date is None
    assert "unknown date format" in caplog.text
    assert "m2064554806" in caplog.text


@pytest.mark.parametrize(
    ("pictures", "expected_count"),
    [
        (None, 0),
        ([], 0),
        ("mock", 1),
        ("mock*3", 3),
    ],
)
def test_first_image(
    mocked: responses.RequestsMock, pictures: str | None, expected_count: int
) -> None:
    raw = _listing()
    mock_pictures = raw["pictures"]
    if pictures is None:
        del raw["pictures"]
    elif pictures == "mock":
        raw["pictures"] = mock_pictures
    elif pictures == "mock*3":
        raw["pictures"] = mock_pictures * 3
    else:
        raw["pictures"] = pictures

    (listing,) = _search_with_listings(mocked, raw).get_listings()

    with pytest.warns(DeprecationWarning, match=r"^Listing\.images is deprecated"):
        assert len(listing.images) == expected_count
    if expected_count:
        assert listing.first_image is not None
        assert listing.first_image.medium.endswith("_82.jpg")
    else:
        assert listing.first_image is None


@pytest.mark.parametrize(
    ("distance_meters", "expected_km", "expected_m"),
    [
        (1000, 1, 1000),
        (0, 0, 0),
        (25000, 25, 25000),
        (1500, 1, 1000),  # Whole kilometers only
        (-1000, None, None),  # Marktplaats' "unknown" value
    ],
)
def test_location_distance(
    mocked: responses.RequestsMock,
    distance_meters: int,
    expected_km: int | None,
    expected_m: int | None,
) -> None:
    raw = _listing()
    raw["location"]["distanceMeters"] = distance_meters
    (listing,) = _search_with_listings(mocked, raw).get_listings()

    assert listing.location.distance_km == expected_km
    with pytest.warns(
        DeprecationWarning,
        match=r"^ListingLocation\.distance is deprecated\. Use distance_km instead\.$",
    ):
        assert listing.location.distance == expected_m


@pytest.mark.parametrize(
    ("latitude", "longitude", "expected"),
    [
        (51.96, 4.61, (51.96, 4.61)),
        (0, 0, (None, None)),  # Marktplaats' "unknown" value
        (0, 4.61, (None, 4.61)),
        (52.37, 0, (52.37, None)),
    ],
)
def test_location_coordinates(
    mocked: responses.RequestsMock,
    latitude: float,
    longitude: float,
    expected: tuple[float | None, float | None],
) -> None:
    raw = _listing()
    raw["location"].update(latitude=latitude, longitude=longitude)
    (listing,) = _search_with_listings(mocked, raw).get_listings()

    assert (listing.location.latitude, listing.location.longitude) == expected


def test_location_fields(mocked: responses.RequestsMock) -> None:
    (listing,) = _search_with_listings(mocked, _listing()).get_listings()
    assert listing.location.city == "Nieuwerkerk aan den IJssel"
    assert listing.location.country == "Nederland"
    assert listing.location.country_short == "NL"


def test_location_missing_optional_fields(mocked: responses.RequestsMock) -> None:
    raw = _listing()
    for key in ("cityName", "countryName", "countryAbbreviation"):
        del raw["location"][key]
    (listing,) = _search_with_listings(mocked, raw).get_listings()
    assert listing.location.city is None
    assert listing.location.country is None
    assert listing.location.country_short is None


def test_missing_attributes(mocked: responses.RequestsMock) -> None:
    raw = _listing()
    del raw["attributes"]
    del raw["extendedAttributes"]
    (listing,) = _search_with_listings(mocked, raw).get_listings()
    assert listing.attributes == []
    assert listing.extended_attributes == []


def test_listing_equality(mocked: responses.RequestsMock) -> None:
    listings = _search_with_listings(
        mocked,
        _listing(itemId="m1", title="first"),
        _listing(itemId="m1", title="same id, other title"),
        _listing(itemId="m2"),
        limit=3,
    ).get_listings()

    first, same_id, other = listings
    assert first == same_id
    assert first != other
    assert first != "m1"
    assert len({first, same_id, other}) == 2


@pytest.mark.parametrize("status", [400, 403, 404, 429, 500, 502, 503])
def test_http_errors(mocked: responses.RequestsMock, status: int) -> None:
    import requests  # ruff:ignore[import-outside-top-level]

    mocked.get(SEARCH_URL, status=status)
    with pytest.raises(requests.HTTPError):
        SearchQuery("fiets")


@pytest.mark.parametrize("status", [201, 202, 204, 301, 304])
def test_non_200_success_codes(mocked: responses.RequestsMock, status: int) -> None:
    from marktplaats import BadStatusCodeError  # ruff:ignore[import-outside-top-level]

    mocked.get(SEARCH_URL, status=status)
    with pytest.raises(BadStatusCodeError, match=r"^Received non-200 status code:"):
        SearchQuery("fiets")


@pytest.mark.parametrize("body", ["", "not json", "<html></html>", "{"])
def test_invalid_json_variants(mocked: responses.RequestsMock, body: str) -> None:
    from marktplaats import JSONDecodeError  # ruff:ignore[import-outside-top-level]

    mocked.get(SEARCH_URL, body=body)
    with pytest.raises(JSONDecodeError) as exc_info:
        SearchQuery("fiets")
    # The raw body is kept for debugging
    assert exc_info.value.obj == body
    assert str(exc_info.value) == f"Received invalid (non-json) response: {body}"


@pytest.mark.parametrize(
    "kwargs",
    [
        {},
        {"price_to": 10},
        {"zip_code": "1016LV", "distance_km": 10},
        {"condition": Condition.NEW},
    ],
)
def test_query_or_category_required(kwargs: dict[str, Any]) -> None:
    with pytest.raises(ValueError, match="a category must be specified"):
        SearchQuery(**kwargs)
