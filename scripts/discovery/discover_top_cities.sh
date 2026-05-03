#!/bin/bash
# Discover top N largest jurisdictions nationwide

set -e

cd /home/developer/projects/open-navigator
source .venv/bin/activate

# Default to top 100, can override with argument
TOP_N=${1:-100}

echo "=========================================="
echo "DISCOVERING TOP ${TOP_N} JURISDICTIONS"
echo "=========================================="
echo ""

python scripts/discovery/comprehensive_discovery_pipeline.py \
    --top ${TOP_N} \
    --youtube-api-key ${YOUTUBE_API_KEY} \
    --max-concurrent 5

echo ""
echo "=========================================="
echo "TOP ${TOP_N} JURISDICTIONS DISCOVERED!"
echo "=========================================="
echo ""
echo "Results saved to:"
echo "  - data/gold/jurisdictions_details.parquet (gold layer)"
echo "  - data/bronze/discovered_sources/ (detailed JSON)"
echo ""
