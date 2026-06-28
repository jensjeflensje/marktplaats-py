from __future__ import annotations

from types import SimpleNamespace

import responses

from marktplaats import Listing
from tests.utils import get_mock_file


@responses.activate
def test_get_raw_details_mocked() -> None:
    """Test get_raw_details method with a mocked response."""
    responses.get(
        "https://link.marktplaats.nl/m123456789",
        status=200,
        body=get_mock_file("raw_details_response.html"),
    )
    fake = SimpleNamespace(id="m123456789")
    details = Listing.get_raw_details(fake)  # type: ignore[arg-type]

    assert details["seller"]["activeSinceDiff"] == "16 jaar"
    assert details["seller"]["sellerType"] == "CONSUMER"
    assert details["stats"]["viewCount"] == 5
    assert (
        details["shippingInformation"]["deliveryType"]["attributeValueLabel"]
        == "Ophalen of Verzenden"
    )
    assert details["bidsInfo"]["bids"] == []
    assert details["adType"] == "RegularFree"
