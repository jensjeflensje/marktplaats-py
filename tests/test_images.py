from __future__ import annotations

import responses

from marktplaats.models.listing_image import fetch_listing_images
from tests.utils import get_mock_file


"""Basic tests to test image scraping."""


@responses.activate
def test_parse_images() -> None:
    responses.get(
        "https://link.marktplaats.nl/m123456789",
        status=200,
        body=get_mock_file("image_response.html"),
    )

    urls = fetch_listing_images("m123456789")
    assert len(urls) == 9
    assert urls[0].startswith("https://images.marktplaats.com")


@responses.activate
def test_no_photos_returns_empty_list() -> None:
    # Listings without photos have an absolute placeholder URL in
    #  their ld+json data instead of the usual protocol-relative
    #  photo URLs. That placeholder is not a real image.
    responses.get(
        "https://link.marktplaats.nl/m2404914283",
        status=200,
        body=get_mock_file("image_response_no_photos.html"),
    )

    urls = fetch_listing_images("m2404914283")
    assert urls == []
