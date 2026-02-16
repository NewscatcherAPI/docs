#!/usr/bin/env python3
"""
Update Internal Links Script

Uses the JSON redirect mapping to automatically update all internal links
in MDX files and OpenAPI YAML files.

Usage:
    python update_links.py redirect-map.json

Author: Documentation Team
"""

import os
import re
import sys
import json
from pathlib import Path
from typing import Dict, List, Tuple


def load_redirect_mapping(json_file: str) -> Dict[str, str]:
    """
    Load URL mappings from JSON file.

    Returns dict of source -> destination
    """
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    mappings = {}

    # Load individual redirects
    for redirect in data.get("redirects", []):
        source = redirect["source"]
        destination = redirect["destination"]

        # Store both with and without /docs prefix
        mappings[source] = destination

        # Also handle paths without /docs prefix
        if source.startswith("/docs/"):
            mappings[source.replace("/docs/", "/")] = destination.replace("/docs/", "/")

    print(f"Loaded {len(data.get('redirects', []))} redirect rules")
    print(f"Total mappings (including variants): {len(mappings)}")

    return mappings


def update_markdown_links(content: str, mappings: Dict[str, str]) -> Tuple[str, int]:
    """
    Update markdown-style links: [text](/old/path) -> [text](/new/path)

    Returns (updated_content, number_of_replacements)
    """
    replacements = 0

    # Pattern for markdown links: [text](url)
    # Captures: [1] = link text, [2] = URL
    pattern = r"\[([^\]]+)\]\((/[^\)]+)\)"

    def replace_link(match):
        nonlocal replacements
        text = match.group(1)
        url = match.group(2)

        # Remove anchor and query string for matching
        base_url = url.split("#")[0].split("?")[0]
        anchor = "#" + url.split("#")[1] if "#" in url else ""
        query = (
            "?" + url.split("?")[1]
            if "?" in url and "#" not in url.split("?")[1]
            else ""
        )

        # Try to find mapping
        if base_url in mappings:
            new_url = mappings[base_url] + anchor + query
            replacements += 1
            return f"[{text}]({new_url})"

        # Try with /docs prefix if not found
        docs_url = f"/docs{base_url}"
        if docs_url in mappings:
            new_url = mappings[docs_url] + anchor + query
            replacements += 1
            return f"[{text}]({new_url})"

        # No mapping found, keep original
        return match.group(0)

    updated = re.sub(pattern, replace_link, content)

    # Also handle MDX component href attributes: href="/path"
    def replace_href(match):
        nonlocal replacements
        quote = match.group(1)  # " or '
        url = match.group(2)

        # Remove anchor and query string for matching
        base_url = url.split("#")[0].split("?")[0]
        anchor = "#" + url.split("#")[1] if "#" in url else ""
        query = (
            "?" + url.split("?")[1]
            if "?" in url and "#" not in url.split("?")[1]
            else ""
        )

        # Try to find mapping
        if base_url in mappings:
            new_url = mappings[base_url] + anchor + query
            replacements += 1
            return f"href={quote}{new_url}{quote}"

        # Try with /docs prefix if not found
        docs_url = f"/docs{base_url}"
        if docs_url in mappings:
            new_url = mappings[docs_url] + anchor + query
            replacements += 1
            return f"href={quote}{new_url}{quote}"

        # No mapping found, keep original
        return match.group(0)

    # Pattern for MDX href attributes: href="/path" or href='/path'
    href_pattern = r'href=(["\'])(/[^"\']+)\1'
    updated = re.sub(href_pattern, replace_href, updated)

    return updated, replacements


def update_yaml_refs(content: str, mappings: Dict[str, str]) -> Tuple[str, int]:
    """
    Update YAML references in OpenAPI specs.

    Common patterns:
    - externalDocs: url: "..." or url: ...
    - description: "See [link](/path)" or description: |
        [link](https://full-url)
    - servers: url: "..." (but DON'T change API endpoints like v3-api.newscatcherapi.com)

    Returns (updated_content, number_of_replacements)
    """
    replacements = 0

    # Pattern 1: YAML url fields (with or without quotes)
    # Matches: url: "https://..." or url: https://... or url: '/path'
    def replace_yaml_url(match):
        nonlocal replacements
        prefix = match.group(1)  # "url: " with any whitespace
        quote = match.group(2) if match.group(2) else ""  # ", ', or empty
        url = match.group(3)  # the actual URL

        # DON'T change API server URLs (v3-api.newscatcherapi.com, etc.)
        if "v3-api.newscatcherapi.com" in url or "-api.newscatcherapi.com" in url:
            return match.group(0)

        # Only process docs URLs
        if "/docs/" not in url and not url.startswith("/v3/"):
            return match.group(0)

        # Extract path from full URL
        if "newscatcherapi.com/docs/" in url:
            path = "/" + url.split("/docs/", 1)[1]
        elif url.startswith("/v3/"):
            path = url
        elif url.startswith("/"):
            path = url
        else:
            return match.group(0)

        # Remove trailing slash and anchors for matching
        base_path = path.rstrip("/").split("#")[0].split("?")[0]
        anchor = "#" + path.split("#")[1] if "#" in path else ""

        if base_path in mappings:
            new_path = mappings[base_path]
            if "newscatcherapi.com" in url:
                # Reconstruct full URL
                base_url = url.split("/docs/")[0]
                new_url = f"{base_url}/docs{new_path}{anchor}"
            else:
                new_url = new_path + anchor

            replacements += 1
            if quote:
                return f"{prefix}{quote}{new_url}{quote}"
            else:
                return f"{prefix}{new_url}"

        return match.group(0)

    # Match url: with optional quotes and any URL
    # Captures: (1) "url:" with whitespace, (2) quote or None, (3) URL
    pattern1 = r'(url:\s*)(["\']?)([^\s"\']+)\2'
    updated = re.sub(pattern1, replace_yaml_url, content)

    # Pattern 2: Markdown links within YAML strings (multiline descriptions)
    # These are in description fields like:
    # description: |
    #   See [link](https://www.newscatcherapi.com/docs/v3/...)
    def replace_md_in_yaml(match):
        nonlocal replacements
        text = match.group(1)
        url = match.group(2)

        # Only process docs URLs
        if "/docs/" not in url and not url.startswith("/v3/"):
            return match.group(0)

        # Extract path from full URL
        if "newscatcherapi.com/docs/" in url:
            path = "/" + url.split("/docs/", 1)[1]
        elif url.startswith("/v3/"):
            path = url
        elif url.startswith("/"):
            path = url
        else:
            return match.group(0)

        # Remove trailing slash and anchors for matching
        base_path = path.rstrip("/").split("#")[0].split("?")[0]
        anchor = "#" + path.split("#")[1] if "#" in path else ""

        if base_path in mappings:
            new_path = mappings[base_path]
            if "newscatcherapi.com" in url:
                # Reconstruct full URL
                base_url = url.split("/docs/")[0]
                new_url = f"{base_url}/docs{new_path}{anchor}"
            else:
                new_url = new_path + anchor

            replacements += 1
            return f"[{text}]({new_url})"

        return match.group(0)

    # Pattern for markdown links with full or relative URLs
    md_pattern = r"\[([^\]]+)\]\((https://[^\)]+|/[^\)]+)\)"
    updated = re.sub(md_pattern, replace_md_in_yaml, updated)

    return updated, replacements


