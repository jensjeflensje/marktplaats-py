import unittest
from datetime import datetime, timezone
from unittest.mock import patch

from marktplaats.categories import category_from_name
from marktplaats.models import ListingLocation

from marktplaats import SearchQuery, PriceType


class BasicSearchQueryTest(unittest.TestCase):
    """
    Basic tests to test search query functionality.
    """

    def test_request(self):
        with patch('requests.get') as get_request:
            get_request.return_value.text = """{
                "listings": [
                    {
                        "itemId": "m2064554806",
                        "title": "Batavus damesfiets 26 inch",
                        "description": "Degelijke batavus damesfiets 26 inch met slot, verlichting en versnellingen.",
                        "categorySpecificDescription": "Degelijke batavus damesfiets 26 inch met slot, verlichting en versnellingen.",
                        "thinContent": true,
                        "priceInfo": {
                            "priceCents": 7500,
                            "priceType": "FIXED"
                        },
                        "location": {
                            "cityName": "Nieuwerkerk aan den IJssel",
                            "countryName": "Nederland",
                            "countryAbbreviation": "NL",
                            "distanceMeters": 1000,
                            "isBuyerLocation": false,
                            "onCountryLevel": false,
                            "abroad": false,
                            "latitude": 51.965397128056,
                            "longitude": 4.6119871732025
                        },
                        "date": "2024-01-02T20:40:25Z",
                        "imageUrls": [
                            "//images.marktplaats.com/api/v1/listing-mp-p/images/63/636424bb-b0bd-458b-964c-747af344c793?rule=ecg_mp_eps$_82.jpg"
                        ],
                        "sellerInformation": {
                            "sellerId": 7405065,
                            "sellerName": "Vogel",
                            "showSoiUrl": true,
                            "showWebsiteUrl": false,
                            "isVerified": false
                        },
                        "categoryId": 447,
                        "priorityProduct": "NONE",
                        "videoOnVip": false,
                        "urgencyFeatureActive": false,
                        "napAvailable": false,
                        "attributes": [
                            {
                                "key": "condition",
                                "value": "Gebruikt",
                                "values": [
                                    "Gebruikt"
                                ]
                            },
                            {
                                "key": "delivery",
                                "value": "Ophalen",
                                "values": [
                                    "Ophalen"
                                ]
                            }
                        ],
                        "extendedAttributes": [
                            {
                                "key": "condition",
                                "value": "Gebruikt",
                                "values": [
                                    "Gebruikt"
                                ]
                            },
                            {
                                "key": "delivery",
                                "value": "Ophalen",
                                "values": [
                                    "Ophalen"
                                ]
                            }
                        ],
                        "traits": [
                            "PACKAGE_FREE"
                        ],
                        "verticals": [
                            "bicycles_and_mopeds",
                            "bicycles_ladies_bike"
                        ],
                        "pictures": [
                            {
                                "id": 9322832634,
                                "mediaId": "",
                                "url": "https://images.marktplaats.com/api/v1/listing-mp-p/images/63/636424bb-b0bd-458b-964c-747af344c793?rule=ecg_mp_eps$_#.jpg",
                                "extraSmallUrl": "https://images.marktplaats.com/api/v1/listing-mp-p/images/63/636424bb-b0bd-458b-964c-747af344c793?rule=ecg_mp_eps$_14.jpg",
                                "mediumUrl": "https://images.marktplaats.com/api/v1/listing-mp-p/images/63/636424bb-b0bd-458b-964c-747af344c793?rule=ecg_mp_eps$_82.jpg",
                                "largeUrl": "https://images.marktplaats.com/api/v1/listing-mp-p/images/63/636424bb-b0bd-458b-964c-747af344c793?rule=ecg_mp_eps$_83.jpg",
                                "extraExtraLargeUrl": "https://images.marktplaats.com/api/v1/listing-mp-p/images/63/636424bb-b0bd-458b-964c-747af344c793?rule=ecg_mp_eps$_85.jpg",
                                "aspectRatio": {
                                    "width": 3,
                                    "height": 4
                                }
                            }
                        ],
                        "vipUrl": "/v/fietsen-en-brommers/fietsen-dames-damesfietsen/m2064554806-batavus-damesfiets-26-inch"
                    }
                ]
            }"""
            
            query = SearchQuery(
                "fiets",
                price_from=10,
                price_to=200,
                offered_since=datetime(2024, 12, 31, 14, 10, 0),
                category=category_from_name("Beschrijfbare discs"),
            )

            get_request.assert_called_once_with(
                "https://www.marktplaats.nl/lrp/api/search",
                params={
                    "attributeRanges[]": [
                        "PriceCents:1000:20000",
                    ],
                    "attributesByKey[]": [
                        "offeredSince:1735650600000",
                    ],
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
            )

        listings = query.get_listings()
        self.assertEqual(1, len(listings))

        listing = listings[0]
        self.assertEqual(75, listing.price)
        self.assertEqual(75, listing.price)
        self.assertEqual(PriceType.FIXED, listing.price_type)
        self.assertEqual(1, len(listing.images))
        self.assertIsInstance(listing.location, ListingLocation)
        self.assertEqual(
            datetime(year=2024, month=1, day=2, hour=20, minute=40, second=25, tzinfo=timezone.utc),
            listing.date
        )
        self.assertEqual("https://link.marktplaats.nl/m2064554806", listing.link)

        self.assertEqual(7405065, listing.seller.id)
        self.assertFalse(listing.seller.is_verified)

        with patch('requests.get') as get_request:
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
                headers={
                    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.0.0 Safari/537.36",
                    "Accept": "application/json",
                    "Sec-Fetch-Mode": "cors",
                    "Sec-Fetch-Site": "same-origin",
                },
            )

        self.assertFalse(seller.is_verified)  # should still be false
        self.assertEqual(7405065, seller.id)  # should still be the same
        self.assertEqual(5, seller.average_score)
        self.assertTrue(seller.bank_account)
        self.assertFalse(seller.identification)
        self.assertTrue(seller.phone_number)


if __name__ == '__main__':
    unittest.main()
