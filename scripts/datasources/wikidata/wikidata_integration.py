"""
Wikidata Integration for Civic Engagement Data

Wikidata is a collaborative knowledge base that powers Wikipedia's infoboxes.
It is the BEST FREE SOURCE for connecting people to organizations and locations.

SPARQL Endpoint: https://query.wikidata.org/sparql
REST API: https://www.wikidata.org/w/api.php
Query Service: https://query.wikidata.org/

KEY ADVANTAGES:
✅ Completely FREE - no API key required
✅ Highly interconnected - find person → see all linked organizations
✅ Structured data - triples (subject-predicate-object)
✅ Real Wikipedia data - millions of entities
✅ SPARQL queries - powerful graph queries

USE CASES FOR CIVIC ENGAGEMENT:
- Find all members of school boards in a state
- Find all mayors in a county
- Link people to their organizations
- Discover city council members
- Get organizational hierarchies

EXAMPLE QUERIES:
- "All school board members in Alabama"
- "All cities in Tuscaloosa County"
- "All elected officials in a city"
- "Organizations a person is affiliated with"

API DOCUMENTATION:
- SPARQL: https://www.wikidata.org/wiki/Wikidata:SPARQL_query_service
- REST API: https://www.wikidata.org/w/api.php
- Query Examples: https://www.wikidata.org/wiki/Wikidata:SPARQL_query_service/queries/examples

USAGE:
    from scripts.discovery.wikidata_integration import WikidataQuery
    
    wikidata = WikidataQuery()
    
    # Find school board members in Alabama
    members = await wikidata.find_school_board_members(state="Alabama")
    
    # Find all cities in a county
    cities = await wikidata.find_cities_in_county("Tuscaloosa County", "Alabama")
    
    # Find organizations a person is affiliated with
    orgs = await wikidata.find_person_organizations("Walt Maddox")
"""
import asyncio
from typing import List, Dict, Optional, Any
from datetime import datetime
from pathlib import Path
import httpx
from loguru import logger

try:
    from pyspark.sql import SparkSession
    from config.settings import settings
    SPARK_AVAILABLE = True
except ImportError:
    SPARK_AVAILABLE = False
    settings = None