def process_file(
    filepath: Path, mappings: Dict[str, str], dry_run: bool = False
) -> Tuple[bool, int]:
    """
    Process a single file to update links.

    Returns (was_modified, num_replacements)
    """
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
    except UnicodeDecodeError:
        print(f"  ⚠ Skipping binary file: {filepath}")
        return False, 0
    except Exception as e:
        print(f"  ✗ Error reading {filepath}: {e}")
        return False, 0

    original = content
    replacements = 0

    # Update based on file type
    if filepath.suffix in [".md", ".mdx"]:
        content, replacements = update_markdown_links(content, mappings)
    elif filepath.suffix in [".yml", ".yaml"]:
        content, replacements = update_yaml_refs(content, mappings)
    else:
        return False, 0

    if content == original:
        return False, 0

    if not dry_run:
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
        except Exception as e:
            print(f"  ✗ Error writing {filepath}: {e}")
            return False, 0

    return True, replacements


def find_documentation_files(root_dir: str, extensions: List[str]) -> List[Path]:
    """Find all documentation files with specified extensions."""
    root = Path(root_dir)
    files = []

    # Only search in target directories
    target_dirs = ["home", "web-search-api", "news-api", "local-news-api"]

    for target_dir in target_dirs:
        target_path = root / target_dir
        if target_path.exists():
            for ext in extensions:
                files.extend(target_path.glob(f"**/*{ext}"))

    # Filter out node_modules, .git, etc.
    files = [
        f
        for f in files
        if not any(part.startswith(".") for part in f.parts)
        and "node_modules" not in f.parts
        and "backup-" not in str(f)
    ]

    return sorted(files)


def main():
    import os
    from pathlib import Path

    script_dir = Path(__file__).parent
    project_root = script_dir.parent if script_dir.name == "scripts" else script_dir
    os.chdir(project_root)
    print(f"Working directory: {project_root}\n")

    if len(sys.argv) < 2:
        print("Usage: python update_links.py redirect-map.json [--dry-run]")
        sys.exit(1)

    json_file = sys.argv[1]
    dry_run = "--dry-run" in sys.argv

    if not os.path.exists(json_file):
        print(f"Error: JSON file not found: {json_file}")
        sys.exit(1)

    print("=" * 70)
    print("Internal Links Update Script")
    print("=" * 70)
    print()

    if dry_run:
        print("🔍 DRY RUN MODE - No files will be modified")
        print()

    # Load mappings
    mappings = load_redirect_mapping(json_file)
    print()

    # Find files to process
    print("Finding documentation files...")
    mdx_files = find_documentation_files(".", [".md", ".mdx"])
    yaml_files = find_documentation_files(".", [".yml", ".yaml"])

    all_files = mdx_files + yaml_files
    print(f"Found {len(mdx_files)} MDX files and {len(yaml_files)} YAML files")
    print()

    if not all_files:
        print("No files found to process.")
        return

    # Process files
    print("=" * 70)
    print("Processing files...")
    print("=" * 70)
    print()

    modified_files = []
    total_replacements = 0

    for filepath in all_files:
        modified, replacements = process_file(filepath, mappings, dry_run)

        if modified:
            modified_files.append(filepath)
            total_replacements += replacements
            rel_path = filepath.relative_to(".")
            print(f"  ✓ {rel_path} - {replacements} link(s) updated")

    # Summary
    print()
    print("=" * 70)
    print("Summary")
    print("=" * 70)
    print(f"Files processed: {len(all_files)}")
    print(f"Files modified: {len(modified_files)}")
    print(f"Total links updated: {total_replacements}")
    print()

    if dry_run:
        print("🔍 This was a dry run. No files were modified.")
        print("Run without --dry-run to apply changes.")
    else:
        print("✓ All links updated successfully!")
        print()
        print("Next steps:")
        print("1. Review changes: git diff")
        print("2. Test locally: mint dev")
        print(
            "3. Commit changes: git add . && git commit -m 'docs: update internal links'"
        )

    print()


if __name__ == "__main__":
    main()
