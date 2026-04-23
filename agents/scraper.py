"""
Scraper Agent for collecting government meeting minutes from various sources.
"""
import asyncio
import hashlib
import io
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
