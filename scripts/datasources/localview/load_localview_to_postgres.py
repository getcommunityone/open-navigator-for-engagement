#!/usr/bin/env python3
"""
Load LocalView Meeting Data into bronze.bronze_events_localview table

This script reads all LocalView parquet files and inserts meeting data
into the bronze.bronze_events_localview table following the medallion architecture.
"""
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any
import pandas as pd
import psycopg2
from psycopg2.extras import execute_batch
from loguru import logger
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database connection
DATABASE_URL = os.getenv('NEON_DATABASE_URL_DEV', 'postgresql://postgres:password@localhost:5433/open_navigator')

# LocalView data directory
LOCALVIEW_DIR = Path('data/cache/localview')

CREATE_TABLE_SQL = """
    CREATE SCHEMA IF NOT EXISTS bronze;
    CREATE TABLE IF NOT EXISTS bronze.bronze_events_localview (
        event_id          BIGINT PRIMARY KEY,
        event_date        DATE,
        jurisdiction_name VARCHAR(500),
        jurisdiction_type VARCHAR(100),
        city_name         VARCHAR(255),
        state_code        VARCHAR(2),
        state             VARCHAR(100),
        meeting_type      VARCHAR(255),
        title             VARCHAR(500),
        video_url         TEXT,
        datasource        VARCHAR(100),
        datasource_id     VARCHAR(255),
        loaded_at         TIMESTAMP DEFAULT NOW(),

        -- Raw LocalView columns (kept for lineage/debugging)
        st_fips                 VARCHAR(10),
        place_govt              VARCHAR(255),
        channel_title           VARCHAR(500),
        vid_title               VARCHAR(500),
        vid_desc                TEXT,
        vid_length_min          DOUBLE PRECISION,
        vid_upload_date         TIMESTAMP,
        vid_livestreamed        BOOLEAN,
        vid_views               DOUBLE PRECISION,
        vid_likes               DOUBLE PRECISION,
        vid_dislikes            DOUBLE PRECISION,
        vid_comments            DOUBLE PRECISION,
        vid_favorites           DOUBLE PRECISION,
        meeting_date_raw        VARCHAR(50),
        caption_text            TEXT,
        caption_text_clean      TEXT,
        channel_type            VARCHAR(100),
        acs_18_amind             DOUBLE PRECISION,
        acs_18_asian             DOUBLE PRECISION,
        acs_18_black             DOUBLE PRECISION,
        acs_18_hispanic          DOUBLE PRECISION,
        acs_18_median_age        DOUBLE PRECISION,
        acs_18_median_gross_rent DOUBLE PRECISION,
        acs_18_median_hh_inc     DOUBLE PRECISION,
        acs_18_nhapi             DOUBLE PRECISION,
        acs_18_pop               DOUBLE PRECISION,
        acs_18_white             DOUBLE PRECISION
    );

    -- Backward-compat: add any new columns to pre-existing tables
    ALTER TABLE bronze.bronze_events_localview
        ADD COLUMN IF NOT EXISTS city_name VARCHAR(255);
    ALTER TABLE bronze.bronze_events_localview
        ADD COLUMN IF NOT EXISTS st_fips VARCHAR(10);
    ALTER TABLE bronze.bronze_events_localview
        ADD COLUMN IF NOT EXISTS place_govt VARCHAR(255);
    ALTER TABLE bronze.bronze_events_localview
        ADD COLUMN IF NOT EXISTS channel_title VARCHAR(500);
    ALTER TABLE bronze.bronze_events_localview
        ADD COLUMN IF NOT EXISTS vid_title VARCHAR(500);
    ALTER TABLE bronze.bronze_events_localview
        ADD COLUMN IF NOT EXISTS vid_desc TEXT;
    ALTER TABLE bronze.bronze_events_localview
        ADD COLUMN IF NOT EXISTS vid_length_min DOUBLE PRECISION;
    ALTER TABLE bronze.bronze_events_localview
        ADD COLUMN IF NOT EXISTS vid_upload_date TIMESTAMP;
    ALTER TABLE bronze.bronze_events_localview
        ADD COLUMN IF NOT EXISTS vid_livestreamed BOOLEAN;
    ALTER TABLE bronze.bronze_events_localview
        ADD COLUMN IF NOT EXISTS vid_views DOUBLE PRECISION;
    ALTER TABLE bronze.bronze_events_localview
        ADD COLUMN IF NOT EXISTS vid_likes DOUBLE PRECISION;
    ALTER TABLE bronze.bronze_events_localview
        ADD COLUMN IF NOT EXISTS vid_dislikes DOUBLE PRECISION;
    ALTER TABLE bronze.bronze_events_localview
        ADD COLUMN IF NOT EXISTS vid_comments DOUBLE PRECISION;
    ALTER TABLE bronze.bronze_events_localview
        ADD COLUMN IF NOT EXISTS vid_favorites DOUBLE PRECISION;
    ALTER TABLE bronze.bronze_events_localview
        ADD COLUMN IF NOT EXISTS meeting_date_raw VARCHAR(50);
    ALTER TABLE bronze.bronze_events_localview
        ADD COLUMN IF NOT EXISTS caption_text TEXT;
    ALTER TABLE bronze.bronze_events_localview
        ADD COLUMN IF NOT EXISTS caption_text_clean TEXT;
    ALTER TABLE bronze.bronze_events_localview
        ADD COLUMN IF NOT EXISTS channel_type VARCHAR(100);
    ALTER TABLE bronze.bronze_events_localview
        ADD COLUMN IF NOT EXISTS acs_18_amind DOUBLE PRECISION;
    ALTER TABLE bronze.bronze_events_localview
        ADD COLUMN IF NOT EXISTS acs_18_asian DOUBLE PRECISION;
    ALTER TABLE bronze.bronze_events_localview
        ADD COLUMN IF NOT EXISTS acs_18_black DOUBLE PRECISION;
    ALTER TABLE bronze.bronze_events_localview
        ADD COLUMN IF NOT EXISTS acs_18_hispanic DOUBLE PRECISION;
    ALTER TABLE bronze.bronze_events_localview
        ADD COLUMN IF NOT EXISTS acs_18_median_age DOUBLE PRECISION;
    ALTER TABLE bronze.bronze_events_localview
        ADD COLUMN IF NOT EXISTS acs_18_median_gross_rent DOUBLE PRECISION;
    ALTER TABLE bronze.bronze_events_localview
        ADD COLUMN IF NOT EXISTS acs_18_median_hh_inc DOUBLE PRECISION;
    ALTER TABLE bronze.bronze_events_localview
        ADD COLUMN IF NOT EXISTS acs_18_nhapi DOUBLE PRECISION;
    ALTER TABLE bronze.bronze_events_localview
        ADD COLUMN IF NOT EXISTS acs_18_pop DOUBLE PRECISION;
    ALTER TABLE bronze.bronze_events_localview
        ADD COLUMN IF NOT EXISTS acs_18_white DOUBLE PRECISION;

    -- If columns exist with the old BIGINT types, widen them to DOUBLE PRECISION
    ALTER TABLE bronze.bronze_events_localview
        ALTER COLUMN vid_views TYPE DOUBLE PRECISION USING vid_views::DOUBLE PRECISION;
    ALTER TABLE bronze.bronze_events_localview
        ALTER COLUMN vid_likes TYPE DOUBLE PRECISION USING vid_likes::DOUBLE PRECISION;
    ALTER TABLE bronze.bronze_events_localview
        ALTER COLUMN vid_dislikes TYPE DOUBLE PRECISION USING vid_dislikes::DOUBLE PRECISION;
    ALTER TABLE bronze.bronze_events_localview
        ALTER COLUMN vid_comments TYPE DOUBLE PRECISION USING vid_comments::DOUBLE PRECISION;
    ALTER TABLE bronze.bronze_events_localview
        ALTER COLUMN vid_favorites TYPE DOUBLE PRECISION USING vid_favorites::DOUBLE PRECISION;
    ALTER TABLE bronze.bronze_events_localview
        ALTER COLUMN acs_18_amind TYPE DOUBLE PRECISION USING acs_18_amind::DOUBLE PRECISION;
    ALTER TABLE bronze.bronze_events_localview
        ALTER COLUMN acs_18_asian TYPE DOUBLE PRECISION USING acs_18_asian::DOUBLE PRECISION;
    ALTER TABLE bronze.bronze_events_localview
        ALTER COLUMN acs_18_black TYPE DOUBLE PRECISION USING acs_18_black::DOUBLE PRECISION;
    ALTER TABLE bronze.bronze_events_localview
        ALTER COLUMN acs_18_hispanic TYPE DOUBLE PRECISION USING acs_18_hispanic::DOUBLE PRECISION;
    ALTER TABLE bronze.bronze_events_localview
        ALTER COLUMN acs_18_nhapi TYPE DOUBLE PRECISION USING acs_18_nhapi::DOUBLE PRECISION;
    ALTER TABLE bronze.bronze_events_localview
        ALTER COLUMN acs_18_pop TYPE DOUBLE PRECISION USING acs_18_pop::DOUBLE PRECISION;
    ALTER TABLE bronze.bronze_events_localview
        ALTER COLUMN acs_18_white TYPE DOUBLE PRECISION USING acs_18_white::DOUBLE PRECISION;

    -- NOTE: we intentionally do NOT drop columns here, because dbt views may
    -- depend on them. If you want to remove legacy columns from this bronze
    -- table, do it in an explicit migration step.
    CREATE INDEX IF NOT EXISTS idx_belv_event_date  ON bronze.bronze_events_localview(event_date);
    CREATE INDEX IF NOT EXISTS idx_belv_state_code  ON bronze.bronze_events_localview(state_code);
    CREATE INDEX IF NOT EXISTS idx_belv_datasource  ON bronze.bronze_events_localview(datasource);
"""

