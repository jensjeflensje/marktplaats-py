from __future__ import annotations

import json
from dataclasses import dataclass
from typing import TYPE_CHECKING

from typing_extensions import Self

from marktplaats.utils import get_request


if TYPE_CHECKING:
    from marktplaats.api_types import Review, SellerInformation


@dataclass
class Seller:
    id: int
    name: str
    is_verified: bool
    average_score: float | None
    number_of_reviews: int | None
    bank_account: bool
    identification: bool
    phone_number: bool


@dataclass
class ListingSeller:
    id: int
    name: str
    is_verified: bool

    @classmethod
    def parse(cls, data: SellerInformation) -> Self:
        return cls(
            data["sellerId"],
            data["sellerName"],
            data["isVerified"],
        )

    def get_seller(self) -> Seller:
        request = get_request(
            f"https://www.marktplaats.nl/v/api/seller-profile/{self.id}"
        )

        body = request.text
        body_json = json.loads(body)

        review: Review | None = (
            body_json["reviews"][0] if body_json["reviews"] else None
        )
        return Seller(
            self.id,
            self.name,
            self.is_verified,
            review["averageScore"] if review else None,
            review["numberOfReviews"] if review else None,
            body_json["bankAccount"],
            body_json["identification"],
            body_json["phoneNumber"],
        )
