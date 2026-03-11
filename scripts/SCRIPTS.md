# Documentation Scripts

This folder contains scripts used for documentation portal maintenance and
historical migration (v3 → current structure).

## Overview

### Maintenance scripts

Ongoing scripts for keeping the documentation portal healthy.

### Migration scripts

Scripts used for the v3 → current structure migration (completed 2025-02-10).
Retained as an audit trail and reference for future restructures.

---

## Maintenance Scripts

### `generate_llms_txt.py`

Generates a structured `llms.txt` file at the repository root, overriding the
default auto-generated file produced by Mintlify.

**What it does:**

- Reads `docs.json` as the navigation source of truth
- Walks every leaf page path recursively, including nested API reference groups
- Reads `title` and `description` from each `.mdx` file's frontmatter
- For API endpoint pages (with an `openapi:` frontmatter field), looks up the
  operation `description` from the corresponding OAS YAML file when no
  frontmatter description is present
- Appends `(GET)` or `(POST)` to titles of endpoint pages whose slugs end in
  `-get` or `-post`, disambiguating twin variants
- Outputs a product-first, navigation-ordered `llms.txt` following the
  [llms.txt spec](https://llmstxt.org)
- Excludes legacy specs (`events-api`, `news-api-v2`) from the API
  Specifications section

**Usage:**

```bash
# Generate llms.txt at the repository root
python scripts/generate_llms_txt.py

# Specify a custom output path
python scripts/generate_llms_txt.py --output path/to/llms.txt

# Validate without writing (used in CI via npm run llms:generate + git diff)
python scripts/generate_llms_txt.py --check
```

**npm shortcut:**

```bash
npm run llms:generate
```

**Requirements:** Python 3.8+, `pyyaml` (`pip install pyyaml`)

**Exit codes:**

- `0` — File generated (or validated as up to date when `--check` is used)
- `1` — File is out of date (`--check` mode only)

**CI:** `.github/workflows/llms-txt.yml` runs this script on every PR and
fails if the committed `llms.txt` does not match the freshly generated output.

---

## Migration Scripts

**Status:** ✅ Migration complete (2025-02-10)

**Usage:** These scripts remain in the repository as:

- Documentation of the migration process
- Reference for future restructures
- Audit trail of changes made
- Training material for team members

---

### `restructure.sh`

Restructures file and folder organization.

**What it does:**

- Moves files from `v3/catch-all/` → `web-search-api/`
- Moves files from `v3/documentation/` + `v3/api-reference/` → `news-api/`
- Moves files from `v3/local-news/` → `local-news-api/`
- Creates timestamped backup automatically before changes
- Cleans up empty directories

**Usage:**

```bash
# Run from project root
./scripts/restructure.sh
```

**Safe to run:** Creates `backup-YYYYMMDD-HHMMSS/` before making any changes.

---

### `update_links.py`

Updates internal links in MDX and YAML files based on redirect map.

**What it does:**

- Finds all markdown links `[text](/docs/old-path)`
- Updates them to `[text](/docs/new-path)` using redirect-map.json
- Updates OpenAPI spec references in YAML files
- Supports dry-run mode for testing

**Usage:**

```bash
# Test without making changes
python scripts/update_links.py redirect-map.json --dry-run

# Apply updates
python scripts/update_links.py redirect-map.json
```

**Requirements:** Python 3.8+, redirect-map.json at project root

---

### `validate_redirects.py`

Validates redirect configuration against schema and best practices.

**What it checks:**

- ✅ Valid JSON syntax
- ✅ Matches JSON schema structure
- ✅ No duplicate source URLs
- ✅ No circular redirects (A→B→A)
- ✅ No long redirect chains (>3 hops)
- ✅ Source and destination format consistency

**Usage:**

```bash
python scripts/validate_redirects.py redirect-map.json --schema redirect-map.schema.json
```

**Exit codes:**

- `0` - All validations passed
- `1` - Validation errors found

---

### `export_redirects.py`

Exports redirect rules to various platform formats.

**Supported formats:**

- **mintlify** - `redirects.json` (for Mintlify projects)
- **cloudflare** - Cloudflare Page Rules
- **nginx** - Nginx configuration directives
- **apache** - `.htaccess` rules
- **vercel** - `vercel.json` format
- **netlify** - `_redirects` file
- **all** - Generates all formats at once

**Usage:**

```bash
# Export for Mintlify
python scripts/export_redirects.py redirect-map.json --format mintlify

# Export all formats
python scripts/export_redirects.py redirect-map.json --format all
```

**Output:** Creates files in `exported-redirects/` directory (at project root,
excluded from git).

---

## Configuration Files

### `redirect-map.json` (Project Root)

Master redirect mapping containing redirect rules.

**Structure:**

```json
{
  "redirects": [
    {
      "source": "/docs/v3/catch-all/overview/introduction",
      "destination": "/docs/web-search-api/get-started/introduction",
      "type": "permanent",
      "status_code": 301
    }
  ]
}
```

**Used by:** `update_links.py`, `export_redirects.py`, `validate_redirects.py`

---

### `redirect-map.schema.json` (Project Root)

JSON Schema for validating redirect-map.json structure.

**Usage:** Automatically used by `validate_redirects.py`

---

## Quick Start

### Regenerate llms.txt

```bash
npm run llms:generate
git add llms.txt
git commit -m "chore: regenerate llms.txt"
```

### Complete Migration Workflow (historical reference)

```bash
# 1. Validate redirect configuration
python scripts/validate_redirects.py redirect-map.json --schema redirect-map.schema.json

# 2. Restructure files (creates backup automatically)
./scripts/restructure.sh

# 3. Update internal links (test first!)
python scripts/update_links.py redirect-map.json --dry-run
python scripts/update_links.py redirect-map.json

# 4. Export redirects for deployment
python scripts/export_redirects.py redirect-map.json --format mintlify
```

---

## Requirements

### System Requirements

- **Bash** 4.0+ (for `restructure.sh`)
- **Python** 3.8+ (for Python scripts)
- **Git** (for version control and commits)

### Python Dependencies

| Script | Dependencies |
|--------|-------------|
| `generate_llms_txt.py` | `pyyaml` (external) |
| All migration scripts | stdlib only (`json`, `pathlib`, `re`, `argparse`, `datetime`, `shutil`) |

Install maintenance script dependencies:

```bash
pip install pyyaml
```

---

## Version History

| Date       | Version | Changes                                                  |
|------------|---------|----------------------------------------------------------|
| 2025-02-10 | 1.0.0   | Initial migration scripts created                        |
| 2025-02-10 | 1.1.0   | Scripts patched and moved to `scripts/` folder           |
| 2026-03-11 | 1.2.0   | Added `generate_llms_txt.py` maintenance script          |

---

**Last Updated:** 2026-03-11
**Scripts Location:** `docs/scripts/`