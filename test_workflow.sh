#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "Starting local workflow test..."

# Check if python is installed
if ! command -v python &> /dev/null; then
    echo -e "${RED}Python is not installed. Please install Python first.${NC}"
    exit 1
fi

# Check if required files exist
if [ ! -f "mint.json" ]; then
    echo -e "${RED}Error: mint.json not found in current directory${NC}"
    exit 1
fi

if [ ! -f "sitemap_generator.py" ]; then
    echo -e "${RED}Error: sitemap_generator.py not found in current directory${NC}"
    exit 1
fi

# Create a backup of existing sitemap.xml if it exists
if [ -f "sitemap.xml" ]; then
    cp sitemap.xml sitemap.xml.backup
    echo "Created backup of existing sitemap.xml"
fi

# Run the sitemap generator
echo "Running sitemap generator..."
python sitemap_generator.py

# Check if sitemap.xml was generated
if [ ! -f "sitemap.xml" ]; then
    echo -e "${RED}Error: sitemap.xml was not generated${NC}"
    exit 1
fi

# Validate XML format
if command -v xmllint &> /dev/null; then
    echo "Validating XML format..."
    if xmllint --noout sitemap.xml; then
        echo -e "${GREEN}XML validation passed${NC}"
    else
        echo -e "${RED}XML validation failed${NC}"
        # Restore backup if it exists
        if [ -f "sitemap.xml.backup" ]; then
            mv sitemap.xml.backup sitemap.xml
            echo "Restored original sitemap.xml"
        fi
        exit 1
    fi
else
    echo "xmllint not found - skipping XML validation"
fi

# Check if the generated sitemap has expected content
echo "Checking sitemap content..."
if grep -q "www.newscatcherapi.com" sitemap.xml; then
    echo -e "${GREEN}Found expected domain in sitemap${NC}"
else
    echo -e "${RED}Warning: Expected domain not found in sitemap${NC}"
fi

if grep -q "lastmod" sitemap.xml; then
    echo -e "${GREEN}Found lastmod tags${NC}"
else
    echo -e "${RED}Warning: lastmod tags not found${NC}"
fi

# Print first few lines of generated sitemap
echo -e "\nFirst few lines of generated sitemap:"
head -n 10 sitemap.xml

# Clean up backup if everything succeeded
if [ -f "sitemap.xml.backup" ]; then
    rm sitemap.xml.backup
    echo "Removed backup file"
fi

echo -e "\n${GREEN}Local test completed successfully!${NC}"