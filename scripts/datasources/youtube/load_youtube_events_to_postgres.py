#!/usr/bin/env python3
"""
Load YouTube Events from jurisdictions_details_search to events_search

This script:
1. Reads YouTube channels from jurisdictions_details_search.youtube_channels (JSONB)
2. For each channel, fetches videos using YouTube API or yt-dlp fallback
3. Fetches video transcripts (captions/subtitles) from YouTube
4. Incrementally adds/updates events in events_search table
5. Stores video transcripts in events_text_search table
6. Links events to jurisdictions via jurisdiction_id

Usage:
    # Process all jurisdictions with YouTube channels
    python scripts/datasources/youtube/load_youtube_events_to_postgres.py
    
    # Process specific states only
    python scripts/datasources/youtube/load_youtube_events_to_postgres.py --states AL,MA,WI
    
    # Process only new videos (published in last N days)
    python scripts/datasources/youtube/load_youtube_events_to_postgres.py --days 30
    
    # Limit videos per channel
    python scripts/datasources/youtube/load_youtube_events_to_postgres.py --max-videos 10
    
    # Skip transcript fetching (faster)
    python scripts/datasources/youtube/load_youtube_events_to_postgres.py --skip-transcripts
"""

import os
import sys
from pathlib import Path
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Optional, Any
import argparse
import json

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

import pandas as pd
import psycopg2
from psycopg2.extras import execute_batch, RealDictCursor
from loguru import logger
from dotenv import load_dotenv
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    TranscriptsDisabled, 
    NoTranscriptFound, 
    VideoUnavailable
)

# Import YouTube scraper (handles API and yt-dlp fallback)
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'localview'))
from scrape_youtube_channels import MunicipalYouTubeScraper

# Load environment variables
load_dotenv()

# Database connection
DATABASE_URL = os.getenv('NEON_DATABASE_URL_DEV', 'postgresql://postgres:password@localhost:5433/open_navigator')
YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')


