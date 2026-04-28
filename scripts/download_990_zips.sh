#!/bin/bash
# Download all Form 990 ZIPs from GivingTuesday S3 bucket
# This downloads ~38 GB compressed → ~95 GB uncompressed
# Contains ~384K Form 990 XMLs (nationwide, 2017-2023)

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
echo -e "${BLUE}GivingTuesday 990 ZIP Download${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Create directories
echo -e "${GREEN}📁 Creating directories...${NC}"
mkdir -p "$ZIPS_DIR"
mkdir -p "$XMLS_DIR"

# Check if we have the index
INDEX_FILE="${DATA_DIR}/cache/form990_gt_index.parquet"
if [ ! -f "$INDEX_FILE" ]; then
    echo -e "${YELLOW}⚠️  Form 990 index not found. Download it first:${NC}"
    echo ""
    echo "  python3 << 'EOF'"
    echo "  import boto3"
    echo "  from botocore import UNSIGNED"
    echo "  from botocore.config import Config"
    echo "  "
    echo "  s3 = boto3.client('s3', config=Config(signature_version=UNSIGNED))"
    echo "  s3.download_file("
    echo "      'gt990datalake-rawdata',"
    echo "      'Indices/990xmls/index_all_years_efiledata_xmls_created_on_2023-10-29.csv',"
    echo "      '${INDEX_FILE%.parquet}.csv'"
    echo "  )"
    echo "  EOF"
    echo ""
    echo "  # Convert to parquet"
    echo "  python3 -c \"import pandas as pd; pd.read_csv('${INDEX_FILE%.parquet}.csv').to_parquet('${INDEX_FILE}')\""
    echo ""
fi

# Download ZIPs using Python with progress
echo -e "${GREEN}📦 Downloading 97 ZIP files (~38 GB compressed)...${NC}"
echo -e "${YELLOW}⏱️  Estimated time: 1-4 hours depending on bandwidth${NC}"
echo ""

python3 << 'EOF'
import boto3
from botocore import UNSIGNED
from botocore.config import Config
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import os

s3 = boto3.client('s3', config=Config(signature_version=UNSIGNED))
bucket = 'gt990datalake-rawdata'
prefix = 'EfileData/XmlZips/'

# List all ZIPs
response = s3.list_objects_v2(Bucket=bucket, Prefix=prefix)
zips = [obj['Key'] for obj in response.get('Contents', []) if obj['Key'].endswith('.zip')]

print(f"Found {len(zips)} ZIP files")
print("")

zips_dir = Path(os.environ['ZIPS_DIR'])

def download_zip(key):
    filename = Path(key).name
    local_path = zips_dir / filename
    
    if local_path.exists():
        size_mb = local_path.stat().st_size / (1024 * 1024)
        print(f"✓ Skip {filename} (already exists, {size_mb:.1f} MB)")
        return filename, True
    
    try:
        s3.download_file(bucket, key, str(local_path))
        size_mb = local_path.stat().st_size / (1024 * 1024)
        print(f"✓ Downloaded {filename} ({size_mb:.1f} MB)")
        return filename, True
    except Exception as e:
        print(f"✗ Failed {filename}: {e}")
        return filename, False

# Download in parallel (10 concurrent)
with ThreadPoolExecutor(max_workers=10) as executor:
    futures = [executor.submit(download_zip, key) for key in zips]
    
    completed = 0
    for future in as_completed(futures):
        completed += 1
        filename, success = future.result()
        if completed % 10 == 0:
            print(f"\n[{completed}/{len(zips)}] Progress: {completed/len(zips)*100:.0f}%\n")

print("")
print(f"✅ Downloaded {completed} ZIP files to {zips_dir}")
EOF

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✅ Download Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "Next steps:"
echo -e "  1. Extract ZIPs:    ${BLUE}./scripts/extract_990_zips.sh${NC}"
echo -e "  2. Build index:     ${BLUE}python scripts/build_990_local_index.py${NC}"
echo -e "  3. Enrich orgs:     ${BLUE}python scripts/enrich_all_states_990.py${NC}"
echo ""
echo -e "Storage locations:"
echo -e "  ZIPs:      ${ZIPS_DIR}"
echo -e "  XMLs:      ${XMLS_DIR} (after extraction)"
echo ""
