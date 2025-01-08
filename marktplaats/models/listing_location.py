from dataclasses import dataclass
from typing import Optional


@dataclass
class ListingLocation:
    city: str
    country: str
    country_short: str
    latitude: float
    longitude: float
    distance: Optional[int]

    @classmethod
    def parse(cls, data):
        return cls(
            data.get("cityName"),
            data.get("countryName"),
            data.get("countryAbbrevation"),
            data.get("latitude"),
            data.get("longitude"),
            None if data.get("distanceMeters") == -1000 else data.get("distanceMeters"),
        )

