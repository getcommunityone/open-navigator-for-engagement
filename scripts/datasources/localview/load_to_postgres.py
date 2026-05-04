#!/usr/bin/env python3
"""
Load LocalView Meeting Data into PostgreSQL events_search table

This script reads all LocalView parquet files and inserts meeting data
into the events_search table in the open_navigator database.
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


def row_to_event(row: pd.Series) -> Dict[str, Any]:
    """Convert LocalView row to events_search format."""
    # Parse meeting date
    event_date = None
    if pd.notna(row.get('meeting_date')):
        try:
            event_date = pd.to_datetime(row['meeting_date']).date()
        except:
            pass
    
    # Build description from video description and place info
    description_parts = []
    if pd.notna(row.get('vid_desc')):
        description_parts.append(row['vid_desc'])
    if pd.notna(row.get('place_govt')):
        description_parts.append(f"Government body: {row['place_govt']}")
    if pd.notna(row.get('acs_18_pop')):
        description_parts.append(f"Population: {int(row['acs_18_pop']):,}")
    
    description = '\n\n'.join(description_parts) if description_parts else None
    
    # Extract title - use video title or create from place + date
    title = row.get('vid_title')
    if pd.isna(title) or not title:
        place = row.get('place_name', 'City Council')
        date_str = event_date.strftime('%B %d, %Y') if event_date else ''
        title = f"{place} Meeting - {date_str}" if date_str else f"{place} Meeting"
    
    return {
        'title': title[:500] if title else 'City Council Meeting',  # Limit length
        'description': description,
        'event_date': event_date,
        'event_time': None,  # LocalView doesn't have specific times
        'jurisdiction_name': row.get('place_name'),
        'jurisdiction_type': 'city',  # LocalView is municipal data
        'state': get_state_abbrev(row.get('state_name')),
        'city': row.get('place_name'),
        'location': None,  # Not provided in LocalView
        'meeting_type': row.get('place_govt', 'City Council'),
        'status': 'completed',  # All historical meetings
        'agenda_url': None,
        'minutes_url': None,  # Caption text is in description
        'video_url': construct_youtube_url(row.get('vid_id')),
        'source': 'localview'
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
    events = [row_to_event(row) for _, row in df_valid.iterrows()]
    
    # Insert into database in batches
    insert_query = """
        INSERT INTO events_search (
            title, description, event_date, event_time,
            jurisdiction_name, jurisdiction_type, state, city,
            location, meeting_type, status,
            agenda_url, minutes_url, video_url, source
        ) VALUES (
            %(title)s, %(description)s, %(event_date)s, %(event_time)s,
            %(jurisdiction_name)s, %(jurisdiction_type)s, %(state)s, %(city)s,
            %(location)s, %(meeting_type)s, %(status)s,
            %(agenda_url)s, %(minutes_url)s, %(video_url)s, %(source)s
        )
        ON CONFLICT DO NOTHING
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
    
    # Connect to database
    logger.info("Connecting to database...")
    try:
        conn = psycopg2.connect(DATABASE_URL)
        logger.success("✓ Connected")
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
        cursor.execute("SELECT COUNT(*) FROM events_search WHERE source = 'localview'")
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
