from __future__ import annotations

import logging
from datetime import date, datetime, timedelta

import pytest
import requests

from marktplaats import (
    Condition,
    ListingFirstImage,
    ListingLocation,
    ListingSeller,
    PriceType,
    SearchQuery,
    SortBy,
    SortOrder,
    category_from_name,
)
from marktplaats.models.listing_seller import Seller
from marktplaats.utils import get_request


"""
Live tests (sent to Marktplaats) to ensure they
haven't deployed breaking changes to the search API.
"""


def _validate_response(search: SearchQuery, check_time: bool = False) -> None:
    listings = search.get_listings()

    for listing in listings:
        assert isinstance(listing.title, str)
        assert isinstance(listing.description, str)
        assert isinstance(listing.price, float)
        assert isinstance(listing.price_as_string(lang="nl"), str)
        assert isinstance(listing.price_as_string(lang="en"), str)
        assert isinstance(listing.price_type, PriceType)

        assert isinstance(listing.link, str)
        assert listing.link.startswith("https://")

        # the location object
        assert isinstance(listing.location, ListingLocation)
        assert isinstance(listing.location.city, str)
        assert isinstance(listing.location.latitude, float)
        assert isinstance(listing.location.longitude, float)

        # the seller object
        assert isinstance(listing.seller, ListingSeller)
        assert isinstance(listing.seller.id, int)
        assert isinstance(listing.seller.name, str)
        assert isinstance(listing.seller.is_verified, bool)

        # the date object
        assert isinstance(listing.date, date)
        assert isinstance(listing.date, date)  # for the type checker
        if check_time:
            # should be greater or equal to what we queried for
            assert listing.date >= datetime.now().date() - timedelta(days=7)

        # the full seller object (another request)
        seller = listing.seller.get_seller()
        assert isinstance(seller, Seller)
        assert isinstance(seller.id, int)
        assert isinstance(seller.name, str)
        assert isinstance(seller.is_verified, bool)
        if seller.average_score is not None:
            assert isinstance(seller.average_score, (float, int))
            assert isinstance(seller.number_of_reviews, int)
        assert isinstance(seller.bank_account, bool)
        assert isinstance(seller.identification, bool)
        assert isinstance(seller.phone_number, bool)

        image = listing.first_image
        if image is not None:
            assert isinstance(image, ListingFirstImage)
            assert isinstance(image.extra_small, str)
            assert isinstance(image.medium, str)
            assert isinstance(image.large, str)
            assert isinstance(image.extra_large, str)

            images = listing.get_images()
            assert len(images) >= 1

    # Marktplaats currently returns distanceMeters in whole kilometers, which is
    # why this library exposes distance_km. The following fails if Marktplaats
    # ever increases the precision, so we can reconsider that API.
    for listing in search.body_json["listings"]:
        assert listing["location"]["distanceMeters"] % 1000 == 0, (
            "Sub-kilometer precision detected"
        )


def test_request() -> None:
    search = SearchQuery(
        "fiets",
        zip_code="1016LV",
        distance_km=100,
        price_from=0,
        price_to=100,
        limit=5,
        offset=0,
        sort_by=SortBy.LOCATION,
        sort_order=SortOrder.ASC,
        offered_since=datetime.now() - timedelta(days=7),
        category=category_from_name("Fietsen en Brommers"),
    )

    _validate_response(search, check_time=True)


def test_request_with_condition() -> None:
    search = SearchQuery(
        "schijf",
        zip_code="1016LV",
        distance_km=100,
        price_from=0,
        price_to=100,
        offered_since=datetime.now() - timedelta(days=7),
        condition=Condition.NOT_WORKING,
        category=category_from_name("Computers en Software"),
    )

    _validate_response(search)


# Filters


