from datetime import datetime, timezone

import requests
import json
import logging
from enum import Enum

from marktplaats.models import Listing, ListingSeller, ListingImage, ListingLocation

class SortBy(str, Enum):
    DATE= "SORT_INDEX"
    PRICE= "PRICE"
    DEFAULT= "OPTIMIZED"

class SortOrder(str, Enum):
    DESC= "DECREASING"
    ASC = "INCREASING"

class SearchQuery:
    log: logging

    def __init__(self,
                query:      str,
                zip_code:   str         = "",
                distance:   int         = 1000000,
                price_from: int         = 0,
                price_to:   int         = 1000000,
                limit:      int         = 1,
                offset:     int         = 0,
                sort_by:    SortBy      = SortBy.DEFAULT,
                sort_order: SortOrder   = SortOrder.DESC
                ):

        self.log = logging.getLogger(__name__)
        self.log.debug(f"Init markplaats module")

        if query is None:
            self.log.error(f"Empty search string!")
            raise ValueError(f"Empty search string!")

        self.request = requests.get(
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
                "sortOrder": sort_order,
            },
            # Some headers to make the request look legit
            headers={
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.0.0 Safari/537.36",
                "Accept": "application/json",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-origin",
            }
        )

        try:
            self.body = self.request.text
            self.body_json = json.loads(self.body)
        except Exception as e:
            raise e

    def get_listings(self):
        listings = []
        for listing in self.body_json["listings"]:
            try:
                listing_time = datetime.strptime(listing["date"], "%Y-%m-%dT%H:%M:%S%z")
            except Exception as e:
                listing_time = datetime.now(timezone.utc)

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
                listing["attributes"],
            )
            listings.append(listing_obj)
        return listings
