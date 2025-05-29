from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from typing_extensions import Self


@dataclass
class ListingLocation:
    city: str | None
    country: str | None
    country_short: str | None
    latitude: float | None
    longitude: float | None
    distance: int | None

    @classmethod
    def parse(cls, data: dict[str, Any]) -> Self:
        return cls(
            data.get("cityName"),
            data.get("countryName"),
            data.get("countryAbbrevation"),
            data["latitude"] if data["latitude"] != 0 else None,
            data["longitude"] if data["longitude"] != 0 else None,
            data.get("distanceMeters") if data.get("distanceMeters") != -1000 else None,
        )
