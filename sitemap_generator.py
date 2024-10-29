import json
from datetime import datetime
import xml.etree.ElementTree as ET
from xml.dom import minidom
from typing import List, Dict, Any, Set
from urllib.parse import urlparse, urlunparse


class SitemapGenerator:
    def __init__(
        self,
        base_url: str = "https://www.newscatcherapi.com/docs",
        force_www: bool = True,  # Default to True to always include www
    ):
        """
        Initialize the sitemap generator.

        Args:
            base_url: Base URL for the documentation
            force_www: If True, ensures www is in the domain. If False, removes www.
        """
        # Parse the base URL
        parsed = urlparse(base_url)

        # Handle www in domain
        netloc = parsed.netloc
        if force_www:
            if not netloc.startswith("www."):
                netloc = "www." + netloc
        else:
            netloc = netloc.replace("www.", "")

        # Reconstruct the URL
        self.base_url = urlunparse(
            (
                parsed.scheme,
                netloc,
                parsed.path.rstrip("/"),  # Remove trailing slash from base URL
                parsed.params,
                parsed.query,
                parsed.fragment,
            )
        )

    def _process_navigation_pages(self, pages: List[Any]) -> Set[str]:
        """Process pages from navigation section to extract all URLs."""
        urls = set()

        for page in pages:
            if isinstance(page, str):
                # Direct page URL
                urls.add(page)
            elif isinstance(page, dict):
                if "pages" in page:
                    # Handle nested pages (e.g., in groups)
                    if isinstance(page["pages"], list):
                        urls.update(self._process_navigation_pages(page["pages"]))
                elif "url" in page:
                    # Handle direct URL in dictionary
                    urls.add(page["url"])

        return urls

    def _create_url_element(self, url: str) -> ET.Element:
        """Create a URL element for the sitemap."""
        url_element = ET.Element("url")

        # Create loc element with full URL
        loc = ET.SubElement(url_element, "loc")
        # Add trailing slash to all URLs for consistency
        loc.text = f"{self.base_url}/{url}".rstrip("/") + "/"

        # Add lastmod element
        lastmod = ET.SubElement(url_element, "lastmod")
        lastmod.text = datetime.utcnow().strftime("%Y-%m-%d")

        # Add changefreq element
        changefreq = ET.SubElement(url_element, "changefreq")
        changefreq.text = "weekly"

        # Add priority element
        priority = ET.SubElement(url_element, "priority")
        priority.text = "0.8"

        return url_element

    def generate_sitemap(self, mint_json_path: str) -> str:
        """Generate sitemap XML from mint.json file."""
        # Read mint.json
        with open(mint_json_path, "r") as f:
            config = json.load(f)

        # Create root element
        root = ET.Element("urlset")
        root.set("xmlns", "http://www.sitemaps.org/schemas/sitemap/0.9")

        # Add base documentation URL
        root.append(self._create_url_element(""))

        # Process all URLs from navigation
        urls = set()
        for nav_item in config.get("navigation", []):
            if "pages" in nav_item:
                urls.update(self._process_navigation_pages(nav_item["pages"]))

        # Create URL elements for each unique URL
        for url in sorted(urls):
            root.append(self._create_url_element(url))

        # Convert to pretty XML string
        return minidom.parseString(ET.tostring(root)).toprettyxml(indent="  ")

    def save_sitemap(self, sitemap_content: str, output_path: str):
        """Save sitemap to file."""
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(sitemap_content)


def main():
    generator = SitemapGenerator(
        base_url="https://www.newscatcherapi.com/docs",
        force_www=True,  # Ensure www is included
    )
    sitemap_content = generator.generate_sitemap("mint.json")
    generator.save_sitemap(sitemap_content, "sitemap.xml")


if __name__ == "__main__":
    main()
