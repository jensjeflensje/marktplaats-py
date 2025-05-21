import unittest
from datetime import datetime, timedelta, date

from marktplaats import SearchQuery, SortBy, SortOrder, Condition, category_from_name, PriceType, ListingLocation, \
    ListingSeller
from marktplaats.models.listing_seller import Seller


class LiveSearchQueryTest(unittest.TestCase):
    """
    Live tests (sent to Marktplaats) to ensure they
    haven't deployed breaking changes.
    """

    def _validate_response(self, search):
        listings = search.get_listings()

        for listing in listings:
            self.assertIsInstance(listing.title, str)
            self.assertIsInstance(listing.description, str)
            self.assertIsInstance(listing.price, float)
            self.assertIsInstance(listing.price_as_string(lang="nl"), str)
            self.assertIsInstance(listing.price_as_string(lang="en"), str)
            self.assertIsInstance(listing.price_type, PriceType)

            self.assertIsInstance(listing.link, str)
            self.assertTrue(listing.link.startswith("https://"))

            # the location object
            self.assertIsInstance(listing.location, ListingLocation)
            self.assertIsInstance(listing.location.city, str)
            self.assertIsInstance(listing.location.latitude, float)
            self.assertIsInstance(listing.location.longitude, float)

            # the seller object
            self.assertIsInstance(listing.seller, ListingSeller)
            self.assertIsInstance(listing.seller.id, int)
            self.assertIsInstance(listing.seller.name, str)
            self.assertIsInstance(listing.seller.is_verified, bool)

            # the date object
            self.assertIsInstance(listing.date, date)
            # should be greater or equal to what we queried for
            self.assertGreaterEqual(listing.date, datetime.now().date() - timedelta(days=7))

            # the full seller object (another request)
            seller = listing.seller.get_seller()
            self.assertIsInstance(seller, Seller)
            self.assertIsInstance(seller.id, int)
            self.assertIsInstance(seller.name, str)
            self.assertIsInstance(seller.is_verified, bool)
            self.assertIsNotNone(seller.average_score)
            self.assertIsInstance(seller.number_of_reviews, int)
            self.assertIsInstance(seller.bank_account, bool)
            self.assertIsInstance(seller.identification, bool)
            self.assertIsInstance(seller.phone_number, bool)

            for image in listing.images:
                self.assertIsInstance(image.extra_small, str)
                self.assertIsInstance(image.medium, str)
                self.assertIsInstance(image.large, str)
                self.assertIsInstance(image.extra_large, str)

    def test_request(self):
        search = SearchQuery("fiets",
                             zip_code="1016LV",
                             distance=100000,
                             price_from=0,
                             price_to=100,
                             limit=5,
                             offset=0,
                             sort_by=SortBy.LOCATION,
                             sort_order=SortOrder.ASC,
                             offered_since=datetime.now() - timedelta(days=7),
                             category=category_from_name("Fietsen en Brommers"))

        self._validate_response(search)


    def test_request_with_condition(self):
        search = SearchQuery("schijf",
                             zip_code="1016LV",
                             distance=100000,
                             price_from=0,
                             price_to=100,
                             offered_since=datetime.now() - timedelta(days=7),
                             condition=Condition.NOT_WORKING,
                             category=category_from_name("Computers en Software"))

        self._validate_response(search)


if __name__ == '__main__':
    unittest.main()
