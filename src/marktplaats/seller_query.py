from __future__ import annotations

from typing import TYPE_CHECKING

from marktplaats.utils import get_request


if TYPE_CHECKING:
    from marktplaats.api_types import SellerDetailsResponse, SellerListingsResponse


class SellerQuery:
    """Query a seller."""

    def __init__(self, seller_id: int) -> None:
        self.seller_id = seller_id
        self._listings_raw: SellerListingsResponse | None = None
        self._details_raw: SellerDetailsResponse | None = None

    def fetch_details(self) -> SellerDetailsResponse:
        """
        Fetch the seller details from the API.

        Returns:
            Response body as an unparsed dictionary.

        """
        if self._details_raw is None:
            url = f"https://www.marktplaats.nl/v/api/seller-profile/{self.seller_id}"
            res = get_request(url)
            res.raise_for_status()
            payload = res.json()
            self._details_raw = payload
        return self._details_raw

    def fetch_listings(self) -> SellerListingsResponse:
        """
        Fetch all listings for this seller from the API.

        Returns:
            Response body as an unparsed dictionary.

        """
        if self._listings_raw is None:
            url = "https://www.marktplaats.nl/v/api/seller-other-items"
            params = {
                "sellerId": self.seller_id,
                "itemId": "m0123456789",  # Any item ID will do.
                "l2CategoryId": "1",  # Any L2 category ID will do.
            }
            res = get_request(url, params)
            res.raise_for_status()
            payload = res.json()
            self._listings_raw = payload
        return self._listings_raw
