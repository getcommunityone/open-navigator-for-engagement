#!/usr/bin/env python3
"""
Migrate ALL parquet files to use state_code + state naming convention

This script:
1. Finds all parquet files with 'state' column containing 2-letter codes
2. Renames 'state' → 'state_code'
3. Adds 'state' column with full state names
4. Saves updated parquet files (with backups)
"""
import pandas as pd
from pathlib import Path
from loguru import logger

# State code to full name mapping
STATE_NAMES = {
    'AL': 'Alabama', 'AK': 'Alaska', 'AZ': 'Arizona', 'AR': 'Arkansas', 'CA': 'California',
    'CO': 'Colorado', 'CT': 'Connecticut', 'DE': 'Delaware', 'FL': 'Florida', 'GA': 'Georgia',
    'HI': 'Hawaii', 'ID': 'Idaho', 'IL': 'Illinois', 'IN': 'Indiana', 'IA': 'Iowa',
    'KS': 'Kansas', 'KY': 'Kentucky', 'LA': 'Louisiana', 'ME': 'Maine', 'MD': 'Maryland',
    'MA': 'Massachusetts', 'MI': 'Michigan', 'MN': 'Minnesota', 'MS': 'Mississippi', 'MO': 'Missouri',
    'MT': 'Montana', 'NE': 'Nebraska', 'NV': 'Nevada', 'NH': 'New Hampshire', 'NJ': 'New Jersey',
    'NM': 'New Mexico', 'NY': 'New York', 'NC': 'North Carolina', 'ND': 'North Dakota', 'OH': 'Ohio',
    'OK': 'Oklahoma', 'OR': 'Oregon', 'PA': 'Pennsylvania', 'RI': 'Rhode Island', 'SC': 'South Carolina',
    'SD': 'South Dakota', 'TN': 'Tennessee', 'TX': 'Texas', 'UT': 'Utah', 'VT': 'Vermont',
    'VA': 'Virginia', 'WA': 'Washington', 'WV': 'West Virginia', 'WI': 'Wisconsin', 'WY': 'Wyoming',
    'DC': 'District of Columbia', 'PR': 'Puerto Rico'
}

# Special handling for files with 'USPS' or 'STATE' instead of 'state'
COLUMN_MAPPINGS = {
    'jurisdictions_cities.parquet': 'USPS',
    'jurisdictions_counties.parquet': 'USPS',
    'jurisdictions_townships.parquet': 'USPS',
    'jurisdictions_school_districts.parquet': 'STATE',
}


