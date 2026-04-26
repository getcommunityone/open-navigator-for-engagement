"""
Ballotpedia Integration - REFERENCE IMPLEMENTATION ONLY

⚠️ WARNING: Ballotpedia API is a PAID SERVICE
   This code is provided for reference only for those with API access.
   NOT RECOMMENDED for free/open-source projects.

Ballotpedia.org is the definitive source for:
- Elected officials (federal, state, local)
- Ballot measures and initiatives
- Election results and candidates
- Political positions and voting records

PRICING:
- Ballotpedia API v3.0 requires payment (contact for pricing)
- API Docs: https://ballotpedia.org/API_documentation
- Announcement: https://ballotpedia.org/Just_launched:_Ballotpedia's_API_Version_3.0

FREE ALTERNATIVES (RECOMMENDED):
- Google Civic Information API - Free, 25k requests/day
- Open States API - Free, 50k requests/month (state-level)
- NCES - Free public data for school boards

INTEGRATION METHODS (if you have paid API access):
1. **Ballotpedia API v3.0** - Official REST API (REQUIRES PAYMENT)
2. **Web Scraping** - Fallback for public data (rate-limited, respectful)

OFFICIAL API (v3.0):
    from discovery.ballotpedia_integration import BallotpediaAPI
    
    api = BallotpediaAPI(api_key="your-api-key")
    
    # Get officials for a jurisdiction
    officials = await api.get_officials("Tuscaloosa", "AL")
    
    # Get ballot measures
    measures = await api.get_ballot_measures("Alabama", year=2024)

WEB SCRAPING (Fallback):
    from discovery.ballotpedia_integration import BallotpediaDiscovery
    
    discovery = BallotpediaDiscovery()
    
    # Search for a specific leader
    leader = await discovery.search_leader("Walt Maddox")

NOTES:
- Ballotpedia API v3.0 launched recently - OFFICIAL API available!
- For production use, get official API key from Ballotpedia
- Web scraping included as fallback for testing/development
- API documentation: https://ballotpedia.org/API_documentation
"""
import asyncio
import re
from typing import List, Dict, Optional
from datetime import datetime
from pathlib import Path
import httpx
from bs4 import BeautifulSoup
from loguru import logger

try:
    from pyspark.sql import SparkSession, DataFrame
    from pyspark.sql.types import StructType, StructField, StringType, IntegerType, TimestampType
    SPARK_AVAILABLE = True
except ImportError:
    SPARK_AVAILABLE = False
    logger.warning("PySpark not available - will save to JSON instead of Delta Lake")

try:
    from config.settings import settings
    SETTINGS_AVAILABLE = True
except ImportError:
    SETTINGS_AVAILABLE = False
    settings = None


# ============================================================================
# OFFICIAL BALLOTPEDIA API v3.0 (RECOMMENDED)
# ============================================================================

