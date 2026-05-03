#!/usr/bin/env python3
"""
Scrape Municipal YouTube Channels for Meeting Videos

Downloads meeting videos and metadata from municipal government YouTube channels.
Updates LocalView dataset with 2025/2026 data.

Usage:
    # Scrape all known channels
    python scripts/localview/scrape_youtube_channels.py --update
    
    # Scrape specific channels
    python scripts/localview/scrape_youtube_channels.py --channels "UCxxxxx,UCyyyyy"
    
    # Scrape by state
    python scripts/localview/scrape_youtube_channels.py --states AL,GA,IN,MA,WA,WI
"""

import argparse
import sys
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import re
import time

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from loguru import logger
import polars as pl
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from youtube_transcript_api import YouTubeTranscriptApi
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logger
logger.add(sys.stderr, format="{time} {level} {message}", level="INFO")


class MunicipalYouTubeScraper:
    """Scrape municipal government YouTube channels for meeting videos"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('YOUTUBE_API_KEY')
        if not self.api_key:
            raise ValueError("YOUTUBE_API_KEY environment variable required")
        
        self.youtube = build('youtube', 'v3', developerKey=self.api_key)
        self.cache_dir = Path("data/cache/localview")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Known municipal YouTube channels
        self.known_channels = self.load_known_channels()
    
    def load_known_channels(self) -> List[Dict]:
        """Load known municipal YouTube channels from cache"""
        channels_file = self.cache_dir / "municipality_channels.csv"
        
        if channels_file.exists():
            df = pl.read_csv(channels_file)
            return df.to_dicts()
        else:
            # Default starter list
            return [
                {"municipality": "Seattle, WA", "channel_id": "UCMFAKdxL6sATpkRqLdJyKUg", "state": "WA"},
                {"municipality": "Boston, MA", "channel_id": "UCiMB3gH6PLe-JMDhxX4ZsmA", "state": "MA"},
                # Add more as discovered
            ]
    
    def get_channel_videos(
        self,
        channel_id: str,
        max_results: int = 50,
        published_after: Optional[datetime] = None
    ) -> List[Dict]:
        """
        Get videos from a YouTube channel
        
        Args:
            channel_id: YouTube channel ID
            max_results: Maximum number of videos to return
            published_after: Only get videos after this date
        
        Returns:
            List of video dictionaries with metadata
        """
        videos = []
        
        try:
            # Get channel's uploads playlist
            channel_response = self.youtube.channels().list(
                id=channel_id,
                part='contentDetails'
            ).execute()
            
            if not channel_response.get('items'):
                logger.warning(f"Channel {channel_id} not found")
                return []
            
            uploads_playlist_id = channel_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
            
            # Get videos from uploads playlist
            next_page_token = None
            
            while len(videos) < max_results:
                playlist_request = self.youtube.playlistItems().list(
                    playlistId=uploads_playlist_id,
                    part='snippet,contentDetails',
                    maxResults=min(50, max_results - len(videos)),
                    pageToken=next_page_token
                )
                
                playlist_response = playlist_request.execute()
                
                for item in playlist_response.get('items', []):
                    snippet = item['snippet']
                    
                    # Parse published date
                    published_at = datetime.fromisoformat(snippet['publishedAt'].replace('Z', '+00:00'))
                    
                    # Filter by date if specified
                    if published_after and published_at < published_after:
                        continue
                    
                    video_id = snippet['resourceId']['videoId']
                    
                    # Get additional video details
                    video_details = self.get_video_details(video_id)
                    
                    if video_details:
                        videos.append(video_details)
                
                next_page_token = playlist_response.get('nextPageToken')
                if not next_page_token:
                    break
                
                # Rate limiting
                time.sleep(0.5)
        
        except HttpError as e:
            logger.error(f"YouTube API error for channel {channel_id}: {e}")
        
        return videos
    
    def get_video_details(self, video_id: str) -> Optional[Dict]:
        """Get detailed information about a video"""
        try:
            response = self.youtube.videos().list(
                id=video_id,
                part='snippet,contentDetails,statistics'
            ).execute()
            
            if not response.get('items'):
                return None
            
            item = response['items'][0]
            snippet = item['snippet']
            content_details = item['contentDetails']
            
            # Parse duration (ISO 8601 format: PT1H2M10S)
            duration_str = content_details['duration']
            duration_minutes = self.parse_duration(duration_str)
            
            # Check if captions available
            has_captions = content_details.get('caption', 'false') == 'true'
            
            # Detect meeting type from title
            meeting_type = self.detect_meeting_type(snippet['title'])
            
            return {
                'video_id': video_id,
                'title': snippet['title'],
                'description': snippet.get('description', ''),
                'published_at': snippet['publishedAt'],
                'channel_id': snippet['channelId'],
                'channel_title': snippet['channelTitle'],
                'duration_minutes': duration_minutes,
                'has_captions': has_captions,
                'view_count': int(item['statistics'].get('viewCount', 0)),
                'meeting_type': meeting_type,
                'video_url': f"https://www.youtube.com/watch?v={video_id}"
            }
        
        except HttpError as e:
            logger.error(f"Error getting details for video {video_id}: {e}")
            return None
    
    def parse_duration(self, duration_str: str) -> int:
        """Parse ISO 8601 duration to minutes"""
        match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', duration_str)
        if not match:
            return 0
        
        hours = int(match.group(1) or 0)
        minutes = int(match.group(2) or 0)
        seconds = int(match.group(3) or 0)
        
        return hours * 60 + minutes + (1 if seconds > 30 else 0)
    
    def detect_meeting_type(self, title: str) -> str:
        """Detect meeting type from video title"""
        title_lower = title.lower()
        
        if any(word in title_lower for word in ['city council', 'council meeting']):
            return 'City Council'
        elif any(word in title_lower for word in ['planning', 'zoning']):
            return 'Planning Commission'
        elif any(word in title_lower for word in ['school board', 'board of education']):
            return 'School Board'
        elif 'special' in title_lower:
            return 'Special Meeting'
        elif 'workshop' in title_lower:
            return 'Workshop'
        else:
            return 'Other'
    
    def scrape_channels(
        self,
        channel_ids: List[str],
        states: Optional[List[str]] = None,
        since_days: int = 30
    ) -> pl.DataFrame:
        """
        Scrape videos from multiple channels
        
        Args:
            channel_ids: List of YouTube channel IDs
            states: Filter to specific states
            since_days: Only get videos from last N days
        
        Returns:
            DataFrame with video metadata
        """
        all_videos = []
        published_after = datetime.now() - timedelta(days=since_days)
        
        for channel_info in self.known_channels:
            channel_id = channel_info['channel_id']
            
            # Filter by channel_ids if specified
            if channel_ids and channel_id not in channel_ids:
                continue
            
            # Filter by states if specified
            if states and channel_info.get('state') not in states:
                continue
            
            logger.info(f"Scraping {channel_info['municipality']} ({channel_id})")
            
            videos = self.get_channel_videos(
                channel_id,
                max_results=100,
                published_after=published_after
            )
            
            # Add municipality info
            for video in videos:
                video['municipality'] = channel_info['municipality']
                video['state'] = channel_info.get('state', 'Unknown')
            
            all_videos.extend(videos)
            logger.info(f"  Found {len(videos)} videos")
            
            # Rate limiting
            time.sleep(1)
        
        if not all_videos:
            logger.warning("No videos found")
            return pl.DataFrame()
        
        return pl.DataFrame(all_videos)
    
    def save_videos(self, videos_df: pl.DataFrame, year: int = None):
        """Save videos to LocalView format"""
        if len(videos_df) == 0:
            logger.warning("No videos to save")
            return
        
        year = year or datetime.now().year
        output_file = self.cache_dir / f"videos_{year}.csv"
        
        # Convert to LocalView format
        localview_df = videos_df.select([
            pl.col('video_id'),
            pl.col('municipality'),
            pl.col('published_at').str.slice(0, 10).alias('meeting_date'),
            pl.col('meeting_type'),
            pl.col('video_url'),
            pl.lit('youtube').alias('platform'),
            pl.col('duration_minutes'),
            pl.col('has_captions'),
            pl.col('has_captions').alias('transcript_available')
        ])
        
        # Append or create
        if output_file.exists():
            existing_df = pl.read_csv(output_file)
            combined_df = pl.concat([existing_df, localview_df])
            combined_df = combined_df.unique(subset=['video_id'])
            combined_df.write_csv(output_file)
            logger.info(f"✅ Updated {output_file} ({len(combined_df)} total videos)")
        else:
            localview_df.write_csv(output_file)
            logger.info(f"✅ Created {output_file} ({len(localview_df)} videos)")


def main():
    parser = argparse.ArgumentParser(
        description="Scrape municipal YouTube channels for meeting videos"
    )
    parser.add_argument(
        '--channels',
        type=str,
        help='Comma-separated YouTube channel IDs'
    )
    parser.add_argument(
        '--states',
        type=str,
        help='Comma-separated state codes (e.g., CA,MA,TX)'
    )
    parser.add_argument(
        '--since-days',
        type=int,
        default=30,
        help='Only get videos from last N days (default: 30)'
    )
    parser.add_argument(
        '--update',
        action='store_true',
        help='Update all known channels'
    )
    
    args = parser.parse_args()
    
    # Parse inputs
    channel_ids = None
    if args.channels:
        channel_ids = [c.strip() for c in args.channels.split(',')]
    
    states = None
    if args.states:
        states = [s.strip().upper() for s in args.states.split(',')]
    
    # Initialize scraper
    logger.info("=" * 80)
    logger.info("LOCALVIEW YOUTUBE SCRAPER")
    logger.info("=" * 80)
    
    try:
        scraper = MunicipalYouTubeScraper()
    except ValueError as e:
        logger.error(str(e))
        logger.info("\nSet YOUTUBE_API_KEY in .env file:")
        logger.info("  YOUTUBE_API_KEY=your_api_key_here")
        logger.info("\nGet an API key at: https://console.cloud.google.com/apis/credentials")
        sys.exit(1)
    
    # Scrape videos
    videos_df = scraper.scrape_channels(
        channel_ids=channel_ids,
        states=states,
        since_days=args.since_days
    )
    
    # Save results
    if len(videos_df) > 0:
        scraper.save_videos(videos_df)
        logger.success(f"\n✅ Scraped {len(videos_df)} videos")
    else:
        logger.warning("\n⚠️  No videos found")


if __name__ == "__main__":
    main()
