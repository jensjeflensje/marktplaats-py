from __future__ import annotations

import warnings
from dataclasses import dataclass
from typing import TYPE_CHECKING

from typing_extensions import Self


if TYPE_CHECKING:
    from marktplaats.api_types import Location


@dataclass
class ListingLocation:
    city: str | None
    country: str | None
    country_short: str | None
    latitude: float | None
    longitude: float | None
    distance_km: int | None

    @property
    def distance(self) -> int | None:
        warnings.warn(
            "ListingLocation.distance is deprecated. Use distance_km instead.",
            category=DeprecationWarning,
            stacklevel=2,
        )
        return self.distance_km * 1000 if self.distance_km is not None else None

    @classmethod
    def parse(cls, data: Location) -> Self:
        return cls(
            data.get("cityName"),
            data.get("countryName"),
            data.get("countryAbbreviation"),
            data["latitude"] if data["latitude"] != 0 else None,
            data["longitude"] if data["longitude"] != 0 else None,
            data.get("distanceMeters") // 1000
            if data.get("distanceMeters") != -1000  # ruff:ignore[magic-value-comparison] magic value
            else None,
        )
