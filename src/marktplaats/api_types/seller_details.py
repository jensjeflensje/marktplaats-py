"""Response from the API endpoint `/v/api/seller-profile`."""

from __future__ import annotations

from typing import TypedDict


class PaymentMethod(TypedDict):
    name: str


class ProfilePictures(TypedDict):
    backgroundPicture: str
    logoPicture: str


class Review(TypedDict):
    numberOfReviews: int
    rating: float
    reviewSystem: str


class SellerDetailsResponse(TypedDict):
    bankAccount: bool
    phoneNumber: bool
    identification: bool
    paymentMethod: PaymentMethod
    smbVerified: bool
    profilePictures: ProfilePictures
    salesRepresentatives: list[str]
    availableForCallingUntil: str
    lowBidThresholdPercentage: int
    workshopServices: list[str]
    reviews: list[Review]
