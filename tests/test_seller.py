from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any

import pytest
import requests
import responses

from marktplaats import SellerQuery
from marktplaats.models import ListingSeller
from tests.utils import get_mock_file


if TYPE_CHECKING:
    from collections.abc import Iterator


"""Tests for fetching seller information."""

PROFILE_URL = "https://www.marktplaats.nl/v/api/seller-profile/{}"
LISTINGS_URL = "https://www.marktplaats.nl/v/api/seller-other-items"

SELLER_LISTINGS_BODY = {
    "items": [
        {
            "itemId": "m2064554806",
            "title": "Batavus damesfiets 26 inch",
            "price": {"priceCents": 7500, "priceType": "FIXED"},
            "url": "/v/fietsen-en-brommers/fietsen-dames-damesfietsen/m2064554806",
        },
        {
            "itemId": "m2064554807",
            "title": "Gazelle herenfiets",
            "price": {"priceCents": 0, "priceType": "FAST_BID"},
            "url": "/v/fietsen-en-brommers/fietsen-heren-herenfietsen/m2064554807",
        },
    ],
    "total": 2,
}


def _profile(**overrides: object) -> dict[str, Any]:
    body: dict[str, Any] = json.loads(get_mock_file("seller_response.json"))
    body.update(overrides)
    return body


@pytest.fixture
def mocked() -> Iterator[responses.RequestsMock]:
    with responses.RequestsMock() as rsps:
        yield rsps


# Fetching the full seller of a listing


@pytest.mark.parametrize(
    ("reviews", "expected_score", "expected_count"),
    [
        ([{"numberOfReviews": 175, "averageScore": 4.8}], 4.8, 175),
        ([{"numberOfReviews": 1, "averageScore": 5}], 5, 1),
        # Some sellers only have "rating" (#184)
        ([{"numberOfReviews": 12, "rating": 4}], 4, 12),
        ([{"numberOfReviews": 3, "averageScore": None, "rating": 3}], 3, 3),
        ([], None, None),
    ],
)
def test_get_seller_reviews(
    mocked: responses.RequestsMock,
    reviews: list[dict[str, Any]],
    expected_score: float | None,
    expected_count: int | None,
) -> None:
    mocked.get(PROFILE_URL.format(42), json=_profile(reviews=reviews))

    seller = ListingSeller(42, "Vogel", is_verified=True).get_seller()

    assert seller.average_score == expected_score
    assert seller.number_of_reviews == expected_count


@pytest.mark.parametrize(
    ("bank_account", "identification", "phone_number"),
    [
        (True, True, True),
        (False, False, False),
        (True, False, True),
        (False, True, False),
    ],
)
@pytest.mark.parametrize("is_verified", [True, False])
def test_get_seller_flags(
    mocked: responses.RequestsMock,
    bank_account: bool,
    identification: bool,
    phone_number: bool,
    is_verified: bool,
) -> None:
    mocked.get(
        PROFILE_URL.format(7405065),
        json=_profile(
            bankAccount=bank_account,
            identification=identification,
            phoneNumber=phone_number,
        ),
        match=[responses.matchers.request_kwargs_matcher({"timeout": 15})],
    )

    seller = ListingSeller(7405065, "Vogel", is_verified).get_seller()

    # These come from the listing, not the profile request
    assert seller.id == 7405065
    assert seller.name == "Vogel"
    assert seller.is_verified is is_verified
    # These come from the profile request
    assert seller.bank_account is bank_account
    assert seller.identification is identification
    assert seller.phone_number is phone_number


def test_listing_seller_parse() -> None:
    seller = ListingSeller.parse(
        {
            "sellerId": 123,
            "sellerName": "Jan",
            "isVerified": True,
            "showSoiUrl": True,
            "showWebsiteUrl": False,
        }
    )
    assert seller == ListingSeller(123, "Jan", is_verified=True)


# SellerQuery


@pytest.mark.parametrize("seller_id", [1, 7405065, 99999999])
def test_fetch_details(mocked: responses.RequestsMock, seller_id: int) -> None:
    mocked.get(PROFILE_URL.format(seller_id), json=_profile())

    details = SellerQuery(seller_id).fetch_details()

    assert details["bankAccount"] is True
    assert details["reviews"][0]["numberOfReviews"] == 175


@pytest.mark.parametrize("seller_id", [1, 7405065, 99999999])
def test_fetch_listings(mocked: responses.RequestsMock, seller_id: int) -> None:
    mocked.get(
        LISTINGS_URL,
        json=SELLER_LISTINGS_BODY,
        match=[
            responses.matchers.query_param_matcher(
                {
                    "sellerId": str(seller_id),
                    "itemId": "m0123456789",
                    "l2CategoryId": "1",
                }
            )
        ],
    )

    listings = SellerQuery(seller_id).fetch_listings()

    assert listings["total"] == 2
    assert [item["itemId"] for item in listings["items"]] == [
        "m2064554806",
        "m2064554807",
    ]


def test_fetch_details_is_cached(mocked: responses.RequestsMock) -> None:
    call = mocked.get(PROFILE_URL.format(42), json=_profile())
    seller = SellerQuery(42)

    first = seller.fetch_details()
    second = seller.fetch_details()

    assert first is second
    assert call.call_count == 1


def test_fetch_listings_is_cached(mocked: responses.RequestsMock) -> None:
    call = mocked.get(LISTINGS_URL, json=SELLER_LISTINGS_BODY)
    seller = SellerQuery(42)

    first = seller.fetch_listings()
    second = seller.fetch_listings()

    assert first is second
    assert call.call_count == 1


def test_caches_are_per_instance(mocked: responses.RequestsMock) -> None:
    call = mocked.get(PROFILE_URL.format(42), json=_profile())

    SellerQuery(42).fetch_details()
    SellerQuery(42).fetch_details()

    assert call.call_count == 2


@pytest.mark.parametrize("status", [400, 404, 500, 503])
def test_fetch_details_http_error(mocked: responses.RequestsMock, status: int) -> None:
    mocked.get(PROFILE_URL.format(42), status=status)
    with pytest.raises(requests.HTTPError):
        SellerQuery(42).fetch_details()


@pytest.mark.parametrize("status", [400, 404, 500, 503])
def test_fetch_listings_http_error(mocked: responses.RequestsMock, status: int) -> None:
    mocked.get(LISTINGS_URL, status=status)
    with pytest.raises(requests.HTTPError):
        SellerQuery(42).fetch_listings()


def test_failed_fetch_is_not_cached(mocked: responses.RequestsMock) -> None:
    mocked.get(PROFILE_URL.format(42), status=500)
    mocked.get(PROFILE_URL.format(42), json=_profile())
    seller = SellerQuery(42)

    with pytest.raises(requests.HTTPError):
        seller.fetch_details()
    assert seller.fetch_details()["bankAccount"] is True
