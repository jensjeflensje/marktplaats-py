from __future__ import annotations

import json
from dataclasses import dataclass
from typing import TYPE_CHECKING

from bs4 import BeautifulSoup
from typing_extensions import Self

from marktplaats.utils import get_request


if TYPE_CHECKING:
    from marktplaats.api_types import Picture


@dataclass
class ListingFirstImage:
    """
    Data format for the listing image that marktplaats responds with when doing a search query.

    The get_images() method will not use this format, but instead return a list of URLs.
    """  # noqa: E501 Line too long, we can't easily wrap it in the docstring

    extra_small: str
    medium: str
    large: str
    extra_large: str

    @classmethod
    def parse(cls, data: list[Picture] | None) -> list[Self]:
        if data is None:
            return []
        return [
            cls(
                image_data["extraSmallUrl"],
                image_data["mediumUrl"],
                image_data["largeUrl"],
                image_data["extraExtraLargeUrl"],
            )
            for image_data in data
        ]


def fetch_listing_images(listing_id: str) -> list[str]:
    """
    Return a list of image URLs for a given listing.

    It scrapes the listing page and parses the ld+json objects on that page.
    :param listing_id: The listing ID to get images for.
    :return: A list of image URLs (https).
    """  # noqa: DOC201 TODO: all the docstrings are a bit inconsistent
    r = get_request(f"https://link.marktplaats.nl/{listing_id}")
    r.raise_for_status()  # raises so we can stop the fetching on a higher level

    soup = BeautifulSoup(r.text, "html.parser")

    images: list[str] = []

    # get the data objects from the HTML response
    for data in soup.select('script[type="application/ld+json"]'):
        parsed = json.loads(data.text)
        # the list of image URLs is hidden within the product object
        if type(parsed) is dict and parsed["@type"] == "Product":
            # the returned images are in a format that don't include a scheme,
            #  so we add one manually
            images.extend(f"https:{image}" for image in parsed["image"])
            break

    return images
