#!/usr/bin/env python3
"""
Cleanup old nonprofit files and consolidate into single unified file.

This script:
1. Identifies old/redundant nonprofit data files
2. Merges any enrichment data into the main file
3. Archives or deletes old files
4. Leaves only data/gold/nonprofits_organizations.parquet
"""

import shutil
from pathlib import Path

import pandas as pd
from loguru import logger

# Main file to keep
MAIN_FILE = Path("data/gold/nonprofits_organizations.parquet")

# Files to check and potentially merge
OLD_FILES = [
    "data/gold/nonprofits_tuscaloosa.parquet",
    "data/gold/nonprofits_tuscaloosa_form990.parquet",
    "data/gold/nonprofits_tuscaloosa_enriched.parquet",
    "data/gold/nonprofits_990_enriched.parquet",
    "data/gold/nonprofits_organizations_enriched.parquet",
    "data/gold/nonprofits_organizations_everyorg.parquet",
    "data/gold/nonprofits_organizations_sample.parquet",
]

# Temp files to delete
TEMP_PATTERNS = [
    "/tmp/test_*.parquet",
    "/tmp/*_enrichment.parquet",
]


def find_files():
    """Find all old nonprofit files."""
    files_found = []
    files_seen = set()
    
    # Check specific old files
    for file_path in OLD_FILES:
        p = Path(file_path)
        if p.exists() and str(p) not in files_seen:
            files_found.append(p)
            files_seen.add(str(p))
    
    # Check temp patterns
    import glob
    for pattern in TEMP_PATTERNS:
        for file in glob.glob(pattern):
            p = Path(file)
            if p.exists() and str(p) not in files_seen:
                files_found.append(p)
                files_seen.add(str(p))
    
    return files_found


def merge_enrichment_data():
    """Merge enrichment data from old files into main file."""
    logger.info(f"📂 Loading main file: {MAIN_FILE}")
    
    if not MAIN_FILE.exists():
        logger.error(f"❌ Main file not found: {MAIN_FILE}")
        return
    
    df_main = pd.read_parquet(MAIN_FILE)
    logger.info(f"   Main file: {len(df_main):,} nonprofits")
    
    updated = False
    
    # Check Tuscaloosa Form 990 file
    tusc_990 = Path("data/gold/nonprofits_tuscaloosa_form990.parquet")
    if tusc_990.exists():
        logger.info(f"\n🔄 Found enriched data: {tusc_990}")
        df_tusc = pd.read_parquet(tusc_990)
        
        # Get enriched columns
        form_990_cols = [col for col in df_tusc.columns if col.startswith('form_990_')]
        
        if form_990_cols:
            logger.info(f"   Found {len(form_990_cols)} Form 990 columns")
            logger.info(f"   Enriched: {len(df_tusc):,} Tuscaloosa nonprofits")
            
            # Remove old enrichment for these EINs from main file
            eins = df_tusc['ein'].values
            df_main = df_main[~df_main['ein'].isin(eins)]
            
            # Append enriched data
            df_main = pd.concat([df_main, df_tusc], ignore_index=True)
            df_main = df_main.sort_values('ein').reset_index(drop=True)
            
            logger.success(f"   ✅ Merged {len(df_tusc):,} enriched organizations")
            updated = True
    
    if updated:
        # Save updated main file
        logger.info(f"\n💾 Saving updated main file...")
        df_main.to_parquet(MAIN_FILE, index=False)
        logger.success(f"✅ Saved {len(df_main):,} nonprofits to {MAIN_FILE}")
    else:
        logger.info(f"\n✓ No enrichment data to merge")


def cleanup_files(dry_run=True):
    """Remove old files."""
    files = find_files()
    
    if not files:
        logger.info("✓ No old files to clean up")
        return
    
    logger.info(f"\n🗑️  Found {len(files)} file(s) to clean up:")
    
    total_size = 0
    for file in files:
        size = file.stat().st_size / (1024 * 1024)  # MB
        total_size += size
        logger.info(f"   - {file} ({size:.1f} MB)")
    
    logger.info(f"\n   Total size: {total_size:.1f} MB")
    
    if dry_run:
        logger.warning("\n⚠️  DRY RUN - No files will be deleted")
        logger.info("   Run with --execute to actually delete files")
    else:
        confirm = input(f"\n❓ Delete {len(files)} file(s)? [y/N]: ")
        if confirm.lower() != 'y':
            logger.info("Aborted.")
            return
        
        for file in files:
            try:
                if file.exists():  # Check again before deleting
                    logger.info(f"   Deleting: {file}")
                    file.unlink()
            except Exception as e:
                logger.warning(f"   ⚠️  Could not delete {file}: {e}")
        
        logger.success(f"✅ Cleanup complete, freed {total_size:.1f} MB")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Cleanup and consolidate nonprofit data files"
    )
    parser.add_argument('--execute', action='store_true', 
                        help='Actually delete files (default is dry run)')
    parser.add_argument('--skip-merge', action='store_true',
                        help='Skip merging enrichment data')
    
    args = parser.parse_args()
    
    logger.info("=" * 70)
    logger.info("NONPROFIT DATA CONSOLIDATION")
    logger.info("=" * 70)
    
    # Step 1: Merge enrichment data
    if not args.skip_merge:
        merge_enrichment_data()
    
    # Step 2: Clean up old files
    cleanup_files(dry_run=not args.execute)
    
    logger.info("\n" + "=" * 70)
    logger.info("✅ CONSOLIDATION COMPLETE")
    logger.info("=" * 70)
    logger.info(f"\nSingle unified file: {MAIN_FILE}")
    logger.info("Use: python scripts/manage_nonprofits.py stats")


if __name__ == '__main__':
    main()
