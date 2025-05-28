import json
from dataclasses import dataclass
from typing import Any

import requests
from typing_extensions import Self

from marktplaats.utils import REQUEST_HEADERS


@dataclass
class Seller:
    id: int
    name: str
    is_verified: bool
    average_score: float
    number_of_reviews: int
    bank_account: bool
    identification: bool
    phone_number: bool


@dataclass
class ListingSeller:
    id: int
    name: str
    is_verified: bool

    @classmethod
    def parse(cls, data: dict[str, Any]) -> Self:
        return cls(
            data["sellerId"],
            data["sellerName"],
            data["isVerified"],
        )

    def get_seller(self) -> Seller:
        request = requests.get(
            f"https://www.marktplaats.nl/v/api/seller-profile/{self.id}",
            # Some headers to make the request look legit
            headers=REQUEST_HEADERS,
        )

        body = request.text
        body_json = json.loads(body)

        return Seller(
            self.id,
            self.name,
            self.is_verified,
            body_json["averageScore"],
            body_json["numberOfReviews"],
            body_json["bankAccount"],
            body_json["identification"],
            body_json["phoneNumber"],
        )