class WikidataQuery:
    """
    Query Wikidata using SPARQL for civic engagement data.
    
    Wikidata is completely FREE and provides structured knowledge
    about people, organizations, and places.
    """
    
    SPARQL_ENDPOINT = "https://query.wikidata.org/sparql"
    REST_API = "https://www.wikidata.org/w/api.php"
    
    # Wikidata property IDs (for SPARQL queries)
    PROPERTIES = {
        "instance_of": "P31",  # What type of thing is this?
        "position_held": "P39",  # What position does this person hold?
        "member_of": "P463",  # What organization is this person a member of?
        "location": "P276",  # Where is this located?
        "located_in": "P131",  # Administrative territory
        "country": "P17",  # Country
        "state": "P131",  # State/province
        "occupation": "P106",  # Occupation
        "official_website": "P856",  # Official website
    }
    
    # Wikidata item IDs (common entities)
    ITEMS = {
        "human": "Q5",  # A human being
        "school_board": "Q7430706",  # School board
        "city": "Q515",  # City
        "county": "Q28575",  # County (US)
        "mayor": "Q30185",  # Mayor
        "city_council": "Q871419",  # City council
        "school_district": "Q1244442",  # School district
    }
    
    def __init__(self, cache_dir: str = "data/cache/wikidata"):
        """Initialize Wikidata query client."""
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    async def execute_sparql(self, query: str) -> List[Dict]:
        """
        Execute a SPARQL query against Wikidata.
        
        Args:
            query: SPARQL query string
            
        Returns:
            List of result dicts
        """
        logger.info(f"Executing SPARQL query...")
        logger.debug(f"Query: {query}")
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                response = await client.get(
                    self.SPARQL_ENDPOINT,
                    params={
                        "query": query,
                        "format": "json"
                    },
                    headers={
                        "User-Agent": "CivicEngagementBot/1.0 (Educational Research)",
                        "Accept": "application/sparql-results+json"
                    }
                )
                response.raise_for_status()
                data = response.json()
                
                # Extract results
                bindings = data.get("results", {}).get("bindings", [])
                results = []
                
                for binding in bindings:
                    result = {}
                    for key, value in binding.items():
                        result[key] = value.get("value")
                    results.append(result)
                
                logger.info(f"✅ Query returned {len(results)} results")
                return results
                
            except httpx.HTTPStatusError as e:
                logger.error(f"SPARQL query failed: {e.response.status_code}")
                logger.error(f"Response: {e.response.text}")
                raise
            except Exception as e:
                logger.error(f"Error executing SPARQL query: {e}")
                raise
    
    async def find_school_board_members(
        self,
        state: Optional[str] = None,
        district: Optional[str] = None
    ) -> List[Dict]:
        """
        Find school board members.
        
        Args:
            state: State name (e.g., "Alabama")
            district: School district name (optional)
            
        Returns:
            List of school board member dicts
        """
        # SPARQL query to find school board members
        query = """
        SELECT ?person ?personLabel ?board ?boardLabel ?position ?positionLabel
        WHERE {
          # Person holds a position
          ?person wdt:P39 ?position .
          
          # Position is on a school board
          ?position wdt:P31 wd:Q7430706 .  # instance of school board
          
          # Board is the organization
          ?person wdt:P463 ?board .
          
          # Filter by state if provided
          FILTER_STATE
          
          SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
        }
        LIMIT 100
        """
        
        # Add state filter if provided
        if state:
            state_filter = f'FILTER(CONTAINS(LCASE(?boardLabel), "{state.lower()}")).'
            query = query.replace("FILTER_STATE", state_filter)
        else:
            query = query.replace("FILTER_STATE", "")
        
        results = await self.execute_sparql(query)
        
        # Format results
        members = []
        for result in results:
            members.append({
                "name": result.get("personLabel"),
                "wikidata_id": result.get("person", "").split("/")[-1],
                "board": result.get("boardLabel"),
                "board_id": result.get("board", "").split("/")[-1],
                "position": result.get("positionLabel"),
                "source": "wikidata",
                "fetched_at": datetime.utcnow().isoformat()
            })
        
        logger.info(f"✅ Found {len(members)} school board members")
        return members
    
    async def find_cities_in_county(
        self,
        county: str,
        state: Optional[str] = None
    ) -> List[Dict]:
        """
        Find all cities in a county.
        
        Args:
            county: County name (e.g., "Tuscaloosa County")
            state: State name (e.g., "Alabama")
            
        Returns:
            List of city dicts
        """
        query = f"""
        SELECT ?city ?cityLabel ?population ?website
        WHERE {{
          # City is an instance of city
          ?city wdt:P31 wd:Q515 .
          
          # Located in the county
          ?city wdt:P131 ?county .
          ?county rdfs:label "{county}"@en .
          
          # Optional: population
          OPTIONAL {{ ?city wdt:P1082 ?population . }}
          
          # Optional: official website
          OPTIONAL {{ ?city wdt:P856 ?website . }}
          
          SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
        }}
        """
        
        results = await self.execute_sparql(query)
        
        cities = []
        for result in results:
            cities.append({
                "name": result.get("cityLabel"),
                "wikidata_id": result.get("city", "").split("/")[-1],
                "population": result.get("population"),
                "website": result.get("website"),
                "county": county,
                "state": state,
                "source": "wikidata",
                "fetched_at": datetime.utcnow().isoformat()
            })
        
        logger.info(f"✅ Found {len(cities)} cities in {county}")
        return cities
    
    async def find_person_organizations(self, person_name: str) -> List[Dict]:
        """
        Find all organizations a person is affiliated with.
        
        Args:
            person_name: Person's name (e.g., "Walt Maddox")
            
        Returns:
            List of organization dicts
        """
        query = f"""
        SELECT ?person ?personLabel ?org ?orgLabel ?position ?positionLabel
        WHERE {{
          # Find person by name
          ?person rdfs:label "{person_name}"@en .
          ?person wdt:P31 wd:Q5 .  # is a human
          
          # Person is member of organization
          ?person wdt:P463 ?org .
          
          # Optional: position held
          OPTIONAL {{ ?person wdt:P39 ?position . }}
          
          SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
        }}
        """
        
        results = await self.execute_sparql(query)
        
        organizations = []
        for result in results:
            organizations.append({
                "person_name": result.get("personLabel"),
                "person_id": result.get("person", "").split("/")[-1],
                "organization": result.get("orgLabel"),
                "organization_id": result.get("org", "").split("/")[-1],
                "position": result.get("positionLabel"),
                "source": "wikidata",
                "fetched_at": datetime.utcnow().isoformat()
            })
        
        logger.info(f"✅ Found {len(organizations)} organizations for {person_name}")
        return organizations
    
    async def find_elected_officials(
        self,
        city: Optional[str] = None,
        state: Optional[str] = None,
        position_type: Optional[str] = None
    ) -> List[Dict]:
        """
        Find elected officials.
        
        Args:
            city: City name
            state: State name
            position_type: Type of position (e.g., "mayor", "council member")
            
        Returns:
            List of official dicts
        """
        # Build SPARQL query dynamically
        filters = []
        if city:
            filters.append(f'FILTER(CONTAINS(LCASE(?cityLabel), "{city.lower()}")).')
        if state:
            filters.append(f'FILTER(CONTAINS(LCASE(?stateLabel), "{state.lower()}")).')
        
        filter_clause = " ".join(filters) if filters else ""
        
        query = f"""
        SELECT ?person ?personLabel ?position ?positionLabel ?location ?locationLabel
        WHERE {{
          # Person holds a position
          ?person wdt:P39 ?position .
          ?person wdt:P31 wd:Q5 .  # is a human
          
          # Position is at a location
          OPTIONAL {{ ?position wdt:P276 ?location . }}
          
          {filter_clause}
          
          SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
        }}
        LIMIT 100
        """
        
        results = await self.execute_sparql(query)
        
        officials = []
        for result in results:
            officials.append({
                "name": result.get("personLabel"),
                "wikidata_id": result.get("person", "").split("/")[-1],
                "position": result.get("positionLabel"),
                "location": result.get("locationLabel"),
                "city": city,
                "state": state,
                "source": "wikidata",
                "fetched_at": datetime.utcnow().isoformat()
            })
        
        logger.info(f"✅ Found {len(officials)} elected officials")
        return officials
    
    def save_to_json(self, data: List[Dict], filename: str):
        """Save data to JSON cache."""
        import json
        
        filepath = self.cache_dir / filename
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"💾 Saved {len(data)} records to {filepath}")