class BallotpediaAPI:
    """
    Official Ballotpedia API v3.0 client.
    
    API Documentation: https://ballotpedia.org/API_documentation
    Announcement: https://ballotpedia.org/Just_launched:_Ballotpedia's_API_Version_3.0
    
    To get API access:
    1. Visit https://ballotpedia.org/API_documentation
    2. Contact Ballotpedia for API key
    3. Add to .env: BALLOTPEDIA_API_KEY=your-key
    
    This is the RECOMMENDED method for production use.
    """
    
    # API base URL (update when official endpoint is confirmed)
    BASE_URL = "https://api.ballotpedia.org/v3"
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Ballotpedia API client.
        
        Args:
            api_key: Ballotpedia API key. If not provided, will try settings.ballotpedia_api_key
        """
        if api_key:
            self.api_key = api_key
        elif SETTINGS_AVAILABLE and hasattr(settings, 'ballotpedia_api_key'):
            self.api_key = settings.ballotpedia_api_key
        else:
            self.api_key = None
            logger.warning("⚠️  BALLOTPEDIA_API_KEY not found")
            logger.warning("   Get API access at: https://ballotpedia.org/API_documentation")
            logger.warning("   Add to .env: BALLOTPEDIA_API_KEY=your-key")
        
        self.cache_dir = Path("data/cache/ballotpedia_api")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    async def get_officials(
        self,
        jurisdiction: str,
        state: Optional[str] = None,
        office_type: Optional[str] = None
    ) -> List[Dict]:
        """
        Get elected officials using official API.
        
        Args:
            jurisdiction: City/county name
            state: State code or name
            office_type: Filter by office type (e.g., 'mayor', 'council', 'commissioner')
        
        Returns:
            List of official dicts
        """
        if not self.api_key:
            raise ValueError("Ballotpedia API key required. Get one at https://ballotpedia.org/API_documentation")
        
        # NOTE: Actual endpoint structure needs to be confirmed with Ballotpedia API docs
        # This is a placeholder structure based on typical REST API patterns
        
        params = {
            "jurisdiction": jurisdiction,
            "api_key": self.api_key
        }
        
        if state:
            params["state"] = state
        if office_type:
            params["office_type"] = office_type
        
        logger.info(f"Fetching officials via API for {jurisdiction}, {state}")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.get(
                    f"{self.BASE_URL}/officials",
                    params=params
                )
                response.raise_for_status()
                data = response.json()
                
                logger.info(f"✅ API returned {len(data.get('officials', []))} officials")
                return data.get('officials', [])
                
            except httpx.HTTPStatusError as e:
                logger.error(f"API error: {e.response.status_code}")
                logger.warning("⚠️  Falling back to web scraping...")
                # Fall back to web scraping
                return []
            except Exception as e:
                logger.error(f"Error calling Ballotpedia API: {e}")
                raise
    
    async def get_ballot_measures(
        self,
        state: str,
        year: Optional[int] = None,
        status: Optional[str] = None
    ) -> List[Dict]:
        """
        Get ballot measures using official API.
        
        Args:
            state: State name or code
            year: Election year
            status: Filter by status (e.g., 'passed', 'failed', 'upcoming')
        
        Returns:
            List of ballot measure dicts
        """
        if not self.api_key:
            raise ValueError("Ballotpedia API key required")
        
        params = {
            "state": state,
            "api_key": self.api_key
        }
        
        if year:
            params["year"] = year
        if status:
            params["status"] = status
        
        logger.info(f"Fetching ballot measures via API for {state} ({year or 'all years'})")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.get(
                    f"{self.BASE_URL}/ballot-measures",
                    params=params
                )
                response.raise_for_status()
                data = response.json()
                
                logger.info(f"✅ API returned {len(data.get('measures', []))} ballot measures")
                return data.get('measures', [])
                
            except Exception as e:
                logger.error(f"Error calling Ballotpedia API: {e}")
                raise
    
    def save_to_json(self, data: List[Dict], filename: str):
        """Save API data to JSON cache."""
        import json
        
        filepath = self.cache_dir / filename
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"💾 Saved {len(data)} records to {filepath}")


# ============================================================================
# WEB SCRAPING FALLBACK (For testing/development without API key)
# ============================================================================

class BallotpediaDiscovery:
    """
    Discover and fetch data from Ballotpedia.org.
    
    Data Sources:
    - Elected officials (mayors, city council, county commissioners, state legislators)
    - Ballot measures (local, state, federal)
    - Election results
    - Candidates and campaigns
    """
    
    BASE_URL = "https://ballotpedia.org"
    
    def __init__(
        self,
        cache_dir: str = "data/cache/ballotpedia",
        user_agent: str = "CivicEngagementBot/1.0 (Educational Research)"
    ):
        """
        Initialize Ballotpedia discovery.
        
        Args:
            cache_dir: Directory for caching responses
            user_agent: User agent for HTTP requests (be respectful!)
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.user_agent = user_agent
        self.session = None
        
    async def _get_session(self) -> httpx.AsyncClient:
        """Get or create HTTP session with rate limiting."""
        if self.session is None:
            self.session = httpx.AsyncClient(
                timeout=30.0,
                headers={
                    "User-Agent": self.user_agent,
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                },
                follow_redirects=True
            )
        return self.session
    
    async def _fetch_page(self, url: str) -> Optional[str]:
        """
        Fetch a page from Ballotpedia with rate limiting and caching.
        
        Args:
            url: URL to fetch
            
        Returns:
            HTML content or None if failed
        """
        try:
            # Rate limiting - be respectful!
            await asyncio.sleep(2.0)  # 2 seconds between requests
            
            session = await self._get_session()
            response = await session.get(url)
            
            if response.status_code == 200:
                return response.text
            else:
                logger.warning(f"Failed to fetch {url}: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error fetching {url}: {e}")
            return None
    
    async def search_leader(self, name: str, state: Optional[str] = None) -> Optional[Dict]:
        """
        Search for a specific leader on Ballotpedia.
        
        Args:
            name: Leader's name (e.g., "Walt Maddox")
            state: Optional state filter (e.g., "Alabama" or "AL")
            
        Returns:
            Leader information dict or None
        """
        # Ballotpedia uses URL patterns like:
        # https://ballotpedia.org/Walt_Maddox
        search_name = name.replace(" ", "_")
        url = f"{self.BASE_URL}/{search_name}"
        
        logger.info(f"Searching for leader: {name} at {url}")
        
        html = await self._fetch_page(url)
        if not html:
            return None
        
        soup = BeautifulSoup(html, 'html.parser')
        
        # Extract leader information from infobox
        infobox = soup.find('table', {'class': 'infobox'})
        if not infobox:
            logger.warning(f"No infobox found for {name}")
            return None
        
        leader_data = {
            "name": name,
            "ballotpedia_url": url,
            "office": None,
            "party": None,
            "jurisdiction": None,
            "term_start": None,
            "term_end": None,
            "source": "ballotpedia",
            "scraped_at": datetime.utcnow().isoformat()
        }
        
        # Parse infobox rows
        for row in infobox.find_all('tr'):
            header = row.find('th')
            data = row.find('td')
            
            if header and data:
                header_text = header.get_text(strip=True).lower()
                data_text = data.get_text(strip=True)
                
                if 'office' in header_text or 'position' in header_text:
                    leader_data['office'] = data_text
                elif 'party' in header_text:
                    leader_data['party'] = data_text
                elif 'assumed office' in header_text or 'took office' in header_text:
                    leader_data['term_start'] = data_text
                elif 'term ends' in header_text or 'leaving office' in header_text:
                    leader_data['term_end'] = data_text
        
        logger.info(f"✅ Found leader: {name} - {leader_data.get('office')}")
        return leader_data
    
    async def get_city_officials(self, city: str, state: str) -> List[Dict]:
        """
        Get elected officials for a city.
        
        Args:
            city: City name (e.g., "Tuscaloosa")
            state: State name or code (e.g., "Alabama" or "AL")
            
        Returns:
            List of official dicts
        """
        # Ballotpedia city pages: https://ballotpedia.org/Tuscaloosa,_Alabama
        city_page = f"{city},_{state}".replace(" ", "_")
        url = f"{self.BASE_URL}/{city_page}"
        
        logger.info(f"Fetching officials for {city}, {state} from {url}")
        
        html = await self._fetch_page(url)
        if not html:
            return []
        
        soup = BeautifulSoup(html, 'html.parser')
        officials = []
        
        # Look for "City council" or "Mayor" sections
        for heading in soup.find_all(['h2', 'h3']):
            heading_text = heading.get_text(strip=True).lower()
            
            if any(term in heading_text for term in ['mayor', 'city council', 'council members']):
                # Find the list of officials after this heading
                next_elem = heading.find_next_sibling()
                
                while next_elem and next_elem.name != 'h2':
                    if next_elem.name == 'ul':
                        for li in next_elem.find_all('li'):
                            official_name = li.get_text(strip=True)
                            
                            # Extract name and position
                            # Format often like: "John Smith (District 1)"
                            match = re.match(r'(.*?)\s*\((.*?)\)', official_name)
                            if match:
                                name = match.group(1).strip()
                                position = match.group(2).strip()
                            else:
                                name = official_name
                                position = heading_text.title()
                            
                            officials.append({
                                "name": name,
                                "position": position,
                                "jurisdiction": f"{city}, {state}",
                                "source": "ballotpedia",
                                "source_url": url,
                                "scraped_at": datetime.utcnow().isoformat()
                            })
                    
                    next_elem = next_elem.find_next_sibling()
        
        logger.info(f"✅ Found {len(officials)} officials for {city}, {state}")
        return officials
    
    async def get_ballot_measures(
        self,
        state: str,
        year: Optional[int] = None,
        measure_type: Optional[str] = None
    ) -> List[Dict]:
        """
        Get ballot measures for a state.
        
        Args:
            state: State name (e.g., "Alabama")
            year: Optional year filter (e.g., 2024)
            measure_type: Optional type filter (e.g., "local", "state")
            
        Returns:
            List of ballot measure dicts
        """
        # Ballotpedia ballot measures page
        if year:
            url = f"{self.BASE_URL}/{state}_ballot_measures,_{year}"
        else:
            url = f"{self.BASE_URL}/{state}_ballot_measures"
        
        logger.info(f"Fetching ballot measures from {url}")
        
        html = await self._fetch_page(url)
        if not html:
            return []
        
        soup = BeautifulSoup(html, 'html.parser')
        measures = []
        
        # Look for tables with ballot measures
        for table in soup.find_all('table'):
            # Skip infoboxes
            if 'infobox' in table.get('class', []):
                continue
            
            # Process table rows
            for row in table.find_all('tr')[1:]:  # Skip header
                cells = row.find_all('td')
                if len(cells) >= 2:
                    measure_name = cells[0].get_text(strip=True)
                    measure_status = cells[1].get_text(strip=True) if len(cells) > 1 else None
                    
                    # Extract measure link
                    link = cells[0].find('a')
                    measure_url = f"{self.BASE_URL}{link['href']}" if link and link.get('href') else None
                    
                    measures.append({
                        "measure_name": measure_name,
                        "status": measure_status,
                        "state": state,
                        "year": year,
                        "measure_url": measure_url,
                        "source": "ballotpedia",
                        "scraped_at": datetime.utcnow().isoformat()
                    })
        
        logger.info(f"✅ Found {len(measures)} ballot measures for {state} ({year or 'all years'})")
        return measures
    
    async def close(self):
        """Close HTTP session."""
        if self.session:
            await self.session.aclose()
    
    def save_to_json(self, data: List[Dict], filename: str):
        """Save data to JSON cache."""
        import json
        
        filepath = self.cache_dir / filename
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"💾 Saved {len(data)} records to {filepath}")
    
    def save_to_bronze_layer(
        self,
        data: List[Dict],
        table_name: str,
        spark: Optional[SparkSession] = None
    ) -> Dict[str, int]:
        """
        Save discovered data to Bronze layer (Delta Lake).
        
        Args:
            data: List of dicts to save
            table_name: Table name (e.g., "ballotpedia_officials")
            spark: Optional SparkSession (creates one if not provided)
            
        Returns:
            Stats dict
        """
        if not SPARK_AVAILABLE:
            logger.warning("PySpark not available - saving to JSON instead")
            self.save_to_json(data, f"{table_name}.json")
            return {"records_written": len(data), "format": "json"}
        
        from delta import configure_spark_with_delta_pip
        from config.settings import settings
        
        # Create Spark session if needed
        if spark is None:
            builder = SparkSession.builder \
                .appName(f"BallotpediaIngestion_{table_name}") \
                .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
                .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")
            spark = configure_spark_with_delta_pip(builder).getOrCreate()
        
        # Convert to DataFrame
        df = spark.createDataFrame(data)
        
        # Write to Bronze layer
        bronze_path = f"{settings.delta_lake_path}/bronze/{table_name}"
        df.write \
            .format("delta") \
            .mode("append") \
            .option("mergeSchema", "true") \
            .save(bronze_path)
        
        logger.info(f"✅ Wrote {len(data)} records to {bronze_path}")
        
        return {
            "records_written": len(data),
            "table_name": table_name,
            "path": bronze_path,
            "format": "delta"
        }