@pytest.mark.parametrize(
    ("condition", "expected", "category"),
    [
        pytest.param(Condition.NEW, "Nieuw", None, marks=pytest.mark.smoke),
        (Condition.AS_GOOD_AS_NEW, "Zo goed als nieuw", None),
        (Condition.USED, "Gebruikt", None),
        # These two only exist in some categories
        (Condition.REFURBISHED, "Refurbished", "Computers en Software"),
        (Condition.NOT_WORKING, "Niet werkend", "Computers en Software"),
    ],
)
def test_condition_filter(
    condition: Condition, expected: str, category: str | None
) -> None:
    search = SearchQuery(
        "laptop",
        condition=condition,
        category=category_from_name(category) if category else None,
        limit=30,
    )
    listings = search.get_listings()

    assert listings
    for listing in listings:
        conditions = [a["value"] for a in listing.attributes if a["key"] == "condition"]
        assert conditions == [expected], listing.link


@pytest.mark.parametrize("limit", [1, 10, 30, 100])
def test_limit(limit: int) -> None:
    search = SearchQuery("fiets", limit=limit)
    assert len(search.get_listings()) == limit


def test_limit_above_maximum() -> None:
    # Marktplaats rejects pages larger than 100 listings
    with pytest.raises(requests.HTTPError):
        SearchQuery("fiets", limit=101)


@pytest.mark.parametrize(
    ("price_from", "price_to"), [(10, 50), (100, 200), (0, 5), (500, None), (None, 20)]
)
def test_price_range(price_from: int | None, price_to: int | None) -> None:
    search = SearchQuery("fiets", price_from=price_from, price_to=price_to, limit=30)
    listings = search.get_listings()

    assert listings
    for listing in listings:
        if listing.price_type in {PriceType.FIXED, PriceType.BID_FROM}:
            if price_from is not None:
                assert listing.price >= price_from, listing.link
            if price_to is not None:
                assert listing.price <= price_to, listing.link


@pytest.mark.parametrize("distance_km", [5, 25, 100])
@pytest.mark.parametrize("zip_code", ["1016LV", "3011AA", "9711LM"])
def test_distance_km(distance_km: int, zip_code: str) -> None:
    search = SearchQuery("fiets", zip_code=zip_code, distance_km=distance_km, limit=30)
    listings = search.get_listings()

    assert listings
    for listing in listings:
        assert listing.location.distance_km is not None
        assert listing.location.distance_km <= distance_km, listing.link


def test_deprecated_distance_still_works() -> None:
    with pytest.warns(DeprecationWarning, match=r"^distance is deprecated"):
        search = SearchQuery("fiets", zip_code="1016LV", distance=10_000, limit=30)
    for listing in search.get_listings():
        assert listing.location.distance_km is not None
        assert listing.location.distance_km <= 10


@pytest.mark.parametrize("days", [1, 7, 30])
def test_offered_since(days: int) -> None:
    since = datetime.now() - timedelta(days=days)
    search = SearchQuery("fiets", offered_since=since, limit=30)
    listings = search.get_listings()

    assert listings
    for listing in listings:
        assert listing.date is not None
        assert listing.date >= since.date(), listing.link


def test_filters_narrow_the_results() -> None:
    everything = SearchQuery("fiets")
    narrowed = SearchQuery(
        "fiets",
        zip_code="1016LV",
        distance_km=10,
        price_from=50,
        price_to=100,
        condition=Condition.USED,
        category=category_from_name("Fietsen en Brommers"),
    )
    assert isinstance(everything.total_result_count, int)
    assert isinstance(narrowed.total_result_count, int)
    assert 0 < narrowed.total_result_count < everything.total_result_count


# Sorting and paging


@pytest.mark.parametrize("sort_order", list(SortOrder))
def test_sort_by_date(sort_order: SortOrder) -> None:
    search = SearchQuery("fiets", sort_by=SortBy.DATE, sort_order=sort_order, limit=30)
    dates = [listing.date for listing in search.get_listings()]

    assert all(d is not None for d in dates)
    assert dates == sorted(dates, reverse=sort_order is SortOrder.DESC)


