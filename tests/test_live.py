from __future__ import annotations

from datetime import date, datetime, timedelta

import pytest

from marktplaats import (
    Condition,
    ListingFirstImage,
    ListingLocation,
    ListingSeller,
    PriceType,
    SearchQuery,
    SellerQuery,
    SortBy,
    SortOrder,
    category_from_name,
)
from marktplaats.models.listing_seller import Seller


"""
Live tests (sent to Marktplaats) to ensure they
haven't deployed breaking changes.
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


def test_request() -> None:
    search = SearchQuery(
        "fiets",
        zip_code="1016LV",
        distance=100000,
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
        distance=100000,
        price_from=0,
        price_to=100,
        offered_since=datetime.now() - timedelta(days=7),
        condition=Condition.NOT_WORKING,
        category=category_from_name("Computers en Software"),
    )

    _validate_response(search)


@pytest.fixture
def seller_id() -> int:
    """
    Get the seller ID of a random listing.

    Returns:
        The seller ID.

    """
    search_query = SearchQuery(query="fiets", limit=1)
    return search_query.get_listings()[0].seller.id


def test_seller_details(seller_id: int) -> None:
    details = SellerQuery(seller_id).fetch_details()

    assert isinstance(details["bankAccount"], bool)
    assert isinstance(details["phoneNumber"], bool)
    assert isinstance(details["identification"], bool)
    assert isinstance(details["reviews"], list)


def test_seller_listings(seller_id: int) -> None:
    listings = SellerQuery(seller_id).fetch_listings()

    assert listings["total"] >= 1
    assert len(listings["items"]) >= 1

    listing = listings["items"][0]
    assert isinstance(listing["itemId"], str)
    assert isinstance(listing["title"], str)
    assert isinstance(listing["price"]["priceCents"], int)
    assert isinstance(listing["url"], str)
