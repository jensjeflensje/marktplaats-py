import logging
from datetime import datetime
from enum import Enum

import requests
import json

from marktplaats.categories import L2Category
from marktplaats.config import ISSUE_LINK
from marktplaats.models import Listing, ListingSeller, ListingImage, ListingLocation
from marktplaats.models.price_type import PriceType
from marktplaats.utils import REQUEST_HEADERS


logger = logging.getLogger(__name__)


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


class Condition(Enum):
    """
    Enumeration of different conditions for items listed on Marktplaats.
    NEW, AS_GOOD_AS_NEW, and USED always work.
    REFURBISHED and NOT_WORKING are specific to some categories.
    """
    NEW = 30
    REFURBISHED = 14050
    AS_GOOD_AS_NEW = 31
    USED = 32
    NOT_WORKING = 13940


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
            condition=None,
            offered_since=None,  # A datetime object
            category=None,
            extra_attributes=None, # EXPERIMENTAL: list of integers, just like Condition
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
            "attributesById[]": []
        }

        # Only add price parameters if any scoping is actually done, to match the website's behavior.
        if price_from is not None or price_to is not None:
            params["attributeRanges[]"] = [
                f"PriceCents:{get_price_cents(price_from)}:{get_price_cents(price_to)}",
            ]

        if condition is not None:
            params["attributesById[]"].append(condition.value)

        if extra_attributes is not None:
            params["attributesById[]"].append(condition.value)

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

            try:
                price_type = PriceType(listing["priceInfo"]["priceType"])
            except ValueError:
                # this means marktplaats has a PriceType this library doesn't know about
                logger.warning(f"Marktplaats-py found an unknown PriceType found for "
                               f"listing {listing['itemId']}: '{listing['priceInfo']['priceType']}'. "
                               f"This is not your fault. "
                               f"Please create an issue on {ISSUE_LINK} and include this log message.")
                # set a fallback value
                price_type = PriceType.UNKNOWN

            listing_obj = Listing(
                listing["itemId"],
                listing["title"],
                listing["description"],
                listing_time,
                ListingSeller.parse(listing["sellerInformation"]),
                ListingLocation.parse(listing["location"]),
                listing["priceInfo"]["priceCents"] / 100,
                price_type,
                "https://link.marktplaats.nl/" + listing["itemId"],
                ListingImage.parse(listing.get("pictures")),
                listing["categoryId"],
                listing.get("attributes", []),
                listing.get("extendedAttributes", []),
            )
            listings.append(listing_obj)
        return listings
