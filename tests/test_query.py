from __future__ import annotations

from datetime import date, datetime
from unittest.mock import (
    patch,  # TODO(GideonBear): switch to something else?  # noqa: FIX002, TD003
)

import pytest
import requests
import requests_mock

from marktplaats import BadStatusCodeError, JSONDecodeError, PriceType, SearchQuery
from marktplaats.categories import category_from_name
from marktplaats.models import ListingLocation


"""Basic tests to test search query functionality."""


def test_request() -> None:
    with patch("requests.get") as get_request:
        get_request.return_value.status_code = 200
        get_request.return_value.json.return_value = {
            "totalResultCount": 100,
            "listings": [
                {
                    "itemId": "m2064554806",
                    "title": "Batavus damesfiets 26 inch",
                    "description": "Degelijke batavus damesfiets 26 inch met slot, verlichting en versnellingen.",
                    "categorySpecificDescription": "Degelijke batavus damesfiets 26 inch met slot, verlichting en versnellingen.",
                    "thinContent": True,
                    "priceInfo": {"priceCents": 7500, "priceType": "FIXED"},
                    "location": {
                        "cityName": "Nieuwerkerk aan den IJssel",
                        "countryName": "Nederland",
                        "countryAbbreviation": "NL",
                        "distanceMeters": 1000,
                        "isBuyerLocation": False,
                        "onCountryLevel": False,
                        "abroad": False,
                        "latitude": 51.965397128056,
                        "longitude": 4.6119871732025,
                    },
                    "date": "10 mrt 24",
                    "imageUrls": [
                        "//images.marktplaats.com/api/v1/listing-mp-p/images/63/636424bb-b0bd-458b-964c-747af344c793?rule=ecg_mp_eps$_82.jpg"
                    ],
                    "sellerInformation": {
                        "sellerId": 7405065,
                        "sellerName": "Vogel",
                        "showSoiUrl": True,
                        "showWebsiteUrl": False,
                        "isVerified": False,
                    },
                    "categoryId": 447,
                    "priorityProduct": "NONE",
                    "videoOnVip": False,
                    "urgencyFeatureActive": False,
                    "napAvailable": False,
                    "attributes": [
                        {
                            "key": "condition",
                            "value": "Gebruikt",
                            "values": ["Gebruikt"],
                        },
                        {
                            "key": "delivery",
                            "value": "Ophalen",
                            "values": ["Ophalen"],
                        },
                    ],
                    "extendedAttributes": [
                        {
                            "key": "condition",
                            "value": "Gebruikt",
                            "values": ["Gebruikt"],
                        },
                        {
                            "key": "delivery",
                            "value": "Ophalen",
                            "values": ["Ophalen"],
                        },
                    ],
                    "traits": ["PACKAGE_FREE"],
                    "verticals": ["bicycles_and_mopeds", "bicycles_ladies_bike"],
                    "pictures": [
                        {
                            "id": 9322832634,
                            "mediaId": "",
                            "url": "https://images.marktplaats.com/api/v1/listing-mp-p/images/63/636424bb-b0bd-458b-964c-747af344c793?rule=ecg_mp_eps$_#.jpg",
                            "extraSmallUrl": "https://images.marktplaats.com/api/v1/listing-mp-p/images/63/636424bb-b0bd-458b-964c-747af344c793?rule=ecg_mp_eps$_14.jpg",
                            "mediumUrl": "https://images.marktplaats.com/api/v1/listing-mp-p/images/63/636424bb-b0bd-458b-964c-747af344c793?rule=ecg_mp_eps$_82.jpg",
                            "largeUrl": "https://images.marktplaats.com/api/v1/listing-mp-p/images/63/636424bb-b0bd-458b-964c-747af344c793?rule=ecg_mp_eps$_83.jpg",
                            "extraExtraLargeUrl": "https://images.marktplaats.com/api/v1/listing-mp-p/images/63/636424bb-b0bd-458b-964c-747af344c793?rule=ecg_mp_eps$_85.jpg",
                            "aspectRatio": {"width": 3, "height": 4},
                        }
                    ],
                    "vipUrl": "/v/fietsen-en-brommers/fietsen-dames-damesfietsen/m2064554806-batavus-damesfiets-26-inch",
                }
            ],
        }

        query = SearchQuery(
            "fiets",
            price_from=10,
            price_to=200,
            offered_since=datetime(2024, 12, 31, 14, 10, 0),
            category=category_from_name("Beschrijfbare discs"),
            extra_attributes=[1],
        )

        get_request.assert_called_once_with(
            "https://www.marktplaats.nl/lrp/api/search",
            params={
                "attributeRanges[]": [
                    "PriceCents:1000:20000",
                ],
                "attributesByKey[]": [
                    f"offeredSince:{int(datetime(2024, 12, 31, 14, 10, 0).timestamp() * 1000)}",
                ],
                "attributesById[]": [1],
                "limit": "1",
                "offset": "0",
                "query": "fiets",
                "searchInTitleAndDescription": "true",
                "viewOptions": "list-view",
                "distanceMeters": "1000000",  # basically unlimited
                "postcode": "",
                "sortBy": "OPTIMIZED",
                "sortOrder": "INCREASING",
                "l1CategoryId": "322",
                "l2CategoryId": "1415",
            },
            headers={
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.0.0 Safari/537.36",
                "Accept": "application/json",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-origin",
            },
            timeout=15,
        )

    listings = query.get_listings()
    assert len(listings) == 1

    listing = listings[0]
    assert listing.price == 75
    assert listing.price == 75
    assert listing.price_type == PriceType.FIXED
    assert len(listing.images) == 1
    assert isinstance(listing.location, ListingLocation)
    assert date(year=2024, month=3, day=10) == listing.date
    assert listing.link == "https://link.marktplaats.nl/m2064554806"
    assert query.total_result_count == 100

    assert listing.seller.id == 7405065
    assert not listing.seller.is_verified

    with patch("requests.get") as get_request:
        get_request.return_value.text = """{
            "bankAccount": true,
            "phoneNumber": true,
            "identification": false,
            "paymentMethod": {
                "name": "ideal"
            },
            "numberOfReviews": 26,
            "averageScore": 5,
            "smbVerified": false,
            "profilePictures": {}
        }"""

        seller = listing.seller.get_seller()

        get_request.assert_called_once_with(
            "https://www.marktplaats.nl/v/api/seller-profile/7405065",
            params=None,
            headers={
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.0.0 Safari/537.36",
                "Accept": "application/json",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-origin",
            },
            timeout=15,
        )

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