# State abbreviation mapping
STATE_ABBREV = {
    'Alabama': 'AL', 'Alaska': 'AK', 'Arizona': 'AZ', 'Arkansas': 'AR', 'California': 'CA',
    'Colorado': 'CO', 'Connecticut': 'CT', 'Delaware': 'DE', 'Florida': 'FL', 'Georgia': 'GA',
    'Hawaii': 'HI', 'Idaho': 'ID', 'Illinois': 'IL', 'Indiana': 'IN', 'Iowa': 'IA',
    'Kansas': 'KS', 'Kentucky': 'KY', 'Louisiana': 'LA', 'Maine': 'ME', 'Maryland': 'MD',
    'Massachusetts': 'MA', 'Michigan': 'MI', 'Minnesota': 'MN', 'Mississippi': 'MS', 'Missouri': 'MO',
    'Montana': 'MT', 'Nebraska': 'NE', 'Nevada': 'NV', 'New Hampshire': 'NH', 'New Jersey': 'NJ',
    'New Mexico': 'NM', 'New York': 'NY', 'North Carolina': 'NC', 'North Dakota': 'ND', 'Ohio': 'OH',
    'Oklahoma': 'OK', 'Oregon': 'OR', 'Pennsylvania': 'PA', 'Rhode Island': 'RI', 'South Carolina': 'SC',
    'South Dakota': 'SD', 'Tennessee': 'TN', 'Texas': 'TX', 'Utah': 'UT', 'Vermont': 'VT',
    'Virginia': 'VA', 'Washington': 'WA', 'West Virginia': 'WV', 'Wisconsin': 'WI', 'Wyoming': 'WY'
}


