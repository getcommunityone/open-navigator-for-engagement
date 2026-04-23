"""
YouTube Channel Discovery & Statistics

Enhanced discovery that:
1. Finds ALL YouTube channels (not just first match)
2. Fetches channel statistics (video count, subscribers)
3. Ranks channels by activity
4. Stores all channels found

Requires YouTube Data API v3 key (optional - falls back to scraping)
"""
import asyncio
import re
from typing import List, Dict, Optional
from datetime import datetime
import httpx
from bs4 import BeautifulSoup
from loguru import logger
import os


class YouTubeChannelDiscovery:
    """
    Comprehensive YouTube channel discovery for government entities.
    
    Strategies:
    1. Scrape government website for embedded/linked channels
    2. Search YouTube API by government name
    3. Test common handle patterns (@CityNameAL, @CityOfName, etc.)
    4. Fetch statistics for all discovered channels
    5. Rank by video count and recency
    """
    
    # Common channel handle patterns for cities
    CITY_HANDLE_PATTERNS = [
        "{city}City",           # TuscaloosaCity
        "{city}CityAL",         # TuscaloosaCityAL  
        "{city}City{state}",    # TuscaloosaCityAlabama
        "CityOf{city}",         # CityOfTuscaloosa
        "City{city}",           # CityTuscaloosa
        "{city}Alabama",        # TuscaloosaAlabama
        "{city}AL",             # TuscaloosaAL
        "{city}Gov",            # TuscaloosaGov
        "{city}Government",     # TuscaloosaGovernment
        "Official{city}",       # OfficialTuscaloosa
    ]
    
    # Common for counties
    COUNTY_HANDLE_PATTERNS = [
        "{county}County",       # TuscaloosaCounty
        "{county}CountyAL",     # TuscaloosaCountyAL
        "{county}Co",           # TuscaloosaCo
        "{county}CoAL",         # TuscaloosaCoAL
    ]
    
    def __init__(self, youtube_api_key: Optional[str] = None):
        """
        Initialize YouTube discovery.
        
        Args:
            youtube_api_key: YouTube Data API v3 key (optional)
                            Get from: https://console.cloud.google.com/
                            Falls back to scraping if not provided
        """
        self.api_key = youtube_api_key or os.getenv("YOUTUBE_API_KEY")
        self.client = httpx.AsyncClient(
            timeout=20.0,
            follow_redirects=True,
            headers={"User-Agent": "Mozilla/5.0 (compatible; OralHealthPolicyBot/2.0)"}
        )
    
    async def discover_channels(
        self,
        city_name: Optional[str],
        state_code: str,
        county_name: Optional[str] = None,
        homepage_url: Optional[str] = None
    ) -> List[Dict]:
        """
        Discover ALL YouTube channels for a jurisdiction.
        
        Args:
            city_name: City name (e.g., "Tuscaloosa")
            state_code: State code (e.g., "AL")
            county_name: County name (e.g., "Tuscaloosa County")
            homepage_url: Government website to scrape
            
        Returns:
            List of channel dictionaries with statistics:
            [
                {
                    "channel_url": "https://www.youtube.com/@TuscaloosaCityAL",
                    "channel_id": "UCxxx",
                    "channel_title": "City of Tuscaloosa",
                    "video_count": 245,
                    "subscriber_count": 1500,
                    "view_count": 50000,
                    "latest_upload": "2026-04-15",
                    "discovery_method": "pattern_match",
                    "confidence": 0.95
                },
                ...
            ]
        """
        resolved_city_name = city_name
        if not resolved_city_name and county_name:
            resolved_city_name = county_name.replace(" County", "").strip()
        if not resolved_city_name:
            logger.warning("No city or county name provided for YouTube discovery")
            return []

        logger.info(f"Discovering YouTube channels for {resolved_city_name}, {state_code}")
        
        discovered = []
        tested_urls = set()
        
        # Strategy 1: Test common handle patterns
        patterns_to_test = self._generate_handle_patterns(
            resolved_city_name, state_code, county_name
        )
        
        logger.info(f"Testing {len(patterns_to_test)} common handle patterns...")
        
        for handle in patterns_to_test:
            url = f"https://www.youtube.com/@{handle}"
            
            if url in tested_urls:
                continue
            tested_urls.add(url)
            
            channel_info = await self._check_channel_exists(url, "pattern_match")
            if channel_info:
                discovered.append(channel_info)
                logger.success(f"✓ Found: {url} ({channel_info['video_count']} videos)")
            
            # Rate limiting
            await asyncio.sleep(0.3)
        
        # Strategy 2: Scrape homepage if provided
        if homepage_url:
            logger.info(f"Scraping {homepage_url} for YouTube links...")
            scraped_channels = await self._scrape_website_for_channels(homepage_url)
            
            for url in scraped_channels:
                if url not in tested_urls:
                    tested_urls.add(url)
                    channel_info = await self._check_channel_exists(url, "website_scrape")
                    if channel_info:
                        discovered.append(channel_info)
                        logger.success(f"✓ Found: {url}")
        
        # Strategy 3: YouTube API search (if key available)
        if self.api_key:
            logger.info(f"Searching YouTube API for '{resolved_city_name}'...")
            api_channels = await self._search_youtube_api(resolved_city_name, state_code)
            
            for channel in api_channels:
                url = channel['channel_url']
                if url not in tested_urls:
                    tested_urls.add(url)
                    discovered.append(channel)
                    logger.success(f"✓ Found via API: {url}")
        
        # Deduplicate by channel_id
        seen_ids = set()
        unique_channels = []
        for channel in discovered:
            if channel.get('channel_id') and channel['channel_id'] not in seen_ids:
                seen_ids.add(channel['channel_id'])
                unique_channels.append(channel)
            elif not channel.get('channel_id'):  # No ID extracted
                unique_channels.append(channel)
        
        # Sort by video count (descending)
        unique_channels.sort(key=lambda x: x.get('video_count', 0), reverse=True)
        
        logger.success(f"✓ Total channels found: {len(unique_channels)}")
        
        return unique_channels
    
    def _generate_handle_patterns(
        self,
        city_name: str,
        state_code: str,
        county_name: Optional[str]
    ) -> List[str]:
        """Generate common handle patterns to test."""
        patterns = []
        
        # Clean city name (remove spaces, apostrophes)
        city_clean = city_name.replace(" ", "").replace("'", "")
        
        # City patterns
        for pattern in self.CITY_HANDLE_PATTERNS:
            handle = pattern.format(
                city=city_clean,
                state=state_code
            )
            patterns.append(handle)
        
        # County patterns
        if county_name:
            county_clean = county_name.replace(" County", "").replace(" ", "")
            for pattern in self.COUNTY_HANDLE_PATTERNS:
                handle = pattern.format(
                    county=county_clean,
                    state=state_code
                )
                patterns.append(handle)
        
        return patterns
    
    async def _check_channel_exists(
        self,
        channel_url: str,
        discovery_method: str
    ) -> Optional[Dict]:
        """
        Check if channel exists and extract statistics.
        
        Returns channel info dict or None if not found.
        """
        try:
            response = await self.client.get(channel_url)
            
            if response.status_code != 200:
                return None
            
            html = response.text
            
            # Extract channel statistics from page HTML
            stats = self._extract_channel_stats(html)
            
            if not stats:  # Couldn't extract stats = likely not a valid channel
                return None
            
            return {
                "channel_url": channel_url,
                "channel_id": stats.get("channel_id"),
                "channel_title": stats.get("title", "Unknown"),
                "video_count": stats.get("video_count", 0),
                "subscriber_count": stats.get("subscriber_count", 0),
                "view_count": stats.get("view_count", 0),
                "latest_upload": stats.get("latest_upload"),
                "discovery_method": discovery_method,
                "discovered_at": datetime.now().isoformat(),
                "confidence": 0.9 if discovery_method == "website_scrape" else 0.7
            }
        
        except Exception as e:
            logger.debug(f"Error checking {channel_url}: {e}")
            return None
    
    def _extract_channel_stats(self, html: str) -> Optional[Dict]:
        """
        Extract channel statistics from YouTube channel page HTML.
        
        YouTube embeds data in JavaScript objects in the page source.
        """
        stats = {}
        
        try:
            # Extract channel ID
            match = re.search(r'"channelId":"([^"]+)"', html)
            if match:
                stats['channel_id'] = match.group(1)
            
            # Extract channel title
            match = re.search(r'"channelMetadataRenderer".*?"title":"([^"]+)"', html)
            if match:
                stats['title'] = match.group(1)
            
            # Extract subscriber count
            # Pattern: "subscriberCountText":{"simpleText":"1.2K subscribers"}
            match = re.search(r'"subscriberCountText".*?"(?:simpleText|text)":"([\d.KMB]+)\s*subscribers?"', html)
            if match:
                stats['subscriber_count'] = self._parse_count(match.group(1))
            
            # Extract video count  
            # Pattern: "videosCountText":{"runs":[{"text":"245"},{"text":" videos"}]}
            match = re.search(r'"videosCountText".*?"text":"([\d,]+)"', html)
            if match:
                stats['video_count'] = int(match.group(1).replace(',', ''))
            
            # Alternative video count pattern
            if 'video_count' not in stats:
                match = re.search(r'(\d+)\s*videos?', html, re.IGNORECASE)
                if match:
                    stats['video_count'] = int(match.group(1))
            
            return stats if stats else None
        
        except Exception as e:
            logger.debug(f"Error extracting stats: {e}")
            return None
    
    def _parse_count(self, count_str: str) -> int:
        """Parse subscriber/view counts like '1.2K', '500K', '1.5M'."""
        count_str = count_str.upper().strip()
        
        multipliers = {'K': 1_000, 'M': 1_000_000, 'B': 1_000_000_000}
        
        for suffix, multiplier in multipliers.items():
            if suffix in count_str:
                number = float(count_str.replace(suffix, ''))
                return int(number * multiplier)
        
        # No suffix = literal number
        try:
            return int(count_str.replace(',', ''))
        except:
            return 0
    
    async def _scrape_website_for_channels(self, url: str) -> List[str]:
        """Scrape government website for YouTube channel links."""
        channels = []
        
        try:
            response = await self.client.get(url)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find all links
            links = soup.find_all('a', href=True)
            
            for link in links:
                href = link['href']
                # Match YouTube channel URLs
                if re.search(r'youtube\.com/(@[\w-]+|c/[\w-]+|channel/[\w-]+|user/[\w-]+)', href):
                    # Normalize to @handle format if possible
                    match = re.search(r'youtube\.com/(@[\w-]+)', href)
                    if match:
                        full_url = f"https://www.youtube.com/{match.group(1)}"
                        if full_url not in channels:
                            channels.append(full_url)
        
        except Exception as e:
            logger.debug(f"Error scraping {url}: {e}")
        
        return channels
    
    async def _search_youtube_api(
        self,
        city_name: str,
        state_code: str
    ) -> List[Dict]:
        """
        Search YouTube API for channels matching city name.
        
        Requires YouTube Data API v3 key.
        """
        if not self.api_key:
            return []
        
        channels = []
        
        try:
            # Search for channels
            search_query = f"{city_name} {state_code} government"
            api_url = "https://www.googleapis.com/youtube/v3/search"
            
            params = {
                "part": "snippet",
                "q": search_query,
                "type": "channel",
                "maxResults": 10,
                "key": self.api_key
            }
            
            response = await self.client.get(api_url, params=params)
            data = response.json()
            
            if "items" in data:
                for item in data["items"]:
                    channel_id = item["id"]["channelId"]
                    title = item["snippet"]["title"]
                    
                    # Get channel statistics
                    stats_url = "https://www.googleapis.com/youtube/v3/channels"
                    stats_params = {
                        "part": "statistics,snippet",
                        "id": channel_id,
                        "key": self.api_key
                    }
                    
                    stats_response = await self.client.get(stats_url, params=stats_params)
                    stats_data = stats_response.json()
                    
                    if "items" in stats_data and stats_data["items"]:
                        stats = stats_data["items"][0]["statistics"]
                        
                        channels.append({
                            "channel_url": f"https://www.youtube.com/channel/{channel_id}",
                            "channel_id": channel_id,
                            "channel_title": title,
                            "video_count": int(stats.get("videoCount", 0)),
                            "subscriber_count": int(stats.get("subscriberCount", 0)),
                            "view_count": int(stats.get("viewCount", 0)),
                            "discovery_method": "youtube_api",
                            "confidence": 0.95
                        })
        
        except Exception as e:
            logger.warning(f"YouTube API search failed: {e}")
        
        return channels
    
    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, *args):
        await self.close()


# Example usage
async def main():
    """Example: Discover all Tuscaloosa YouTube channels."""
    
    # Initialize (with or without API key)
    async with YouTubeChannelDiscovery() as discovery:
        
        channels = await discovery.discover_channels(
            city_name="Tuscaloosa",
            state_code="AL",
            county_name="Tuscaloosa County",
            homepage_url="https://www.tuscaloosa.com"
        )
        
        print(f"\n{'='*70}")
        print(f"FOUND {len(channels)} YOUTUBE CHANNELS")
        print(f"{'='*70}\n")
        
        for i, channel in enumerate(channels, 1):
            print(f"{i}. {channel['channel_url']}")
            print(f"   Title: {channel['channel_title']}")
            print(f"   Videos: {channel['video_count']:,}")
            print(f"   Subscribers: {channel.get('subscriber_count', 0):,}")
            print(f"   Method: {channel['discovery_method']}")
            print()


if __name__ == "__main__":
    asyncio.run(main())