def migrate_parquet_file(file_path: Path, dry_run=False):
    """Migrate a single parquet file to new naming convention."""
    
    try:
        df = pd.read_parquet(file_path)
        
        # Determine which column name is used
        state_col_name = None
        file_name = file_path.name
        
        if file_name in COLUMN_MAPPINGS:
            state_col_name = COLUMN_MAPPINGS[file_name]
        elif 'state' in df.columns:
            state_col_name = 'state'
        elif 'STATE' in df.columns:
            state_col_name = 'STATE'
        elif 'USPS' in df.columns:
            state_col_name = 'USPS'
        else:
            # No state column
            return None
        
        # Check if already migrated
        if 'state_code' in df.columns and 'state' in df.columns:
            # Verify state has full names
            if len(df) > 0:
                sample_state = df['state'].iloc[0]
                if sample_state and len(str(sample_state)) > 2:
                    logger.info(f"✅ {file_path.relative_to('data/gold')}: Already migrated")
                    return 'already_migrated'
        
        # Check if state column has 2-letter codes
        if len(df) > 0:
            sample_values = df[state_col_name].dropna()
            if len(sample_values) == 0:
                logger.info(f"⏭️  {file_path.relative_to('data/gold')}: State column is empty")
                return 'not_applicable'
            
            sample_state = sample_values.iloc[0]
            if not sample_state or len(str(sample_state)) != 2:
                logger.info(f"⏭️  {file_path.relative_to('data/gold')}: State column doesn't have 2-letter codes")
                return 'not_applicable'
        
        if dry_run:
            logger.info(f"🔍 {file_path.relative_to('data/gold')}: Would migrate")
            return 'would_migrate'
        
        # Backup original file
        backup_path = file_path.parent / f"{file_path.stem}_backup{file_path.suffix}"
        logger.info(f"💾 {file_path.relative_to('data/gold')}: Creating backup...")
        df.to_parquet(backup_path)
        
        # Rename state column to state_code
        logger.info(f"🔄 {file_path.relative_to('data/gold')}: Renaming '{state_col_name}' → 'state_code'...")
        df = df.rename(columns={state_col_name: 'state_code'})
        
        # Add state column with full names
        logger.info(f"➕ {file_path.relative_to('data/gold')}: Adding 'state' column...")
        df['state'] = df['state_code'].map(STATE_NAMES)
        
        # Check for unmapped states
        unmapped = df[df['state'].isna() & df['state_code'].notna()]['state_code'].unique()
        if len(unmapped) > 0:
            logger.warning(f"   ⚠️  Unmapped state codes: {unmapped.tolist()}")
        
        # Reorder columns (state_code and state together)
        cols = df.columns.tolist()
        # Remove state_code and state
        cols = [c for c in cols if c not in ['state_code', 'state']]
        # Find a good position to insert (after first few columns)
        insert_pos = min(3, len(cols))
        cols.insert(insert_pos, 'state_code')
        cols.insert(insert_pos + 1, 'state')
        df = df[cols]
        
        # Save migrated file
        logger.info(f"💾 {file_path.relative_to('data/gold')}: Saving...")
        df.to_parquet(file_path)
        
        logger.success(f"✅ {file_path.relative_to('data/gold')}: Migrated successfully")
        return 'migrated'
        
    except Exception as e:
        logger.error(f"❌ {file_path.relative_to('data/gold')}: {e}")
        return 'error'


def main(dry_run=False):
    """Main migration function."""
    
    logger.info("=" * 80)
    logger.info("PARQUET FILES STATE NAMING MIGRATION")
    logger.info("=" * 80)
    if dry_run:
        logger.info("🔍 DRY RUN MODE - No files will be modified")
    logger.info("")
    
    # Find all parquet files
    gold_dir = Path('data/gold')
    parquet_files = list(gold_dir.rglob('*.parquet'))
    
    logger.info(f"Found {len(parquet_files)} parquet files")
    logger.info("")
    
    stats = {
        'migrated': 0,
        'already_migrated': 0,
        'not_applicable': 0,
        'would_migrate': 0,
        'error': 0
    }
    
    for file_path in sorted(parquet_files):
        result = migrate_parquet_file(file_path, dry_run=dry_run)
        if result:
            stats[result] += 1
    
    logger.info("")
    logger.info("=" * 80)
    logger.info("MIGRATION SUMMARY")
    logger.info("=" * 80)
    logger.success(f"✅ Migrated: {stats['migrated']}")
    logger.info(f"✅ Already migrated: {stats['already_migrated']}")
    logger.info(f"⏭️  Not applicable: {stats['not_applicable']}")
    if dry_run:
        logger.info(f"🔍 Would migrate: {stats['would_migrate']}")
    if stats['error'] > 0:
        logger.error(f"❌ Errors: {stats['error']}")
    logger.info("=" * 80)
    
    if not dry_run and stats['migrated'] > 0:
        logger.info("")
        logger.info("✨ Backups created with '_backup' suffix")
        logger.info("📊 All files now use:")
        logger.info("   - state_code: 2-letter code (AL, MA, etc.)")
        logger.info("   - state: Full name (Alabama, Massachusetts, etc.)")


if __name__ == "__main__":
    import sys
    
    dry_run = '--dry-run' in sys.argv or '-n' in sys.argv
    
    main(dry_run=dry_run)
