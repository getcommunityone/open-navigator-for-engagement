"""
Ballotpedia Integration for Leader & Ballot Measure Data

Ballotpedia.org is the definitive source for:
- Elected officials (federal, state, local)
- Ballot measures and initiatives
- Election results and candidates
- Political positions and voting records

INTEGRATION METHODS:
1. **Web Scraping** - Structured HTML parsing (no API key needed)
2. **Bulk Data** - Check if Ballotpedia offers CSV/JSON exports
3. **API Access** - Contact Ballotpedia for partnership/API key

USAGE:
    from discovery.ballotpedia_integration import BallotpediaDiscovery
    
    discovery = BallotpediaDiscovery()
    
    # Get officials for a jurisdiction
    officials = await discovery.get_officials("Tuscaloosa", "AL")
    
    # Get ballot measures
    measures = await discovery.get_ballot_measures("Alabama", year=2024)
    
    # Search for a specific leader
    leader = await discovery.search_leader("Walt Maddox")

NOTES:
- Ballotpedia does NOT have a free public API
- Web scraping is allowed but be respectful (rate limiting)
- For production, contact Ballotpedia for data partnership
- See: https://ballotpedia.org/Ballotpedia:Index_of_Contents
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
    """Example usage of Ballotpedia integration."""
    
    discovery = BallotpediaDiscovery()
    
    # 1. Search for a specific leader
    logger.info("\n" + "="*80)
    logger.info("Example 1: Search for Mayor Walt Maddox")
    logger.info("="*80)
    
    leader = await discovery.search_leader("Walt Maddox", "Alabama")
    if leader:
        print(f"\n✅ Found: {leader['name']}")
        print(f"   Office: {leader['office']}")
        print(f"   Party: {leader['party']}")
        print(f"   URL: {leader['ballotpedia_url']}")
    
    # 2. Get city officials
    logger.info("\n" + "="*80)
    logger.info("Example 2: Get Tuscaloosa city officials")
    logger.info("="*80)
    
    officials = await discovery.get_city_officials("Tuscaloosa", "Alabama")
    print(f"\n✅ Found {len(officials)} officials:")
    for official in officials[:5]:  # Show first 5
        print(f"   • {official['name']} - {official['position']}")
    
    # 3. Get ballot measures
    logger.info("\n" + "="*80)
    logger.info("Example 3: Get Alabama ballot measures (2024)")
    logger.info("="*80)
    
    measures = await discovery.get_ballot_measures("Alabama", year=2024)
    print(f"\n✅ Found {len(measures)} ballot measures:")
    for measure in measures[:5]:  # Show first 5
        print(f"   • {measure['measure_name']} - {measure['status']}")
    
    # Save to cache
    if officials:
        discovery.save_to_json(officials, "tuscaloosa_officials.json")
    
    if measures:
        discovery.save_to_json(measures, "alabama_ballot_measures_2024.json")
    
    # Close session
    await discovery.close()
    
    logger.info("\n✅ Integration examples complete!")


if __name__ == "__main__":
    # Run examples
    asyncio.run(example_usage())
