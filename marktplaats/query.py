from datetime import datetime
from enum import Enum

import requests
import json

from marktplaats.categories import L2Category
from marktplaats.models import Listing, ListingSeller, ListingImage, ListingLocation
from marktplaats.models.price_type import PriceType
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


def get_price_cents(price):
    # Marktplaats uses the string "null" if the lower/upper bound is empty
    return "null" if price is None else price * 100


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
            price_from=None,
            price_to=None,
            limit=1,
            offset=0,
            sort_by=SortBy.OPTIMIZED,
            sort_order=SortOrder.ASC,
            offered_since=None,  # A datetime object
            category=None,
    ):
        params = {
            "limit": str(limit),
            "offset": str(offset),
            "query": str(query),
            "searchInTitleAndDescription": "true",
            "viewOptions": "list-view",
            "distanceMeters": str(distance),
            "postcode": zip_code,
            "sortBy": sort_by.value,
            "sortOrder": sort_order.value,
        }

        # Only add price parameters if any scoping is actually done, to match the website's behavior.
        if price_from is not None or price_to is not None:
            params["attributeRanges[]"] = [
                f"PriceCents:{get_price_cents(price_from)}:{get_price_cents(price_to)}",
            ]

        if offered_since is not None:
            params["attributesByKey[]"] = [
                f"offeredSince:{int(offered_since.timestamp()) * 1000}",  # Unix timestamp millis
            ]

        if category:
            # If it is an L2 category
            if isinstance(category, L2Category):
                params["l2CategoryId"] = str(category.id)
                # Set the parent category as well
                category = category.parent
            # Set the L1 category in both cases
            params["l1CategoryId"] = str(category.id)

        self.response = requests.get(
            "https://www.marktplaats.nl/lrp/api/search",
            params=params,
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
                PriceType(listing["priceInfo"]["priceType"]),
                "https://link.marktplaats.nl/" + listing["itemId"],
                ListingImage.parse(listing.get("pictures")),
                listing["categoryId"],
                listing.get("attributes", []),
                listing.get("extendedAttributes", []),
            )
            listings.append(listing_obj)
        return listings
