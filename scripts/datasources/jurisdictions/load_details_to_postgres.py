#!/usr/bin/env python3
"""
Load Jurisdictions Details into PostgreSQL jurisdictions_details_search table

This script creates the jurisdictions_details_search table and loads data from
data/gold/jurisdictions_details.parquet into PostgreSQL.
"""
import os
import sys
from pathlib import Path
from datetime import datetime
import json
import pandas as pd
import psycopg2
from psycopg2.extras import execute_batch
from loguru import logger
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database connection
DATABASE_URL = os.getenv('NEON_DATABASE_URL_DEV', 'postgresql://postgres:password@localhost:5433/open_navigator')

# Source parquet file
PARQUET_FILE = Path('data/gold/jurisdictions_details.parquet')


def create_table(conn):
    """Create jurisdictions_details_search table if it doesn't exist."""
    
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS jurisdictions_details_search (
        id SERIAL PRIMARY KEY,
        jurisdiction_id VARCHAR(50) UNIQUE NOT NULL,
        jurisdiction_name VARCHAR(200) NOT NULL,
        state VARCHAR(2) NOT NULL,
        jurisdiction_type VARCHAR(50),
        population INTEGER,
        discovery_timestamp TIMESTAMP,
        website_url TEXT,
        youtube_channel_count INTEGER DEFAULT 0,
        youtube_channels JSONB,
        meeting_platform_count INTEGER DEFAULT 0,
        meeting_platforms JSONB,
        social_media JSONB,
        agenda_portal_count INTEGER DEFAULT 0,
        status VARCHAR(50),
        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    -- Create indexes for common queries
    CREATE INDEX IF NOT EXISTS idx_jurisdiction_details_state ON jurisdictions_details_search(state);
    CREATE INDEX IF NOT EXISTS idx_jurisdiction_details_name ON jurisdictions_details_search(jurisdiction_name);
    CREATE INDEX IF NOT EXISTS idx_jurisdiction_details_type ON jurisdictions_details_search(jurisdiction_type);
    CREATE INDEX IF NOT EXISTS idx_jurisdiction_details_youtube ON jurisdictions_details_search(youtube_channel_count) WHERE youtube_channel_count > 0;
    CREATE INDEX IF NOT EXISTS idx_jurisdiction_details_population ON jurisdictions_details_search(population DESC);
    CREATE INDEX IF NOT EXISTS idx_jurisdiction_details_status ON jurisdictions_details_search(status);
    
    -- GIN index for JSONB search
    CREATE INDEX IF NOT EXISTS idx_jurisdiction_details_youtube_channels ON jurisdictions_details_search USING GIN (youtube_channels);
    CREATE INDEX IF NOT EXISTS idx_jurisdiction_details_platforms ON jurisdictions_details_search USING GIN (meeting_platforms);
    CREATE INDEX IF NOT EXISTS idx_jurisdiction_details_social ON jurisdictions_details_search USING GIN (social_media);
    """
    
    cursor = conn.cursor()
    try:
        cursor.execute(create_table_sql)
        conn.commit()
        logger.success("✓ Table jurisdictions_details_search created/verified")
    except Exception as e:
        conn.rollback()
        logger.error(f"✗ Failed to create table: {e}")
        raise
    finally:
        cursor.close()


def load_data(conn, parquet_file: Path, batch_size: int = 1000):
    """Load data from parquet file into database."""
    
    logger.info(f"Loading data from {parquet_file.name}...")
    
    # Read parquet file
    df = pd.read_parquet(parquet_file)
    logger.info(f"  Rows in file: {len(df):,}")
    
    # Convert timestamp strings to datetime
    df['discovery_timestamp'] = pd.to_datetime(df['discovery_timestamp'])
    
    # Prepare data for insertion
    records = []
    for _, row in df.iterrows():
        # Convert Python string representations to proper JSON
        youtube_channels = row['youtube_channels'] if pd.notna(row['youtube_channels']) else '[]'
        if isinstance(youtube_channels, str):
            try:
                # Try to parse as Python literal and convert to JSON
                import ast
                youtube_channels = json.dumps(ast.literal_eval(youtube_channels))
            except:
                youtube_channels = '[]'
        elif isinstance(youtube_channels, (list, dict)):
            youtube_channels = json.dumps(youtube_channels)
        
        meeting_platforms = row['meeting_platforms'] if pd.notna(row['meeting_platforms']) else '[]'
        if isinstance(meeting_platforms, str):
            try:
                import ast
                meeting_platforms = json.dumps(ast.literal_eval(meeting_platforms))
            except:
                meeting_platforms = '[]'
        elif isinstance(meeting_platforms, (list, dict)):
            meeting_platforms = json.dumps(meeting_platforms)
        
        social_media = row['social_media'] if pd.notna(row['social_media']) else '{}'
        if isinstance(social_media, str):
            try:
                import ast
                social_media = json.dumps(ast.literal_eval(social_media))
            except:
                social_media = '{}'
        elif isinstance(social_media, dict):
            social_media = json.dumps(social_media)
        
        record = {
            'jurisdiction_id': row['jurisdiction_id'],
            'jurisdiction_name': row['jurisdiction_name'],
            'state': row['state'],
            'jurisdiction_type': row['jurisdiction_type'],
            'population': int(row['population']) if pd.notna(row['population']) else 0,
            'discovery_timestamp': row['discovery_timestamp'],
            'website_url': row['website_url'] if pd.notna(row['website_url']) else None,
            'youtube_channel_count': int(row['youtube_channel_count']) if pd.notna(row['youtube_channel_count']) else 0,
            'youtube_channels': youtube_channels,
            'meeting_platform_count': int(row['meeting_platform_count']) if pd.notna(row['meeting_platform_count']) else 0,
            'meeting_platforms': meeting_platforms,
            'social_media': social_media,
            'agenda_portal_count': int(row['agenda_portal_count']) if pd.notna(row['agenda_portal_count']) else 0,
            'status': row['status'] if pd.notna(row['status']) else 'unknown'
        }
        records.append(record)
    
    # Insert into database
    insert_query = """
        INSERT INTO jurisdictions_details_search (
            jurisdiction_id, jurisdiction_name, state, jurisdiction_type,
            population, discovery_timestamp, website_url,
            youtube_channel_count, youtube_channels,
            meeting_platform_count, meeting_platforms,
            social_media, agenda_portal_count, status
        ) VALUES (
            %(jurisdiction_id)s, %(jurisdiction_name)s, %(state)s, %(jurisdiction_type)s,
            %(population)s, %(discovery_timestamp)s, %(website_url)s,
            %(youtube_channel_count)s, %(youtube_channels)s::jsonb,
            %(meeting_platform_count)s, %(meeting_platforms)s::jsonb,
            %(social_media)s::jsonb, %(agenda_portal_count)s, %(status)s
        )
        ON CONFLICT (jurisdiction_id) 
        DO UPDATE SET
            jurisdiction_name = EXCLUDED.jurisdiction_name,
            state = EXCLUDED.state,
            jurisdiction_type = EXCLUDED.jurisdiction_type,
            population = EXCLUDED.population,
            discovery_timestamp = EXCLUDED.discovery_timestamp,
            website_url = EXCLUDED.website_url,
            youtube_channel_count = EXCLUDED.youtube_channel_count,
            youtube_channels = EXCLUDED.youtube_channels,
            meeting_platform_count = EXCLUDED.meeting_platform_count,
            meeting_platforms = EXCLUDED.meeting_platforms,
            social_media = EXCLUDED.social_media,
            agenda_portal_count = EXCLUDED.agenda_portal_count,
            status = EXCLUDED.status,
            last_updated = CURRENT_TIMESTAMP
    """
    
    cursor = conn.cursor()
    inserted = 0
    
    try:
        for i in range(0, len(records), batch_size):
            batch = records[i:i + batch_size]
            execute_batch(cursor, insert_query, batch, page_size=batch_size)
            inserted += len(batch)
            conn.commit()
            
            if i % 1000 == 0 and i > 0:
                logger.info(f"  Inserted {i:,} / {len(records):,} jurisdictions...")
        
        logger.success(f"  ✓ Inserted/updated {inserted:,} jurisdictions")
        return inserted
        
    except Exception as e:
        conn.rollback()
        logger.error(f"  ✗ Error inserting data: {e}")
        raise
    finally:
        cursor.close()


def main():
    """Main loading function."""
    logger.info("=" * 80)
    logger.info("JURISDICTIONS DETAILS → POSTGRES LOADER")
    logger.info("=" * 80)
    logger.info(f"Source: {PARQUET_FILE}")
    logger.info(f"Database: {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else 'localhost'}")
    logger.info("")
    
    # Check if file exists
    if not PARQUET_FILE.exists():
        logger.error(f"Parquet file not found: {PARQUET_FILE}")
        return 1
    
    # Connect to database
    logger.info("Connecting to database...")
    try:
        conn = psycopg2.connect(DATABASE_URL)
        logger.success("✓ Connected")
    except Exception as e:
        logger.error(f"✗ Database connection failed: {e}")
        return 1
    
    start_time = datetime.now()
    
    try:
        # Create table
        create_table(conn)
        
        # Load data
        inserted = load_data(conn, PARQUET_FILE)
        
        # Get final stats
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                COUNT(DISTINCT state) as states,
                SUM(youtube_channel_count) as total_youtube_channels,
                COUNT(*) FILTER (WHERE youtube_channel_count > 0) as jurisdictions_with_youtube,
                COUNT(*) FILTER (WHERE website_url IS NOT NULL) as with_websites
            FROM jurisdictions_details_search
        """)
        stats = cursor.fetchone()
        cursor.close()
        
        duration = (datetime.now() - start_time).total_seconds()
        
        logger.info("")
        logger.success("=" * 80)
        logger.success("✓ LOADING COMPLETE")
        logger.success("=" * 80)
        logger.success(f"Total jurisdictions: {stats[0]:,}")
        logger.success(f"States covered: {stats[1]}")
        logger.success(f"Total YouTube channels discovered: {stats[2]:,}")
        logger.success(f"Jurisdictions with YouTube: {stats[3]:,}")
        logger.success(f"Jurisdictions with websites: {stats[4]:,}")
        logger.success(f"Duration: {duration:.1f} seconds")
        logger.info("")
        logger.info("Next steps:")
        logger.info("1. Query: SELECT * FROM jurisdictions_details_search WHERE youtube_channel_count > 0 LIMIT 10")
        logger.info("2. Search YouTube channels: SELECT jurisdiction_name, state, youtube_channels FROM jurisdictions_details_search WHERE state='MA'")
        
        return 0
        
    except Exception as e:
        logger.error(f"✗ Loading failed: {e}")
        return 1
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
