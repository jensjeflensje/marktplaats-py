"""
Response from the API endpoint `/v/api/seller-other-items`.

Note that this listing data is less detailed than what is returned when
performing a search query, which uses the `/lrp/api/search` endpoint.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, TypedDict


if TYPE_CHECKING:
    from marktplaats.api_types.search import Picture, PriceInfo


class Category(TypedDict):
    id: int
    name: str
    fullName: str
    parentId: int
    parentName: str


class Item(TypedDict):
    itemId: str
    title: str
    price: PriceInfo
    imageUrls: list[str]
    category: Category
    traits: list[str]
    pictures: list[Picture]
    thinContent: bool
    isLease: bool
    url: str


class SellerListingsResponse(TypedDict):
    items: list[Item]
    total: int
