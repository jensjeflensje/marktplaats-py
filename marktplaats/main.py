import requests
import json

from marktplaats.models import Listing, ListingSeller, ListingImage


class Marktplaats:
    listings = []

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
        if len(self.listings):
            return self.listings
        for listing in self.body_json["listings"]:
            listing_obj = Listing(
                listing["title"],
                listing["description"],
                ListingSeller(listing["sellerInformation"]["sellerName"], listing["sellerInformation"]["isVerified"]),
                listing["priceInfo"]["priceCents"] / 100,
                "https://link.marktplaats.nl/" + listing["itemId"],
                ListingImage.parse_images(listing["pictures"]),
                listing["categoryId"],
                listing["attributes"],
            )
            self.listings.append(listing_obj)
        return self.listings
