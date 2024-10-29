import unittest
import json
import os
from sitemap_generator import SitemapGenerator
import xml.etree.ElementTree as ET


class TestSitemapGenerator(unittest.TestCase):
    def setUp(self):
        self.generator = SitemapGenerator(
            "https://www.newscatcherapi.com/docs", force_www=True
        )

        # Create a test mint.json file
        self.test_config = {
            "navigation": [
                {
                    "group": "Get started",
                    "version": "v3",
                    "pages": [
                        "v3/documentation/get-started/overview",
                        "v3/documentation/get-started/quickstart",
                        "v3/documentation/get-started/libraries",
                    ],
                },
                {
                    "group": "Endpoints",
                    "version": "v3",
                    "pages": [
                        {
                            "group": "Search",
                            "pages": [
                                "v3/api-reference/endpoints/search/search-articles-get",
                                "v3/api-reference/endpoints/search/search-articles-post",
                            ],
                        }
                    ],
                },
            ]
        }

        with open("test_mint.json", "w") as f:
            json.dump(self.test_config, f)

    def tearDown(self):
        # Clean up test files
        if os.path.exists("test_mint.json"):
            os.remove("test_mint.json")
        if os.path.exists("test_sitemap.xml"):
            os.remove("test_sitemap.xml")

    def test_url_generation(self):
        # Generate sitemap
        sitemap_content = self.generator.generate_sitemap("test_mint.json")
        self.generator.save_sitemap(sitemap_content, "test_sitemap.xml")

        # Parse generated sitemap
        tree = ET.parse("test_sitemap.xml")
        root = tree.getroot()

        # Extract all URLs from sitemap
        urls = [
            url.find("{http://www.sitemaps.org/schemas/sitemap/0.9}loc").text
            for url in root.findall("{http://www.sitemaps.org/schemas/sitemap/0.9}url")
        ]

        # Expected URLs
        expected_urls = [
            "https://www.newscatcherapi.com/docs/",
            "https://www.newscatcherapi.com/docs/v3/documentation/get-started/overview/",
            "https://www.newscatcherapi.com/docs/v3/documentation/get-started/quickstart/",
            "https://www.newscatcherapi.com/docs/v3/documentation/get-started/libraries/",
            "https://www.newscatcherapi.com/docs/v3/api-reference/endpoints/search/search-articles-get/",
            "https://www.newscatcherapi.com/docs/v3/api-reference/endpoints/search/search-articles-post/",
        ]

        # Sort both lists for comparison
        urls.sort()
        expected_urls.sort()

        # Compare URLs
        self.assertEqual(urls, expected_urls)

    def test_sitemap_structure(self):
        sitemap_content = self.generator.generate_sitemap("test_mint.json")
        self.generator.save_sitemap(sitemap_content, "test_sitemap.xml")

        # Parse generated sitemap
        tree = ET.parse("test_sitemap.xml")
        root = tree.getroot()

        # Check first URL element structure
        first_url = root.find("{http://www.sitemaps.org/schemas/sitemap/0.9}url")

        # Verify all required elements exist
        self.assertIsNotNone(
            first_url.find("{http://www.sitemaps.org/schemas/sitemap/0.9}loc")
        )
        self.assertIsNotNone(
            first_url.find("{http://www.sitemaps.org/schemas/sitemap/0.9}lastmod")
        )
        self.assertIsNotNone(
            first_url.find("{http://www.sitemaps.org/schemas/sitemap/0.9}changefreq")
        )
        self.assertIsNotNone(
            first_url.find("{http://www.sitemaps.org/schemas/sitemap/0.9}priority")
        )


if __name__ == "__main__":
    unittest.main()
