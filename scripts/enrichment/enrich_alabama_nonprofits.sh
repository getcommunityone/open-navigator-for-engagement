#!/bin/bash
# Enrich Alabama nonprofits with contact information and grants data

set -e  # Exit on error

source .venv/bin/activate

echo "🏛️  Enriching Alabama Nonprofits"
echo "================================"
echo ""

# Step 1: Add officer contact information from GT990 API
echo "📇 Step 1: Adding officer contact information..."
python scripts/enrich_nonprofits_gt990.py \
  --input data/gold/states/AL/nonprofits_organizations.parquet \
  --output data/gold/states/AL/nonprofits_organizations.parquet \
  --concurrent 10

echo ""
echo "✅ COMPLETE!"
echo ""
echo "📊 Updated files:"
ls -lh data/gold/states/AL/nonprofits_organizations.parquet

echo ""
echo "📈 To verify enrichment:"
echo "python -c \"import pandas as pd; df = pd.read_parquet('data/gold/states/AL/nonprofits_organizations.parquet'); print('Total orgs:', len(df)); print('Columns:', df.columns.tolist())\""
