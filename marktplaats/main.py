from datetime import datetime, timezone

import requests
import json

from marktplaats.models import Listing, ListingSeller, ListingImage, ListingLocation


class SearchQuery:
    def __init__(self, query, zip_code="", distance=1000000, price_from=0, price_to=1000000, limit=1, offset=0):
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
            },
            # Some headers to make the request look legit
            headers={
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.0.0 Safari/537.36",
                "Accept": "application/json",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-origin",
            }
        )

        self.body = self.request.text
        self.body_json = json.loads(self.body)

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
                listing.get("attributes")
            )
            listings.append(listing_obj)
        return listings