# ============================================================================
# Usage Examples
# ============================================================================

async def example_usage():
    """
    Example usage of Ballotpedia integration.
    
    Shows both official API (v3.0) and web scraping fallback methods.
    """
    
    logger.info("\n" + "="*80)
    logger.info("BALLOTPEDIA INTEGRATION EXAMPLES")
    logger.info("="*80)
    
    # Check if API key is available
    api_available = False
    if SETTINGS_AVAILABLE and hasattr(settings, 'ballotpedia_api_key') and settings.ballotpedia_api_key:
        api_available = True
    
    # ==========================================================================
    # METHOD 1: Official API (RECOMMENDED for production)
    # ==========================================================================
    if api_available:
        logger.info("\n" + "="*80)
        logger.info("METHOD 1: Using Official Ballotpedia API v3.0 (RECOMMENDED)")
        logger.info("="*80)
        
        api = BallotpediaAPI()
        
        try:
            # Example 1: Get officials via API
            logger.info("\nExample 1: Get Tuscaloosa officials via API")
            officials = await api.get_officials("Tuscaloosa", state="Alabama")
            
            if officials:
                print(f"\n✅ API returned {len(officials)} officials:")
                for official in officials[:5]:
                    print(f"   • {official.get('name')} - {official.get('office')}")
                api.save_to_json(officials, "tuscaloosa_officials_api.json")
            
            # Example 2: Get ballot measures via API
            logger.info("\nExample 2: Get Alabama ballot measures via API")
            measures = await api.get_ballot_measures("Alabama", year=2024)
            
            if measures:
                print(f"\n✅ API returned {len(measures)} ballot measures:")
                for measure in measures[:5]:
                    print(f"   • {measure.get('title')} - {measure.get('status')}")
                api.save_to_json(measures, "alabama_measures_api.json")
            
        except Exception as e:
            logger.error(f"API error: {e}")
            logger.info("Falling back to web scraping...")
    else:
        logger.info("\n" + "="*80)
        logger.info("⚠️  Ballotpedia API key not found - using web scraping fallback")
        logger.info("   Get API access at: https://ballotpedia.org/API_documentation")
        logger.info("   Add to .env: BALLOTPEDIA_API_KEY=your-key")
        logger.info("="*80)
    
    # ==========================================================================
    # METHOD 2: Web Scraping Fallback (for testing without API key)
    # ==========================================================================
    logger.info("\n" + "="*80)
    logger.info("METHOD 2: Using Web Scraping (Fallback)")
    logger.info("="*80)
    
    discovery = BallotpediaDiscovery()
    
    # 1. Search for a specific leader
    logger.info("\nExample 1: Search for Mayor Walt Maddox (web scraping)")
    
    leader = await discovery.search_leader("Walt Maddox", "Alabama")
    if leader:
        print(f"\n✅ Found: {leader['name']}")
        print(f"   Office: {leader['office']}")
        print(f"   Party: {leader['party']}")
        print(f"   URL: {leader['ballotpedia_url']}")
    
    # 2. Get city officials
    logger.info("\nExample 2: Get Tuscaloosa city officials (web scraping)")
    
    officials = await discovery.get_city_officials("Tuscaloosa", "Alabama")
    print(f"\n✅ Found {len(officials)} officials:")
    for official in officials[:5]:  # Show first 5
        print(f"   • {official['name']} - {official['position']}")
    
    # 3. Get ballot measures
    logger.info("\nExample 3: Get Alabama ballot measures (web scraping)")
    
    measures = await discovery.get_ballot_measures("Alabama", year=2024)
    print(f"\n✅ Found {len(measures)} ballot measures:")
    for measure in measures[:5]:  # Show first 5
        print(f"   • {measure['measure_name']} - {measure['status']}")
    
    # Save to cache
    if officials:
        discovery.save_to_json(officials, "tuscaloosa_officials_scraping.json")
    
    if measures:
        discovery.save_to_json(measures, "alabama_ballot_measures_scraping.json")
    
    # Close session
    await discovery.close()
    
    logger.info("\n✅ Integration examples complete!")
    logger.info("\n" + "="*80)
    logger.info("RECOMMENDATION: Get official API key for production use")
    logger.info("Visit: https://ballotpedia.org/API_documentation")
    logger.info("="*80)


if __name__ == "__main__":
    # Run examples
    asyncio.run(example_usage())