class YouTubeEventsLoader:
    """Load YouTube videos from jurisdictions into events_search table."""
    
    def __init__(
        self,
        database_url: str,
        youtube_api_key: Optional[str] = None,
        max_videos_per_channel: int = 100,
        days_lookback: Optional[int] = None,
        fetch_transcripts: bool = True,
        force_full_fetch: bool = False
    ):
        self.database_url = database_url
        self.youtube_api_key = youtube_api_key
        self.max_videos = max_videos_per_channel
        self.days_lookback = days_lookback
        self.fetch_transcripts = fetch_transcripts
        self.force_full_fetch = force_full_fetch
        
        # Initialize YouTube scraper
        self.scraper = MunicipalYouTubeScraper(api_key=youtube_api_key)
        
        # Connect to database
        self.conn = psycopg2.connect(database_url)
        
        # Ensure tables and columns exist
        self._add_jurisdiction_id_column()
        self._create_events_text_search_table()
    
    def _add_jurisdiction_id_column(self):
        """Add jurisdiction_id column to events_search if it doesn't exist."""
        cursor = self.conn.cursor()
        
        try:
            cursor.execute("""
                ALTER TABLE events_search 
                ADD COLUMN IF NOT EXISTS jurisdiction_id VARCHAR(50);
            """)
            
            # Create index for jurisdiction_id
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_events_jurisdiction_id 
                ON events_search(jurisdiction_id);
            """)
            
            # Add unique constraint on video_url to prevent duplicates
            cursor.execute("""
                DO $$ 
                BEGIN
                    ALTER TABLE events_search 
                    ADD CONSTRAINT unique_video_url 
                    UNIQUE (video_url);
                EXCEPTION
                    WHEN duplicate_object THEN NULL;
                END $$;
            """)
            
            # Add foreign key constraint (optional - helps data integrity)
            cursor.execute("""
                DO $$ 
                BEGIN
                    ALTER TABLE events_search 
                    ADD CONSTRAINT fk_events_jurisdiction
                    FOREIGN KEY (jurisdiction_id) 
                    REFERENCES jurisdictions_details_search(jurisdiction_id)
                    ON DELETE SET NULL;
                EXCEPTION
                    WHEN duplicate_object THEN NULL;
                END $$;
            """)
            
            self.conn.commit()
            logger.success("✓ Ensured jurisdiction_id column and unique constraint exist")
            
        except Exception as e:
            self.conn.rollback()
            logger.warning(f"Note: {e}")
        finally:
            cursor.close()
    
    def _create_events_text_search_table(self):
        """Create events_text_search table if it doesn't exist."""
        cursor = self.conn.cursor()
        
        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS events_text_search (
                    id SERIAL PRIMARY KEY,
                    event_id INTEGER,
                    video_id VARCHAR(20) NOT NULL,
                    raw_text TEXT,
                    language VARCHAR(10),
                    is_auto_generated BOOLEAN DEFAULT FALSE,
                    transcript_source VARCHAR(50),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(video_id)
                );
            """)
            
            # Create indexes
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_events_text_event_id 
                ON events_text_search(event_id);
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_events_text_video_id 
                ON events_text_search(video_id);
            """)
            
            # Full-text search index on raw_text
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_events_text_search_gin 
                ON events_text_search USING GIN (to_tsvector('english', COALESCE(raw_text, '')));
            """)
            
            # Add foreign key constraint (optional - helps data integrity)
            cursor.execute("""
                DO $$ 
                BEGIN
                    ALTER TABLE events_text_search 
                    ADD CONSTRAINT fk_events_text_event
                    FOREIGN KEY (event_id) 
                    REFERENCES events_search(id)
                    ON DELETE CASCADE;
                EXCEPTION
                    WHEN duplicate_object THEN NULL;
                END $$;
            """)
            
            self.conn.commit()
            logger.success("✓ Ensured events_text_search table exists")
            
        except Exception as e:
            self.conn.rollback()
            logger.warning(f"Note: {e}")
        finally:
            cursor.close()
    
    def get_jurisdictions_with_youtube(self, states_filter: Optional[List[str]] = None) -> List[Dict]:
        """Get all jurisdictions that have YouTube channels."""
        cursor = self.conn.cursor(cursor_factory=RealDictCursor)
        
        query = """
            SELECT 
                jurisdiction_id,
                jurisdiction_name,
                state_code,
                state,
                jurisdiction_type,
                youtube_channels,
                youtube_channel_count
            FROM jurisdictions_details_search
            WHERE youtube_channel_count > 0
                AND youtube_channels IS NOT NULL
        """
        
        params = []
        if states_filter:
            query += " AND state_code = ANY(%s)"
            params.append(states_filter)
        
        query += " ORDER BY youtube_channel_count DESC, jurisdiction_name"
        
        cursor.execute(query, params)
        jurisdictions = cursor.fetchall()
        cursor.close()
        
        logger.info(f"Found {len(jurisdictions)} jurisdictions with YouTube channels")
        return jurisdictions
    
    def extract_channel_ids(self, youtube_channels_json: Any) -> List[Dict[str, str]]:
        """Extract channel IDs and metadata from youtube_channels JSONB field."""
        if not youtube_channels_json:
            return []
        
        channels = []
        
        # Handle different JSON formats
        if isinstance(youtube_channels_json, str):
            youtube_channels_json = json.loads(youtube_channels_json)
        
        if isinstance(youtube_channels_json, list):
            for item in youtube_channels_json:
                if isinstance(item, dict):
                    # Extract channel_id from various possible field names
                    channel_id = (
                        item.get('channel_id') or 
                        item.get('channelId') or
                        item.get('id')
                    )
                    
                    if channel_id:
                        channels.append({
                            'channel_id': channel_id,
                            'channel_title': item.get('channel_title') or item.get('title', ''),
                            'channel_url': item.get('channel_url') or f"https://www.youtube.com/channel/{channel_id}"
                        })
        
        return channels
    
    def video_to_event_record(
        self,
        video: Dict,
        jurisdiction_id: str,
        jurisdiction_name: str,
        jurisdiction_type: str,
        state_code: str,
        state: str
    ) -> Dict[str, Any]:
        """Convert YouTube video metadata to events_search record format."""
        
        # Parse published date
        event_date = None
        event_time = None
        if video.get('published_at'):
            try:
                dt = pd.to_datetime(video['published_at'])
                event_date = dt.date()
                event_time = dt.time()
            except:
                pass
        
        # Extract city from jurisdiction name if it's a city
        city = None
        if jurisdiction_type == 'city':
            # Remove state suffix like ", AL" from "Birmingham, AL"
            city = jurisdiction_name.split(',')[0].strip()
        
        # Build description
        description_parts = [video.get('description', '')]
        
        if video.get('view_count'):
            description_parts.append(f"Views: {video['view_count']:,}")
        if video.get('duration_minutes'):
            description_parts.append(f"Duration: {video['duration_minutes']} minutes")
        
        description = '\n\n'.join([p for p in description_parts if p])
        
        return {
            'jurisdiction_id': jurisdiction_id,
            'title': video.get('title', 'Meeting Video')[:500],  # Limit length
            'description': description,
            'event_date': event_date,
            'event_time': event_time,
            'jurisdiction_name': jurisdiction_name,
            'jurisdiction_type': jurisdiction_type,
            'state_code': state_code,
            'state': state,
            'city': city,
            'location': None,
            'meeting_type': video.get('meeting_type', 'YouTube Video'),
            'status': 'completed',
            'agenda_url': None,
            'minutes_url': None,
            'video_url': video.get('video_url'),
            'source': 'youtube',
            'last_updated': datetime.now(),
            'video_id': video.get('video_id')  # Store video_id for transcript linking
        }
    
    def fetch_transcript(self, video_id: str) -> Optional[Dict[str, Any]]:
        """Fetch transcript/captions for a YouTube video."""
        if not video_id:
            return None
        
        try:
            # Get list of available transcripts
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            
            # Try to get English transcript first (auto-generated or manual)
            try:
                transcript = transcript_list.find_transcript(['en'])
                is_auto = transcript.is_generated
                language = 'en'
            except NoTranscriptFound:
                # Fall back to any available transcript
                try:
                    transcript = transcript_list.find_generated_transcript(['en'])
                    is_auto = True
                    language = 'en'
                except:
                    # Get first available transcript
                    available = list(transcript_list)
                    if not available:
                        return None
                    transcript = available[0]
                    is_auto = transcript.is_generated
                    language = transcript.language_code
            
            # Fetch the actual transcript data
            transcript_data = transcript.fetch()
            
            # Combine all text segments
            raw_text = ' '.join([entry['text'] for entry in transcript_data])
            
            return {
                'video_id': video_id,
                'raw_text': raw_text,
                'language': language,
                'is_auto_generated': is_auto,
                'transcript_source': 'youtube_api'
            }
            
        except TranscriptsDisabled:
            logger.debug(f"    Transcripts disabled for video {video_id}")
            return None
        except NoTranscriptFound:
            logger.debug(f"    No transcript found for video {video_id}")
            return None
        except VideoUnavailable:
            logger.debug(f"    Video {video_id} unavailable")
            return None
        except Exception as e:
            logger.debug(f"    Error fetching transcript for {video_id}: {e}")
            return None
    
    def insert_events(self, events: List[Dict[str, Any]], batch_size: int = 500) -> int:
        """Insert events into events_search table."""
        if not events:
            return 0
        
        insert_query = """
            INSERT INTO events_search (
                jurisdiction_id, title, description, event_date, event_time,
                jurisdiction_name, jurisdiction_type, state_code, state, city,
                location, meeting_type, status,
                agenda_url, minutes_url, video_url, source, last_updated
            ) VALUES (
                %(jurisdiction_id)s, %(title)s, %(description)s, %(event_date)s, %(event_time)s,
                %(jurisdiction_name)s, %(jurisdiction_type)s, %(state_code)s, %(state)s, %(city)s,
                %(location)s, %(meeting_type)s, %(status)s,
                %(agenda_url)s, %(minutes_url)s, %(video_url)s, %(source)s, %(last_updated)s
            )
            ON CONFLICT DO NOTHING
            RETURNING id
        """
        
        cursor = self.conn.cursor()
        inserted = 0
        event_ids = {}  # Map video_id to event_id
        
        try:
            # Insert events and collect their IDs
            for event in events:
                cursor.execute(insert_query, event)
                result = cursor.fetchone()
                if result:
                    event_id = result[0]
                    video_id = event.get('video_id')
                    if video_id:
                        event_ids[video_id] = event_id
                    inserted += 1
            
            self.conn.commit()
            
            # Fetch and insert transcripts if enabled
            if self.fetch_transcripts and event_ids:
                logger.info(f"  Fetching transcripts for {len(event_ids)} videos...")
                transcripts_inserted = self.insert_transcripts(event_ids)
                logger.info(f"  Inserted {transcripts_inserted} transcripts")
            
            return inserted
            
        except Exception as e:
            self.conn.rollback()
            logger.error(f"Error inserting events: {e}")
            raise
        finally:
            cursor.close()
    
    def insert_transcripts(self, event_ids: Dict[str, int]) -> int:
        """Fetch and insert transcripts for events."""
        cursor = self.conn.cursor()
        inserted = 0
        
        insert_query = """
            INSERT INTO events_text_search (
                event_id, video_id, raw_text, language, 
                is_auto_generated, transcript_source
            ) VALUES (
                %(event_id)s, %(video_id)s, %(raw_text)s, %(language)s,
                %(is_auto_generated)s, %(transcript_source)s
            )
            ON CONFLICT (video_id) DO NOTHING
        """
        
        try:
            for video_id, event_id in event_ids.items():
                # Fetch transcript
                transcript_data = self.fetch_transcript(video_id)
                
                if transcript_data:
                    transcript_data['event_id'] = event_id
                    cursor.execute(insert_query, transcript_data)
                    inserted += 1
                    
                    # Commit every 10 transcripts to avoid long transactions
                    if inserted % 10 == 0:
                        self.conn.commit()
            
            self.conn.commit()
            return inserted
            
        except Exception as e:
            self.conn.rollback()
            logger.error(f"Error inserting transcripts: {e}")
            return inserted
        finally:
            cursor.close()
    
    def get_most_recent_video_date(self, jurisdiction_id: str) -> Optional[datetime]:
        """Get the most recent video date for a jurisdiction from the database."""
        cursor = self.conn.cursor()
        
        try:
            # Get the most recent video date for this specific jurisdiction
            cursor.execute("""
                SELECT MAX(event_date) 
                FROM events_search 
                WHERE jurisdiction_id = %s
                AND source = 'youtube'
                AND video_url IS NOT NULL
            """, (jurisdiction_id,))
            
            result = cursor.fetchone()
            if result and result[0]:
                # Convert date to timezone-aware datetime (UTC) for comparison with YouTube API
                naive_dt = datetime.combine(result[0], datetime.min.time())
                # Make it timezone-aware (assume UTC)
                return naive_dt.replace(tzinfo=timezone.utc)
            return None
            
        finally:
            cursor.close()
    
    def process_jurisdiction(self, jurisdiction: Dict) -> int:
        """Process all YouTube channels for a single jurisdiction."""
        jurisdiction_id = jurisdiction['jurisdiction_id']
        jurisdiction_name = jurisdiction['jurisdiction_name']
        state_code = jurisdiction['state_code']
        state = jurisdiction['state']
        jurisdiction_type = jurisdiction['jurisdiction_type']
        
        logger.info(f"Processing: {jurisdiction_name}, {state_code}")
        
        # Extract channel IDs from JSONB
        channels = self.extract_channel_ids(jurisdiction['youtube_channels'])
        
        if not channels:
            logger.warning(f"  No valid channels found in youtube_channels field")
            return 0
        
        logger.info(f"  Found {len(channels)} YouTube channel(s)")
        
        # Get most recent video date for this jurisdiction to enable incremental fetching
        most_recent_date = None
        if not self.force_full_fetch:
            most_recent_date = self.get_most_recent_video_date(jurisdiction_id)
            if most_recent_date:
                logger.info(f"  Most recent video in DB: {most_recent_date.date()}")
        else:
            logger.info(f"  Force mode: fetching all videos (ignoring existing data)")
        
        # Collect all events from all channels
        all_events = []
        
        for channel in channels:
            channel_id = channel['channel_id']
            channel_title = channel.get('channel_title', 'Unknown Channel')
            
            logger.info(f"  Fetching videos from: {channel_title} ({channel_id})")
            
            try:
                # Determine published_after date (use most recent date for incremental fetching)
                published_after = None
                if self.days_lookback:
                    published_after = datetime.now() - timedelta(days=self.days_lookback)
                    logger.info(f"    Filtering videos from last {self.days_lookback} days")
                elif most_recent_date:
                    # Incremental: only fetch videos newer than what we have
                    published_after = most_recent_date
                    logger.info(f"    Incremental: fetching videos newer than {most_recent_date.date()}")
                
                # Get videos from channel
                videos = self.scraper.get_channel_videos(
                    channel_id=channel_id,
                    max_results=self.max_videos,
                    published_after=published_after
                )
                
                if not videos:
                    logger.info(f"    No new videos found (already up to date)")
                    continue
                
                logger.info(f"    Retrieved {len(videos)} new videos")
                
                # Convert videos to event records
                for video in videos:
                    event = self.video_to_event_record(
                        video=video,
                        jurisdiction_id=jurisdiction_id,
                        jurisdiction_name=jurisdiction_name,
                        jurisdiction_type=jurisdiction_type,
                        state_code=state_code,
                        state=state
                    )
                    all_events.append(event)
                
            except Exception as e:
                logger.error(f"    Error fetching videos from channel {channel_id}: {e}")
                continue
        
        # Insert all events for this jurisdiction
        if all_events:
            inserted = self.insert_events(all_events)
            if inserted > 0:
                logger.success(f"  ✓ Inserted {inserted:,} new events")
            else:
                logger.info(f"  No new events to insert (all videos already exist)")
            return inserted
        else:
            logger.info(f"  No new videos found for this jurisdiction")
        
        return 0
    
    def run(self, states_filter: Optional[List[str]] = None):
        """Run the full loading process."""
        logger.info("=" * 80)
        logger.info("YOUTUBE EVENTS LOADER")
        logger.info("=" * 80)
        logger.info(f"Database: {self.database_url.split('@')[1] if '@' in self.database_url else 'localhost'}")
        logger.info(f"Max videos per channel: {self.max_videos}")
        logger.info(f"Fetch transcripts: {self.fetch_transcripts}")
        logger.info(f"Incremental mode: {not self.force_full_fetch}")
        if self.days_lookback:
            logger.info(f"Only videos from last {self.days_lookback} days")
        if states_filter:
            logger.info(f"States filter: {', '.join(states_filter)}")
        logger.info("")
        
        start_time = datetime.now()
        
        # Get jurisdictions with YouTube channels
        jurisdictions = self.get_jurisdictions_with_youtube(states_filter)
        
        if not jurisdictions:
            logger.warning("No jurisdictions found with YouTube channels")
            return
        
        # Process each jurisdiction
        total_inserted = 0
        for i, jurisdiction in enumerate(jurisdictions, 1):
            logger.info(f"\n[{i}/{len(jurisdictions)}] Processing jurisdiction...")
            inserted = self.process_jurisdiction(jurisdiction)
            total_inserted += inserted
        
        # Get final stats
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT 
                COUNT(*) as total_events,
                COUNT(DISTINCT jurisdiction_id) as jurisdictions_with_events,
                COUNT(DISTINCT state_code) as states,
                MIN(event_date) as earliest_date,
                MAX(event_date) as latest_date
            FROM events_search 
            WHERE source = 'youtube'
        """)
        stats = cursor.fetchone()
        
        # Get transcript stats
        cursor.execute("""
            SELECT COUNT(*) FROM events_text_search
        """)
        transcript_count = cursor.fetchone()[0]
        cursor.close()
        
        duration = (datetime.now() - start_time).total_seconds()
        
        logger.info("")
        logger.success("=" * 80)
        logger.success("✓ LOADING COMPLETE")
        logger.success("=" * 80)
        logger.success(f"New events inserted this run: {total_inserted:,}")
        logger.success(f"Total YouTube events in database: {stats[0]:,}")
        logger.success(f"Total transcripts in database: {transcript_count:,}")
        logger.success(f"Jurisdictions with events: {stats[1]:,}")
        logger.success(f"States covered: {stats[2]}")
        logger.success(f"Date range: {stats[3]} to {stats[4]}")
        logger.success(f"Duration: {duration:.1f} seconds")
        logger.info("")
        
        if total_inserted == 0:
            logger.info("No new videos found - all jurisdictions are up to date!")
        else:
            logger.info("Incremental update successful - only new videos were added.")
        
        logger.info("")
        logger.info("Next steps:")
        logger.info("1. Query events: SELECT jurisdiction_name, COUNT(*) FROM events_search WHERE source='youtube' GROUP BY jurisdiction_name ORDER BY COUNT(*) DESC LIMIT 10")
        logger.info("2. Query transcripts: SELECT COUNT(*) FROM events_text_search")
        logger.info("3. View in app: http://localhost:5173/meetings")
    
    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Load YouTube events from jurisdictions into events_search')
    
    parser.add_argument(
        '--states',
        type=str,
        help='Comma-separated list of state codes to process (e.g., AL,MA,WI)'
    )
    
    parser.add_argument(
        '--days',
        type=int,
        help='Only process videos published in the last N days'
    )
    
    parser.add_argument(
        '--max-videos',
        type=int,
        default=100,
        help='Maximum videos to fetch per channel (default: 100)'
    )
    
    parser.add_argument(
        '--skip-transcripts',
        action='store_true',
        help='Skip fetching video transcripts (faster)'
    )
    parser.add_argument(
        '--force',
        action='store_true',
        help='Force full fetch (ignore incremental mode, refetch all videos)'
    )
    
    
    args = parser.parse_args()
    
    # Parse states filter
    states_filter = None
    if args.states:
        states_filter = [s.strip().upper() for s in args.states.split(',')]
    
    # Initialize loader,
        force_full_fetch=args.force
    loader = YouTubeEventsLoader(
        database_url=DATABASE_URL,
        youtube_api_key=YOUTUBE_API_KEY,
        max_videos_per_channel=args.max_videos,
        days_lookback=args.days,
        fetch_transcripts=not args.skip_transcripts
    )
    
    try:
        loader.run(states_filter=states_filter)
        return 0
    except Exception as e:
        logger.error(f"✗ Loading failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        loader.close()


if __name__ == "__main__":
    sys.exit(main())