@pytest.mark.parametrize("sort_order", list(SortOrder))
def test_sort_by_price(sort_order: SortOrder) -> None:
    # Listings without a price (bids, free, ...) count as 0 and would fill
    #  the whole page when sorting ascending, so only look at priced listings.
    search = SearchQuery(
        "fiets",
        price_from=50,
        sort_by=SortBy.PRICE,
        sort_order=sort_order,
        limit=30,
    )
    prices = [listing.price for listing in search.get_listings()]

    assert prices
    assert prices == sorted(prices, reverse=sort_order is SortOrder.DESC)


@pytest.mark.parametrize("sort_by", list(SortBy))
def test_every_sort_option_is_accepted(sort_by: SortBy) -> None:
    search = SearchQuery("fiets", zip_code="1016LV", sort_by=sort_by, limit=10)
    assert len(search.get_listings()) == 10


@pytest.mark.parametrize("page_size", [10, 30])
def test_pagination(page_size: int) -> None:
    def page(offset: int) -> set[str]:
        search = SearchQuery(
            "fiets",
            limit=page_size,
            offset=offset,
            sort_by=SortBy.DATE,
            sort_order=SortOrder.DESC,
        )
        return {listing.id for listing in search.get_listings()}

    first, second = page(0), page(page_size)
    assert len(first) == page_size
    assert len(second) == page_size
    # Allow a little overlap, new listings can come in between the two requests
    assert len(first & second) <= 2


# The response format


@pytest.mark.parametrize(
    "query",
    [
        pytest.param("fiets", marks=pytest.mark.smoke),
        "bank",
        "auto",
        "gratis",
        "iphone",
        "lego",
    ],
)
def test_all_values_are_understood(
    caplog: pytest.LogCaptureFixture, query: str
) -> None:
    # The library logs a warning for price types and date formats it
    #  doesn't know. Those mean Marktplaats added something new.
    with caplog.at_level(logging.WARNING, logger="marktplaats"):
        listings = SearchQuery(query, limit=100).get_listings()

    assert len(listings) == 100
    assert not caplog.records, caplog.text
    assert all(listing.price_type is not PriceType.UNKNOWN for listing in listings)
    assert all(listing.date is not None for listing in listings)


@pytest.mark.parametrize(
    "query", [pytest.param("fiets", marks=pytest.mark.smoke), "bank", "auto"]
)
def test_response_format(query: str) -> None:
    # Everything the library reads from the raw response,
    #  so a renamed or removed field fails here with a clear message.
    body = SearchQuery(query, limit=30).body_json

    assert isinstance(body["totalResultCount"], int)
    assert isinstance(body["listings"], list)
    assert body["listings"]

    for raw in body["listings"]:
        assert isinstance(raw["itemId"], str)
        # "m" for regular listings, "a" for Admarkt (business) listings
        assert raw["itemId"][0] in {"m", "a"}, raw["itemId"]
        assert isinstance(raw["title"], str)
        assert isinstance(raw["description"], str)
        assert isinstance(raw["date"], str)
        assert isinstance(raw["categoryId"], int)

        assert isinstance(raw["priceInfo"]["priceCents"], int)
        assert isinstance(raw["priceInfo"]["priceType"], str)

        seller = raw["sellerInformation"]
        assert isinstance(seller["sellerId"], int)
        assert isinstance(seller["sellerName"], str)
        assert isinstance(seller["isVerified"], bool)

        location = raw["location"]
        assert isinstance(location["latitude"], (int, float))
        assert isinstance(location["longitude"], (int, float))
        assert isinstance(location["distanceMeters"], int)
        for key in ("cityName", "countryName", "countryAbbreviation"):
            assert isinstance(location.get(key, ""), str)

        for picture in raw.get("pictures", []):
            for key in ("extraSmallUrl", "mediumUrl", "largeUrl", "extraExtraLargeUrl"):
                assert picture[key].startswith("https://"), key

        for attribute in raw.get("attributes", []) + raw.get("extendedAttributes", []):
            assert isinstance(attribute["key"], str)


def test_listing_links_resolve() -> None:
    listings = SearchQuery("fiets", limit=3).get_listings()
    for listing in listings:
        response = get_request(listing.link)
        assert response.status_code == 200, listing.link
        assert listing.id in response.url
