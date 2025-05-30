from __future__ import annotations

import logging
from datetime import date, datetime, timedelta
from enum import Enum
from typing import TYPE_CHECKING, Any

from requests.exceptions import (  # noqa: TID251 Not doing any requests
    JSONDecodeError as requests_JSONDecodeError,
)

from marktplaats.categories import L1Category, L2Category
from marktplaats.config import ISSUE_LINK
from marktplaats.models import (
    Listing,
    ListingFirstImage,
    ListingLocation,
    ListingSeller,
)
from marktplaats.models.price_type import PriceType
from marktplaats.utils import MessageObjectException, get_request


if TYPE_CHECKING:
    from collections.abc import Iterable


logger = logging.getLogger(__name__)

MONTH_MAPPING = {
    "jan": "Jan",
    "feb": "Feb",
    "mrt": "Mar",
    "apr": "Apr",
    "mei": "May",
    "jun": "Jun",
    "jul": "Jul",
    "aug": "Aug",
    "sep": "Sep",
    "okt": "Oct",
    "nov": "Nov",
    "dec": "Dec",
}


class BadStatusCodeError(MessageObjectException):
    pass


class JSONDecodeError(MessageObjectException):
    pass


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


def get_price_cents(price: int | None) -> str:
    # Marktplaats uses the string "null" if the lower/upper bound is empty
    return "null" if price is None else str(price * 100)


def replace_dutch_months(date_str: str) -> str:
    # marktplaats returns Dutch names for months
    # so we need to convert them to english to be parsed
    for dutch, english in MONTH_MAPPING.items():
        date_str = date_str.replace(dutch, english)
    return date_str


def parse_date(date_str: str) -> date:
    # marktplaats returns these relative words for the date
    # OR a date like '10 mrt 24'
    if date_str == "Eergisteren":
        result = datetime.now() - timedelta(days=2)
    elif date_str == "Gisteren":
        result = datetime.now() - timedelta(days=1)
    elif date_str == "Vandaag":
        result = datetime.now()
    else:
        date_str = replace_dutch_months(date_str)
        result = datetime.strptime(date_str, "%d %b %y")

    return result.date()


class SearchQuery:
    """
    A search query for Marktplaats.

    Raises a requests.HTTPError if the request fails.
    """

    def __init__(  # noqa: PLR0917, PLR0913 TODO: consider making the arguments keyword-only (self, *, query...)
        self,
        query: str = "",
        zip_code: str = "",
        distance: int = 1000000,  # in meters, basically unlimited
        price_from: int | None = None,
        price_to: int | None = None,
        limit: int = 1,
        offset: int = 0,
        sort_by: SortBy = SortBy.OPTIMIZED,
        sort_order: SortOrder = SortOrder.ASC,
        condition: Condition | None = None,
        offered_since: datetime | None = None,  # A datetime object
        category: L1Category | L2Category | None = None,
        extra_attributes: Iterable[int]
        | None = None,  # EXPERIMENTAL: list of integers, just like Condition
    ) -> None:
        if not query and category is None:
            msg = (
                "Invalid arguments: When the query is empty, "
                "a category must be specified."
            )
            raise ValueError(msg)

        params: dict[str, Any] = {
            "limit": str(limit),
            "offset": str(offset),
            "query": str(query),
            "searchInTitleAndDescription": "true",
            "viewOptions": "list-view",
            "distanceMeters": str(distance),
            "postcode": zip_code,
            "sortBy": sort_by.value,
            "sortOrder": sort_order.value,
            "attributesById[]": [],
        }

        # Only add price parameters if any scoping is actually done,
        #  to match the website's behavior.
        if price_from is not None or price_to is not None:
            params["attributeRanges[]"] = [
                f"PriceCents:{get_price_cents(price_from)}:{get_price_cents(price_to)}",
            ]

        if condition is not None:
            params["attributesById[]"].append(condition.value)

        if extra_attributes is not None:
            params["attributesById[]"].extend(extra_attributes)

        if offered_since is not None:
            params["attributesByKey[]"] = [
                # Unix timestamp millis
                f"offeredSince:{int(offered_since.timestamp()) * 1000}",
            ]

        if category:
            # If it is an L2 category
            if isinstance(category, L2Category):
                params["l2CategoryId"] = str(category.id)
                # Set the parent category as well
                category = category.parent
            # Set the L1 category in both cases
            params["l1CategoryId"] = str(category.id)

        self.response = get_request(
            "https://www.marktplaats.nl/lrp/api/search",
            params=params,
        )

        # This catches HTTP 4xx and 5xx errors
        self.response.raise_for_status()

        # But if it's something else non-200, still fail fast.
        if self.response.status_code != 200:  # noqa: PLR2004 HTTP status codes are a universal constant
            msg = "Received non-200 status code:"
            raise BadStatusCodeError(msg, self.response)

        try:
            self.body_json = self.response.json()
        except requests_JSONDecodeError as err:
            # Note: this is not the same error type. This will propagate as:
            #  json.decoder.JSONDecodeError
            #  -> requests.exceptions.JSONDecodeError
            #  -> marktplaats.JSONDecodeError
            msg = "Received invalid (non-json) response:"
            raise JSONDecodeError(msg, self.response.text) from err

        self._set_query_data()

    def _set_query_data(self) -> None:
        # More fields will be added.
        # For now, this is a nice way to get the total result count
        #  when looping through pages.
        self.total_result_count = self.body_json.get("totalResultCount")

    def get_listings(self) -> list[Listing]:
        listings = []
        for listing in self.body_json["listings"]:
            try:
                listing_time = parse_date(listing["date"])
            except ValueError:
                logger.warning(
                    "Marktplaats-py found an unknown date format for listing %s: '%s'. "
                    "This is not your fault. "
                    "Please create an issue on %s and include this log message.",
                    listing["itemId"],
                    listing["date"],
                    ISSUE_LINK,
                )
                listing_time = None

            try:
                price_type = PriceType(listing["priceInfo"]["priceType"])
            except ValueError:
                # this means marktplaats has a PriceType this library doesn't know about
                logger.warning(
                    "Marktplaats-py found an unknown PriceType found for "
                    "listing %s: '%s'. "
                    "This is not your fault. "
                    "Please create an issue on %s and include this log message.",
                    listing["itemId"],
                    listing["priceInfo"]["priceType"],
                    ISSUE_LINK,
                )
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
                ListingFirstImage.parse(listing.get("pictures")),
                listing["categoryId"],
                listing.get("attributes", []),
                listing.get("extendedAttributes", []),
            )
            listings.append(listing_obj)
        return listings
