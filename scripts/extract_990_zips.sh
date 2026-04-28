#!/bin/bash
# Extract all Form 990 ZIPs in parallel
# ~95 GB uncompressed, ~384K XML files

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
DATA_DIR="${PROJECT_ROOT}/data/form990"
ZIPS_DIR="${DATA_DIR}/zips"
XMLS_DIR="${DATA_DIR}/xmls"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Extract Form 990 ZIPs${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check if ZIPs exist
if [ ! -d "$ZIPS_DIR" ] || [ -z "$(ls -A "$ZIPS_DIR"/*.zip 2>/dev/null)" ]; then
    echo -e "${YELLOW}⚠️  No ZIP files found in $ZIPS_DIR${NC}"
    echo -e "Run: ${BLUE}./scripts/download_990_zips.sh${NC}"
    exit 1
fi

# Create XML directory
mkdir -p "$XMLS_DIR"

ZIP_COUNT=$(ls -1 "$ZIPS_DIR"/*.zip 2>/dev/null | wc -l)
echo -e "${GREEN}Found $ZIP_COUNT ZIP files${NC}"
echo -e "${YELLOW}⏱️  Estimated time: 1-2 hours${NC}"
echo ""

# Check if parallel is installed
if command -v parallel &> /dev/null; then
    echo -e "${GREEN}Using GNU parallel for extraction...${NC}"
    echo ""
    
    # Extract in parallel (use all cores)
    find "$ZIPS_DIR" -name "*.zip" | parallel -j+0 --bar \
        'unzip -q -o {} -d '"$XMLS_DIR"' && echo "✓ Extracted {/}"'
else
    echo -e "${YELLOW}GNU parallel not found. Installing or using sequential extraction...${NC}"
    
    # Try to install parallel
    if command -v apt-get &> /dev/null; then
        echo "Installing parallel..."
        sudo apt-get update && sudo apt-get install -y parallel
    elif command -v brew &> /dev/null; then
        echo "Installing parallel..."
        brew install parallel
    else
        echo "Extracting sequentially (slower)..."
        for zipfile in "$ZIPS_DIR"/*.zip; do
            echo "Extracting $(basename "$zipfile")..."
            unzip -q -o "$zipfile" -d "$XMLS_DIR"
            echo "✓ Extracted $(basename "$zipfile")"
        done
    fi
fi

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✅ Extraction Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Count XMLs
XML_COUNT=$(find "$XMLS_DIR" -name "*.xml" | wc -l)
echo -e "Extracted: ${BLUE}$XML_COUNT${NC} XML files"
echo -e "Location:  ${BLUE}$XMLS_DIR${NC}"
echo ""

# Calculate size
TOTAL_SIZE=$(du -sh "$XMLS_DIR" | cut -f1)
echo -e "Total size: ${BLUE}$TOTAL_SIZE${NC}"
echo ""

echo -e "Next steps:"
echo -e "  1. Build local index:   ${BLUE}python scripts/build_990_local_index.py${NC}"
echo -e "  2. Enrich all states:   ${BLUE}python scripts/enrich_all_states_990.py${NC}"
echo ""
