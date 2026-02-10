#!/bin/bash
# Documentation Restructure Script
# Run this script from the docs repository root

set -e  # Exit on error

echo "====================================="
echo "Documentation Restructure Script"
echo "====================================="
echo ""

# Safety check
if [ ! -f "docs.json" ]; then
    echo "ERROR: docs.json not found. Are you in the docs repository root?"
    exit 1
fi

echo "Creating backup..."
BACKUP_DIR="backup-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$BACKUP_DIR"
cp -r v3/ "$BACKUP_DIR/" 2>/dev/null || true
cp docs.json "$BACKUP_DIR/"
echo "✓ Backup created: $BACKUP_DIR"
echo ""

# =====================================
# Phase 1: Create new directory structure
# =====================================

echo "Phase 1: Creating new directory structure..."

# Home
mkdir -p home

# Web Search API (formerly CatchAll)
mkdir -p web-search-api/get-started
mkdir -p web-search-api/guides-and-concepts
mkdir -p web-search-api/how-to
mkdir -p web-search-api/api-reference/overview
mkdir -p web-search-api/api-reference/endpoints/jobs
mkdir -p web-search-api/api-reference/endpoints/monitors
mkdir -p web-search-api/api-reference/endpoints/meta
mkdir -p web-search-api/libraries
mkdir -p web-search-api/integrations

# News API
mkdir -p news-api/get-started
mkdir -p news-api/guides-and-concepts
mkdir -p news-api/how-to
mkdir -p news-api/troubleshooting
mkdir -p news-api/migration
mkdir -p news-api/api-reference/overview
mkdir -p news-api/api-reference/endpoints
mkdir -p news-api/libraries

# Local News API
mkdir -p local-news-api/get-started
mkdir -p local-news-api/guides-and-concepts
mkdir -p local-news-api/api-reference/overview
mkdir -p local-news-api/api-reference/endpoints

echo "✓ New directories created"
echo ""

# =====================================
# Phase 2: Move Web Search API files
# =====================================

echo "Phase 2: Moving Web Search API files..."

# Get started
mv v3/catch-all/overview/introduction.mdx web-search-api/get-started/introduction.mdx 2>/dev/null || true
mv v3/catch-all/overview/quickstart.mdx web-search-api/get-started/quickstart.mdx 2>/dev/null || true
mv v3/catch-all/overview/changelog.mdx web-search-api/get-started/changelog.mdx 2>/dev/null || true

# Guides and concepts
mv v3/catch-all/overview/monitors.mdx web-search-api/guides-and-concepts/monitors.mdx 2>/dev/null || true
mv v3/catch-all/overview/dynamic-schemas.mdx web-search-api/guides-and-concepts/dynamic-schemas.mdx 2>/dev/null || true

