from __future__ import annotations

import os
from pathlib import Path

import requests_mock

from marktplaats.models.listing_image import fetch_listing_images


"""Basic tests to test image scraping."""


def test_parse_images() -> None:
    dir_path = Path(os.path.realpath(__file__)).parent
    with (dir_path / "mock/image_response.html").open(encoding="utf-8") as file:
        mock_response = file.read()
    with requests_mock.Mocker() as m:
        m.get(
            "https://link.marktplaats.nl/m123456789",
            status_code=200,
            text=mock_response,
        )

        urls = fetch_listing_images("m123456789")
        assert len(urls) == 9
        assert urls[0].startswith("https://images.marktplaats.com")
