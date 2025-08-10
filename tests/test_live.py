from __future__ import annotations

from datetime import date, datetime, timedelta

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
        assert seller.average_score is not None
        assert isinstance(seller.number_of_reviews, int)
        assert isinstance(seller.bank_account, bool)
        assert isinstance(seller.identification, bool)
        assert isinstance(seller.phone_number, bool)

        image = listing.first_image
        if isinstance(image, ListingFirstImage):
            assert isinstance(image.extra_small, str)
            assert isinstance(image.medium, str)
            assert isinstance(image.large, str)
            assert isinstance(image.extra_large, str)
        else:
            assert image is None


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
