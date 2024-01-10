from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from marktplaats.models import ListingSeller
from marktplaats.models.listing_location import ListingLocation


@dataclass
class Listing:
    id: str
    title: str
    description: str
    date: Optional[datetime]
    seller: ListingSeller
    location: ListingLocation
    price: float
    link: str
    images: list
    category_id: int
    attributes: list
    extended_attributes: list
