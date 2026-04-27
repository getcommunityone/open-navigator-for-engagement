#!/usr/bin/env python3
"""
Create partitioned parquet datasets for efficient state-based queries.

This converts consolidated files into partitioned datasets where each partition
represents a state. This allows:
- Querying the full national dataset
- Automatically filtering to only read needed states (partition pruning)
- Efficient analytics with tools like Spark, DuckDB, Pandas

Example:
    # Read only Alabama data (only reads AL partition)
    df = pd.read_parquet('data/gold/nonprofits_organizations', 
                         filters=[('state', '=', 'AL')])
    
    # Read multiple states
    df = pd.read_parquet('data/gold/nonprofits_organizations',
                         filters=[('state', 'in', ['AL', 'GA', 'FL'])])
    
    # Read everything (reads all partitions)
    df = pd.read_parquet('data/gold/nonprofits_organizations')

Usage:
    # Create all partitioned datasets
    python scripts/create_partitioned_datasets.py --all
    
    # Create specific dataset
    python scripts/create_partitioned_datasets.py --file nonprofits_organizations.parquet
    
    # Dry run
    python scripts/create_partitioned_datasets.py --all --dry-run
"""

import argparse
from pathlib import Path
import pandas as pd
from loguru import logger
from typing import List, Dict


class PartitionedDatasetCreator:
    """Create partitioned parquet datasets by state."""
    
    # Files that have direct 'state' column
    STATE_COLUMN_FILES = {
        'nonprofits_organizations.parquet': 'state',
        'nonprofits_locations.parquet': 'state',
        'nonprofits_financials.parquet': 'state',
        'nonprofits_programs.parquet': 'state',
    }
    
    # Files that have 'State' column (capitalized)
    STATE_UPPER_FILES = {
        'domains_gsa_domains.parquet': 'State',
    }
    
    # Files that have 'USPS' column (state abbreviation)
    USPS_FILES = {
        'jurisdictions_cities.parquet': 'USPS',
        'jurisdictions_counties.parquet': 'USPS',
        'jurisdictions_school_districts.parquet': 'USPS',
        'jurisdictions_townships.parquet': 'USPS',
    }
    
    def __init__(self, gold_dir: str = "data/gold", output_dir: str = None):
        """
        Initialize creator.
        
        Args:
            gold_dir: Directory containing gold parquet files and output location
            output_dir: Directory for partitioned datasets (defaults to same as gold_dir)
        """
        self.gold_dir = Path(gold_dir)
        self.output_dir = Path(output_dir) if output_dir else self.gold_dir
        
        # Combined mapping
        self.all_files = {
            **self.STATE_COLUMN_FILES,
            **self.STATE_UPPER_FILES,
            **self.USPS_FILES,
        }
    
    def get_state_column(self, filename: str) -> str:
        """Get the state column name for a file."""
        if filename in self.STATE_COLUMN_FILES:
            return self.STATE_COLUMN_FILES[filename]
        elif filename in self.STATE_UPPER_FILES:
            return self.STATE_UPPER_FILES[filename]
        elif filename in self.USPS_FILES:
            return self.USPS_FILES[filename]
        else:
            raise ValueError(f"Unknown file: {filename}")
    
    def create_partitioned_dataset(self, filename: str, dry_run: bool = False) -> bool:
        """
        Create a partitioned dataset from a consolidated file.
        
        Args:
            filename: Name of file to partition (e.g., 'nonprofits_organizations.parquet')
            dry_run: If True, only report what would be done
            
        Returns:
            True if successful, False otherwise
        """
        input_path = self.gold_dir / filename
        
        if not input_path.exists():
            logger.warning(f"File not found: {input_path}")
            return False
        
        logger.info(f"📂 Processing: {filename}")
        
        # Read the file
        df = pd.read_parquet(input_path)
        logger.info(f"  Total records: {len(df):,}")
        
        # Get state column
        state_col = self.get_state_column(filename)
        
        if state_col not in df.columns:
            logger.error(f"  ❌ Column '{state_col}' not found in {filename}")
            return False
        
        # Normalize column name to 'state' for consistent partitioning
        if state_col != 'state':
            df['state'] = df[state_col]
            # Keep original column too for backward compatibility
        
        # Create output directory name (remove .parquet extension)
        dataset_name = filename.replace('.parquet', '')
        output_path = self.output_dir / dataset_name
        
        if dry_run:
            unique_states = df['state'].nunique()
            total_size = input_path.stat().st_size / 1024 / 1024
            logger.info(f"  [DRY RUN] Would create partitioned dataset:")
            logger.info(f"    Path: {output_path}")
            logger.info(f"    Partitions: {unique_states} states")
            logger.info(f"    Total size: {total_size:.2f} MB")
            return True
        
        # Write partitioned dataset
        logger.info(f"  Writing partitioned dataset to: {output_path}")
        df.to_parquet(
            output_path,
            engine='pyarrow',
            partition_cols=['state'],
            index=False
        )
        
        # Get statistics
        partitions = list((output_path).glob('state=*'))
        total_size = sum(
            sum(f.stat().st_size for f in partition.rglob('*.parquet'))
            for partition in partitions
        ) / 1024 / 1024
        
        logger.success(f"✅ Created partitioned dataset:")
        logger.success(f"   Path: {output_path}")
        logger.success(f"   Partitions: {len(partitions)} states")
        logger.success(f"   Total size: {total_size:.2f} MB")
        logger.success(f"   Query example: pd.read_parquet('{output_path}', filters=[('state', '=', 'AL')])")
        
        return True
    
    def create_all(self, dry_run: bool = False) -> Dict[str, bool]:
        """
        Create partitioned datasets for all configured files.
        
        Args:
            dry_run: If True, only report what would be done
            
        Returns:
            Dict mapping filename to success status
        """
        logger.info("🚀 Creating partitioned datasets...")
        logger.info(f"  Input directory: {self.gold_dir}")
        logger.info(f"  Output directory: {self.output_dir}")
        logger.info("")
        
        # Create output directory
        if not dry_run:
            self.output_dir.mkdir(parents=True, exist_ok=True)
        
        results = {}
        for filename in self.all_files.keys():
            try:
                success = self.create_partitioned_dataset(filename, dry_run=dry_run)
                results[filename] = success
                logger.info("")
            except Exception as e:
                logger.error(f"❌ Error processing {filename}: {e}")
                results[filename] = False
                logger.info("")
        
        # Summary
        successful = sum(1 for v in results.values() if v)
        logger.success("=" * 70)
        logger.success(f"✅ Created {successful}/{len(results)} partitioned datasets")
        logger.success(f"📂 Output directory: {self.output_dir}")
        logger.success("=" * 70)
        
        return results


