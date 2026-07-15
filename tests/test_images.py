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
def test_absolute_image_urls_are_not_mangled() -> None:
    # Listings without photos have a placeholder image in their
    #  ld+json data. That one already includes a scheme, so it
    #  shouldn't get another "https:" glued in front of it.
    responses.get(
        "https://link.marktplaats.nl/m2404914283",
        status=200,
        body=get_mock_file("image_response_no_photos.html"),
    )

    urls = fetch_listing_images("m2404914283")
    assert urls == [
        "https://www.hzcdn.io/bff/static/vendor/hz-web-ui/mp/assets/tenant-coin--nlnl.e0064ede.svg",
    ]
