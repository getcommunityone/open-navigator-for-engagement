"""
Scraper Agent for collecting government meeting minutes from various sources.
"""
import asyncio
import hashlib
import io
import json
import re
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from urllib.parse import urljoin, urlparse
import httpx
from bs4 import BeautifulSoup
from loguru import logger

try:
    from PyPDF2 import PdfReader
except Exception:
    PdfReader = None

try:
    import pdfplumber
except Exception:
    pdfplumber = None

try:
    import pytesseract
    from pytesseract import TesseractNotFoundError
except Exception:
    pytesseract = None
    TesseractNotFoundError = Exception

try:
    from PIL import Image
except Exception:
    Image = None

try:
    from youtube_transcript_api import YouTubeTranscriptApi
except Exception:
    YouTubeTranscriptApi = None

from agents.base import BaseAgent, AgentRole, AgentMessage, MessageType, AgentStatus


class MeetingDocument(dict):
    """Structured representation of a meeting document."""
    
    def __init__(
        self,
        document_id: str,
        source_url: str,
        municipality: str,
        state: str,
        meeting_date: datetime,
        meeting_type: str,
        title: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            document_id=document_id,
            source_url=source_url,
            municipality=municipality,
            state=state,
            meeting_date=meeting_date.isoformat() if isinstance(meeting_date, datetime) else meeting_date,
            meeting_type=meeting_type,
            title=title,
            content=content,
            scraped_at=datetime.utcnow().isoformat(),
            metadata=metadata or {}
        )


