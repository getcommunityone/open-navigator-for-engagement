#!/bin/bash
# Clear Python cache and run gold table creation
# Usage: ./run_gold_tables.sh [--meetings-only|--nonprofits-only] [--states STATE1 STATE2 ...]

cd "$(dirname "$0")"

echo "🧹 Clearing Python cache..."
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete
echo "✅ Cache cleared"

echo ""
echo "🚀 Running gold table creation..."
source .venv/bin/activate
python scripts/create_all_gold_tables.py "$@"