def main():
    parser = argparse.ArgumentParser(
        description="Create partitioned parquet datasets by state",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Create all partitioned datasets
  python scripts/create_partitioned_datasets.py --all
  
  # Create specific dataset
  python scripts/create_partitioned_datasets.py --file nonprofits_organizations.parquet
  
  # Dry run
  python scripts/create_partitioned_datasets.py --all --dry-run

Query Examples:
  # Read only Alabama data (efficient - only reads AL partition)
  import pandas as pd
  df = pd.read_parquet('data/gold/partitioned/nonprofits_organizations',
                       filters=[('state', '=', 'AL')])
  
  # Read multiple states
  df = pd.read_parquet('data/gold/partitioned/nonprofits_organizations',
                       filters=[('state', 'in', ['AL', 'GA', 'FL'])])
  
  # Read all states
  df = pd.read_parquet('data/gold/partitioned/nonprofits_organizations')
        """
    )
    
    parser.add_argument('--all', action='store_true',
                       help='Create all partitioned datasets')
    parser.add_argument('--file', type=str,
                       help='Create partitioned dataset for specific file')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be done without creating datasets')
    parser.add_argument('--gold-dir', type=str, default='data/gold',
                       help='Directory containing gold parquet files (default: data/gold)')
    parser.add_argument('--output-dir', type=str,
                       help='Output directory for partitioned datasets (default: same as gold-dir)')
    
    args = parser.parse_args()
    
    # Initialize creator
    creator = PartitionedDatasetCreator(
        gold_dir=args.gold_dir,
        output_dir=args.output_dir
    )
    
    # Handle commands
    if args.all:
        creator.create_all(dry_run=args.dry_run)
    elif args.file:
        creator.create_partitioned_dataset(args.file, dry_run=args.dry_run)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
