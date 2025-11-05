#!/usr/bin/env python3
"""
Script to find and check all links in documentation files.
Identifies broken links (404) and reports their status.
"""

import os
import re
import requests
from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import defaultdict
from urllib.parse import urlparse
import time
import json

# Configuration
FILE_EXTENSIONS = [".mdx", ".yml", ".yaml", ".md"]
REQUEST_TIMEOUT = 10  # seconds
DELAY_BETWEEN_REQUESTS = 0.5  # seconds to avoid rate limiting
USER_AGENT = "Mozilla/5.0 (compatible; LinkChecker/1.0)"
TARGET_DOMAIN = (
    "newscatcherapi.com"  # Will match www.newscatcherapi.com, newscatcherapi.com, etc.
)


class LinkChecker:
    def __init__(self, root_dir: str, target_domain: str = None):
        self.root_dir = Path(root_dir).resolve()
        self.target_domain = target_domain
        self.links_cache: Dict[str, Tuple[int, str]] = (
            {}
        )  # url -> (status_code, status_text)
        self.link_locations: Dict[str, List[Path]] = defaultdict(
            list
        )  # url -> [file_paths]

    def is_target_domain(self, url: str) -> bool:
        """Check if URL belongs to target domain."""
        if not self.target_domain:
            return True  # If no target domain specified, include all links

        try:
            parsed = urlparse(url)
            hostname = parsed.netloc.lower()

            # Check if hostname matches or is a subdomain of target domain
            return hostname == self.target_domain or hostname.endswith(
                f".{self.target_domain}"
            )
        except:
            return False

    def find_files(self, extensions: List[str]) -> List[Path]:
        """Find all files with specified extensions."""
        files = []
        for ext in extensions:
            files.extend(self.root_dir.rglob(f"*{ext}"))
        return files

    def extract_links_from_file(self, file_path: Path) -> Set[str]:
        """Extract all HTTP/HTTPS links from a file."""
        links = set()
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Pattern to match URLs in various formats
            patterns = [
                r"https?://[^\s\)\]\}\"\'\`<>]+",  # Standard URLs
                r'href=["\']([^"\']+)["\']',  # href attributes
                r'url:\s*["\']?([^\s"\']+)["\']?',  # YAML url fields
            ]

            for pattern in patterns:
                matches = re.finditer(pattern, content)
                for match in matches:
                    url = match.group(1) if match.lastindex else match.group(0)
                    # Clean up the URL
                    url = url.rstrip(".,;:!?)")
                    if url.startswith("http") and self.is_target_domain(url):
                        links.add(url)

        except Exception as e:
            print(f"Error reading {file_path}: {e}")

        return links

    def check_url(self, url: str) -> Tuple[int, str]:
        """Check if a URL is accessible and return status code."""
        if url in self.links_cache:
            return self.links_cache[url]

        try:
            # Make request with timeout
            headers = {"User-Agent": USER_AGENT}
            response = requests.head(
                url, timeout=REQUEST_TIMEOUT, headers=headers, allow_redirects=True
            )

            # Some servers don't respond to HEAD, try GET
            if response.status_code == 405 or response.status_code == 404:
                response = requests.get(
                    url,
                    timeout=REQUEST_TIMEOUT,
                    headers=headers,
                    allow_redirects=True,
                    stream=True,
                )

            status = (response.status_code, response.reason)

        except requests.exceptions.Timeout:
            status = (-1, "Timeout")
        except requests.exceptions.ConnectionError:
            status = (-2, "Connection Error")
        except requests.exceptions.TooManyRedirects:
            status = (-3, "Too Many Redirects")
        except requests.exceptions.RequestException as e:
            status = (-4, f"Request Error: {str(e)[:50]}")
        except Exception as e:
            status = (-5, f"Unknown Error: {str(e)[:50]}")

        self.links_cache[url] = status
        time.sleep(DELAY_BETWEEN_REQUESTS)  # Rate limiting

        return status

    def scan_repository(self) -> Dict[str, List[Tuple[Path, str]]]:
        """Scan all files and collect links with their locations."""
        print(f"Scanning repository: {self.root_dir}")
        if self.target_domain:
            print(
                f"Filtering for domain: {self.target_domain} (including subdomains)\n"
            )
        else:
            print("Checking all links\n")

        files = self.find_files(FILE_EXTENSIONS)
        print(f"Found {len(files)} files to scan.\n")

        all_links = set()

        for i, file_path in enumerate(files, 1):
            rel_path = file_path.relative_to(self.root_dir)
            print(f"[{i}/{len(files)}] Scanning: {rel_path}", end="\r")

            links = self.extract_links_from_file(file_path)
            for link in links:
                all_links.add(link)
                self.link_locations[link].append(file_path)

        print(f"\n\nFound {len(all_links)} unique links.\n")
        return all_links

    def check_all_links(self, links: Set[str]) -> Dict[str, Tuple[int, str]]:
        """Check status of all links."""
        print("=" * 70)
        print("CHECKING LINKS")
        print("=" * 70 + "\n")

        results = {}
        total = len(links)

        for i, url in enumerate(sorted(links), 1):
            print(f"[{i}/{total}] Checking: {url[:60]}...", end="\r")
            results[url] = self.check_url(url)

        print("\n")
        return results

    def generate_report(self, results: Dict[str, Tuple[int, str]]):
        """Generate and display report of broken links."""
        broken_links = []
        working_links = []
        redirects = []
        errors = []

        for url, (status_code, status_text) in results.items():
            if status_code == 404:
                broken_links.append((url, status_code, status_text))
            elif status_code < 0:
                errors.append((url, status_code, status_text))
            elif 300 <= status_code < 400:
                redirects.append((url, status_code, status_text))
            elif 200 <= status_code < 300:
                working_links.append((url, status_code, status_text))
            else:
                errors.append((url, status_code, status_text))

        # Print summary
        print("=" * 70)
        print("LINK CHECK SUMMARY")
        print("=" * 70)
        print(f"✓ Working links (2xx): {len(working_links)}")
        print(f"→ Redirects (3xx): {len(redirects)}")
        print(f"✗ Broken links (404): {len(broken_links)}")
        print(f"⚠ Errors/Timeouts: {len(errors)}")
        print(f"Total unique links: {len(results)}")
        print("=" * 70 + "\n")

        # Detailed broken links report
        if broken_links:
            print("=" * 70)
            print("BROKEN LINKS (404)")
            print("=" * 70)
            for url, status_code, status_text in sorted(broken_links):
                print(f"\n✗ {url}")
                print(f"  Status: {status_code} {status_text}")
                print(f"  Found in:")
                for file_path in self.link_locations[url]:
                    rel_path = file_path.relative_to(self.root_dir)
                    print(f"    - {rel_path}")
            print()

        # Errors report
        if errors:
            print("=" * 70)
            print("ERRORS & TIMEOUTS")
            print("=" * 70)
            for url, status_code, status_text in sorted(errors):
                print(f"\n⚠ {url}")
                print(f"  Status: {status_text}")
                print(f"  Found in:")
                for file_path in self.link_locations[url]:
                    rel_path = file_path.relative_to(self.root_dir)
                    print(f"    - {rel_path}")
            print()

        # Redirects report
        if redirects:
            print("=" * 70)
            print("REDIRECTS (3xx) - Consider updating to final URL")
            print("=" * 70)
            for url, status_code, status_text in sorted(redirects):
                print(f"\n→ {url}")
                print(f"  Status: {status_code} {status_text}")
                print(f"  Found in: {len(self.link_locations[url])} file(s)")
            print()

        # Save detailed report to file
        self.save_json_report(results, broken_links, errors, redirects, working_links)

    def save_json_report(self, results, broken_links, errors, redirects, working_links):
        """Save detailed report as JSON file."""
        report = {
            "summary": {
                "total_links": len(results),
                "working": len(working_links),
                "broken_404": len(broken_links),
                "redirects": len(redirects),
                "errors": len(errors),
            },
            "broken_links": [
                {
                    "url": url,
                    "status_code": code,
                    "status_text": text,
                    "files": [
                        str(f.relative_to(self.root_dir))
                        for f in self.link_locations[url]
                    ],
                }
                for url, code, text in broken_links
            ],
            "errors": [
                {
                    "url": url,
                    "status_text": text,
                    "files": [
                        str(f.relative_to(self.root_dir))
                        for f in self.link_locations[url]
                    ],
                }
                for url, code, text in errors
            ],
            "redirects": [
                {
                    "url": url,
                    "status_code": code,
                    "status_text": text,
                    "file_count": len(self.link_locations[url]),
                }
                for url, code, text in redirects
            ],
        }

        report_file = self.root_dir / "link_check_report.json"
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)

        print(f"Detailed report saved to: {report_file}")


def main():
    # Get repository root directory
    repo_path = input(
        "Enter the path to your repository (or '.' for current directory): "
    ).strip()
    if not repo_path:
        repo_path = "."

    repo_path = os.path.abspath(repo_path)

    if not os.path.exists(repo_path):
        print(f"Error: Directory '{repo_path}' does not exist.")
        return

    # Ask about domain filtering
    filter_choice = (
        input("\nFilter links by domain? (yes/no, default=yes): ").strip().lower()
    )
    target_domain = None

    if filter_choice in ["", "yes", "y"]:
        domain_input = input(
            f"Enter domain to check (default={TARGET_DOMAIN}): "
        ).strip()
        target_domain = domain_input if domain_input else TARGET_DOMAIN
        print(f"\nWill check only links from: {target_domain} and its subdomains")
    else:
        print("\nWill check ALL links")

    # Create checker and run
    checker = LinkChecker(repo_path, target_domain)

    # Scan for links
    links = checker.scan_repository()

    if not links:
        print("No links found in the repository.")
        return

    # Check all links
    results = checker.check_all_links(links)

    # Generate report
    checker.generate_report(results)


if __name__ == "__main__":
    main()
