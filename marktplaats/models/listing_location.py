from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from typing_extensions import Self


@dataclass
class ListingLocation:
    city: str | None
    country: str | None
    country_short: str | None
    latitude: float
    longitude: float
    distance: int | None

    @classmethod
    def parse(cls, data: dict[str, Any]) -> Self:
        return cls(
            data.get("cityName"),
            data.get("countryName"),
            data.get("countryAbbrevation"),
            data["latitude"],
            data["longitude"],
            None if data.get("distanceMeters") == -1000 else data.get("distanceMeters"),
        )

