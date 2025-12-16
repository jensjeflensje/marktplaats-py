from __future__ import annotations

from datetime import date, datetime

import pytest
import requests
import responses

from marktplaats import (
    BadStatusCodeError,
    JSONDecodeError,
    ListingFirstImage,
    PriceType,
    SearchQuery,
)
from marktplaats.categories import category_from_name
from marktplaats.models import ListingLocation
from tests.utils import get_mock_file


"""Basic tests to test search query functionality."""


@responses.activate
def test_request_1() -> None:
    responses.get(
        "https://www.marktplaats.nl/lrp/api/search",
        status=200,
        headers={
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.0.0 Safari/537.36",
            "Accept": "application/json",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
        },
        body=get_mock_file("query_response.json"),
        match=[
            responses.matchers.request_kwargs_matcher({"timeout": 15}),
            responses.matchers.query_param_matcher(
                {
                    "attributeRanges[]": "PriceCents:1000:20000",
                    "attributesByKey[]": f"offeredSince:{int(datetime(2024, 12, 31, 14, 10, 0).timestamp() * 1000)}",
                    "attributesById[]": "1",
                    "limit": "1",
                    "offset": "0",
                    "query": "fiets",
                    "searchInTitleAndDescription": "true",
                    "viewOptions": "list-view",
                    "distanceMeters": "1000000",
                    "sortBy": "OPTIMIZED",
                    "sortOrder": "INCREASING",
                    "l1CategoryId": "322",
                    "l2CategoryId": "1415",
                }
            ),
        ],
    )

    query = SearchQuery(
        "fiets",
        price_from=10,
        price_to=200,
        offered_since=datetime(2024, 12, 31, 14, 10, 0),
        category=category_from_name("Beschrijfbare discs"),
        extra_attributes=[1],
    )

    listings = query.get_listings()
    assert len(listings) == 1

    listing = listings[0]
    assert listing.price == 75
    assert listing.price == 75
    assert listing.price_type == PriceType.FIXED
    with pytest.warns(
        DeprecationWarning,
        match=(
            r"^Listing.images is deprecated since marktplaats version 0\.3\.0\. "
            r"Please use Listing\.first_image or Listing\.get_images\(\) instead.$"
        ),
    ):
        assert len(listing.images) == 1
    with pytest.warns(
        DeprecationWarning,
        match=(
            r"^Listing.images is deprecated since marktplaats version 0\.3\.0\. "
            r"Please use Listing\.first_image or Listing\.get_images\(\) instead.$"
        ),
    ):
        assert listing.images[0] is listing.first_image
    assert isinstance(listing.first_image, ListingFirstImage)
    assert (
        listing.first_image.extra_small
        == "https://images.marktplaats.com/api/v1/listing-mp-p/images/63/636424bb-b0bd-458b-964c-747af344c793?rule=ecg_mp_eps$_14.jpg"
    )
    assert (
        listing.first_image.medium
        == "https://images.marktplaats.com/api/v1/listing-mp-p/images/63/636424bb-b0bd-458b-964c-747af344c793?rule=ecg_mp_eps$_82.jpg"
    )
    assert (
        listing.first_image.large
        == "https://images.marktplaats.com/api/v1/listing-mp-p/images/63/636424bb-b0bd-458b-964c-747af344c793?rule=ecg_mp_eps$_83.jpg"
    )
    assert (
        listing.first_image.extra_large
        == "https://images.marktplaats.com/api/v1/listing-mp-p/images/63/636424bb-b0bd-458b-964c-747af344c793?rule=ecg_mp_eps$_85.jpg"
    )
    assert isinstance(listing.location, ListingLocation)
    assert date(year=2024, month=3, day=10) == listing.date
    assert listing.link == "https://link.marktplaats.nl/m2064554806"
    assert query.total_result_count == 100

    assert listing.seller.id == 7405065
    assert not listing.seller.is_verified

    responses.get(
        "https://www.marktplaats.nl/v/api/seller-profile/7405065",
        status=200,
        headers={
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.0.0 Safari/537.36",
            "Accept": "application/json",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
        },
        body=get_mock_file("seller_response.json"),
        match=[
            responses.matchers.request_kwargs_matcher({"timeout": 15}),
            responses.matchers.query_param_matcher({}),
        ],
    )

    seller = listing.seller.get_seller()

    assert not seller.is_verified  # should still be false
    assert seller.id == 7405065  # should still be the same
    assert seller.average_score == 5
    assert seller.bank_account
    assert not seller.identification
    assert seller.phone_number


@responses.activate
def test_http_error_400() -> None:
    # This should be the same for other 4xx and 5xx errors

    responses.get(
        "https://www.marktplaats.nl/lrp/api/search?limit=1&offset=0&query=fiets&searchInTitleAndDescription=true&viewOptions=list-view&distanceMeters=1000000&postcode=&sortBy=OPTIMIZED&sortOrder=INCREASING",
        status=400,
    )
    with pytest.raises(requests.HTTPError):
        _query = SearchQuery("fiets")


@responses.activate
def test_http_error_204() -> None:
    # This should be the same for all other non-200 non-4xx non-5xx errors

    responses.get(
        "https://www.marktplaats.nl/lrp/api/search?limit=1&offset=0&query=fiets&searchInTitleAndDescription=true&viewOptions=list-view&distanceMeters=1000000&postcode=&sortBy=OPTIMIZED&sortOrder=INCREASING",
        status=204,
    )
    with pytest.raises(BadStatusCodeError):
        _query = SearchQuery("fiets")


@responses.activate
def test_invalid_json() -> None:
    responses.get(
        "https://www.marktplaats.nl/lrp/api/search?limit=1&offset=0&query=fiets&searchInTitleAndDescription=true&viewOptions=list-view&distanceMeters=1000000&postcode=&sortBy=OPTIMIZED&sortOrder=INCREASING",
        body="this is some invalid JSON",
    )
    with pytest.raises(JSONDecodeError):
        _query = SearchQuery("fiets")


def test_query_category_valueerror() -> None:
    with pytest.raises(
        ValueError,
        match=r"^Invalid arguments: When the query is empty, a category must be specified.$",
    ):
        _query = SearchQuery(price_to=10)