# ============================================================================
# Example Usage
# ============================================================================

async def example_usage():
    """Example usage of Wikidata integration."""
    
    wikidata = WikidataQuery()
    
    # Example 1: Find school board members in Alabama
    logger.info("\n" + "="*80)
    logger.info("Example 1: Find school board members in Alabama")
    logger.info("="*80)
    
    try:
        members = await wikidata.find_school_board_members(state="Alabama")
        
        print(f"\n✅ Found {len(members)} school board members in Alabama:")
        for member in members[:10]:  # Show first 10
            print(f"   • {member['name']} - {member['board']}")
            if member.get('position'):
                print(f"     Position: {member['position']}")
        
        if members:
            wikidata.save_to_json(members, "alabama_school_board_members.json")
        
    except Exception as e:
        logger.error(f"Error: {e}")
    
    # Example 2: Find cities in Tuscaloosa County
    logger.info("\n" + "="*80)
    logger.info("Example 2: Find cities in Tuscaloosa County")
    logger.info("="*80)
    
    try:
        cities = await wikidata.find_cities_in_county("Tuscaloosa County", "Alabama")
        
        print(f"\n✅ Found {len(cities)} cities in Tuscaloosa County:")
        for city in cities[:10]:
            print(f"   • {city['name']}")
            if city.get('population'):
                print(f"     Population: {city['population']}")
            if city.get('website'):
                print(f"     Website: {city['website']}")
        
        if cities:
            wikidata.save_to_json(cities, "tuscaloosa_county_cities.json")
        
    except Exception as e:
        logger.error(f"Error: {e}")
    
    # Example 3: Find organizations for a person
    logger.info("\n" + "="*80)
    logger.info("Example 3: Find organizations for Walt Maddox")
    logger.info("="*80)
    
    try:
        orgs = await wikidata.find_person_organizations("Walt Maddox")
        
        print(f"\n✅ Found {len(orgs)} organizations:")
        for org in orgs:
            print(f"   • {org['organization']}")
            if org.get('position'):
                print(f"     Position: {org['position']}")
        
        if orgs:
            wikidata.save_to_json(orgs, "walt_maddox_organizations.json")
        
    except Exception as e:
        logger.error(f"Error: {e}")
    
    logger.info("\n✅ Examples complete!")


if __name__ == "__main__":
    asyncio.run(example_usage())