def get_state_abbrev(state_name: str) -> str:
    """Convert state name to abbreviation."""
    if pd.isna(state_name):
        return None
    return STATE_ABBREV.get(state_name, state_name[:2].upper())


def construct_youtube_url(vid_id: str) -> str:
    """Construct YouTube URL from video ID."""
    if pd.isna(vid_id):
        return None
    return f"https://www.youtube.com/watch?v={vid_id}"


def extract_channel_id_from_url(video_url: str) -> str:
    """Extract YouTube channel ID from video URL."""
    if pd.isna(video_url):
        return None
    # We'll need to query YouTube API or lookup from existing data
    # For now, return None - will be enriched later
    return None


def row_to_event(row: pd.Series, row_index: int) -> Dict[str, Any]:
    """Convert LocalView row to bronze_events_localview format."""
    # Parse meeting date
    event_date = None
    if pd.notna(row.get('meeting_date')):
        try:
            event_date = pd.to_datetime(row['meeting_date']).date()
        except:
            pass
    
    # Get video URL
    video_url = construct_youtube_url(row.get('vid_id'))
    
    # Extract title - use video title or create from place + date
    title = row.get('vid_title')
    if pd.isna(title) or not title:
        place = row.get('place_name', 'City Council')
        date_str = event_date.strftime('%B %d, %Y') if event_date else ''
        title = f"{place} Meeting - {date_str}" if date_str else f"{place} Meeting"
    
    # Get state info
    state_name = row.get('state_name')
    state_code = get_state_abbrev(state_name)
    
    # Generate event_id from video_id
    vid_id = row.get('vid_id')
    event_id = hash(f"localview_{vid_id}") % 2147483647 if pd.notna(vid_id) else None
    
    # Get jurisdiction info
    jurisdiction_name = row.get('place_name')
    
    return {
        'event_id': event_id,
        'event_date': event_date,
        'jurisdiction_name': jurisdiction_name,
        'jurisdiction_type': 'city',  # LocalView is municipal data
        'city_name': row.get('place_name'),
        'state_code': state_code,
        'state': state_name,
        'meeting_type': row.get('place_govt', 'City Council'),
        'title': title[:500] if title else 'City Council Meeting',  # Limit length
        'video_url': video_url,
        'datasource': 'localview',
        'datasource_id': vid_id,  # YouTube video ID
        'loaded_at': datetime.now(),

        # Raw LocalView columns
        'st_fips': row.get('st_fips'),
        'place_govt': row.get('place_govt'),
        'channel_title': row.get('channel_title'),
        'vid_title': row.get('vid_title'),
        'vid_desc': row.get('vid_desc'),
        'vid_length_min': row.get('vid_length_min'),
        'vid_upload_date': pd.to_datetime(row.get('vid_upload_date'), errors='coerce') if row.get('vid_upload_date') is not None else None,
        'vid_livestreamed': bool(row.get('vid_livestreamed')) if pd.notna(row.get('vid_livestreamed')) else None,
        'vid_views': row.get('vid_views'),
        'vid_likes': row.get('vid_likes'),
        'vid_dislikes': row.get('vid_dislikes'),
        'vid_comments': row.get('vid_comments'),
        'vid_favorites': row.get('vid_favorites'),
        'meeting_date_raw': str(row.get('meeting_date')) if pd.notna(row.get('meeting_date')) else None,
        'caption_text': row.get('caption_text'),
        'caption_text_clean': row.get('caption_text_clean'),
        'channel_type': row.get('channel_type'),
        'acs_18_amind': row.get('acs_18_amind'),
        'acs_18_asian': row.get('acs_18_asian'),
        'acs_18_black': row.get('acs_18_black'),
        'acs_18_hispanic': row.get('acs_18_hispanic'),
        'acs_18_median_age': row.get('acs_18_median_age'),
        'acs_18_median_gross_rent': row.get('acs_18_median_gross_rent'),
        'acs_18_median_hh_inc': row.get('acs_18_median_hh_inc'),
        'acs_18_nhapi': row.get('acs_18_nhapi'),
        'acs_18_pop': row.get('acs_18_pop'),
        'acs_18_white': row.get('acs_18_white'),
    }


