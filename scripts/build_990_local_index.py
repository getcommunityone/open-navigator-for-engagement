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
XMLS_DIR = PROJECT_ROOT / "data" / "cache" / "form990" / "xmls_dev_states"
INDEX_FILE = PROJECT_ROOT / "data" / "cache" / "form990" / "local_index_dev_states.parquet"


def extract_metadata_from_xml(xml_path: Path) -> Optional[Dict[str, str]]:
    """
    Extract key metadata from Form 990 XML.
    
    Returns:
        Dict with: EIN, org_name, tax_year, form_type, object_id, state
    """
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
        
        # Helper function to find element ignoring namespace
        def find_elem(tag_name: str):
            # Try with namespace first
            ns_match = re.match(r'\{(.+)\}', root.tag)
            if ns_match:
                ns = {'irs': ns_match.group(1)}
                elem = root.find(f'.//irs:{tag_name}', ns)
                if elem is not None:
                    return elem
            
            # Try without namespace
            elem = root.find(f'.//{tag_name}')
            if elem is not None:
                return elem
            
            # Try searching by tag name (ignoring namespace)
            for elem in root.iter():
                if elem.tag.endswith('}' + tag_name) or elem.tag == tag_name:
                    return elem
            return None
        
        # Extract EIN
        ein_elem = find_elem('EIN')
        ein = ein_elem.text.strip() if ein_elem is not None and ein_elem.text else None
        
        # Extract org name (try multiple possible tag names)
        org_name = None
        for tag in ['BusinessNameLine1Txt', 'BusinessNameLine1']:
            name_elem = find_elem(tag)
            if name_elem is not None and name_elem.text:
                org_name = name_elem.text.strip()
                break
        
        # Extract tax year
        year_elem = find_elem('TaxYr')
        tax_year = None
        if year_elem is not None and year_elem.text:
            try:
                tax_year = int(year_elem.text.strip())
            except ValueError:
                pass
        
        # Extract state
        state_elem = find_elem('StateAbbreviationCd')
        state = state_elem.text.strip() if state_elem is not None and state_elem.text else None
        
        # Fallback: Get state from parent directory
        if not state and xml_path.parent.name in ['WA', 'MA', 'AL', 'GA', 'WI']:
            state = xml_path.parent.name
        
        # Determine form type from root element
        form_type = None
        root_tag = root.tag.split('}')[-1]  # Remove namespace
        if 'Return990PF' in root_tag:
            form_type = '990-PF'
        elif 'Return990EZ' in root_tag:
            form_type = '990-EZ'
        elif 'Return990' in root_tag:
            form_type = '990'
        
        # Extract ObjectId from filename
        object_id = xml_path.stem.replace('_public', '')
        
        if not ein:
            return None
            
        return {
            'ein': ein,
            'org_name': org_name,
            'tax_year': tax_year,
            'state': state,
            'form_type': form_type,
            'object_id': object_id,
            'file_path': str(xml_path.relative_to(PROJECT_ROOT)),
            'file_size_mb': xml_path.stat().st_size / (1024 * 1024)
        }
        
    except Exception as e:
        # Only print errors if verbose mode (skip for now to reduce noise)
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
    
    # Find all XML files (in state subdirectories)
    print(f"📁 Scanning {XMLS_DIR}...")
    xml_files = []
    for state_dir in XMLS_DIR.glob('*'):
        if state_dir.is_dir():
            state_xmls = list(state_dir.glob("*.xml"))
            print(f"  {state_dir.name}: {len(state_xmls):,} XMLs")
            xml_files.extend(state_xmls)
    
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
    
    # Sort by EIN and tax year (most recent first)
    df = df.sort_values(['ein', 'tax_year'], ascending=[True, False])
    
    # Summary stats
    print("📊 Index Statistics:")
    print(f"  Total filings:        {len(df):,}")
    print(f"  Unique EINs:          {df['ein'].nunique():,}")
    print(f"  Tax years:            {df['tax_year'].min():.0f} - {df['tax_year'].max():.0f}")
    
    if 'state' in df.columns and df['state'].notna().any():
        print(f"  States:")
        for state, count in df['state'].value_counts().items():
            print(f"    - {state}: {count:,}")
    
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
