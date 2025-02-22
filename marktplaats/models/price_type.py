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
    # "N.o.t.k.", `.price` should be 0
    TO_BE_AGREED_UPON = "NOTK"
    # 'Op aanvraag', `.price` should be 0
    ON_REQUEST = "ON_REQUEST"
    # 'Ruilen', `.price` should be 0
    EXCHANGE = "EXCHANGE"
    # Just the price
    FIXED = "FIXED"
    # Just the price, but the API also lets us know there's a bidding option separate from the asking price
    #  This bid does not start from `.price`, but from another unknown value.
    #  The `.price` is the asking price shown in the search results.
    BID_FROM = "MIN_BID"

    # Used when the price type marktplaats returns doesn't match any of our price types
    UNKNOWN = "UNKNOWN"

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
        elif self == PriceType.TO_BE_AGREED_UPON:
            return {
                "en": "To be agreed upon",
                "nl": "N.o.t.k.",
            }[lang]
        elif self == PriceType.ON_REQUEST:
            return {
                "en": "On request",
                "nl": "Op aanvraag",
            }[lang]
        elif self == PriceType.EXCHANGE:
            return {
                "en": "Exchange",
                "nl": "Ruilen",
            }[lang]
        elif self == PriceType.UNKNOWN:
            return {
                # we don't want a real translation for these
                # as they're the result of an error in the library
                "en": "UNKNOWN",
                "nl": "UNKNOWN",
            }[lang]
        elif self == PriceType.FIXED:
            return f"{'€ ' if euro_sign else ''}{price:.2f}"
        elif self == PriceType.BID_FROM:
            return f"{'€ ' if euro_sign else ''}{price:.2f}"

        assert False