def load_parquet_file(filepath: Path, conn, batch_size: int = 1000) -> int:
    """Load a single parquet file into database."""
    logger.info(f"Loading {filepath.name}...")
    
    # Read parquet file
    df = pd.read_parquet(filepath)
    logger.info(f"  Rows in file: {len(df):,}")
    
    # Filter: only rows with meeting_date and video URL
    df_valid = df[df['meeting_date'].notna() & df['vid_id'].notna()].copy()
    logger.info(f"  Valid meetings with dates and videos: {len(df_valid):,}")
    
    if len(df_valid) == 0:
        return 0
    
    # Convert to events
    events = [row_to_event(row, idx) for idx, row in df_valid.iterrows()]
    
    # Insert into bronze table in batches
    insert_query = """
        INSERT INTO bronze.bronze_events_localview (
            event_id, event_date, jurisdiction_name, jurisdiction_type,
            city_name, state_code, state, meeting_type,
            title, video_url, datasource, datasource_id, loaded_at,
            st_fips, place_govt, channel_title, vid_title, vid_desc,
            vid_length_min, vid_upload_date, vid_livestreamed,
            vid_views, vid_likes, vid_dislikes, vid_comments, vid_favorites,
            meeting_date_raw, caption_text, caption_text_clean, channel_type,
            acs_18_amind, acs_18_asian, acs_18_black, acs_18_hispanic,
            acs_18_median_age, acs_18_median_gross_rent, acs_18_median_hh_inc,
            acs_18_nhapi, acs_18_pop, acs_18_white
        ) VALUES (
            %(event_id)s, %(event_date)s, %(jurisdiction_name)s, %(jurisdiction_type)s,
            %(city_name)s, %(state_code)s, %(state)s, %(meeting_type)s,
            %(title)s, %(video_url)s, %(datasource)s, %(datasource_id)s, %(loaded_at)s,
            %(st_fips)s, %(place_govt)s, %(channel_title)s, %(vid_title)s, %(vid_desc)s,
            %(vid_length_min)s, %(vid_upload_date)s, %(vid_livestreamed)s,
            %(vid_views)s, %(vid_likes)s, %(vid_dislikes)s, %(vid_comments)s, %(vid_favorites)s,
            %(meeting_date_raw)s, %(caption_text)s, %(caption_text_clean)s, %(channel_type)s,
            %(acs_18_amind)s, %(acs_18_asian)s, %(acs_18_black)s, %(acs_18_hispanic)s,
            %(acs_18_median_age)s, %(acs_18_median_gross_rent)s, %(acs_18_median_hh_inc)s,
            %(acs_18_nhapi)s, %(acs_18_pop)s, %(acs_18_white)s
        )
        ON CONFLICT (event_id) DO UPDATE SET
            event_date = COALESCE(EXCLUDED.event_date, bronze.bronze_events_localview.event_date),
            jurisdiction_name = COALESCE(EXCLUDED.jurisdiction_name, bronze.bronze_events_localview.jurisdiction_name),
            jurisdiction_type = COALESCE(EXCLUDED.jurisdiction_type, bronze.bronze_events_localview.jurisdiction_type),
            city_name = COALESCE(EXCLUDED.city_name, bronze.bronze_events_localview.city_name),
            state_code = COALESCE(EXCLUDED.state_code, bronze.bronze_events_localview.state_code),
            state = COALESCE(EXCLUDED.state, bronze.bronze_events_localview.state),
            meeting_type = COALESCE(EXCLUDED.meeting_type, bronze.bronze_events_localview.meeting_type),
            title = COALESCE(EXCLUDED.title, bronze.bronze_events_localview.title),
            video_url = COALESCE(EXCLUDED.video_url, bronze.bronze_events_localview.video_url),
            datasource_id = COALESCE(EXCLUDED.datasource_id, bronze.bronze_events_localview.datasource_id),
            st_fips = COALESCE(EXCLUDED.st_fips, bronze.bronze_events_localview.st_fips),
            place_govt = COALESCE(EXCLUDED.place_govt, bronze.bronze_events_localview.place_govt),
            channel_title = COALESCE(EXCLUDED.channel_title, bronze.bronze_events_localview.channel_title),
            vid_title = COALESCE(EXCLUDED.vid_title, bronze.bronze_events_localview.vid_title),
            vid_desc = COALESCE(EXCLUDED.vid_desc, bronze.bronze_events_localview.vid_desc),
            vid_length_min = COALESCE(EXCLUDED.vid_length_min, bronze.bronze_events_localview.vid_length_min),
            vid_upload_date = COALESCE(EXCLUDED.vid_upload_date, bronze.bronze_events_localview.vid_upload_date),
            vid_livestreamed = COALESCE(EXCLUDED.vid_livestreamed, bronze.bronze_events_localview.vid_livestreamed),
            vid_views = COALESCE(EXCLUDED.vid_views, bronze.bronze_events_localview.vid_views),
            vid_likes = COALESCE(EXCLUDED.vid_likes, bronze.bronze_events_localview.vid_likes),
            vid_dislikes = COALESCE(EXCLUDED.vid_dislikes, bronze.bronze_events_localview.vid_dislikes),
            vid_comments = COALESCE(EXCLUDED.vid_comments, bronze.bronze_events_localview.vid_comments),
            vid_favorites = COALESCE(EXCLUDED.vid_favorites, bronze.bronze_events_localview.vid_favorites),
            meeting_date_raw = COALESCE(EXCLUDED.meeting_date_raw, bronze.bronze_events_localview.meeting_date_raw),
            caption_text = COALESCE(EXCLUDED.caption_text, bronze.bronze_events_localview.caption_text),
            caption_text_clean = COALESCE(EXCLUDED.caption_text_clean, bronze.bronze_events_localview.caption_text_clean),
            channel_type = COALESCE(EXCLUDED.channel_type, bronze.bronze_events_localview.channel_type),
            acs_18_amind = COALESCE(EXCLUDED.acs_18_amind, bronze.bronze_events_localview.acs_18_amind),
            acs_18_asian = COALESCE(EXCLUDED.acs_18_asian, bronze.bronze_events_localview.acs_18_asian),
            acs_18_black = COALESCE(EXCLUDED.acs_18_black, bronze.bronze_events_localview.acs_18_black),
            acs_18_hispanic = COALESCE(EXCLUDED.acs_18_hispanic, bronze.bronze_events_localview.acs_18_hispanic),
            acs_18_median_age = COALESCE(EXCLUDED.acs_18_median_age, bronze.bronze_events_localview.acs_18_median_age),
            acs_18_median_gross_rent = COALESCE(EXCLUDED.acs_18_median_gross_rent, bronze.bronze_events_localview.acs_18_median_gross_rent),
            acs_18_median_hh_inc = COALESCE(EXCLUDED.acs_18_median_hh_inc, bronze.bronze_events_localview.acs_18_median_hh_inc),
            acs_18_nhapi = COALESCE(EXCLUDED.acs_18_nhapi, bronze.bronze_events_localview.acs_18_nhapi),
            acs_18_pop = COALESCE(EXCLUDED.acs_18_pop, bronze.bronze_events_localview.acs_18_pop),
            acs_18_white = COALESCE(EXCLUDED.acs_18_white, bronze.bronze_events_localview.acs_18_white)
    """
    
    cursor = conn.cursor()
    inserted = 0
    
    try:
        for i in range(0, len(events), batch_size):
            batch = events[i:i + batch_size]
            execute_batch(cursor, insert_query, batch, page_size=batch_size)
            inserted += len(batch)
            conn.commit()
            
            if i % 10000 == 0 and i > 0:
                logger.info(f"  Inserted {i:,} / {len(events):,} events...")
        
        logger.success(f"  ✓ Inserted {inserted:,} events from {filepath.name}")
        return inserted
        
    except Exception as e:
        conn.rollback()
        logger.error(f"  ✗ Error inserting from {filepath.name}: {e}")
        raise
    finally:
        cursor.close()


