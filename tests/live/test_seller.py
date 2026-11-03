from __future__ import annotations

import pytest

from marktplaats import Listing, SearchQuery, SellerQuery, SortBy, SortOrder
from marktplaats.models.listing_seller import Seller


"""
Live tests (sent to Marktplaats) to ensure they
haven't deployed breaking changes to the seller APIs.
"""


@pytest.fixture(scope="module")
def listings() -> list[Listing]:
    """
    Get a few recent listings, from different sellers.

    Returns:
        The listings.

    """
    search = SearchQuery(
        "fiets", limit=30, sort_by=SortBy.DATE, sort_order=SortOrder.DESC
    )
    by_seller = {listing.seller.id: listing for listing in search.get_listings()}
    return list(by_seller.values())[:5]


@pytest.fixture
def seller_id(listings: list[Listing]) -> int:
    """
    Get the seller ID of a random listing.

    Returns:
        The seller ID.

    """
    return listings[0].seller.id


@pytest.mark.smoke
def test_seller_details(seller_id: int) -> None:
    details = SellerQuery(seller_id).fetch_details()

    assert isinstance(details["bankAccount"], bool)
    assert isinstance(details["phoneNumber"], bool)
    assert isinstance(details["identification"], bool)
    assert isinstance(details["reviews"], list)


@pytest.mark.smoke
def test_seller_listings(seller_id: int) -> None:
    listings = SellerQuery(seller_id).fetch_listings()

    assert listings["total"] >= 1
    assert len(listings["items"]) >= 1

    listing = listings["items"][0]
    assert isinstance(listing["itemId"], str)
    assert isinstance(listing["title"], str)
    assert isinstance(listing["price"]["priceCents"], int)
    assert isinstance(listing["url"], str)


@pytest.mark.parametrize(
    "index", [pytest.param(0, marks=pytest.mark.smoke), 1, 2, 3, 4]
)
def test_get_seller(listings: list[Listing], index: int) -> None:
    listing = listings[index]
    seller = listing.seller.get_seller()

    assert isinstance(seller, Seller)
    assert seller.id == listing.seller.id
    assert seller.name == listing.seller.name
    assert seller.is_verified is listing.seller.is_verified
    assert isinstance(seller.bank_account, bool)
    assert isinstance(seller.identification, bool)
    assert isinstance(seller.phone_number, bool)
    if seller.number_of_reviews is None:
        assert seller.average_score is None
    else:
        assert isinstance(seller.number_of_reviews, int)
        assert seller.number_of_reviews >= 1
        # Marktplaats has sent both "averageScore" and "rating" (#184)
        assert isinstance(seller.average_score, (int, float))
        assert 0 < seller.average_score <= 5


@pytest.mark.parametrize("index", range(5))
def test_seller_details_reviews(listings: list[Listing], index: int) -> None:
    details = SellerQuery(listings[index].seller.id).fetch_details()

    for review in details["reviews"]:
        assert isinstance(review["numberOfReviews"], int)
        # The library needs one of these for Seller.average_score
        assert "averageScore" in review or "rating" in review, review


@pytest.mark.parametrize(
    "index", [pytest.param(0, marks=pytest.mark.smoke), 1, 2, 3, 4]
)
def test_seller_listings_include_the_listing(
    listings: list[Listing], index: int
) -> None:
    # The seller listings endpoint is called with a fake item id,
    #  so it should return all of the seller's listings.
    listing = listings[index]
    seller_listings = SellerQuery(listing.seller.id).fetch_listings()

    item_ids = {item["itemId"] for item in seller_listings["items"]}
    assert listing.id in item_ids
    assert seller_listings["total"] >= len(seller_listings["items"]) >= 1


@pytest.mark.parametrize("index", range(5))
def test_seller_listings_format(listings: list[Listing], index: int) -> None:
    seller_listings = SellerQuery(listings[index].seller.id).fetch_listings()

    for item in seller_listings["items"]:
        assert isinstance(item["itemId"], str)
        assert item["itemId"][0] in {"m", "a"}, item["itemId"]
        assert isinstance(item["title"], str)
        assert isinstance(item["price"]["priceCents"], int)
        assert isinstance(item["price"]["priceType"], str)
        assert isinstance(item["category"]["id"], int)
        assert isinstance(item["category"]["name"], str)
        assert item["url"].startswith("/v/")
