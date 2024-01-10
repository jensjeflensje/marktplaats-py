from datetime import datetime
from enum import Enum

import requests
import json

from marktplaats.models import Listing, ListingSeller, ListingImage, ListingLocation
from marktplaats.utils import REQUEST_HEADERS


class SortBy(Enum):
    """
    Enumeration of the different sorting methods Marktplaats supports.
    The DATE method sorts by absolute time. So ascending is from oldest to newest.
    """
    DATE = "SORT_INDEX"
    PRICE = "PRICE"
    OPTIMIZED = "OPTIMIZED"
    LOCATION = "LOCATION"


class SortOrder(Enum):
    DESC = "DECREASING"
    ASC = "INCREASING"


class SearchQuery:
    """
    A search query for Marktplaats.
    Raises a requests HTTPError if the request fails.
    """

    def __init__(
            self,
            query,
            zip_code="",
            distance=1000000,  # in meters, basically unlimited
            price_from=0,
            price_to=1000000,
            limit=1,
            offset=0,
            sort_by=SortBy.OPTIMIZED,
            sort_order=SortOrder.ASC,
    ):
        self.response = requests.get(
            "https://www.marktplaats.nl/lrp/api/search",
            params={
                "attributeRanges[]":  [
                    f"PriceCents:{price_from * 100}:{price_to * 100}",
                ],
                "limit": str(limit),
                "offset": str(offset),
                "query": str(query),
                "searchInTitleAndDescription": "true",
                "viewOptions": "list-view",
                "distanceMeters": str(distance),
                "postcode": zip_code,
                "sortBy": sort_by,
                "sort_order": sort_order,
            },
            # Some headers to make the request look legit
            headers=REQUEST_HEADERS,
        )

        # every request exception should raise here
        self.response.raise_for_status()

        self.body = self.response.text
        self.body_json = json.loads(self.body)

    def get_listings(self):
        listings = []
        for listing in self.body_json["listings"]:
            try:
                listing_time = datetime.strptime(listing["date"], "%Y-%m-%dT%H:%M:%S%z")
            except ValueError:
                listing_time = None

            listing_obj = Listing(
                listing["itemId"],
                listing["title"],
                listing["description"],
                listing_time,
                ListingSeller.parse(listing["sellerInformation"]),
                ListingLocation.parse(listing["location"]),
                listing["priceInfo"]["priceCents"] / 100,
                "https://link.marktplaats.nl/" + listing["itemId"],
                ListingImage.parse(listing.get("pictures")),
                listing["categoryId"],
                listing.get("attributes", []),
                listing.get("extendedAttributes", []),
            )
            listings.append(listing_obj)
        return listings
