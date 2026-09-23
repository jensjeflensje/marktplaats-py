from __future__ import annotations

import json

import pytest
import requests
import responses

from marktplaats import Listing, ListingLocation, ListingSeller, PriceType
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


def _page(*ld_json: object) -> str:
    scripts = "".join(
        f'<script type="application/ld+json">{json.dumps(data)}</script>'
        for data in ld_json
    )
    return f"<html><head>{scripts}</head><body></body></html>"


def _product(images: list[str]) -> dict[str, object]:
    return {"@context": "https://schema.org", "@type": "Product", "image": images}


@pytest.mark.parametrize(
    ("images", "expected"),
    [
        # Protocol-relative URLs get https added
        (
            ["//images.marktplaats.com/a.jpg"],
            ["https://images.marktplaats.com/a.jpg"],
        ),
        # Absolute URLs are kept as-is (#231)
        (
            ["https://images.marktplaats.com/a.jpg"],
            ["https://images.marktplaats.com/a.jpg"],
        ),
        # A mix of both, order is kept
        (
            [
                "//images.marktplaats.com/a.jpg",
                "https://images.marktplaats.com/b.jpg",
                "//images.marktplaats.com/c.jpg",
            ],
            [
                "https://images.marktplaats.com/a.jpg",
                "https://images.marktplaats.com/b.jpg",
                "https://images.marktplaats.com/c.jpg",
            ],
        ),
        # The placeholder for listings without photos is dropped (#213)
        (
            [
                "https://www.hzcdn.io/bff/static/vendor/hz-web-ui/mp/assets/tenant-coin--nlnl.e0064ede.svg"
            ],
            [],
        ),
        # Other hosts are dropped too
        (["https://example.com/a.jpg", "https://cdn.example.com/a.jpg"], []),
        ([], []),
    ],
)
def test_image_url_variants(images: list[str], expected: list[str]) -> None:
    with responses.RequestsMock() as rsps:
        rsps.get("https://link.marktplaats.nl/m1", body=_page(_product(images)))
        assert fetch_listing_images("m1") == expected


@pytest.mark.parametrize(
    "ld_json",
    [
        # No ld+json at all
        (),
        # Only other schema.org types
        ({"@type": "BreadcrumbList", "itemListElement": []},),
        ({"@type": "Organization", "name": "Marktplaats"},),
        # A list at the top level instead of an object
        ([{"@type": "Product", "image": ["//images.marktplaats.com/a.jpg"]}],),
    ],
)
def test_no_product_data(ld_json: tuple[object, ...]) -> None:
    with responses.RequestsMock() as rsps:
        rsps.get("https://link.marktplaats.nl/m1", body=_page(*ld_json))
        assert fetch_listing_images("m1") == []


def test_only_first_product_is_used() -> None:
    page = _page(
        {"@type": "BreadcrumbList"},
        _product(["//images.marktplaats.com/first.jpg"]),
        _product(["//images.marktplaats.com/second.jpg"]),
    )
    with responses.RequestsMock() as rsps:
        rsps.get("https://link.marktplaats.nl/m1", body=page)
        assert fetch_listing_images("m1") == [
            "https://images.marktplaats.com/first.jpg"
        ]


@pytest.mark.parametrize("status", [404, 410, 500])
def test_image_http_error(status: int) -> None:
    with responses.RequestsMock() as rsps:
        rsps.get("https://link.marktplaats.nl/m1", status=status)
        with pytest.raises(requests.HTTPError):
            fetch_listing_images("m1")


def test_listing_get_images_uses_listing_id() -> None:
    listing = Listing(
        "m2064554806",
        "title",
        "description",
        None,
        ListingSeller(1, "seller", is_verified=False),
        ListingLocation(None, None, None, None, None, None),
        0,
        PriceType.FREE,
        "https://link.marktplaats.nl/m2064554806",
        [],
        1,
        [],
        [],
    )
    with responses.RequestsMock() as rsps:
        rsps.get(
            "https://link.marktplaats.nl/m2064554806",
            body=_page(_product(["//images.marktplaats.com/a.jpg"])),
        )
        assert listing.get_images() == ["https://images.marktplaats.com/a.jpg"]
