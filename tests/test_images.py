import os
import unittest

import requests_mock

from marktplaats.models.listing_image import fetch_listing_images


class ImageFetchTest(unittest.TestCase):
    """
    Basic tests to test image scraping.
    """

    def test_parse_images(self):
        with open('mock/image_response.html', 'r') as file:
            mock_response = file.read()
        with requests_mock.Mocker() as m:
            m.get(
                "https://link.marktplaats.nl/m123456789",
                status_code=200,
                text=mock_response
            )

            urls = fetch_listing_images("m123456789")
            self.assertEqual(len(urls), 9)
            self.assertTrue(urls[0].startswith("https://images.marktplaats.com"))


if __name__ == '__main__':
    unittest.main()
