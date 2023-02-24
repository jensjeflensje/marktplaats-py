from dataclasses import dataclass


@dataclass
class ListingLocation:
    city: str
    country: str
    country_short: str
    latitude: float
    longitude: float

    @classmethod
    def parse(cls, data):
        return cls(
            data.get("cityName"),
            data.get("countryName"),
            data.get("countryAbbrevation"),
            data.get("latitude"),
            data.get("longitude"),
        )

