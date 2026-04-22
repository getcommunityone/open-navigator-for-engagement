"""
URL Discovery Agent

Discovers official websites and meeting minutes URLs for local governments
using search APIs and domain validation.

Strategy:
1. Query search engines for each jurisdiction
2. Validate against GSA .gov domain list
3. Crawl homepage for "minutes" or "agendas" links
4. Detect CMS platforms (Granicus, CivicClerk, etc.)
"""
import asyncio
from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass
from datetime import datetime
import httpx
from bs4 import BeautifulSoup
from loguru import logger
from urllib.parse import urljoin, urlparse
import re
from config import settings


@dataclass
class JurisdictionURL:
    """Discovered URL for a jurisdiction."""
    jurisdiction_id: str
    jurisdiction_name: str
    state: str
    homepage_url: Optional[str] = None
    minutes_url: Optional[str] = None
    cms_platform: Optional[str] = None
    is_gov_domain: bool = False
    discovery_method: str = "unknown"
    confidence_score: float = 0.0
    last_verified: Optional[datetime] = None


class URLDiscoveryAgent:
    """Agent to discover government websites and minutes URLs."""
    
    # Keywords to search for
    MINUTES_KEYWORDS = [
        "meeting minutes",
        "agendas",
        "city council minutes",
        "board meetings",
        "public meetings"
    ]
    
    # CMS platform indicators
    CMS_SIGNATURES = {
        "granicus": ["granicus.com", "legistar.com"],
        "civicclerk": ["civicclerk.com", "civicweb.net"],
        "municode": ["municode.com"],
        "carahsoft": ["carahsoft.com"],
        "laserfiche": ["laserfiche.com"],
        "primegov": ["primegov.com"]
    }
    
    def __init__(self, gsa_domains: Set[str]):
        """
        Initialize discovery agent.
        
        Args:
            gsa_domains: Set of validated .gov domains from GSA list
        """
        self.gsa_domains = gsa_domains
        self.http_client = httpx.AsyncClient(timeout=15.0, follow_redirects=True)
    
    async def search_google(self, query: str, num_results: int = 3) -> List[str]:
        """
        Search Google for jurisdiction URLs.
        
        Note: Requires Google Custom Search API key
        
        Args:
            query: Search query
            num_results: Number of results to return
        
        Returns:
            List of URLs
        """
        # This is a placeholder - real implementation needs Google API key
        # See: https://developers.google.com/custom-search/v1/overview
        
        api_key = settings.google_search_api_key
        search_engine_id = settings.google_search_engine_id
        
        if not api_key or not search_engine_id:
            logger.warning("Google Search API not configured")
            return []
        
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            "key": api_key,
            "cx": search_engine_id,
            "q": query,
            "num": num_results
        }
        
        try:
            response = await self.http_client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            urls = [item["link"] for item in data.get("items", [])]
            return urls
        
        except Exception as e:
            logger.error(f"Google search failed: {e}")
            return []
    
    async def search_bing(self, query: str, num_results: int = 3) -> List[str]:
        """
        Search Bing for jurisdiction URLs.
        
        Args:
            query: Search query
            num_results: Number of results to return
        
        Returns:
            List of URLs
        """
        api_key = settings.bing_search_api_key
        
        if not api_key:
            logger.warning("Bing Search API not configured")
            return []
        
        url = "https://api.bing.microsoft.com/v7.0/search"
        headers = {"Ocp-Apim-Subscription-Key": api_key}
        params = {"q": query, "count": num_results}
        
        try:
            response = await self.http_client.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            
            urls = [item["url"] for item in data.get("webPages", {}).get("value", [])]
            return urls
        
        except Exception as e:
            logger.error(f"Bing search failed: {e}")
            return []
    
    def validate_domain(self, url: str) -> bool:
        """
        Check if URL is in GSA .gov domain list.
        
        Args:
            url: URL to validate
        
        Returns:
            True if domain is validated .gov
        """
        domain = urlparse(url).netloc.lower()
        return domain in self.gsa_domains
    
    async def discover_homepage(
        self,
        jurisdiction_name: str,
        state: str,
        jurisdiction_type: str
    ) -> Optional[str]:
        """
        Discover official homepage for jurisdiction.
        
        Args:
            jurisdiction_name: Name of jurisdiction
            state: State abbreviation
            jurisdiction_type: Type (city, county, etc.)
        
        Returns:
            Homepage URL or None
        """
        # Build search query
        query = f"{jurisdiction_name} {state} {jurisdiction_type} official website"
        
        logger.info(f"Searching for: {query}")
        
        # Try Google first
        urls = await self.search_google(query)
        
        # Fall back to Bing
        if not urls:
            urls = await self.search_bing(query)
        
        # Prioritize .gov domains
        gov_urls = [url for url in urls if self.validate_domain(url)]
        if gov_urls:
            logger.success(f"Found .gov domain: {gov_urls[0]}")
            return gov_urls[0]
        
        # Return first result if no .gov found
        if urls:
            logger.warning(f"No .gov domain found, using: {urls[0]}")
            return urls[0]
        
        logger.warning(f"No homepage found for {jurisdiction_name}, {state}")
        return None
    
    async def crawl_for_minutes(self, homepage_url: str) -> Optional[str]:
        """
        Crawl homepage looking for meeting minutes link.
        
        Args:
            homepage_url: URL of homepage
        
        Returns:
            URL to minutes page or None
        """
        try:
            response = await self.http_client.get(homepage_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for links with minutes-related keywords
            minutes_patterns = [
                r'minutes?',
                r'agendas?',
                r'meetings?',
                r'city\s+council',
                r'board\s+of\s+supervisors'
            ]
            
            pattern = re.compile('|'.join(minutes_patterns), re.IGNORECASE)
            
            for link in soup.find_all('a', href=True):
                link_text = link.get_text().lower()
                link_href = link['href']
                
                if pattern.search(link_text) or pattern.search(link_href):
                    full_url = urljoin(homepage_url, link_href)
                    logger.success(f"Found minutes link: {full_url}")
                    return full_url
            
            logger.warning(f"No minutes link found on {homepage_url}")
            return None
        
        except Exception as e:
            logger.error(f"Failed to crawl {homepage_url}: {e}")
            return None
    
    def detect_cms_platform(self, url: str, html: Optional[str] = None) -> Optional[str]:
        """
        Detect CMS platform from URL or HTML.
        
        Args:
            url: URL to check
            html: Optional HTML content
        
        Returns:
            CMS platform name or None
        """
        url_lower = url.lower()
        
        for cms, signatures in self.CMS_SIGNATURES.items():
            if any(sig in url_lower for sig in signatures):
                return cms
        
        # Check HTML if provided
        if html:
            html_lower = html.lower()
            for cms, signatures in self.CMS_SIGNATURES.items():
                if any(sig in html_lower for sig in signatures):
                    return cms
        
        return None
    
    async def discover_jurisdiction(
        self,
        jurisdiction_id: str,
        jurisdiction_name: str,
        state: str,
        jurisdiction_type: str
    ) -> JurisdictionURL:
        """
        Full discovery workflow for a jurisdiction.
        
        Args:
            jurisdiction_id: FIPS code
            jurisdiction_name: Name
            state: State abbreviation
            jurisdiction_type: Type of jurisdiction
        
        Returns:
            JurisdictionURL with discovered information
        """
        result = JurisdictionURL(
            jurisdiction_id=jurisdiction_id,
            jurisdiction_name=jurisdiction_name,
            state=state
        )
        
        # Step 1: Find homepage
        homepage = await self.discover_homepage(jurisdiction_name, state, jurisdiction_type)
        if not homepage:
            result.discovery_method = "not_found"
            return result
        
        result.homepage_url = homepage
        result.is_gov_domain = self.validate_domain(homepage)
        result.discovery_method = "search_engine"
        
        # Step 2: Find minutes page
        minutes_url = await self.crawl_for_minutes(homepage)
        if minutes_url:
            result.minutes_url = minutes_url
            result.confidence_score = 0.9 if result.is_gov_domain else 0.7
        else:
            result.confidence_score = 0.5 if result.is_gov_domain else 0.3
        
        # Step 3: Detect CMS
        result.cms_platform = self.detect_cms_platform(homepage)
        
        result.last_verified = datetime.now()
        
        return result
    
    async def close(self):
        """Close HTTP client."""
        await self.http_client.aclose()


async def main():
    """Test URL discovery."""
    # Load GSA domains
    gsa_domains = {
        "sanjose.gov",
        "sf.gov",
        "lacounty.gov",
        "sandiegocounty.gov"
    }
    
    agent = URLDiscoveryAgent(gsa_domains)
    
    # Test discovery
    test_jurisdictions = [
        ("06085", "Santa Clara County", "CA", "county"),
        ("06075", "San Francisco", "CA", "city"),
        ("06073", "San Diego", "CA", "city")
    ]
    
    for jid, name, state, jtype in test_jurisdictions:
        result = await agent.discover_jurisdiction(jid, name, state, jtype)
        
        print(f"\n{name}, {state}:")
        print(f"  Homepage: {result.homepage_url}")
        print(f"  Minutes: {result.minutes_url}")
        print(f"  CMS: {result.cms_platform}")
        print(f"  .gov? {result.is_gov_domain}")
        print(f"  Confidence: {result.confidence_score:.2f}")
    
    await agent.close()


if __name__ == "__main__":
    asyncio.run(main())
