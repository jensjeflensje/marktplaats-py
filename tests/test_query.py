from __future__ import annotations

from datetime import date, datetime

import pytest
import requests
import requests_mock

from marktplaats import BadStatusCodeError, JSONDecodeError, PriceType, SearchQuery
from marktplaats.categories import category_from_name
from marktplaats.models import ListingLocation
from tests.utils import get_mock_file


"""Basic tests to test search query functionality."""


def test_request() -> None:
    with requests_mock.Mocker() as m:
        m.get(
            "https://www.marktplaats.nl/lrp/api/search",
            status_code=200,
            headers={
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.0.0 Safari/537.36",
                "Accept": "application/json",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-origin",
            },
            text=get_mock_file("query_response.json"),
        )

        query = SearchQuery(
            "fiets",
            price_from=10,
            price_to=200,
            offered_since=datetime(2024, 12, 31, 14, 10, 0),
            category=category_from_name("Beschrijfbare discs"),
            extra_attributes=[1],
        )

        assert m.called
        req = m.request_history[0]
        assert req.method == "GET"
        assert req.qs == {
            "attributeranges[]": ["pricecents:1000:20000"],
            "attributesbykey[]": [
                f"offeredsince:{int(datetime(2024, 12, 31, 14, 10, 0).timestamp() * 1000)}"
            ],
            "attributesbyid[]": ["1"],
            "limit": ["1"],
            "offset": ["0"],
            "query": ["fiets"],
            "searchintitleanddescription": ["true"],
            "viewoptions": ["list-view"],
            "distancemeters": ["1000000"],
            "postcode": [""],
            "sortby": ["optimized"],
            "sortorder": ["increasing"],
            "l1categoryid": ["322"],
            "l2categoryid": ["1415"],
        }
        assert req.timeout == 15

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
    assert isinstance(listing.location, ListingLocation)
    assert date(year=2024, month=3, day=10) == listing.date
    assert listing.link == "https://link.marktplaats.nl/m2064554806"
    assert query.total_result_count == 100

    assert listing.seller.id == 7405065
    assert not listing.seller.is_verified

    with requests_mock.Mocker() as m:
        m.get(
            "https://www.marktplaats.nl/v/api/seller-profile/7405065",
            status_code=200,
            headers={
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.0.0 Safari/537.36",
                "Accept": "application/json",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-origin",
            },
            text=get_mock_file("seller_response.json"),
        )

        seller = listing.seller.get_seller()

        req = m.request_history[0]
        assert req.method == "GET"
        assert req.qs == {}
        assert req.timeout == 15

    assert not seller.is_verified  # should still be false
    assert seller.id == 7405065  # should still be the same
    assert seller.average_score == 5
    assert seller.bank_account
    assert not seller.identification
    assert seller.phone_number


def test_http_error_400() -> None:
    # This should be the same for other 4xx and 5xx errors

    with requests_mock.Mocker() as m:
        m.get(
            "https://www.marktplaats.nl/lrp/api/search?limit=1&offset=0&query=fiets&searchInTitleAndDescription=true&viewOptions=list-view&distanceMeters=1000000&postcode=&sortBy=OPTIMIZED&sortOrder=INCREASING",
            status_code=400,
        )
        with pytest.raises(requests.HTTPError):
            _query = SearchQuery("fiets")


def test_http_error_204() -> None:
    # This should be the same for all other non-200 non-4xx non-5xx errors

    with requests_mock.Mocker() as m:
        m.get(
            "https://www.marktplaats.nl/lrp/api/search?limit=1&offset=0&query=fiets&searchInTitleAndDescription=true&viewOptions=list-view&distanceMeters=1000000&postcode=&sortBy=OPTIMIZED&sortOrder=INCREASING",
            status_code=204,
        )
        with pytest.raises(BadStatusCodeError):
            _query = SearchQuery("fiets")


def test_invalid_json() -> None:
    with requests_mock.Mocker() as m:
        m.get(
            "https://www.marktplaats.nl/lrp/api/search?limit=1&offset=0&query=fiets&searchInTitleAndDescription=true&viewOptions=list-view&distanceMeters=1000000&postcode=&sortBy=OPTIMIZED&sortOrder=INCREASING",
            text="this is some invalid JSON",
        )
        with pytest.raises(JSONDecodeError):
            _query = SearchQuery("fiets")


def test_query_category_valueerror() -> None:
    with pytest.raises(
        ValueError,
        match=r"^Invalid arguments: When the query is empty, a category must be specified.$",
    ):
        _query = SearchQuery(price_to=10)
