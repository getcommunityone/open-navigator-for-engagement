#!/bin/bash
# Extract Form 990 ZIPs for dev states - PARALLEL VERSION
# Uses parallel processing and optimized filtering for speed

set -eo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
DATA_DIR="${PROJECT_ROOT}/data/cache/form990"
ZIPS_DIR="${DATA_DIR}"
OUTPUT_DIR="${DATA_DIR}/xmls_dev_states"

# Dev states
DEV_STATES="WA|MA|AL|GA|WI"

# Parallel jobs (adjust based on CPU cores)
PARALLEL_JOBS=${PARALLEL_JOBS:-4}

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Fast Extract - Form 990 Dev States${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "${GREEN}States: WA, MA, AL, GA, WI${NC}"
echo -e "${YELLOW}Parallel jobs: $PARALLEL_JOBS${NC}"
echo -e "${BLUE}Output: $OUTPUT_DIR${NC}"
echo ""

# Create output directories
mkdir -p "$OUTPUT_DIR"
for state in WA MA AL GA WI; do
    mkdir -p "$OUTPUT_DIR/$state"
done

# Check for parallel or fallback to xargs
if command -v parallel &>/dev/null; then
    PARALLEL_CMD="parallel"
    echo -e "${GREEN}✓ Using GNU parallel${NC}"
elif command -v xargs &>/dev/null; then
    PARALLEL_CMD="xargs"
    echo -e "${YELLOW}⚠ Using xargs (slower than GNU parallel)${NC}"
else
    echo -e "${RED}Error: Need GNU parallel or xargs${NC}"
    exit 1
fi

# Function to process one ZIP
process_zip() {
    local zipfile="$1"
    local basename=$(basename "$zipfile")
    local temp_dir=$(mktemp -d)
    
    # Extract to temp
    if ! unzip -q -o "$zipfile" -d "$temp_dir" 2>/dev/null; then
        rm -rf "$temp_dir"
        echo "[$basename] Failed to extract"
        return 1
    fi
    
    local total_xmls=$(find "$temp_dir" -name "*.xml" -type f 2>/dev/null | wc -l)
    local kept=0
    
    # Find matching XMLs and copy them
    # Using grep -l to list files, then process each one
    if command -v rg &>/dev/null; then
        # Use ripgrep (faster)
        local matching_files=$(rg -l "<StateAbbreviationCd>(WA|MA|AL|GA|WI)</StateAbbreviationCd>" "$temp_dir" 2>/dev/null || true)
    else
        # Use grep (slower but more compatible)
        local matching_files=$(grep -rl "<StateAbbreviationCd>\(WA\|MA\|AL\|GA\|WI\)</StateAbbreviationCd>" "$temp_dir" 2>/dev/null || true)
    fi
    
    # Process each matching file
    if [ -n "$matching_files" ]; then
        while IFS= read -r xml; do
            [ -f "$xml" ] || continue
            
            # Extract state code - look for first match
            local state_code=$(grep -oE "<StateAbbreviationCd>(WA|MA|AL|GA|WI)</StateAbbreviationCd>" "$xml" 2>/dev/null | head -1 | sed 's/<[^>]*>//g')
            
            if [ -n "$state_code" ]; then
                local xmlname=$(basename "$xml")
                local dest="$OUTPUT_DIR/$state_code/$xmlname"
                
                # Copy if not already exists
                if [ ! -f "$dest" ]; then
                    cp "$xml" "$dest" 2>/dev/null && ((kept++))
                fi
            fi
        done <<< "$matching_files"
    fi
    
    # Cleanup
    rm -rf "$temp_dir"
    
    echo "[$basename] Total: $total_xmls | Kept: $kept"
    return 0
}

# Export function for parallel
export -f process_zip
export OUTPUT_DIR DEV_STATES

# Get list of ZIPs
mapfile -t ZIPS < <(find "$ZIPS_DIR" -maxdepth 1 -name "*.zip" -type f | sort)
ZIP_COUNT=${#ZIPS[@]}

if [ $ZIP_COUNT -eq 0 ]; then
    echo -e "${YELLOW}No ZIP files found${NC}"
    exit 1
fi

echo -e "${GREEN}Found $ZIP_COUNT ZIP files${NC}"
echo ""

# Process ZIPs in parallel
if [ "$PARALLEL_CMD" = "parallel" ]; then
    # GNU parallel (best performance)
    printf '%s\n' "${ZIPS[@]}" | parallel -j "$PARALLEL_JOBS" --bar process_zip
else
    # xargs fallback
    printf '%s\n' "${ZIPS[@]}" | xargs -P "$PARALLEL_JOBS" -I {} bash -c 'process_zip "$@"' _ {}
fi

# Final stats
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✅ Extraction Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

FINAL_COUNT=$(find "$OUTPUT_DIR" -name "*.xml" 2>/dev/null | wc -l)
FINAL_SIZE=$(du -sh "$OUTPUT_DIR" 2>/dev/null | cut -f1)

echo -e "${GREEN}Total XMLs:${NC} $FINAL_COUNT files ($FINAL_SIZE)"
echo ""
echo -e "${BLUE}XMLs per state:${NC}"
for state in WA MA AL GA WI; do
    count=$(find "$OUTPUT_DIR/$state" -name "*.xml" 2>/dev/null | wc -l)
    size=$(du -sh "$OUTPUT_DIR/$state" 2>/dev/null | cut -f1)
    echo -e "  ${GREEN}$state:${NC} $count files ($size)"
done
echo ""
echo -e "Next step: Build index of these XMLs"
echo -e "  ${BLUE}python scripts/build_990_local_index.py --xmls-dir $OUTPUT_DIR${NC}"
echo ""
