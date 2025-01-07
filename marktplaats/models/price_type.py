from enum import Enum


class PriceType(Enum):
    # "Gratis", `.price` should be 0
    FREE = "FREE"
    # "Bieden", `.price` should be 0
    BID = "FAST_BID"
    # "Gereserveerd", `.price` should be 0
    RESERVED = "RESERVED"
    # "Zie omschrijving", `.price` should be 0
    SEE_DESCRIPTION = "SEE_DESCRIPTION"
    # Just the price
    FIXED = "FIXED"
    # Just the price, but the API also lets us know there's a bidding option separate from the asking price
    #  This bid does not start from `.price`, but from another unknown value.
    #  The `.price` is the asking price shown in the search results.
    BID_FROM = "MIN_BID"

    def _as_string(self, price: float, euro_sign: bool, lang: str) -> str:
        if lang not in ("en", "nl"):
            raise ValueError(f"{lang:r} not in supported languages (nl, en)")

        if self == PriceType.FREE:
            return {
                "en": "Free",
                "nl": "Gratis",
            }[lang]
        elif self == PriceType.BID:
            return {
                "en": "Bid",
                "nl": "Bieden",
            }[lang]
        elif self == PriceType.RESERVED:
            return {
                "en": "Reserved",
                "nl": "Gereserveerd",
            }[lang]
        elif self == PriceType.SEE_DESCRIPTION:
            return {
                "en": "See description",
                "nl": "Zie omschrijving",
            }[lang]
        elif self == PriceType.FIXED:
            return f"{'€ ' if euro_sign else ''}{price:.2f}"
        elif self == PriceType.BID_FROM:
            return f"{'€ ' if euro_sign else ''}{price:.2f}"

        assert False