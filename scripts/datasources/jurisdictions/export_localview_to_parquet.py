#!/usr/bin/env python3
"""
Export in_localview column from PostgreSQL to parquet file

This script updates the jurisdictions_details.parquet file to include the
in_localview column from the database.

Usage:
    python scripts/datasources/jurisdictions/export_localview_to_parquet.py
"""
import os
import sys
from pathlib import Path
import pandas as pd
import psycopg2
from loguru import logger
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database connection
DATABASE_URL = os.getenv('NEON_DATABASE_URL_DEV', 'postgresql://postgres:password@localhost:5433/open_navigator')

# Paths
PARQUET_FILE = Path('data/gold/jurisdictions_details.parquet')


def export_localview_to_parquet():
    """Export in_localview flags from database to parquet file."""
    
    logger.info("=" * 80)
    logger.info("EXPORTING in_localview TO PARQUET")
    logger.info("=" * 80)
    
    # Read existing parquet
    if not PARQUET_FILE.exists():
        logger.error(f"✗ Parquet file not found: {PARQUET_FILE}")
        return
    
    logger.info(f"Reading {PARQUET_FILE}")
    df = pd.read_parquet(PARQUET_FILE)
    logger.info(f"  Loaded {len(df):,} jurisdictions")
    
    # Connect to database
    logger.info("Connecting to database...")
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    try:
        # Get in_localview flags for all jurisdictions
        cursor.execute("""
            SELECT jurisdiction_id, in_localview
            FROM jurisdictions_details_search
        """)
        
        localview_flags = dict(cursor.fetchall())
        logger.info(f"  Retrieved {len(localview_flags):,} in_localview flags from database")
        
        # Add/update in_localview column in parquet
        if 'in_localview' in df.columns:
            logger.info("  Updating existing in_localview column")
        else:
            logger.info("  Adding new in_localview column")
        
        df['in_localview'] = df['jurisdiction_id'].map(localview_flags).fillna(False)
        
        # Count how many are in LocalView
        in_localview_count = df['in_localview'].sum()
        logger.info(f"  Jurisdictions in LocalView: {in_localview_count}")
        
        # Create backup
        backup_file = PARQUET_FILE.with_suffix('.parquet.backup')
        logger.info(f"Creating backup: {backup_file}")
        df_original = pd.read_parquet(PARQUET_FILE)
        df_original.to_parquet(backup_file)
        
        # Save updated parquet
        logger.info(f"Saving updated parquet to {PARQUET_FILE}")
        df.to_parquet(PARQUET_FILE)
        
        logger.success("✓ Successfully exported in_localview to parquet")
        logger.info(f"  Total jurisdictions: {len(df):,}")
        logger.info(f"  In LocalView: {in_localview_count}")
        logger.info(f"  Backup saved: {backup_file}")
        
    except Exception as e:
        logger.error(f"✗ Failed to export: {e}")
        raise
    finally:
        cursor.close()
        conn.close()


def main():
    try:
        export_localview_to_parquet()
    except Exception as e:
        logger.error(f"Export failed: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
