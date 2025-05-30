from __future__ import annotations

import requests_mock

from marktplaats.models.listing_image import fetch_listing_images
from tests.utils import get_mock_file


"""Basic tests to test image scraping."""


def test_parse_images() -> None:
    with requests_mock.Mocker() as m:
        m.get(
            "https://link.marktplaats.nl/m123456789",
            status_code=200,
            text=get_mock_file("image_response.html"),
        )

        urls = fetch_listing_images("m123456789")
        assert len(urls) == 9
        assert urls[0].startswith("https://images.marktplaats.com")
