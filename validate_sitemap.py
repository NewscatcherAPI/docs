import xml.etree.ElementTree as ET
from urllib.parse import urlparse
import sys


def validate_sitemap(filepath: str) -> tuple[bool, list[str]]:
    """
    Validates the sitemap file.
    Returns (is_valid, list_of_issues)
    """
    issues = []
    try:
        # Parse XML
        tree = ET.parse(filepath)
        root = tree.getroot()

        # Check namespace
        if not root.tag.endswith("urlset"):
            issues.append("Root element is not 'urlset'")

        # Validate each URL entry
        urls_found = 0
        for url in root.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}url"):
            urls_found += 1

            # Check required elements
            loc = url.find("{http://www.sitemaps.org/schemas/sitemap/0.9}loc")
            if loc is None or not loc.text:
                issues.append(f"Missing or empty 'loc' element in URL #{urls_found}")
            else:
                # Validate URL format
                parsed_url = urlparse(loc.text)
                if not all([parsed_url.scheme, parsed_url.netloc]):
                    issues.append(f"Invalid URL format: {loc.text}")
                if "www.newscatcherapi.com" not in loc.text:
                    issues.append(f"Unexpected domain in URL: {loc.text}")
                if not loc.text.endswith("/"):
                    issues.append(f"URL doesn't end with trailing slash: {loc.text}")

            # Check other required elements
            lastmod = url.find("{http://www.sitemaps.org/schemas/sitemap/0.9}lastmod")
            if lastmod is None or not lastmod.text:
                issues.append(f"Missing or empty 'lastmod' in URL #{urls_found}")

            changefreq = url.find(
                "{http://www.sitemaps.org/schemas/sitemap/0.9}changefreq"
            )
            if changefreq is None or not changefreq.text:
                issues.append(f"Missing or empty 'changefreq' in URL #{urls_found}")
            elif changefreq.text not in [
                "always",
                "hourly",
                "daily",
                "weekly",
                "monthly",
                "yearly",
                "never",
            ]:
                issues.append(f"Invalid changefreq value: {changefreq.text}")

            priority = url.find("{http://www.sitemaps.org/schemas/sitemap/0.9}priority")
            if priority is None or not priority.text:
                issues.append(f"Missing or empty 'priority' in URL #{urls_found}")
            else:
                try:
                    p = float(priority.text)
                    if not 0 <= p <= 1:
                        issues.append(f"Priority value out of range [0.0, 1.0]: {p}")
                except ValueError:
                    issues.append(f"Invalid priority value: {priority.text}")

        if urls_found == 0:
            issues.append("No URLs found in sitemap")

        print(f"Found {urls_found} URLs in sitemap")

    except ET.ParseError as e:
        issues.append(f"XML parsing error: {str(e)}")
    except Exception as e:
        issues.append(f"Validation error: {str(e)}")

    return len(issues) == 0, issues


def main():
    if len(sys.argv) != 2:
        print("Usage: python validate_sitemap.py sitemap.xml")
        sys.exit(1)

    sitemap_file = sys.argv[1]
    is_valid, issues = validate_sitemap(sitemap_file)

    if is_valid:
        print("✅ Sitemap validation passed!")
    else:
        print("❌ Sitemap validation failed!")
        print("\nIssues found:")
        for issue in issues:
            print(f"- {issue}")
        sys.exit(1)


if __name__ == "__main__":
    main()
