# Documentation Migration Scripts

This folder contains scripts and configuration files used for the documentation portal restructure (v3 → new structure).

## Overview

**Purpose:** Automate the migration of documentation from the `v3/` structure to the new flat structure without URL prefixes.

**Status:** ✅ Migration complete (2025-02-10)

**Usage:** These scripts remain in the repository as:

- Documentation of the migration process
- Reference for future restructures  
- Audit trail of changes made
- Training material for team members

---

## Files

### Core Scripts

#### `restructure.sh`

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

#### `update_links.py`

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

#### `validate_redirects.py`

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

#### `export_redirects.py`

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

**Output:** Creates files in `exported-redirects/` directory.

---

## Configuration Files

### `redirect-map.json` (Project Root)

Master redirect mapping containing redirect rules.

**Purpose:** Single source of truth for all URL changes during migration.

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

**Used by:**

- `update_links.py` - Updates internal links
- `export_redirects.py` - Generates platform-specific redirects
- `validate_redirects.py` - Validates structure

---

### `redirect-map.schema.json` (Project Root)

JSON Schema for validating redirect-map.json structure.

**Validates:**

- Required fields (source, destination, permanent)
- Data types (strings, booleans)
- URL format patterns
- Array structure

**Usage:** Automatically used by `validate_redirects.py`

---

## Quick Start

### Complete Migration Workflow

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

### For Future Migrations

If you need to do similar restructuring:

1. Create new `redirect-map.json` with your mappings
2. Validate with `validate_redirects.py`
3. Adapt `restructure.sh` for your new structure
4. Use `update_links.py` to update internal links
5. Export redirects with `export_redirects.py`

---

## Requirements

### System Requirements

- **Bash** 4.0+ (for `restructure.sh`)
- **Python** 3.8+ (for Python scripts)
- **Git** (for version control and commits)

### Python Dependencies

All scripts use Python standard library only:

- `json` - JSON parsing
- `pathlib` - Path manipulation
- `re` - Regular expressions
- `argparse` - Command-line parsing
- `datetime` - Timestamps
- `shutil` - File operations

No external packages required - ready to run.

---

## Safety Features

### Built-in Protections

✅ **Automatic Backups**

- `restructure.sh` creates timestamped backup before changes
- Located at `backup-YYYYMMDD-HHMMSS/`

✅ **Dry-Run Mode**

- `update_links.py --dry-run` shows changes without applying them
- Preview exactly what will be modified

✅ **Validation Before Changes**

- `validate_redirects.py` catches errors before migration
- Prevents invalid configurations

---

## Files Created/Modified During Migration

### New Directories Created

```
docs/
├── docs.json
├── home/
│   └── index.mdx
├── web-search-api/
│   ├── get-started/
│   ├── guides-and-concepts/
│   ├── how-to/
│   ├── api-reference/
│   │   ├── overview/
│   │   └── endpoints/
│   ├── libraries/
│   └── integrations/
├── news-api/
│   ├── get-started/
│   ├── guides-and-concepts/
│   ├── how-to/
│   ├── troubleshooting/
│   ├── migration/
│   ├── api-reference/
│   │   ├── overview/
│   │   └── endpoints/
│   └── libraries/
├── local-news-api/
│   ├── get-started/
│   ├── guides-and-concepts/
│   └── api-reference/
│       ├── overview/
│       └── endpoints/
│
└── backup-YYYYMMDD-HHMMSS/  # Safety backup (local)
    ├── docs.json
    └── v3/
```

### Modified Files

- `docs.json` - Complete navigation restructure
- All `md`, `.mdx` files with internal links
- All `yml`,`.yaml` files with OpenAPI references

### Preserved Structure

- `v3/events-api/` - Kept unchanged (not part of migration)
- `logos/` - Kept unchanged
- Root configuration files - Kept unchanged (backup added to .gitignore)

---

## Version History

| Date       | Version | Changes                                        |
|------------|---------|------------------------------------------------|
| 2025-02-10 | 1.0.0   | Initial migration scripts created              |
| 2025-02-10 | 1.1.0   | Scripts patched and moved to `scripts/` folder |

---

**Last Updated:** 2025-02-10  
**Migration Status:** ✅ Complete  
**Scripts Location:** `docs/scripts/`