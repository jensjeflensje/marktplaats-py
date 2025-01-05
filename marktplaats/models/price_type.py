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

    def as_string_en(self, price: float, euro_sign: bool = True) -> str:
        if self == PriceType.FREE:
            return "Free"
        elif self == PriceType.BID:
            return "Bid"
        elif self == PriceType.RESERVED:
            return "Reserved"
        elif self == PriceType.SEE_DESCRIPTION:
            return "See description"
        elif self == PriceType.FIXED:
            return f"{'€ ' if euro_sign else ''}{price:.2f}"
        elif self == PriceType.BID_FROM:
            return f"{'€ ' if euro_sign else ''}{price:.2f}"

        assert False

    def as_string_nl(self, price: float, euro_sign: bool = True) -> str:
        if self == PriceType.FREE:
            return "Gratis"
        elif self == PriceType.BID:
            return "Bieden"
        elif self == PriceType.RESERVED:
            return "Gereserveerd"
        elif self == PriceType.SEE_DESCRIPTION:
            return "Zie omschrijving"
        elif self == PriceType.FIXED:
            return f"{'€ ' if euro_sign else ''}{price:.2f}"
        elif self == PriceType.BID_FROM:
            return f"{'€ ' if euro_sign else ''}{price:.2f}"

        assert False
