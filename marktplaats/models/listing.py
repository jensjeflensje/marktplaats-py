from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from marktplaats.models import ListingSeller
from marktplaats.models.listing_location import ListingLocation
from marktplaats.models.price_type import PriceType


@dataclass
class Listing:
    id: str
    title: str
    description: str
    date: Optional[datetime]
    seller: ListingSeller
    location: ListingLocation
    price: float
    price_type: PriceType
    link: str
    images: list
    category_id: int
    attributes: list
    extended_attributes: list

    def __eq__(self, other):
        if not isinstance(other, Listing):
            return NotImplemented
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)

    def price_as_string(self, euro_sign: bool = True, lang: str = "en") -> str:
        return self.price_type._as_string(self.price, euro_sign, lang)
