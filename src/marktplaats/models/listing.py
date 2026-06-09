from __future__ import annotations

import warnings
from dataclasses import dataclass
from http import HTTPStatus
from typing import TYPE_CHECKING

from bs4 import BeautifulSoup

from marktplaats.models.listing_image import ListingFirstImage, fetch_listing_images
from marktplaats.utils import get_request


if TYPE_CHECKING:
    from datetime import date
    from types import NotImplementedType

    from marktplaats.api_types import Attribute
    from marktplaats.models.listing_location import ListingLocation
    from marktplaats.models.listing_seller import ListingSeller
    from marktplaats.models.price_type import PriceType


@dataclass
class Listing:
    id: str
    title: str
    description: str
    date: date | None
    seller: ListingSeller
    location: ListingLocation
    price: float
    price_type: PriceType
    link: str
    _images: list[ListingFirstImage]
    category_id: int
    attributes: list[Attribute]
    extended_attributes: list[Attribute]

    @property
    def images(self) -> list[ListingFirstImage]:
        warnings.warn(
            "Listing.images is deprecated since marktplaats version 0.3.0. "
            "Please use Listing.first_image or Listing.get_images() instead.",
            category=DeprecationWarning,
            stacklevel=2,
        )
        return self._images

    @property
    def first_image(self) -> ListingFirstImage | None:
        try:
            return self._images[0]
        except IndexError:
            # there seem to be no images in the listing, so return None
            return None

    def get_images(self) -> list[str]:
        return fetch_listing_images(self.id)

    def __eq__(self, other: object) -> NotImplementedType | bool:
        if not isinstance(other, Listing):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

    def price_as_string(
        self,
        *,
        euro_sign: bool = True,
        lang: str = "en",
    ) -> str:
        return self.price_type._as_string(  # noqa: SLF001 private member access
            self.price,
            euro_sign=euro_sign,
            lang=lang,
        )

    def get_full_description(self) -> str | None:
        response = get_request(url=self.link)
        if response.status_code != HTTPStatus.OK:
            return None
        description_div = BeautifulSoup(response.text, "html.parser").find(
            "div", class_="Description-module-description")
        if not description_div:
            return None
        self.full_description = description_div.get_text(separator="\n")
        return self.full_description
