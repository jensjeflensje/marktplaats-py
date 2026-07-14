from __future__ import annotations

from typing_extensions import TypedDict


class BiddingUser(TypedDict):
    id: int
    nickname: str


class Bid(TypedDict):
    id: int
    value: int
    date: str
    user: BiddingUser


class BidsInfo(TypedDict):
    isBiddingEnabled: bool
    isRemovingBidEnabled: bool
    currentMinimumBid: int
    bids: list[Bid]


class PriceInfo(TypedDict):
    priceCents: int
    priceType: str


class CustomDimensions(TypedDict):
    index: str
    name: str
    scopeLevel: int
    value: str


class Location(TypedDict):
    isAbroad: bool
    cityName: str
    countryName: str
    isOnCountryLevel: bool
    countryAbbreviation: str
    latitude: float
    longitude: float


class Seller(TypedDict):
    id: int
    encryptedSellerId: str
    name: str
    pageUrl: str
    activeSinceDiff: str
    activeYears: int
    isAsqEnabled: bool
    isSaved: bool
    phoneNumberHidden: bool
    sellerType: str
    showMap: bool
    showProfilePicture: bool
    showSalesRepresentatives: bool
    showSellerResponseRate: bool
    showVerifications: bool
    showDealerLegalDisclaimer: bool
    financeAvailable: bool
    requestExternalReviews: bool
    allowCarTestDriveRequest: bool
    withCallAvailabilityIndicator: bool
    location: Location
    contactOptions: list[str]


class ImageSizes(TypedDict):
    XL: str
    M: str
    XXXL: str
    L: str
    XXL: str
    XXS: str
    XS: str
    S: str


class AspectRatio(TypedDict):
    width: int
    height: int


class Images(TypedDict):
    mediaId: str
    base: str
    originalHeight: int
    originalWidth: int
    aspectRatio: AspectRatio


class Media(TypedDict):
    imageSizes: ImageSizes
    images: list[Images]


class Gallery(TypedDict):
    imageUrls: list[str]
    media: Media
    alt: str


class Labels(TypedDict):
    label: str
    price: str
    carrierName: str
    deliveryMethod: str


class AugmentedLabels(TypedDict):
    shouldShowMoreInfo: bool
    carrierId: str
    promoText: str
    labels: list[Labels]


class DeliveryType(TypedDict):
    attributeLabel: str
    attributeValueLabel: str
    attributeValueKey: str


class ShippingInformation(TypedDict):
    augmentedLabels: list[AugmentedLabels]
    deliveryType: DeliveryType


class Stats(TypedDict):
    favoritedCount: int
    viewCount: int
    since: str


class Category(TypedDict):
    id: int
    name: str
    fullName: str
    parentId: int
    parentName: str


class Flags(TypedDict):
    showBannersOnVip: bool
    showExternalAds: bool
    showSellerOtherItems: bool
    requestRelevantItems: bool
    isAdmarkt: bool
    allowTradeInRequest: bool
    shippable: bool
    requestFeeds: bool
    hasCallTracking: bool
    isLeaseCar: bool
    showLoanIndicators: bool
    withBannersFromSeller: bool
    hasDeliveryPackages: bool
    hasDealerHighlights: bool
    isNoCommercialContent: bool


class ScrapedListing(TypedDict):
    itemId: str
    title: str
    traits: list[str]
    adType: str
    bidsInfo: BidsInfo
    priceInfo: PriceInfo
    customDimensions: list[CustomDimensions]
    seller: Seller
    gallery: Gallery
    shippingInformation: ShippingInformation
    stats: Stats
    category: Category
    isSaved: bool
    isSavingEnabled: bool
    isFreeAd: bool
    isAnimalAd: bool
    isCarAd: bool
    isAutomotiveAd: bool
    isCaravansAndCampingAd: bool
    flags: Flags
    highlights: list[str]
    buyersProtectionAllowed: bool
    thinContent: bool
    buyItNowEnabled: bool
    largeItemShippingLogicalAllowed: bool
    isReserved: bool


class ScrapedResponse(TypedDict):
    listing: ScrapedListing
