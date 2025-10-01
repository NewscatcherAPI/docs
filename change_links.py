#!/usr/bin/env python3
"""
Script to find and replace outdated links in MDX and YAML files.
"""

import os
import re
from pathlib import Path
from typing import List, Tuple

# Configuration
OLD_LINK = "https://www.newscatcherapi.com/pricing"
NEW_LINK = "https://www.newscatcherapi.com/book-a-demo"
FILE_EXTENSIONS = [".md", ".mdx", ".yml", ".yaml"]


def find_files(root_dir: str, extensions: List[str]) -> List[Path]:
    """Find all files with specified extensions in directory tree."""
    files = []
    for ext in extensions:
        files.extend(Path(root_dir).rglob(f"*{ext}"))
    return files


def replace_links_in_file(
    file_path: Path, old_link: str, new_link: str, dry_run: bool = True
) -> Tuple[bool, int]:
    """
    Replace old link with new link in a file.

    Returns:
        Tuple of (file_modified, occurrences_found)
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Count occurrences
        occurrences = content.count(old_link)

        if occurrences == 0:
            return False, 0

        # Replace the link
        new_content = content.replace(old_link, new_link)

        if not dry_run:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(new_content)

        return True, occurrences

    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False, 0


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

    print(f"\nScanning repository: {repo_path}")
    print(f"Looking for: {OLD_LINK}")
    print(f"Will replace with: {NEW_LINK}")
    print(f"File types: {', '.join(FILE_EXTENSIONS)}\n")

    # Find all relevant files
    print("Finding files...")
    files = find_files(repo_path, FILE_EXTENSIONS)
    print(f"Found {len(files)} files to scan.\n")

    # Dry run first
    print("=" * 70)
    print("DRY RUN - No files will be modified yet")
    print("=" * 70)

    modified_files = []
    total_occurrences = 0

    for file_path in files:
        modified, occurrences = replace_links_in_file(
            file_path, OLD_LINK, NEW_LINK, dry_run=True
        )
        if modified:
            modified_files.append((file_path, occurrences))
            total_occurrences += occurrences
            rel_path = file_path.relative_to(repo_path)
            print(f"✓ {rel_path} - {occurrences} occurrence(s)")

    print("\n" + "=" * 70)
    print(
        f"Summary: Found {total_occurrences} occurrence(s) in {len(modified_files)} file(s)"
    )
    print("=" * 70)

    if not modified_files:
        print("\nNo links found to replace. Exiting.")
        return

    # Ask for confirmation
    response = input("\nProceed with replacement? (yes/no): ").strip().lower()

    if response not in ["yes", "y"]:
        print("Operation cancelled.")
        return

    # Actual replacement
    print("\n" + "=" * 70)
    print("REPLACING LINKS")
    print("=" * 70)

    success_count = 0
    for file_path, _ in modified_files:
        modified, occurrences = replace_links_in_file(
            file_path, OLD_LINK, NEW_LINK, dry_run=False
        )
        if modified:
            success_count += 1
            rel_path = file_path.relative_to(repo_path)
            print(f"✓ Updated {rel_path}")

    print("\n" + "=" * 70)
    print(f"✓ Successfully updated {success_count} file(s)!")
    print("=" * 70)
    print("\nDon't forget to:")
    print("1. Review the changes with 'git diff'")
    print("2. Test your documentation")
    print("3. Commit the changes")


if __name__ == "__main__":
    main()