# How to
if [ -d "v3/catch-all/how-to" ]; then
    cp -r v3/catch-all/how-to/* web-search-api/how-to/ 2>/dev/null || true
    rm -rf v3/catch-all/how-to
fi

# API Reference - Endpoints
mv v3/catch-all/endpoints/initialize-job.mdx web-search-api/api-reference/endpoints/jobs/ 2>/dev/null || true
mv v3/catch-all/endpoints/create-job.mdx web-search-api/api-reference/endpoints/jobs/ 2>/dev/null || true
mv v3/catch-all/endpoints/continue-job.mdx web-search-api/api-reference/endpoints/jobs/ 2>/dev/null || true
mv v3/catch-all/endpoints/list-user-jobs.mdx web-search-api/api-reference/endpoints/jobs/ 2>/dev/null || true
mv v3/catch-all/endpoints/get-job-status.mdx web-search-api/api-reference/endpoints/jobs/ 2>/dev/null || true
mv v3/catch-all/endpoints/get-job-results.mdx web-search-api/api-reference/endpoints/jobs/ 2>/dev/null || true

mv v3/catch-all/endpoints/create-monitor.mdx web-search-api/api-reference/endpoints/monitors/ 2>/dev/null || true
mv v3/catch-all/endpoints/update-monitor.mdx web-search-api/api-reference/endpoints/monitors/ 2>/dev/null || true
mv v3/catch-all/endpoints/list-monitors.mdx web-search-api/api-reference/endpoints/monitors/ 2>/dev/null || true
mv v3/catch-all/endpoints/list-monitor-jobs.mdx web-search-api/api-reference/endpoints/monitors/ 2>/dev/null || true
mv v3/catch-all/endpoints/get-monitor-results.mdx web-search-api/api-reference/endpoints/monitors/ 2>/dev/null || true
mv v3/catch-all/endpoints/enable-monitor.mdx web-search-api/api-reference/endpoints/monitors/ 2>/dev/null || true
mv v3/catch-all/endpoints/disable-monitor.mdx web-search-api/api-reference/endpoints/monitors/ 2>/dev/null || true
mv v3/catch-all/endpoints/webhook-payload.mdx web-search-api/api-reference/endpoints/monitors/ 2>/dev/null || true

mv v3/catch-all/endpoints/health.mdx web-search-api/api-reference/endpoints/meta/ 2>/dev/null || true
mv v3/catch-all/endpoints/version.mdx web-search-api/api-reference/endpoints/meta/ 2>/dev/null || true

# Libraries
if [ -d "v3/catch-all/libraries" ]; then
    cp -r v3/catch-all/libraries/* web-search-api/libraries/ 2>/dev/null || true
    rm -rf v3/catch-all/libraries
fi

# Integrations
if [ -d "v3/catch-all/integrations" ]; then
    cp -r v3/catch-all/integrations/* web-search-api/integrations/ 2>/dev/null || true
    rm -rf v3/catch-all/integrations
fi

echo "✓ Web Search API files moved"
echo ""

# =====================================
# Phase 3: Move News API files
# =====================================

echo "Phase 3: Moving News API files..."

# Get started
if [ -d "v3/documentation/get-started" ]; then
    cp -r v3/documentation/get-started/* news-api/get-started/ 2>/dev/null || true
    rm -rf v3/documentation/get-started
fi

# Guides and concepts
if [ -d "v3/documentation/guides-and-concepts" ]; then
    cp -r v3/documentation/guides-and-concepts/* news-api/guides-and-concepts/ 2>/dev/null || true
    rm -rf v3/documentation/guides-and-concepts
fi

# How to
if [ -d "v3/documentation/how-to" ]; then
    cp -r v3/documentation/how-to/* news-api/how-to/ 2>/dev/null || true
    rm -rf v3/documentation/how-to
fi

# Troubleshooting
if [ -d "v3/documentation/troubleshooting" ]; then
    cp -r v3/documentation/troubleshooting/* news-api/troubleshooting/ 2>/dev/null || true
    rm -rf v3/documentation/troubleshooting
fi

# Migration
if [ -d "v3/documentation/migration" ]; then
    cp -r v3/documentation/migration/* news-api/migration/ 2>/dev/null || true
    rm -rf v3/documentation/migration
fi

# API Reference - Overview
if [ -d "v3/api-reference/overview" ]; then
    cp -r v3/api-reference/overview/* news-api/api-reference/overview/ 2>/dev/null || true
    rm -rf v3/api-reference/overview
fi

# API Reference - Endpoints
if [ -d "v3/api-reference/endpoints" ]; then
    cp -r v3/api-reference/endpoints/* news-api/api-reference/endpoints/ 2>/dev/null || true
    rm -rf v3/api-reference/endpoints
fi

# Libraries
if [ -d "v3/api-reference/libraries" ]; then
    cp -r v3/api-reference/libraries/* news-api/libraries/ 2>/dev/null || true
    rm -rf v3/api-reference/libraries
fi

echo "✓ News API files moved"
echo ""

# =====================================
# Phase 4: Move Local News API files
# =====================================

echo "Phase 4: Moving Local News API files..."

# Get started (from overview)
mv v3/local-news/overview/introduction.mdx local-news-api/get-started/introduction.mdx 2>/dev/null || true
mv v3/local-news/overview/quickstart.mdx local-news-api/get-started/quickstart.mdx 2>/dev/null || true
mv v3/local-news/overview/local-news-api-subscription-plans.mdx local-news-api/get-started/subscription-plans.mdx 2>/dev/null || true

# Guides and concepts (from overview)
mv v3/local-news/overview/location-detection-methods.mdx local-news-api/guides-and-concepts/location-detection-methods.mdx 2>/dev/null || true
mv v3/local-news/overview/geonames-filtering.mdx local-news-api/guides-and-concepts/geonames-filtering.mdx 2>/dev/null || true

# API Reference - Endpoints
if [ -d "v3/local-news/endpoints" ]; then
    cp -r v3/local-news/endpoints/* local-news-api/api-reference/endpoints/ 2>/dev/null || true
    rm -rf v3/local-news/endpoints
fi

echo "✓ Local News API files moved"
echo ""

# =====================================
# Phase 5: Cleanup
# =====================================

echo "Phase 5: Cleanup..."

# Remove empty v3 directories
find v3/ -type d -empty -delete 2>/dev/null || true

echo "✓ Empty directories cleaned"
echo ""

# =====================================
# Summary
# =====================================

echo "====================================="
echo "Restructure Complete!"
echo "====================================="
echo ""
echo "Next steps:"
echo "1. Review the changes: git status"
echo "2. Update docs.json navigation"
echo "3. Update internal links in .mdx files"
echo "4. Test locally: mint dev"
echo "5. Commit changes to feature branch"
echo ""
echo "Backup location: $BACKUP_DIR"
echo ""
echo "If something went wrong, restore with:"
echo "  rm -rf web-search-api news-api local-news-api home"
echo "  cp -r $BACKUP_DIR/v3 ."
echo "  cp $BACKUP_DIR/docs.json ."
echo ""
