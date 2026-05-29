from __future__ import annotations

import responses

from marktplaats.enums import Platform
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

    urls = fetch_listing_images("m123456789", Platform.MARKTPLAATS)
    assert len(urls) == 9
    assert urls[0].startswith("https://images.marktplaats.com")


@responses.activate
def test_parse_images_2dehands() -> None:
    responses.get(
        "https://link.2dehands.be/m2404214127",
        status=200,
        body=get_mock_file("image_response_2dehands.html"),
    )

    urls = fetch_listing_images("m2404214127", Platform.TWEEDEHANDS)
    assert len(urls) == 3
    assert urls[0].startswith("https://images.2dehands.com")