class ScraperAgent(BaseAgent):
    """
    Agent responsible for scraping government meeting minutes from various sources.
    
    Supports multiple platforms:
    - Legistar (widely used by city councils)
    - Granicus (meeting management platform)
    - Generic municipal websites
    - PDF documents
    """
    
    def __init__(self, agent_id: str = "scraper-001"):
        """Initialize the scraper agent."""
        super().__init__(agent_id, AgentRole.SCRAPER)
        self.http_client: Optional[httpx.AsyncClient] = None
        self.scraped_urls: set = set()
        self.document_extensions = (".pdf", ".doc", ".docx", ".ppt", ".pptx", ".xls", ".xlsx")
        self.meeting_keywords = ("minutes", "agenda", "meeting", "council", "commission", "board")
        self.document_route_keywords = (
            "getagendafile",
            "getminutesfile",
            "download",
            "agendafile",
            "minutesfile",
        )
        self.ocr_max_pages = 10
        self._ocr_missing_tesseract_warned = False
        self.social_source_limit = 8
        
        # Policy and meeting-focused keywords for social media filtering
        self.policy_meeting_keywords = (
            # Meetings
            "council meeting", "city council", "town council", "board meeting",
            "commission meeting", "public meeting", "town hall", "session",
            "special meeting", "regular meeting", "work session", "workshop",
            # Documents
            "agenda", "minutes", "ordinance", "resolution", "public hearing",
            "hearing", "vote", "voting", "motion", "legislation",
            # Policy topics
            "policy", "budget", "zoning", "planning", "development",
            "public comment", "community meeting", "civic", "government",
            # Video/meeting specific
            "live stream", "livestream", "recorded meeting", "meeting video",
            "council session", "board session", "official meeting"
        )
        
    async def __aenter__(self):
        """Async context manager entry."""
        self.http_client = httpx.AsyncClient(
            timeout=30.0,
            follow_redirects=True,
            headers={
                "User-Agent": "OralHealthPolicyPulse/1.0 (+https://github.com/getcommunityone/oral-health-policy-pulse)"
            }
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.http_client:
            await self.http_client.aclose()
    
    async def process(self, message: AgentMessage) -> List[AgentMessage]:
        """
        Process scraping commands.
        
        Args:
            message: Command message with scraping targets
            
        Returns:
            List of messages containing scraped data
        """
        self.update_status(AgentStatus.PROCESSING, "Scraping government meeting minutes")
        
        try:
            command = message.payload.get("command")
            
            if command == "scrape":
                targets = message.payload.get("targets", [])
                date_range = message.payload.get("date_range", {})
                
                # Initialize HTTP client if not already done
                if not self.http_client:
                    async with self:
                        documents = await self._scrape_targets(targets, date_range)
                else:
                    documents = await self._scrape_targets(targets, date_range)
                
                # Send scraped documents to parser
                response = await self.send_message(
                    AgentRole.PARSER,
                    MessageType.DATA,
                    {
                        "workflow_id": message.payload.get("workflow_id"),
                        "documents": documents,
                        "count": len(documents)
                    }
                )
                
                self.log_success()
                logger.info(f"Scraped {len(documents)} documents")
                
                return [response]
            
            return []
            
        except Exception as e:
            self.log_failure(str(e))
            error_msg = await self.send_message(
                AgentRole.ORCHESTRATOR,
                MessageType.ERROR,
                {"error": str(e), "agent": self.agent_id}
            )
            return [error_msg]
    
    async def _scrape_targets(
        self,
        targets: List[Dict[str, Any]],
        date_range: Dict[str, str]
    ) -> List[Dict[str, Any]]:
        """
        Scrape multiple targets concurrently.
        
        Args:
            targets: List of scraping targets
            date_range: Date range for filtering meetings
            
        Returns:
            List of scraped documents
        """
        tasks = []
        
        for target in targets:
            platform = target.get("platform", "generic")
            url = target.get("url", "")
            
            if platform == "legistar":
                tasks.append(self._scrape_legistar(target, date_range))
            elif platform == "granicus":
                tasks.append(self._scrape_granicus(target, date_range))
            elif platform == "suiteonemedia" or "suiteonemedia" in url.lower():
                tasks.append(self._scrape_suiteonemedia(target, date_range))
            elif platform == "eboard" or "eboardsolutions.com" in url.lower() or "simbli.eboardsolutions" in url.lower():
                tasks.append(self._scrape_eboard(target, date_range))
            elif platform == "youtube":
                tasks.append(self._scrape_youtube_source(target))
            elif platform == "facebook":
                tasks.append(self._scrape_facebook_source(target))
            else:
                tasks.append(self._scrape_generic(target, date_range))
        
        # Execute all scraping tasks concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Flatten results and filter out errors
        documents = []
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Scraping error: {result}")
            elif isinstance(result, list):
                documents.extend(result)
        
        return documents

    async def scrape_social_sources(
        self,
        municipality: str,
        state: str,
        seed_url: str,
        max_sources: int = 8
    ) -> List[Dict[str, Any]]:
        """Discover and scrape YouTube/Facebook sources for a jurisdiction."""
        social_documents: List[Dict[str, Any]] = []

        homepage_url = await self._resolve_homepage_url(municipality, state, seed_url)
        if not homepage_url:
            logger.warning(f"Could not resolve homepage URL for social scraping: {municipality}, {state}")
            return social_documents

        logger.info(f"Discovering social sources from homepage: {homepage_url}")
        social_urls = await self._discover_social_urls(homepage_url, municipality, state)

        youtube_urls = list(dict.fromkeys(social_urls.get("youtube", [])))[:max_sources]
        facebook_urls = list(dict.fromkeys(social_urls.get("facebook", [])))[:max_sources]

        logger.info(
            f"Social discovery for {municipality}: "
            f"{len(youtube_urls)} YouTube, {len(facebook_urls)} Facebook"
        )

        tasks = []
        for y_url in youtube_urls:
            tasks.append(self._scrape_youtube_source({
                "url": y_url,
                "municipality": municipality,
                "state": state,
            }))
        for f_url in facebook_urls:
            tasks.append(self._scrape_facebook_source({
                "url": f_url,
                "municipality": municipality,
                "state": state,
            }))

        if not tasks:
            return social_documents

        results = await asyncio.gather(*tasks, return_exceptions=True)
        for result in results:
            if isinstance(result, Exception):
                logger.warning(f"Social scraping error: {result}")
                continue
            if isinstance(result, list):
                social_documents.extend(result)

        return social_documents

    async def _resolve_homepage_url(self, municipality: str, state: str, seed_url: str) -> str:
        """Resolve an official website homepage used for social discovery."""
        if seed_url and "suiteonemedia" not in seed_url.lower():
            parsed = urlparse(seed_url)
            return f"{parsed.scheme}://{parsed.netloc}" if parsed.scheme and parsed.netloc else seed_url

        city = (municipality or "").lower().replace(" ", "").replace("'", "")
        st = (state or "").lower()
        candidates = [
            f"https://www.{city}{st}.gov",
            f"https://{city}{st}.gov",
            f"https://www.cityof{city}.com",
            f"https://www.{city}.gov",
            f"https://www.{city}.com",
            f"https://{city}.com",
        ]

        for candidate in candidates:
            try:
                resp = await self.http_client.get(candidate, timeout=8)
                if resp.status_code < 400:
                    parsed = urlparse(str(resp.url))
                    return f"{parsed.scheme}://{parsed.netloc}"
            except Exception:
                continue

        return ""

    async def _discover_social_urls(self, homepage_url: str, municipality: str, state: str) -> Dict[str, List[str]]:
        """Discover social media URLs from homepage and YouTube pattern matching."""
        discovered = {"youtube": [], "facebook": []}

        try:
            from discovery.social_media_discovery import SocialMediaDiscovery

            async with SocialMediaDiscovery() as discovery:
                social = await discovery.discover_from_website(
                    homepage_url=homepage_url,
                    jurisdiction_name=municipality,
                    state=state,
                )
                discovered["youtube"] = social.get("youtube", [])
                discovered["facebook"] = social.get("facebook", [])
        except Exception as err:
            logger.debug(f"SocialMediaDiscovery unavailable/failed: {err}")

        # Augment YouTube discovery using handle pattern search for better recall.
        try:
            from discovery.youtube_channel_discovery import YouTubeChannelDiscovery

            async with YouTubeChannelDiscovery() as ydisc:
                channels = await ydisc.discover_channels(
                    city_name=municipality,
                    state_code=state,
                    homepage_url=homepage_url,
                )
                for channel in channels:
                    url = channel.get("channel_url")
                    if url:
                        discovered["youtube"].append(url)
        except Exception as err:
            logger.debug(f"YouTubeChannelDiscovery unavailable/failed: {err}")

        discovered["youtube"] = list(dict.fromkeys(discovered["youtube"]))
        discovered["facebook"] = list(dict.fromkeys(discovered["facebook"]))
        return discovered

    def _is_policy_meeting_content(self, text: str) -> bool:
        """Check if text content is related to policy or meetings."""
        if not text:
            return False
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in self.policy_meeting_keywords)
    
    def _extract_youtube_video_metadata(self, html: str, video_id: str) -> Dict[str, str]:
        """Extract title and description from YouTube video page HTML."""
        metadata = {"title": "", "description": ""}
        
        try:
            # Extract title from various possible patterns
            title_match = re.search(r'"title":"([^"]+)"', html)
            if title_match:
                metadata["title"] = title_match.group(1)
            else:
                # Fallback to meta tags
                title_match = re.search(r'<title>([^<]+)</title>', html)
                if title_match:
                    metadata["title"] = title_match.group(1).replace(" - YouTube", "")
            
            # Extract description
            desc_match = re.search(r'"description":"([^"]+)"', html)
            if desc_match:
                # Unescape and limit description length
                metadata["description"] = desc_match.group(1)[:500]
        
        except Exception as err:
            logger.debug(f"Error extracting metadata for video {video_id}: {err}")
        
        return metadata

    async def _scrape_youtube_source(self, target: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Scrape recent YouTube videos and transcripts from a channel URL, focusing on policy and meeting content."""
        url = target.get("url", "")
        municipality = target.get("municipality", "")
        state = target.get("state", "")

        documents: List[Dict[str, Any]] = []
        if not url:
            return documents

        videos_url = url.rstrip("/") + "/videos"
        try:
            resp = await self.http_client.get(videos_url)
            if resp.status_code >= 400:
                resp = await self.http_client.get(url)
            text = resp.text
        except Exception as err:
            logger.debug(f"Could not fetch YouTube page {url}: {err}")
            return documents

        video_ids = []
        for vid in re.findall(r'watch\?v=([A-Za-z0-9_-]{11})', text):
            if vid not in video_ids:
                video_ids.append(vid)
        
        # Process more videos initially to filter for relevant content
        video_ids = video_ids[: self.social_source_limit * 3]
        
        policy_videos = []
        
        for vid in video_ids:
            video_url = f"https://www.youtube.com/watch?v={vid}"
            
            # Fetch video page to extract metadata
            try:
                video_resp = await self.http_client.get(video_url)
                video_metadata = self._extract_youtube_video_metadata(video_resp.text, vid)
                
                # Filter: Only keep videos with policy/meeting-related titles or descriptions
                if not self._is_policy_meeting_content(video_metadata["title"]) and \
                   not self._is_policy_meeting_content(video_metadata["description"]):
                    logger.debug(f"Skipping non-policy video: {video_metadata['title']}")
                    continue
                
                logger.info(f"Found policy/meeting video: {video_metadata['title']}")
                
            except Exception as err:
                logger.debug(f"Could not fetch metadata for video {vid}: {err}")
                video_metadata = {"title": f"Video {vid}", "description": ""}
            
            # Fetch transcript
            transcript_text = self._fetch_youtube_transcript(vid)
            if not transcript_text:
                logger.debug(f"No transcript available for video {vid}")
                continue
            
            # Double-check transcript content for policy/meeting keywords
            if not self._is_policy_meeting_content(transcript_text):
                logger.debug(f"Transcript doesn't contain policy/meeting content: {vid}")
                continue

            doc_id = hashlib.md5(f"youtube-{municipality}-{vid}".encode()).hexdigest()
            policy_videos.append(MeetingDocument(
                document_id=doc_id,
                source_url=video_url,
                municipality=municipality,
                state=state,
                meeting_date=datetime.utcnow().isoformat(),
                meeting_type="YouTube Video - Policy/Meeting",
                title=video_metadata["title"] or f"YouTube Video {vid}",
                content=transcript_text,
                metadata={
                    "platform": "youtube",
                    "channel_url": url,
                    "video_id": vid,
                    "has_transcript": True,
                    "description": video_metadata["description"],
                    "filtered_for_policy": True,
                }
            ))
            
            # Limit to configured number of policy videos
            if len(policy_videos) >= self.social_source_limit:
                break
            
            # Rate limiting
            await asyncio.sleep(0.5)

        logger.info(f"Found {len(policy_videos)} policy/meeting videos from {url}")
        return policy_videos

    async def _scrape_facebook_source(self, target: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Scrape publicly accessible Facebook page/post text snippets, focusing on policy and meeting content."""
        url = target.get("url", "")
        municipality = target.get("municipality", "")
        state = target.get("state", "")

        documents: List[Dict[str, Any]] = []
        if not url:
            return documents

        normalized = url.replace("www.facebook.com", "m.facebook.com")
        try:
            resp = await self.http_client.get(normalized)
            if resp.status_code >= 400:
                return documents
            soup = BeautifulSoup(resp.content, "html.parser")
        except Exception as err:
            logger.debug(f"Could not fetch Facebook page {url}: {err}")
            return documents

        # Try to extract links to individual post pages first.
        post_links: List[str] = []
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if "/posts/" in href or "/videos/" in href:
                full = urljoin(normalized, href)
                if full not in post_links:
                    post_links.append(full)
        post_links = post_links[: self.social_source_limit * 2]  # Check more posts to filter

        # If direct post links are unavailable, use page text as fallback content.
        if not post_links:
            page_text = soup.get_text(" ", strip=True)
            # Filter: Only use page content if it contains policy/meeting keywords
            if len(page_text) > 200 and self._is_policy_meeting_content(page_text):
                doc_id = hashlib.md5(f"facebook-page-{municipality}-{url}".encode()).hexdigest()
                documents.append(MeetingDocument(
                    document_id=doc_id,
                    source_url=url,
                    municipality=municipality,
                    state=state,
                    meeting_date=datetime.utcnow().isoformat(),
                    meeting_type="Facebook Page - Policy/Meeting",
                    title="Facebook Page Content (Policy-Related)",
                    content=page_text[:8000],
                    metadata={
                        "platform": "facebook",
                        "content_source": "page_fallback",
                        "filtered_for_policy": True,
                    }
                ))
            else:
                logger.debug(f"Facebook page content doesn't contain policy/meeting keywords: {url}")
            return documents

        policy_posts = []
        for post_url in post_links:
            try:
                p_resp = await self.http_client.get(post_url)
                if p_resp.status_code >= 400:
                    continue
                p_soup = BeautifulSoup(p_resp.content, "html.parser")
                post_text = p_soup.get_text(" ", strip=True)
                if len(post_text) < 120:
                    continue
                
                # Filter: Only keep posts that mention policy/meeting keywords
                if not self._is_policy_meeting_content(post_text):
                    logger.debug(f"Skipping non-policy Facebook post: {post_url[:80]}...")
                    continue
                
                logger.info(f"Found policy/meeting Facebook post: {post_url[:80]}...")

                doc_id = hashlib.md5(f"facebook-post-{municipality}-{post_url}".encode()).hexdigest()
                policy_posts.append(MeetingDocument(
                    document_id=doc_id,
                    source_url=post_url,
                    municipality=municipality,
                    state=state,
                    meeting_date=datetime.utcnow().isoformat(),
                    meeting_type="Facebook Post - Policy/Meeting",
                    title="Facebook Post (Policy-Related)",
                    content=post_text[:8000],
                    metadata={
                        "platform": "facebook",
                        "content_source": "post",
                        "filtered_for_policy": True,
                    }
                ))
                
                # Limit to configured number of policy posts
                if len(policy_posts) >= self.social_source_limit:
                    break
                    
                # Rate limiting
                await asyncio.sleep(0.5)
                
            except Exception as err:
                logger.debug(f"Could not parse Facebook post {post_url}: {err}")

        logger.info(f"Found {len(policy_posts)} policy/meeting Facebook posts from {url}")
        return policy_posts

    def _fetch_youtube_transcript(self, video_id: str) -> str:
        """Return concatenated YouTube transcript text when available."""
        if YouTubeTranscriptApi is None:
            return ""

        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=["en"])
            return " ".join(chunk.get("text", "") for chunk in transcript if chunk.get("text")).strip()
        except Exception:
            return ""
    
    async def _scrape_legistar(
        self,
        target: Dict[str, Any],
        date_range: Dict[str, str]
    ) -> List[Dict[str, Any]]:
        """
        Scrape meeting minutes from Legistar platform using the official API.
        
        Legistar provides a REST API at https://webapi.legistar.com/v1/{city}/
        This is much more reliable than HTML scraping.
        
        Args:
            target: Target configuration with 'url' and 'municipality'
            date_range: Date range for filtering (optional)
            
        Returns:
            List of meeting documents
        """
        base_url = target["url"]
        municipality = target["municipality"]
        state = target["state"]
        
        # Extract city slug from URL (e.g., "chicago" from "chicago.legistar.com")
        parsed = urlparse(base_url)
        hostname = parsed.hostname or ""
        city_slug = hostname.split('.')[0] if '.' in hostname else municipality.lower().replace(' ', '')
        
        # Use the official Legistar API
        api_base = f"https://webapi.legistar.com/v1/{city_slug}"
        
        documents = []
        
        try:
            # Build OData filter for date range
            params = {
                "$top": 100,  # Limit to 100 most recent meetings
                "$orderby": "EventDate desc"
            }
            
            if date_range and "start" in date_range:
                params["$filter"] = f"EventDate ge datetime'{date_range['start']}'"
            
            # Get events (meetings)
            events_url = f"{api_base}/events"
            logger.info(f"Fetching Legistar events from {events_url}")
            
            response = await self.http_client.get(events_url, params=params)
            response.raise_for_status()
            events = response.json()
            
            logger.info(f"Found {len(events)} events for {municipality}")
            
            # Process each event
            for event in events[:50]:  # Limit to 50 meetings
                event_id = event.get("EventId")
                event_guid = event.get("EventGuid")
                
                if not event_id:
                    continue
                
                # Get agenda items for this event
                try:
                    items_url = f"{api_base}/events/{event_id}/EventItems"
                    items_response = await self.http_client.get(items_url, timeout=10)
                    
                    if items_response.status_code == 200:
                        items = items_response.json()
                        
                        # Create document from event and items
                        doc = self._create_legistar_document(
                            event,
                            items,
                            municipality,
                            state,
                            base_url
                        )
                        
                        if doc:
                            documents.append(doc)
                    
                    # Rate limiting - be respectful
                    await asyncio.sleep(0.3)
                    
                except Exception as item_error:
                    logger.warning(f"Error fetching items for event {event_id}: {item_error}")
                    continue
        
        except Exception as e:
            logger.error(f"Error scraping Legistar API for {municipality}: {e}")
        
        return documents
    
    def _create_legistar_document(
        self,
        event: Dict[str, Any],
        items: List[Dict[str, Any]],
        municipality: str,
        state: str,
        base_url: str
    ) -> Optional[Dict[str, Any]]:
        """
        Create a meeting document from Legistar API data.
        
        Args:
            event: Event data from API
            items: Agenda items from API
            municipality: Municipality name
            state: State code
            base_url: Base URL for constructing links
            
        Returns:
            Meeting document dict or None
        """
        try:
            event_id = event.get("EventId")
            event_date = event.get("EventDate", "")
            event_body = event.get("EventBodyName", "Unknown Body")
            
            # Combine agenda items into content
            content_parts = [f"Meeting: {event_body}", f"Date: {event_date}", "\n=== AGENDA ===\n"]
            
            for item in items:
                agenda_num = item.get("EventItemAgendaNumber", "")
                title = item.get("EventItemTitle", "")
                matter_file = item.get("EventItemMatterFile", "")
                
                if title:
                    item_text = f"\n{agenda_num}. {title}"
                    if matter_file:
                        item_text += f" (File: {matter_file})"
                    content_parts.append(item_text)
            
            content = "\n".join(content_parts)
            
            # Generate document ID
            doc_id = hashlib.md5(
                f"{municipality}-{state}-{event_id}".encode()
            ).hexdigest()
            
            # Create meeting detail URL
            parsed = urlparse(base_url)
            hostname = parsed.hostname or base_url
            meeting_url = f"https://{hostname}/MeetingDetail.aspx?ID={event_id}"
            
            return MeetingDocument(
                document_id=doc_id,
                source_url=meeting_url,
                municipality=municipality,
                state=state,
                meeting_date=event_date,
                meeting_type=event_body,
                title=f"{event_body} - {event_date}",
                content=content,
                metadata={
                    "event_id": event_id,
                    "event_guid": event.get("EventGuid"),
                    "event_time": event.get("EventTime"),
                    "event_location": event.get("EventLocation"),
                    "video_status": event.get("EventVideoStatus"),
                    "agenda_status": event.get("EventAgendaStatusName"),
                    "minutes_status": event.get("EventMinutesStatusName"),
                    "item_count": len(items),
                    "platform": "legistar_api"
                }
            )
        
        except Exception as e:
            logger.error(f"Error creating document from Legistar data: {e}")
            return None
    
    async def _scrape_granicus(
        self,
        target: Dict[str, Any],
        date_range: Dict[str, str]
    ) -> List[Dict[str, Any]]:
        """
        Scrape meeting minutes from Granicus platform.
        
        Args:
            target: Target configuration
            date_range: Date range for filtering
            
        Returns:
            List of meeting documents
        """
        base_url = target["url"]
        municipality = target["municipality"]
        state = target["state"]
        
        documents = []
        
        try:
            # Granicus often has an API endpoint
            api_url = urljoin(base_url, "api/v1/meetings")
            
            response = await self.http_client.get(api_url)
            response.raise_for_status()
            
            meetings_data = response.json()
            
            for meeting in meetings_data.get("meetings", [])[:50]:
                meeting_id = meeting.get("id")
                meeting_url = urljoin(base_url, f"meeting/{meeting_id}")
                
                if meeting_url in self.scraped_urls:
                    continue
                
                doc = await self._scrape_meeting_page(
                    meeting_url,
                    municipality,
                    state,
                    meeting_data=meeting
                )
                
                if doc:
                    documents.append(doc)
                    self.scraped_urls.add(meeting_url)
                
                await asyncio.sleep(0.5)
        
        except Exception as e:
            logger.error(f"Error scraping Granicus {base_url}: {e}")
        
        return documents

    async def _scrape_suiteonemedia(
        self,
        target: Dict[str, Any],
        date_range: Dict[str, str]
    ) -> List[Dict[str, Any]]:
        """
        Scrape meeting events from a SuiteOne Media portal.

        Strategy:
        1. Fetch the portal homepage — it renders ALL current-year events as
           /event/?id=XXXX anchor links.
          2. Parse each <tr> in the eventTable to get: event ID, title, date,
              agenda/minutes PDF links, and whether a media recording exists.
          3. For events with media (or missing title/date), fetch the event page
              to extract the S3 MP4 video recording URL from jwplayer setup.
          4. Download PDFs for text extraction.
          5. Extend backwards through historical event IDs when max_events > homepage count.

        Parameters via target dict:
          max_events  - maximum events to process (default 500, 0 = unlimited)
          start_year  - only include events on/after this year (0 = all)
                  fetch_videos - whether to fetch event pages for S3 video URLs (default True)
        """
        url = target["url"]
        municipality = target.get("municipality", "")
        state = target.get("state", "")
        max_events: int = int(target.get("max_events", 500))
        start_year: int = int(target.get("start_year", 0))
        fetch_videos: bool = bool(target.get("fetch_videos", True))

        parsed = urlparse(url)
        base_url = f"{parsed.scheme}://{parsed.netloc}"

        documents: List[Dict[str, Any]] = []

        try:
            # ---- Step 1: fetch homepage and parse event table rows ----
            logger.info(f"Fetching SuiteOne homepage: {base_url}/Web/Home.aspx")
            home_resp = await self.http_client.get(f"{base_url}/Web/Home.aspx")
            home_resp.raise_for_status()
            home_soup = BeautifulSoup(home_resp.content, "html.parser")

            # Each <tr> in an eventTable contains: event link, agenda/minutes PDF links, date text
            events: list[dict] = []
            seen_event_ids: set[int] = set()

            for table in home_soup.find_all("table", class_=re.compile("eventTable", re.I)):
                for tr in table.find_all("tr"):
                    row_links = [(a["href"], a.get_text(" ", strip=True)) for a in tr.find_all("a", href=True)]
                    row_text = tr.get_text(" ", strip=True)

                    event_id = None
                    event_title = ""
                    agenda_url = ""
                    minutes_url = ""
                    has_media = False

                    for href, text in row_links:
                        m = re.match(r'/event/\?id=(\d+)', href)
                        if m:
                            eid = int(m.group(1))
                            if event_id is None:
                                event_id = eid
                                event_title = re.sub(r'\(opens in new window\)', '', text).strip()
                        elif "getagendafile" in href.lower():
                            agenda_url = self._normalize_document_url(urljoin(base_url, href))
                        elif "getminutesfile" in href.lower():
                            minutes_url = self._normalize_document_url(urljoin(base_url, href))
                        if "media" in text.lower():
                            has_media = True

                    if event_id is None or event_id in seen_event_ids:
                        continue
                    seen_event_ids.add(event_id)

                    date_m = re.search(
                        r'((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w*'
                        r'\s+\d{1,2},?\s*\d{4}(?:\s*\|\s*\d{2}:\d{2}\s*[AP]M)?)',
                        row_text, re.I
                    )
                    meeting_date = date_m.group(1).strip() if date_m else ""

                    year_m = re.search(r'\b(20\d{2})\b', meeting_date)
                    if start_year and year_m and int(year_m.group(1)) < start_year:
                        continue

                    events.append({
                        "id": event_id,
                        "title": event_title,
                        "date": meeting_date,
                        "agenda_url": agenda_url,
                        "minutes_url": minutes_url,
                        "has_media": has_media,
                    })

            logger.info(
                f"Parsed {len(events)} events from SuiteOne homepage table "
                f"({len([e for e in events if e['agenda_url']])} with agenda, "
                f"{len([e for e in events if e['minutes_url']])} with minutes, "
                f"{len([e for e in events if e['has_media']])} with media)"
            )

            # ---- Step 2: extend with historical events if needed ----
            if events and (max_events == 0 or max_events > len(events)):
                lowest_id = min(e["id"] for e in events)
                logger.info(f"Probing historical events below ID {lowest_id}")
                for eid in range(lowest_id - 1, max(1, lowest_id - 5000), -1):
                    if eid not in seen_event_ids:
                        seen_event_ids.add(eid)
                        events.append({
                            "id": eid, "title": "", "date": "", "agenda_url": "",
                            "minutes_url": "", "has_media": True,
                        })
                logger.info(f"Expanded to {len(events)} total events (including historical)")

            events.sort(key=lambda e: e["id"], reverse=True)
            if max_events > 0:
                events = events[:max_events]

            logger.info(f"Processing {len(events)} SuiteOne events for {municipality}")

            # ---- Step 3 & 4: for each event, fetch video URL + download PDFs ----
            for i, ev in enumerate(events):
                eid = ev["id"]
                event_url = f"{base_url}/event/?id={eid}"

                meeting_date = ev["date"]
                meeting_title = ev["title"]
                meeting_type = re.sub(r'^\d+:\d+\s*[ap]\.m\.\s*', '', meeting_title, flags=re.I).strip() or "Meeting"
                video_url = ""

                # Fetch event page when: has media flag, or missing title/date
                if ev["has_media"] or not meeting_title or not meeting_date:
                    try:
                        ev_resp = await self.http_client.get(event_url)
                        if ev_resp.status_code == 404:
                            continue
                        ev_resp.raise_for_status()
                        ev_text = ev_resp.text
                        ev_soup = BeautifulSoup(ev_resp.content, "html.parser")

                        title_tag = ev_soup.find("title")
                        if title_tag:
                            page_title = title_tag.get_text(strip=True).replace("Meeting:", "").strip()
                            if "upcoming meetings" in page_title.lower():
                                continue
                            if not meeting_title:
                                meeting_title = page_title
                                meeting_type = re.sub(r'^\d+:\d+\s*[ap]\.m\.\s*', '', meeting_title, flags=re.I).strip() or "Meeting"

                        if not meeting_date:
                            dm = re.search(
                                r'((?:January|February|March|April|May|June|July|August|'
                                r'September|October|November|December)\s+\d{1,2},?\s*\d{4})',
                                ev_text
                            )
                            meeting_date = dm.group(1) if dm else ""

                        year_m = re.search(r'\b(20\d{2})\b', meeting_date)
                        if start_year and year_m and int(year_m.group(1)) < start_year:
                            continue

                        if fetch_videos:
                            src_m = re.search(r"var src\s*=\s*'([^']+)';", ev_text)
                            if src_m and src_m.group(1):
                                video_url = src_m.group(1)

                        for a in ev_soup.find_all("a", href=True):
                            href = a["href"]
                            full = self._normalize_document_url(urljoin(base_url, href))
                            if "getagendafile" in full.lower() and not ev["agenda_url"]:
                                ev["agenda_url"] = full
                            elif "getminutesfile" in full.lower() and not ev["minutes_url"]:
                                ev["minutes_url"] = full

                        await asyncio.sleep(0.2)

                    except Exception as fetch_err:
                        logger.debug(f"Could not fetch event page {eid}: {fetch_err}")

                doc_urls = [(ev["agenda_url"], "Agenda"), (ev["minutes_url"], "Minutes")]
                produced = 0
                for doc_url, doc_type in doc_urls:
                    if not doc_url or doc_url in self.scraped_urls:
                        continue
                    doc = await self._scrape_document(
                        url=doc_url,
                        municipality=municipality,
                        state=state,
                        title=f"{meeting_title} — {doc_type}",
                    )
                    if doc:
                        doc["meeting_date"] = meeting_date
                        doc["meeting_type"] = meeting_type
                        meta = doc.setdefault("metadata", {})
                        meta["platform"] = "suiteonemedia"
                        meta["event_id"] = eid
                        meta["doc_type"] = doc_type.lower()
                        if video_url:
                            meta["video_url"] = video_url
                        documents.append(doc)
                        self.scraped_urls.add(doc_url)
                        produced += 1

                if produced == 0 and meeting_title and "upcoming meetings" not in meeting_title.lower():
                    doc_id = hashlib.md5(event_url.encode()).hexdigest()
                    documents.append(MeetingDocument(
                        document_id=doc_id,
                        source_url=event_url,
                        municipality=municipality,
                        state=state,
                        meeting_date=meeting_date or datetime.utcnow().isoformat(),
                        meeting_type=meeting_type,
                        title=meeting_title,
                        content="",
                        metadata={
                            "platform": "suiteonemedia",
                            "event_id": eid,
                            "video_url": video_url,
                            "has_pdf": False,
                        }
                    ))

                if (i + 1) % 50 == 0:
                    logger.info(
                        f"  SuiteOne: {i+1}/{len(events)} events processed, "
                        f"{len(documents)} docs so far"
                    )

                await asyncio.sleep(0.3)

        except Exception as e:
            logger.error(f"Error scraping SuiteOne portal {url}: {e}")

        logger.info(f"SuiteOne scrape complete: {len(documents)} documents from {municipality}")
        return documents

    async def _scrape_eboard(
        self,
        target: Dict[str, Any],
        date_range: Dict[str, str]
    ) -> List[Dict[str, Any]]:
        """
        Scrape eBoard Solutions platform (used by many school districts).
        
        eBoard uses ASP.NET with JavaScript and Incapsula bot protection.
        This implementation uses Playwright Stealth + optional manual cookies.
        
        To bypass Incapsula:
        1. Run without cookies first (will likely get blocked)
        2. Manually visit the site in browser, solve any CAPTCHA
        3. Export cookies using browser extension (EditThisCookie)
        4. Save to eboard_cookies.json
        5. Re-run scraper (will use cookies automatically)
        
        Args:
            target: Scraping target with URL, municipality, state
            date_range: Date range for filtering meetings
            
        Returns:
            List of meeting documents
        """
        url = target.get("url", "")
        municipality = target.get("municipality", "Unknown")
        state = target.get("state", "")
        
        logger.info(f"Scraping eBoard platform: {url} for {municipality}")
        
        documents = []
        
        try:
            from playwright.async_api import async_playwright
            from playwright_stealth import Stealth
            import random
            from pathlib import Path
            
            # Extract school ID from URL (S=xxxx parameter)
            import re
            school_id_match = re.search(r'[?&]s=(\d+)', url, re.IGNORECASE)
            school_id = school_id_match.group(1) if school_id_match else None
            
            if not school_id:
                logger.error(f"Could not extract school ID from URL: {url}")
                return []
            
            # Target the Meeting Listing page directly (bypasses some Incapsula triggers)
            base_url = "https://simbli.eboardsolutions.com"
            meetings_url = f"{base_url}/SB_Meetings/SB_MeetingListing.aspx?S={school_id}"
            
            # Check for manual cookies file
            cookie_file = Path("eboard_cookies.json")
            cookies = None
            if cookie_file.exists():
                try:
                    import json
                    with open(cookie_file, 'r') as f:
                        cookies = json.load(f)
                    logger.success(f"✓ Loaded {len(cookies)} cookies from eboard_cookies.json")
                    logger.info("Using manual session cookies to bypass Incapsula")
                except Exception as e:
                    logger.warning(f"Could not load cookies: {e}")
            else:
                logger.info("No cookie file found. Will attempt without cookies (may be blocked)")
                logger.info(f"To bypass Incapsula: Create {cookie_file.absolute()}")
                logger.info("See docs/EBOARD_MANUAL_DOWNLOAD.md for instructions")
            
            logger.info(f"Targeting Meeting Listing: {meetings_url}")
            
            async with async_playwright() as p:
                # Launch browser with anti-detection settings
                logger.info("Launching browser with stealth settings to bypass Incapsula")
                browser = await p.chromium.launch(
                    headless=True,  # Stealth makes headless work
                    args=[
                        '--disable-blink-features=AutomationControlled',
                        '--disable-dev-shm-usage',
                        '--no-sandbox'
                    ]
                )
                
                # CRITICAL: User-Agent must match the browser used to generate cookies
                # If cookies were from Chrome 123, use Chrome 123 UA
                user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
                
                context = await browser.new_context(
                    viewport={'width': 1920, 'height': 1080},
                    user_agent=user_agent,
                    locale='en-US',
                    timezone_id='America/Chicago',
                    # Additional fingerprinting evasion
                    geolocation={'latitude': 33.2098, 'longitude': -87.5692},  # Tuscaloosa, AL
                    permissions=['geolocation']
                )
                
                page = await context.new_page()
                
                # Apply stealth to bypass Incapsula fingerprinting
                stealth = Stealth()
                await stealth.apply_stealth_async(page)
                logger.info("Stealth mode activated")
                
                # Inject cookies if available (CRITICAL for bypassing Incapsula)
                if cookies:
                    await context.add_cookies(cookies)
                    logger.success("✓ Cookies injected into browser session")
                
                # Navigate to Meeting Listing
                logger.info(f"Loading Meeting Listing page...")
                try:
                    # Simulate human behavior - move mouse before navigation
                    await page.mouse.move(random.randint(100, 500), random.randint(100, 500))
                    
                    response = await page.goto(meetings_url, wait_until='networkidle', timeout=60000)
                    logger.info(f"Response status: {response.status if response else 'No response'}")
                except Exception as e:
                    logger.warning(f"Navigation timeout/error: {e}, continuing anyway...")
                
                # Wait for Incapsula JavaScript challenge to complete
                # CRITICAL: Use randomized delay (not flat sleep) to avoid pattern detection
                wait_time = random.uniform(5.0, 7.0)
                logger.info(f"Waiting {wait_time:.1f}s for Incapsula JavaScript challenge...")
                await page.wait_for_timeout(int(wait_time * 1000))
                
                # Check if we got through
                content = await page.content()
                
                if 'Incapsula' in content or len(content) < 5000:
                    logger.error(f"Still blocked by Incapsula ({len(content)} bytes)")
                    logger.warning(f"Try running with headless=False or use manual session cookies")
                    logger.info(f"See docs/EBOARD_MANUAL_DOWNLOAD.md for manual download guide")
                    await browser.close()
                    return []
                
                logger.success(f"✓ Bypassed Incapsula! Got {len(content)} bytes")
                
                # Parse the page
                soup = BeautifulSoup(content, 'html.parser')
                
                # Extract meeting links - eBoard uses MID parameter
                # Look for links containing "MID=" (Meeting ID)
                meeting_links = []
                
                for link in soup.find_all('a', href=True):
                    href = link.get('href', '')
                    text = link.get_text().strip()
                    
                    # eBoard meeting detail links contain MID parameter
                    if 'MID=' in href.upper() or 'meetingdetail' in href.lower():
                        full_url = urljoin(base_url, href)
                        meeting_links.append({
                            'url': full_url,
                            'text': text,
                            'mid': re.search(r'MID=(\d+)', href, re.IGNORECASE).group(1) if re.search(r'MID=(\d+)', href, re.IGNORECASE) else None
                        })
                
                # Also look for direct PDF links (agendas/minutes)
                for link in soup.find_all('a', href=True):
                    href = link.get('href', '')
                    text = link.get_text().strip()
                    
                    if href.lower().endswith('.pdf') and any(word in text.lower() for word in ['agenda', 'minutes', 'packet']):
                        full_url = urljoin(base_url, href)
                        meeting_links.append({
                            'url': full_url,
                            'text': text,
                            'type': 'pdf'
                        })
                
                logger.info(f"Found {len(meeting_links)} meeting/document links")
                
                # Process each meeting (limit to prevent overwhelming)
                for idx, meeting_info in enumerate(meeting_links[:50]):
                    try:
                        meeting_url = meeting_info['url']
                        meeting_title = meeting_info['text']
                        
                        if idx > 0 and idx % 10 == 0:
                            logger.info(f"  Progress: {idx}/{min(50, len(meeting_links))} meetings processed")
                        
                        # CRITICAL: Randomized rate limiting to prevent Advanced Mode trigger
                        # Never use flat sleep - Incapsula detects patterns
                        wait_time = random.uniform(3.0, 7.0)
                        await asyncio.sleep(wait_time)
                        
                        # Simulate human mouse movement before each action
                        await page.mouse.move(random.randint(200, 800), random.randint(200, 600))
                        
                        # Handle PDF links directly
                        if meeting_info.get('type') == 'pdf':
                            try:
                                # Download PDF
                                pdf_content = await self._scrape_pdf_document(meeting_url)
                                
                                if pdf_content and len(pdf_content.strip()) > 100:
                                    # Extract date from title/text
                                    meeting_date = None
                                    try:
                                        from dateutil import parser as date_parser
                                        date_match = re.search(r'(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})', meeting_title)
                                        if not date_match:
                                            date_match = re.search(r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}', meeting_title, re.IGNORECASE)
                                        
                                        if date_match:
                                            meeting_date = date_parser.parse(date_match.group(0))
                                    except:
                                        meeting_date = datetime.now()
                                    
                                    if not meeting_date:
                                        meeting_date = datetime.now()
                                    
                                    document_id = hashlib.md5(f"{meeting_url}{municipality}".encode()).hexdigest()
                                    
                                    doc = MeetingDocument(
                                        document_id=document_id,
                                        source_url=meeting_url,
                                        municipality=municipality,
                                        state=state,
                                        meeting_date=meeting_date,
                                        meeting_type='Board Meeting',
                                        title=meeting_title,
                                        content=pdf_content[:50000],
                                        metadata={
                                            'platform': 'eboard',
                                            'school_id': school_id,
                                            'scraped_with': 'playwright_stealth'
                                        }
                                    )
                                    
                                    documents.append(doc)
                                    logger.success(f"    ✓ Scraped PDF: {meeting_title[:50]}")
                            
                            except Exception as e:
                                logger.error(f"    Error downloading PDF: {e}")
                                continue
                        
                        # Handle meeting detail pages
                        else:
                            logger.debug(f"  Loading meeting detail: {meeting_title[:50]}")
                            
                            try:
                                # Simulate clicking on link (human-like behavior)
                                await page.mouse.move(random.randint(300, 700), random.randint(200, 500))
                                await page.goto(meeting_url, wait_until='domcontentloaded', timeout=30000)
                                
                                # Random wait to appear human
                                await page.wait_for_timeout(random.randint(1500, 3000))
                                
                                meeting_content = await page.content()
                                meeting_soup = BeautifulSoup(meeting_content, 'html.parser')
                                
                                # Extract meeting date
                                meeting_date = None
                                for elem in meeting_soup.find_all(['h1', 'h2', 'h3', 'div', 'span']):
                                    text = elem.get_text().strip()
                                    date_match = re.search(r'(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})', text)
                                    if not date_match:
                                        date_match = re.search(r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}', text, re.IGNORECASE)
                                    
                                    if date_match:
                                        try:
                                            from dateutil import parser as date_parser
                                            meeting_date = date_parser.parse(date_match.group(0))
                                            break
                                        except:
                                            pass
                                
                                if not meeting_date:
                                    meeting_date = datetime.now()
                                
                                # Find document links (PDFs)
                                doc_links = []
                                for link in meeting_soup.find_all('a', href=True):
                                    href = link.get('href', '')
                                    link_text = link.get_text().strip()
                                    
                                    if (href.lower().endswith('.pdf') or 
                                        'agenda' in link_text.lower() or 
                                        'minutes' in link_text.lower() or
                                        'packet' in link_text.lower()):
                                        
                                        doc_url = urljoin(base_url, href)
                                        doc_links.append({
                                            'url': doc_url,
                                            'text': link_text
                                        })
                                
                                logger.info(f"    Found {len(doc_links)} documents for {meeting_title[:40]}")
                                
                                # Download each document
                                for doc_info in doc_links[:5]:  # Limit per meeting
                                    try:
                                        doc_url = doc_info['url']
                                        doc_title = doc_info['text']
                                        
                                        if doc_url.lower().endswith('.pdf'):
                                            doc_content = await self._scrape_pdf_document(doc_url)
                                            
                                            if doc_content and len(doc_content.strip()) > 100:
                                                document_id = hashlib.md5(f"{doc_url}{municipality}".encode()).hexdigest()
                                                
                                                doc = MeetingDocument(
                                                    document_id=document_id,
                                                    source_url=doc_url,
                                                    municipality=municipality,
                                                    state=state,
                                                    meeting_date=meeting_date,
                                                    meeting_type='Board Meeting',
                                                    title=doc_title or meeting_title,
                                                    content=doc_content[:50000],
                                                    metadata={
                                                        'platform': 'eboard',
                                                        'meeting_page': meeting_url,
                                                        'school_id': school_id,
                                                        'meeting_id': meeting_info.get('mid'),
                                                        'scraped_with': 'playwright_stealth'
                                                    }
                                                )
                                                
                                                documents.append(doc)
                                                logger.success(f"      ✓ Scraped: {doc_title[:50]}")
                                    
                                    except Exception as e:
                                        logger.error(f"      Error scraping document: {e}")
                                        continue
                            
                            except Exception as e:
                                logger.error(f"  Error processing meeting {meeting_title[:40]}: {e}")
                                continue
                    
                    except Exception as e:
                        logger.error(f"Error processing meeting link: {e}")
                        continue
                
                # Close browser
                await browser.close()
        
        except ImportError as e:
            logger.error(f"Missing dependency: {e}")
            logger.error("Install with: pip install playwright-stealth && playwright install chromium")
            return []
        except Exception as e:
            logger.error(f"Error scraping eBoard {url}: {e}")
            import traceback
            logger.error(traceback.format_exc())
        
        logger.success(f"eBoard scrape complete: {len(documents)} documents from {municipality}")
        return documents

    async def _scrape_generic(
        self,
        target: Dict[str, Any],
        date_range: Dict[str, str]
    ) -> List[Dict[str, Any]]:
        """
        Scrape meeting minutes from generic municipal websites.
        
        Args:
            target: Target configuration
            date_range: Date range for filtering
            
        Returns:
            List of meeting documents
        """
        url = target["url"]
        municipality = target["municipality"]
        state = target["state"]
        
        documents = []
        
        try:
            response = await self.http_client.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, "html.parser")

            candidate_documents = self._extract_document_candidates(
                page_url=url,
                html=response.text,
                soup=soup
            )

            # Crawl a few likely meeting pages because many sites (including JS-heavy portals)
            # keep document links off the landing page.
            meeting_pages = self._extract_meeting_pages(page_url=url, soup=soup)
            for meeting_page in meeting_pages[:8]:
                try:
                    page_response = await self.http_client.get(meeting_page)
                    if page_response.status_code >= 400:
                        continue

                    page_soup = BeautifulSoup(page_response.content, "html.parser")
                    page_candidates = self._extract_document_candidates(
                        page_url=meeting_page,
                        html=page_response.text,
                        soup=page_soup
                    )
                    candidate_documents.extend(page_candidates)
                    await asyncio.sleep(0.2)
                except Exception as page_err:
                    logger.debug(f"Could not scrape meeting page {meeting_page}: {page_err}")

            # De-duplicate while preserving order
            seen_urls = set()
            deduped_candidates = []
            for doc_url, doc_label in candidate_documents:
                if doc_url not in seen_urls:
                    seen_urls.add(doc_url)
                    deduped_candidates.append((doc_url, doc_label))

            for doc_url, doc_label in deduped_candidates[:50]:
                if doc_url in self.scraped_urls:
                    continue

                # Prioritize meeting-related labels but still allow document URL heuristics.
                label = (doc_label or "").lower()
                if label and not any(keyword in label for keyword in self.meeting_keywords):
                    if not any(keyword in doc_url.lower() for keyword in self.meeting_keywords):
                        continue

                doc = await self._scrape_document(
                    url=doc_url,
                    municipality=municipality,
                    state=state,
                    title=doc_label or "meeting document"
                )

                if doc:
                    documents.append(doc)
                    self.scraped_urls.add(doc_url)

                await asyncio.sleep(0.2)
        
        except Exception as e:
            logger.error(f"Error scraping generic site {url}: {e}")
        
        return documents

    def _extract_document_candidates(
        self,
        page_url: str,
        html: str,
        soup: BeautifulSoup
    ) -> List[tuple[str, str]]:
        """Extract document URLs from anchors and script text."""
        candidates: List[tuple[str, str]] = []

        # Anchor/link extraction
        for anchor in soup.find_all("a", href=True):
            href = anchor.get("href", "")
            if not href:
                continue
            full_url = urljoin(page_url, href)
            full_url = self._normalize_document_url(full_url)
            lowered = full_url.lower()
            if any(ext in lowered for ext in self.document_extensions) or any(k in lowered for k in self.document_route_keywords):
                text = anchor.get_text(" ", strip=True) or anchor.get("title", "") or "document"
                candidates.append((full_url, text))

        # Script extraction for JS-driven portals that embed links in JSON blobs.
        url_pattern = r'(https?://[^"\'\s)]+\.(?:pdf|docx?|pptx?|xlsx?)(?:\?[^"\'\s)]*)?)'
        rel_pattern = r'([\w/\-.]+\.(?:pdf|docx?|pptx?|xlsx?)(?:\?[^"\'\s)]*)?)'

        for raw in re.findall(url_pattern, html, flags=re.IGNORECASE):
            candidates.append((self._normalize_document_url(raw), "document"))

        route_pattern = r'(["\'](?:/event/Get(?:Agenda|Minutes)File/[^"\']+)["\'])'
        for raw in re.findall(route_pattern, html, flags=re.IGNORECASE):
            cleaned = raw.strip("\"'")
            candidates.append((self._normalize_document_url(urljoin(page_url, cleaned)), "document"))

        for raw in re.findall(rel_pattern, html, flags=re.IGNORECASE):
            if raw.startswith("http"):
                continue
            if raw.startswith("/") or "/" in raw:
                candidates.append((self._normalize_document_url(urljoin(page_url, raw)), "document"))

        return candidates

    def _normalize_document_url(self, url: str) -> str:
        """Clean common malformed URL artifacts found in embedded portal markup."""
        normalized = url.strip()
        normalized = normalized.replace(" %20?", "?")
        normalized = normalized.replace("%20?", "?")
        normalized = normalized.replace(" ?", "?")
        return normalized

    def _extract_meeting_pages(self, page_url: str, soup: BeautifulSoup) -> List[str]:
        """Find likely meeting-related subpages to expand document discovery."""
        pages = []
        for anchor in soup.find_all("a", href=True):
            href = anchor.get("href", "")
            text = anchor.get_text(" ", strip=True).lower()
            if not href:
                continue

            full_url = urljoin(page_url, href)
            combined = f"{text} {full_url.lower()}"
            if "/event/?id=" in full_url.lower() or any(keyword in combined for keyword in self.meeting_keywords):
                pages.append(full_url)

        seen = set()
        deduped = []
        for p in pages:
            if p not in seen:
                seen.add(p)
                deduped.append(p)
        return deduped
    
    async def _scrape_meeting_page(
        self,
        url: str,
        municipality: str,
        state: str,
        meeting_data: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Scrape a single meeting page.
        
        Args:
            url: Meeting page URL
            municipality: Municipality name
            state: State code
            meeting_data: Optional pre-fetched meeting data
            
        Returns:
            Meeting document or None
        """
        try:
            response = await self.http_client.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, "html.parser")
            
            # Extract meeting details (simplified - actual implementation would be more robust)
            title = soup.find("h1") or soup.find("title")
            title_text = title.get_text().strip() if title else "Untitled Meeting"
            
            # Extract main content
            content_div = soup.find("div", class_="meeting-content") or soup.find("main")
            content = content_div.get_text(separator="\n").strip() if content_div else ""
            
            # Generate document ID
            doc_id = hashlib.md5(f"{url}{municipality}".encode()).hexdigest()
            
            document = MeetingDocument(
                document_id=doc_id,
                source_url=url,
                municipality=municipality,
                state=state,
                meeting_date=datetime.utcnow(),  # Would parse from content
                meeting_type="City Council",  # Would determine from content
                title=title_text,
                content=content,
                metadata={"platform": "web", "raw_data": meeting_data}
            )
            
            return document
        
        except Exception as e:
            logger.error(f"Error scraping meeting page {url}: {e}")
            return None
    
    async def _scrape_document(
        self,
        url: str,
        municipality: str,
        state: str,
        title: str
    ) -> Optional[Dict[str, Any]]:
        """
        Download and extract text from a document URL.
        
        Args:
            url: PDF URL
            municipality: Municipality name
            state: State code
            title: Document title
            
        Returns:
            Meeting document or None
        """
        try:
            response = await self.http_client.get(url)
            response.raise_for_status()
            
            content_type = (response.headers.get("content-type") or "").lower()
            url_lower = url.lower()
            is_pdf = ".pdf" in url_lower or "application/pdf" in content_type
            is_image = any(ext in url_lower for ext in [".png", ".jpg", ".jpeg", ".tif", ".tiff"]) or content_type.startswith("image/")

            content = "[Document content extraction unavailable]"
            ocr_used = False
            ocr_pages = 0

            if is_pdf and PdfReader is not None:
                try:
                    reader = PdfReader(io.BytesIO(response.content))
                    pages = []
                    for page in reader.pages[:30]:
                        pages.append(page.extract_text() or "")
                    extracted = "\n".join(pages).strip()
                    if extracted:
                        content = extracted
                    else:
                        content = "[PDF has no extractable text]"
                except Exception as parse_error:
                    logger.debug(f"PDF parse failed for {url}: {parse_error}")
                    content = "[PDF parsing failed]"

            # OCR fallback for scanned/image-based PDFs.
            if is_pdf and content in ["[PDF has no extractable text]", "[PDF parsing failed]"]:
                ocr_text, ocr_pages = self._ocr_pdf_bytes(response.content)
                if ocr_text:
                    content = ocr_text
                    ocr_used = True

            # OCR for image documents.
            if is_image and content == "[Document content extraction unavailable]":
                image_text = self._ocr_image_bytes(response.content)
                if image_text:
                    content = image_text
                    ocr_used = True
                    ocr_pages = 1
            
            doc_id = hashlib.md5(f"{url}{municipality}".encode()).hexdigest()
            
            document = MeetingDocument(
                document_id=doc_id,
                source_url=url,
                municipality=municipality,
                state=state,
                meeting_date=datetime.utcnow(),
                meeting_type="Unknown",
                title=title,
                content=content,
                metadata={
                    "platform": "document",
                    "file_size": len(response.content),
                    "content_type": response.headers.get("content-type"),
                    "is_pdf": is_pdf,
                    "is_image": is_image,
                    "ocr_used": ocr_used,
                    "ocr_pages": ocr_pages,
                    "text_extracted": content not in [
                        "[Document content extraction unavailable]",
                        "[PDF has no extractable text]",
                        "[PDF parsing failed]"
                    ]
                }
            )
            
            return document
        
        except Exception as e:
            if isinstance(e, httpx.HTTPStatusError) and e.response.status_code == 404:
                logger.debug(f"Document not found (404): {url}")
            else:
                logger.error(f"Error downloading document {url}: {e}")
            return None

    def _ocr_pdf_bytes(self, pdf_bytes: bytes) -> tuple[str, int]:
        """OCR PDF pages when direct PDF text extraction fails."""
        if pdfplumber is None or pytesseract is None:
            return "", 0

        try:
            extracted_pages = []
            with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
                for page in pdf.pages[:self.ocr_max_pages]:
                    try:
                        image = page.to_image(resolution=200).original
                        text = pytesseract.image_to_string(image).strip()
                        if text:
                            extracted_pages.append(text)
                    except TesseractNotFoundError:
                        if not self._ocr_missing_tesseract_warned:
                            logger.warning("Tesseract binary not found. Install 'tesseract-ocr' to enable OCR.")
                            self._ocr_missing_tesseract_warned = True
                        return "", 0
                    except Exception as page_err:
                        logger.debug(f"OCR page failed: {page_err}")

            if not extracted_pages:
                return "", 0
            return "\n\n".join(extracted_pages), len(extracted_pages)
        except Exception as err:
            logger.debug(f"OCR PDF fallback failed: {err}")
            return "", 0

    def _ocr_image_bytes(self, image_bytes: bytes) -> str:
        """OCR text from image-based documents."""
        if pytesseract is None or Image is None:
            return ""

        try:
            image = Image.open(io.BytesIO(image_bytes))
            return pytesseract.image_to_string(image).strip()
        except TesseractNotFoundError:
            if not self._ocr_missing_tesseract_warned:
                logger.warning("Tesseract binary not found. Install 'tesseract-ocr' to enable OCR.")
                self._ocr_missing_tesseract_warned = True
            return ""
        except Exception as err:
            logger.debug(f"Image OCR failed: {err}")
            return ""

    async def _scrape_pdf_document(
        self,
        url: str,
        municipality: str,
        state: str,
        title: str
    ) -> Optional[Dict[str, Any]]:
        """Backward-compatible wrapper for existing call sites."""
        return await self._scrape_document(url, municipality, state, title)
