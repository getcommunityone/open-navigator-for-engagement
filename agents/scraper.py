"""
Scraper Agent for collecting government meeting minutes from various sources.
"""
import asyncio
import hashlib
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from urllib.parse import urljoin, urlparse
import httpx
from bs4 import BeautifulSoup
from loguru import logger

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
            
            if platform == "legistar":
                tasks.append(self._scrape_legistar(target, date_range))
            elif platform == "granicus":
                tasks.append(self._scrape_granicus(target, date_range))
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
    
    async def _scrape_legistar(
        self,
        target: Dict[str, Any],
        date_range: Dict[str, str]
    ) -> List[Dict[str, Any]]:
        """
        Scrape meeting minutes from Legistar platform.
        
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
            # Legistar typically has a calendar endpoint
            calendar_url = urljoin(base_url, "Calendar.aspx")
            
            response = await self.http_client.get(calendar_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, "html.parser")
            
            # Find meeting links (this is a simplified example - actual Legistar HTML varies)
            meeting_links = soup.find_all("a", class_="meeting-link")
            
            for link in meeting_links[:50]:  # Limit to 50 meetings per target
                meeting_url = urljoin(base_url, link.get("href"))
                
                if meeting_url in self.scraped_urls:
                    continue
                
                doc = await self._scrape_meeting_page(
                    meeting_url,
                    municipality,
                    state
                )
                
                if doc:
                    documents.append(doc)
                    self.scraped_urls.add(meeting_url)
                
                # Rate limiting
                await asyncio.sleep(0.5)
        
        except Exception as e:
            logger.error(f"Error scraping Legistar {base_url}: {e}")
        
        return documents
    
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
            
            # Look for common patterns in municipal websites
            # This is a heuristic approach - would need refinement per site
            
            # Find PDF links
            pdf_links = soup.find_all("a", href=lambda h: h and ".pdf" in h.lower())
            
            for link in pdf_links[:30]:
                pdf_url = urljoin(url, link.get("href"))
                
                if pdf_url in self.scraped_urls:
                    continue
                
                # Check if link text suggests it's meeting minutes
                link_text = link.get_text().lower()
                if any(keyword in link_text for keyword in ["minutes", "agenda", "meeting"]):
                    doc = await self._scrape_pdf_document(
                        pdf_url,
                        municipality,
                        state,
                        link_text
                    )
                    
                    if doc:
                        documents.append(doc)
                        self.scraped_urls.add(pdf_url)
                
                await asyncio.sleep(0.5)
        
        except Exception as e:
            logger.error(f"Error scraping generic site {url}: {e}")
        
        return documents
    
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
    
    async def _scrape_pdf_document(
        self,
        url: str,
        municipality: str,
        state: str,
        title: str
    ) -> Optional[Dict[str, Any]]:
        """
        Download and extract text from PDF document.
        
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
            
            # Note: Actual PDF parsing would require pypdf or similar
            # For now, store PDF metadata with a placeholder for content
            
            doc_id = hashlib.md5(f"{url}{municipality}".encode()).hexdigest()
            
            document = MeetingDocument(
                document_id=doc_id,
                source_url=url,
                municipality=municipality,
                state=state,
                meeting_date=datetime.utcnow(),
                meeting_type="Unknown",
                title=title,
                content="[PDF content - requires parsing]",
                metadata={
                    "platform": "pdf",
                    "file_size": len(response.content),
                    "content_type": response.headers.get("content-type")
                }
            )
            
            return document
        
        except Exception as e:
            logger.error(f"Error downloading PDF {url}: {e}")
            return None
