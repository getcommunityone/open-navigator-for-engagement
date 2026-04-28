#!/usr/bin/env python3
"""
Build local index of Form 990 XMLs after extracting ZIPs.

Creates a parquet index mapping EIN → local file paths for fast lookup.
Also extracts key metadata (org name, tax year, form type) from filenames and quick XML parse.
"""

import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Optional
import pandas as pd
from concurrent.futures import ProcessPoolExecutor, as_completed
from tqdm import tqdm

PROJECT_ROOT = Path(__file__).parent.parent
XMLS_DIR = PROJECT_ROOT / "data" / "form990" / "xmls"
INDEX_FILE = PROJECT_ROOT / "data" / "form990" / "local_index.parquet"


def extract_metadata_from_xml(xml_path: Path) -> Optional[Dict[str, str]]:
    """
    Extract key metadata from Form 990 XML.
    
    Returns:
        Dict with: EIN, org_name, tax_year, form_type, object_id
    """
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
        
        # Handle namespace (IRS uses different namespaces by year)
        ns_match = re.match(r'\{(.+)\}', root.tag)
        ns = {'irs': ns_match.group(1)} if ns_match else {}
        
        # Extract EIN
        ein_elem = (root.find('.//irs:EIN', ns) or 
                   root.find('.//EIN') or
                   root.find('.//*[local-name()="EIN"]'))
        ein = ein_elem.text if ein_elem is not None else None
        
        # Extract org name
        name_elem = (root.find('.//irs:BusinessName/irs:BusinessNameLine1Txt', ns) or
                    root.find('.//irs:Filer/irs:BusinessName/irs:BusinessNameLine1', ns) or
                    root.find('.//*[local-name()="BusinessNameLine1Txt"]') or
                    root.find('.//*[local-name()="BusinessNameLine1"]'))
        org_name = name_elem.text if name_elem is not None else None
        
        # Extract tax year
        year_elem = (root.find('.//irs:TaxYr', ns) or
                    root.find('.//*[local-name()="TaxYr"]'))
        tax_year = int(year_elem.text) if year_elem is not None else None
        
        # Determine form type from root element
        form_type = None
        if 'Return990' in root.tag:
            form_type = '990'
        elif 'Return990EZ' in root.tag:
            form_type = '990-EZ'
        elif 'Return990PF' in root.tag:
            form_type = '990-PF'
        
        # Extract ObjectId from filename
        object_id = xml_path.stem.replace('_public', '')
        
        if not ein:
            return None
            
        return {
            'ein': ein,
            'org_name': org_name,
            'tax_year': tax_year,
            'form_type': form_type,
            'object_id': object_id,
            'file_path': str(xml_path.relative_to(PROJECT_ROOT)),
            'file_size_mb': xml_path.stat().st_size / (1024 * 1024)
        }
        
    except Exception as e:
        print(f"Error parsing {xml_path.name}: {e}")
        return None


def process_batch(xml_files: List[Path]) -> List[Dict]:
    """Process a batch of XML files."""
    results = []
    for xml_file in xml_files:
        metadata = extract_metadata_from_xml(xml_file)
        if metadata:
            results.append(metadata)
    return results


def main():
    print("=" * 80)
    print("Building Local Form 990 Index")
    print("=" * 80)
    print()
    
    if not XMLS_DIR.exists():
        print(f"❌ XMLs directory not found: {XMLS_DIR}")
        print(f"Run: ./scripts/download_990_zips.sh && ./scripts/extract_990_zips.sh")
        return 1
    
    # Find all XML files
    print(f"📁 Scanning {XMLS_DIR}...")
    xml_files = list(XMLS_DIR.glob("*.xml"))
    total_files = len(xml_files)
    
    if total_files == 0:
        print(f"❌ No XML files found in {XMLS_DIR}")
        print(f"Run: ./scripts/extract_990_zips.sh")
        return 1
    
    print(f"Found {total_files:,} XML files")
    print()
    
    # Process in parallel with progress bar
    print("⚙️  Extracting metadata from XMLs...")
    batch_size = 1000
    batches = [xml_files[i:i+batch_size] for i in range(0, total_files, batch_size)]
    
    all_results = []
    with ProcessPoolExecutor(max_workers=8) as executor:
        futures = [executor.submit(process_batch, batch) for batch in batches]
        
        with tqdm(total=total_files, desc="Processing") as pbar:
            for future in as_completed(futures):
                batch_results = future.result()
                all_results.extend(batch_results)
                pbar.update(len(batch_results))
    
    print(f"✓ Extracted metadata from {len(all_results):,} files")
    print()
    
    # Create DataFrame
    df = pd.DataFrame(all_results)
    
    # Add state column (will be populated during enrichment)
    df['state'] = None
    
    # Sort by EIN and tax year (most recent first)
    df = df.sort_values(['ein', 'tax_year'], ascending=[True, False])
    
    # Summary stats
    print("📊 Index Statistics:")
    print(f"  Total filings:        {len(df):,}")
    print(f"  Unique EINs:          {df['ein'].nunique():,}")
    print(f"  Tax years:            {df['tax_year'].min():.0f} - {df['tax_year'].max():.0f}")
    print(f"  Form types:")
    for form_type, count in df['form_type'].value_counts().items():
        print(f"    - {form_type}: {count:,}")
    print(f"  Total size:           {df['file_size_mb'].sum() / 1024:.1f} GB")
    print()
    
    # Save to parquet
    print(f"💾 Saving index to {INDEX_FILE}...")
    INDEX_FILE.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(INDEX_FILE, index=False)
    
    print(f"✅ Index saved: {INDEX_FILE}")
    print(f"   Size: {INDEX_FILE.stat().st_size / (1024 * 1024):.1f} MB")
    print()
    
    print("=" * 80)
    print("✅ Index Build Complete!")
    print("=" * 80)
    print()
    print("Usage example:")
    print()
    print("  import pandas as pd")
    print(f"  df = pd.read_parquet('{INDEX_FILE}')")
    print("  ")
    print("  # Find all filings for an EIN")
    print("  ein = '043726335'")
    print("  filings = df[df['ein'] == ein]")
    print("  ")
    print("  # Get most recent filing")
    print("  latest = filings.iloc[0]")
    print("  xml_path = latest['file_path']")
    print()
    
    return 0


if __name__ == '__main__':
    exit(main())
