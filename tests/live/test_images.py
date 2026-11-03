from __future__ import annotations

import pytest
import requests

from marktplaats import Listing, SearchQuery, SortBy, SortOrder, category_from_name
from marktplaats.models.listing_image import fetch_listing_images


"""
Live tests (sent to Marktplaats) to ensure they
haven't deployed breaking changes to the listing pages and images.
"""


@pytest.fixture(scope="module")
def listings_with_photos() -> list[Listing]:
    """
    Get a few recent listings that have photos.

    Returns:
        The listings.

    """
    search = SearchQuery(
        "fiets", limit=30, sort_by=SortBy.DATE, sort_order=SortOrder.DESC
    )
    listings = [x for x in search.get_listings() if x.first_image is not None]
    assert len(listings) >= 3
    return listings[:3]


@pytest.fixture(scope="module")
def images(listings_with_photos: list[Listing]) -> list[list[str]]:
    """
    Get the images of each listing, once.

    Listing pages are rate limited, so don't fetch them more than needed.

    Returns:
        The image URLs per listing.

    """
    return [listing.get_images() for listing in listings_with_photos]


@pytest.mark.parametrize("index", [pytest.param(0, marks=pytest.mark.smoke), 1, 2])
def test_get_images(images: list[list[str]], index: int) -> None:
    urls = images[index]

    assert urls
    assert len(urls) == len(set(urls)), "Duplicate images"
    for image in urls:
        assert image.startswith("https://images.marktplaats.com/"), image


@pytest.mark.parametrize("index", [pytest.param(0, marks=pytest.mark.smoke), 1, 2])
def test_images_can_be_downloaded(images: list[list[str]], index: int) -> None:
    image = images[index][0]
    response = requests.head(image, timeout=15)

    assert response.status_code == 200, image
    assert response.headers["Content-Type"].startswith("image/"), image


@pytest.mark.parametrize("index", range(3))
@pytest.mark.parametrize("size", ["extra_small", "medium", "large", "extra_large"])
def test_first_image_can_be_downloaded(
    listings_with_photos: list[Listing], index: int, size: str
) -> None:
    first_image = listings_with_photos[index].first_image
    assert first_image is not None
    url = getattr(first_image, size)
    response = requests.head(url, timeout=15)

    assert response.status_code == 200, url
    assert response.headers["Content-Type"].startswith("image/"), url


@pytest.mark.parametrize("category", [None, "Contacten en Berichten", "Vacatures"])
def test_listing_without_photos(category: str | None) -> None:
    search = SearchQuery(
        "gezocht" if category is None else "",
        category=category_from_name(category) if category else None,
        limit=100,
        sort_by=SortBy.DATE,
        sort_order=SortOrder.DESC,
    )
    listing = next((x for x in search.get_listings() if x.first_image is None), None)
    if listing is None:
        pytest.skip("No listing without photos found")

    # The page shows a placeholder, which must not be returned as an image
    assert listing.get_images() == []


@pytest.mark.smoke
def test_unknown_listing_raises() -> None:
    with pytest.raises(requests.HTTPError):
        fetch_listing_images("m0000000001")
