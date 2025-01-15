import unittest
from datetime import datetime, timedelta

from marktplaats import SearchQuery, SortBy, SortOrder, Condition, category_from_name


class LiveSearchQueryTest(unittest.TestCase):
    """
    Live tests (sent to Marktplaats) to ensure they
    haven't deployed breaking changes.
    """

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

        listings = search.get_listings()

        for listing in listings:
            print(listing.title)
            print(listing.description)
            print(listing.price)
            print(listing.price_as_string(lang="nl"))
            print(listing.price_type)
            print(listing.link)

            # the location object
            print(listing.location)

            # the seller object
            print(listing.seller)

            # the datetime object
            print(listing.date)


            # the full seller object (another request)
            print(listing.seller.get_seller())

            for image in listing.images:
                print(image.medium)

            print("-----------------------------")

    def test_request_with_condition(self):
        search = SearchQuery("schijf",
                             zip_code="1016LV",
                             distance=100000,
                             price_from=0,
                             price_to=100,
                             condition=Condition.NOT_WORKING,
                             category=category_from_name("Computers en Software"))

        listings = search.get_listings()

        for listing in listings:
            print(listing.title)
            print(listing.description)
            print(listing.price)
            print(listing.price_as_string(lang="nl"))
            print(listing.price_type)
            print(listing.link)

            # the location object
            print(listing.location)

            # the seller object
            print(listing.seller)

            # the datetime object
            print(listing.date)


            # the full seller object (another request)
            print(listing.seller.get_seller())

            for image in listing.images:
                print(image.medium)

            print("-----------------------------")


if __name__ == '__main__':
    unittest.main()
