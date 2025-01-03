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

    def price_as_string_en(self) -> str:
        return self.price_type.as_string_en(self.price)

    def price_as_string_nl(self) -> str:
        return self.price_type.as_string_nl(self.price)