def main():
    """Main loading function."""
    logger.info("=" * 80)
    logger.info("LOCALVIEW → POSTGRES LOADER")
    logger.info("=" * 80)
    logger.info(f"Source: {LOCALVIEW_DIR}")
    logger.info(f"Database: {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else 'localhost'}")
    logger.info("")
    
    # Find all parquet files
    parquet_files = sorted(LOCALVIEW_DIR.glob('meetings.*.parquet'))
    logger.info(f"Found {len(parquet_files)} parquet files")
    logger.info("")
    
    if not parquet_files:
        logger.error("No parquet files found!")
        return 1
    
    # Connect to database and ensure table exists
    logger.info("Connecting to database...")
    try:
        conn = psycopg2.connect(DATABASE_URL)
        logger.success("✓ Connected")
        cur = conn.cursor()
        cur.execute(CREATE_TABLE_SQL)
        conn.commit()
        cur.close()
        logger.info("✓ bronze.bronze_events_localview ready")
    except Exception as e:
        logger.error(f"✗ Database connection failed: {e}")
        return 1
    
    # Load each file
    total_inserted = 0
    start_time = datetime.now()
    
    try:
        for filepath in parquet_files:
            inserted = load_parquet_file(filepath, conn)
            total_inserted += inserted
        
        # Get final count
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM bronze.bronze_events_localview WHERE datasource = 'localview'")
        final_count = cursor.fetchone()[0]
        cursor.close()
        
        duration = (datetime.now() - start_time).total_seconds()
        
        logger.info("")
        logger.success("=" * 80)
        logger.success("✓ LOADING COMPLETE")
        logger.success("=" * 80)
        logger.success(f"Events inserted: {total_inserted:,}")
        logger.success(f"Total LocalView events in database: {final_count:,}")
        logger.success(f"Duration: {duration:.1f} seconds")
        logger.info("")
        logger.info("Next steps:")
        logger.info("1. Query events: SELECT COUNT(*), state FROM events_search WHERE source='localview' GROUP BY state")
        logger.info("2. Test search: http://localhost:5173/meetings")
        
        return 0
        
    except Exception as e:
        logger.error(f"✗ Loading failed: {e}")
        return 1
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
