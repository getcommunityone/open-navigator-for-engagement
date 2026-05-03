#!/bin/bash
# Discover all jurisdictions in oral health focus states
# States: AL, GA, IN, MA, WA, WI

set -e

cd /home/developer/projects/open-navigator
source .venv/bin/activate

echo "=========================================="
echo "DISCOVERING ORAL HEALTH FOCUS STATES"
echo "=========================================="
echo ""

STATES=("AL" "GA" "IN" "MA" "WA" "WI")

for STATE in "${STATES[@]}"; do
    echo "=========================================="
    echo "Discovering ${STATE}..."
    echo "=========================================="
    
    python scripts/discovery/comprehensive_discovery_pipeline.py \
        --state ${STATE} \
        --youtube-api-key ${YOUTUBE_API_KEY} \
        --max-concurrent 5
    
    echo ""
    echo "✅ ${STATE} complete!"
    echo ""
    
    # Small delay between states to avoid rate limits
    sleep 5
done

echo "=========================================="
echo "ALL ORAL HEALTH STATES DISCOVERED!"
echo "=========================================="
echo ""
echo "Results saved to:"
echo "  - data/gold/jurisdictions_details.parquet (gold layer)"
echo "  - data/bronze/discovered_sources/ (detailed JSON)"
echo ""
