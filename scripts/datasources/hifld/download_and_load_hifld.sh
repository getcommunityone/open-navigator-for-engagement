#!/bin/bash
# Download and Load HIFLD Datasets to PostgreSQL
# 
# This script downloads HIFLD infrastructure data and loads it into
# the organizations_locations table in PostgreSQL.
#
# Usage: ./download_and_load_hifld.sh

set -e  # Exit on error

echo "========================================="
echo "HIFLD Data Download and Load Pipeline"
echo "========================================="
echo ""

# Activate virtual environment
source .venv/bin/activate

# Step 1: Download datasets (update Item IDs as you find them)
echo "Step 1: Downloading HIFLD datasets..."
echo ""

# Law Enforcement (verified Item ID)
echo "Downloading Law Enforcement locations..."
python scripts/datasources/hifld/download_arcgis_dataset.py \
  --item-id 333a74c8e9c64cb6870689d31e8836af \
  --to-parquet

# Places of Worship (need to find Item ID)
# TODO: Find Item ID at https://hifld-geoplatform.opendata.arcgis.com/
# echo "Downloading Places of Worship..."
# python scripts/datasources/hifld/download_arcgis_dataset.py \
#   --item-id PLACES_OF_WORSHIP_ITEM_ID \
#   --to-parquet

# Schools (need to find Item ID)
# TODO: Find Item ID at https://hifld-geoplatform.opendata.arcgis.com/
# echo "Downloading Schools..."
# python scripts/datasources/hifld/download_arcgis_dataset.py \
#   --item-id SCHOOLS_ITEM_ID \
#   --to-parquet

# Hospitals (need to find Item ID)
# TODO: Find Item ID at https://hifld-geoplatform.opendata.arcgis.com/
# echo "Downloading Hospitals..."
# python scripts/datasources/hifld/download_arcgis_dataset.py \
#   --item-id HOSPITALS_ITEM_ID \
#   --to-parquet

# Fire Stations (need to find Item ID)
# TODO: Find Item ID at https://hifld-geoplatform.opendata.arcgis.com/
# echo "Downloading Fire Stations..."
# python scripts/datasources/hifld/download_arcgis_dataset.py \
#   --item-id FIRE_STATIONS_ITEM_ID \
#   --to-parquet

echo ""
echo "Step 2: Loading data to PostgreSQL..."
echo ""

# Load all downloaded parquet files into organizations_locations table
python scripts/datasources/hifld/load_hifld_to_postgres.py

echo ""
echo "========================================="
echo "✅ HIFLD data pipeline complete!"
echo "========================================="
echo ""
echo "To find missing Item IDs:"
echo "1. Visit https://hifld-geoplatform.opendata.arcgis.com/"
echo "2. Search for dataset (e.g., 'hospitals', 'schools', 'places of worship')"
echo "3. Click on the dataset"
echo "4. Copy Item ID from URL"
echo "5. Update this script with the Item ID"
echo ""
