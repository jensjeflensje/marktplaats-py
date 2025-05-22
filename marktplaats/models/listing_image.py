from dataclasses import dataclass
import json

import requests
from bs4 import BeautifulSoup

from marktplaats.utils import REQUEST_HEADERS


@dataclass
class ListingFirstImage:
    """
    Data format for the listing image that marktplaats responds with when doing a search query.
    The get_images() method will not use this format, but instead return a list of URLs.
    """
    extra_small: str
    medium: str
    large: str
    extra_large: str

    @classmethod
    def parse(cls, data):
        if data is None:
            return []
        images = []
        for image_data in data:
            images.append(cls(
                image_data["extraSmallUrl"],
                image_data["mediumUrl"],
                image_data["largeUrl"],
                image_data["extraExtraLargeUrl"],
            ))
        return images


def fetch_listing_images(listing_id: str) -> list[str]:
    """
    Returns a list of image URLs for a given listing.
    It scrapes the listing page and parses the ld+json objects on that page.
    :param listing_id: The listing ID to get images for.
    :return: A list of image URLs (https).
    """
    r = requests.get(
        f"https://link.marktplaats.nl/{listing_id}",
        headers=REQUEST_HEADERS,
    )
    r.raise_for_status()  # raises so we can stop the fetching on a higher level

    soup = BeautifulSoup(r.text, 'html.parser')

    images = []

    # get the data objects from the HTML response
    for data in soup.select('script[type="application/ld+json"]'):
        parsed = json.loads(data.text)
        # the list of image URLs is hidden within the product object
        if type(parsed) is dict and parsed["@type"] == "Product":
            for image in parsed["image"]:
                # the returned images are in a format that don't include a scheme, so we add one manually
                images.append(f"https:{image}")
            break

    return images
