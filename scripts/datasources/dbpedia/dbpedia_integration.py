"""
DBpedia Integration for Autocomplete and Structured Data

DBpedia extracts structured "triples" from Wikipedia infoboxes.
Every Wikipedia page becomes a "resource" with structured data.

LOOKUP API: http://lookup.dbpedia.org/api/search
REST API: https://dbpedia.org/sparql

KEY ADVANTAGES:
✅ Completely FREE - no API key required
✅ Perfect for autocomplete/type-ahead - Lookup API is designed for this
✅ Structured data from Wikipedia - millions of resources
✅ Instant access to Mayor, population, school district info
✅ Rich context for search results

USE CASES FOR CIVIC ENGAGEMENT:
- Autocomplete in search box (cities, people, organizations)
- Type-ahead suggestions
- Structured data for entities (mayor, population, etc.)
- Linking Wikipedia pages to structured data
- Enriching search results with context

EXAMPLE QUERIES:
- "Tuscaloosa" → Get Mayor, population, school district
- "School Board" → Find all school boards
- "Alabama cities" → Get all cities in Alabama
- Person name → Get positions, affiliations

API DOCUMENTATION:
- Lookup API: http://lookup.dbpedia.org/api/doc/
- SPARQL: https://dbpedia.org/sparql
- Examples: https://wiki.dbpedia.org/develop/datasets

USAGE:
    from discovery.dbpedia_integration import DBpediaLookup
    
    dbpedia = DBpediaLookup()
    
    # Autocomplete search
    results = await dbpedia.search("Tuscaloosa", max_results=10)
    
    # Get detailed info about a resource
    info = await dbpedia.get_resource_info("Tuscaloosa,_Alabama")
    
    # Search for specific types (cities, people, organizations)
    cities = await dbpedia.search_by_type("Alabama", type_filter="Place")
"""
import asyncio
from typing import List, Dict, Optional
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


class DBpediaLookup:
    """
    Query DBpedia for autocomplete and structured data.
    
    DBpedia is completely FREE and perfect for type-ahead search boxes.
    """
    
    LOOKUP_API = "http://lookup.dbpedia.org/api/search"
    SPARQL_ENDPOINT = "https://dbpedia.org/sparql"
    
    # Common DBpedia ontology classes
    CLASSES = {
        "place": "Place",
        "city": "City",
        "person": "Person",
        "organization": "Organisation",
        "government": "GovernmentAgency",
        "school": "School",
        "politician": "Politician",
    }
    
    def __init__(self, cache_dir: str = "data/cache/dbpedia"):
        """Initialize DBpedia lookup client."""
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    async def search(
        self,
        query: str,
        max_results: int = 10,
        type_filter: Optional[str] = None
    ) -> List[Dict]:
        """
        Search DBpedia (autocomplete/type-ahead).
        
        Args:
            query: Search query (e.g., "Tuscaloosa", "School Board")
            max_results: Maximum number of results
            type_filter: Filter by type (e.g., "Place", "Person", "Organisation")
            
        Returns:
            List of result dicts with URI, label, description, etc.
        """
        logger.info(f"Searching DBpedia for: {query}")
        
        params = {
            "query": query,
            "maxResults": max_results,
            "format": "json"
        }
        
        if type_filter:
            params["type"] = type_filter
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.get(
                    self.LOOKUP_API,
                    params=params,
                    headers={
                        "User-Agent": "CivicEngagementBot/1.0 (Educational Research)",
                        "Accept": "application/json"
                    }
                )
                response.raise_for_status()
                data = response.json()
                
                # Extract results
                results = []
                for item in data.get("results", []):
                    results.append({
                        "label": item.get("label"),
                        "uri": item.get("uri"),
                        "description": item.get("description"),
                        "classes": item.get("classes", []),
                        "categories": item.get("categories", []),
                        "refCount": item.get("refCount", 0),  # How many Wikipedia pages link to this
                        "source": "dbpedia",
                        "fetched_at": datetime.utcnow().isoformat()
                    })
                
                logger.info(f"✅ Found {len(results)} results for '{query}'")
                return results
                
            except Exception as e:
                logger.error(f"Error searching DBpedia: {e}")
                raise
    
    async def search_by_type(
        self,
        query: str,
        type_filter: str,
        max_results: int = 20
    ) -> List[Dict]:
        """
        Search for specific entity types.
        
        Args:
            query: Search query
            type_filter: Entity type ("Place", "Person", "Organisation", etc.)
            max_results: Maximum results
            
        Returns:
            Filtered results of that type
        """
        logger.info(f"Searching for {type_filter}: {query}")
        
        return await self.search(
            query=query,
            max_results=max_results,
            type_filter=type_filter
        )
    
    async def get_resource_info(self, resource: str) -> Dict:
        """
        Get detailed information about a DBpedia resource.
        
        Args:
            resource: Resource name (e.g., "Tuscaloosa,_Alabama")
            
        Returns:
            Dict with resource information
        """
        # DBpedia resource URL
        if not resource.startswith("http"):
            resource_url = f"http://dbpedia.org/resource/{resource}"
        else:
            resource_url = resource
        
        logger.info(f"Fetching resource info: {resource_url}")
        
        # Query SPARQL endpoint for all properties
        query = f"""
        SELECT ?property ?value
        WHERE {{
          <{resource_url}> ?property ?value .
        }}
        LIMIT 100
        """
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.get(
                    self.SPARQL_ENDPOINT,
                    params={
                        "query": query,
                        "format": "json"
                    },
                    headers={
                        "User-Agent": "CivicEngagementBot/1.0",
                        "Accept": "application/sparql-results+json"
                    }
                )
                response.raise_for_status()
                data = response.json()
                
                # Parse results into structured dict
                info = {
                    "resource": resource_url,
                    "properties": {},
                    "source": "dbpedia",
                    "fetched_at": datetime.utcnow().isoformat()
                }
                
                for binding in data.get("results", {}).get("bindings", []):
                    prop = binding.get("property", {}).get("value", "")
                    value = binding.get("value", {}).get("value", "")
                    
                    # Extract property name from URI
                    prop_name = prop.split("/")[-1].split("#")[-1]
                    
                    # Store property
                    if prop_name not in info["properties"]:
                        info["properties"][prop_name] = []
                    info["properties"][prop_name].append(value)
                
                logger.info(f"✅ Found {len(info['properties'])} properties for {resource}")
                return info
                
            except Exception as e:
                logger.error(f"Error fetching resource info: {e}")
                raise
    
    async def find_cities(self, state: Optional[str] = None) -> List[Dict]:
        """
        Find cities (with optional state filter).
        
        Args:
            state: State name to filter by
            
        Returns:
            List of city dicts
        """
        if state:
            query = f"cities in {state}"
        else:
            query = "city"
        
        return await self.search_by_type(
            query=query,
            type_filter="City",
            max_results=50
        )
    
    async def find_people(self, name_query: str) -> List[Dict]:
        """
        Find people by name.
        
        Args:
            name_query: Name or partial name
            
        Returns:
            List of person dicts
        """
        return await self.search_by_type(
            query=name_query,
            type_filter="Person",
            max_results=20
        )
    
    async def find_organizations(self, org_query: str) -> List[Dict]:
        """
        Find organizations.
        
        Args:
            org_query: Organization name or keyword
            
        Returns:
            List of organization dicts
        """
        return await self.search_by_type(
            query=org_query,
            type_filter="Organisation",
            max_results=20
        )
    
    def save_to_json(self, data, filename: str):
        """Save data to JSON cache."""
        import json
        
        filepath = self.cache_dir / filename
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"💾 Saved data to {filepath}")


# ============================================================================
# Example Usage
# ============================================================================

async def example_usage():
    """Example usage of DBpedia integration."""
    
    dbpedia = DBpediaLookup()
    
    # Example 1: Autocomplete search for "Tuscaloosa"
    logger.info("\n" + "="*80)
    logger.info("Example 1: Autocomplete search for 'Tuscaloosa'")
    logger.info("="*80)
    
    try:
        results = await dbpedia.search("Tuscaloosa", max_results=10)
        
        print(f"\n✅ Found {len(results)} results:")
        for result in results:
            print(f"\n   • {result['label']}")
            if result.get('description'):
                print(f"     {result['description']}")
            print(f"     URI: {result['uri']}")
            print(f"     Reference count: {result['refCount']}")
        
        if results:
            dbpedia.save_to_json(results, "tuscaloosa_search.json")
        
    except Exception as e:
        logger.error(f"Error: {e}")
    
    # Example 2: Get detailed info about Tuscaloosa, Alabama
    logger.info("\n" + "="*80)
    logger.info("Example 2: Get detailed info about Tuscaloosa, Alabama")
    logger.info("="*80)
    
    try:
        info = await dbpedia.get_resource_info("Tuscaloosa,_Alabama")
        
        print(f"\n✅ Found {len(info['properties'])} properties:")
        
        # Show interesting properties
        interesting = [
            "mayor", "population", "areaCode", "postalCode",
            "website", "leaderTitle", "foundingDate"
        ]
        
        for prop in interesting:
            if prop in info['properties']:
                print(f"   • {prop}: {info['properties'][prop]}")
        
        dbpedia.save_to_json(info, "tuscaloosa_info.json")
        
    except Exception as e:
        logger.error(f"Error: {e}")
    
    # Example 3: Search for cities in Alabama
    logger.info("\n" + "="*80)
    logger.info("Example 3: Search for cities in Alabama")
    logger.info("="*80)
    
    try:
        cities = await dbpedia.find_cities(state="Alabama")
        
        print(f"\n✅ Found {len(cities)} cities in Alabama:")
        for city in cities[:10]:  # Show first 10
            print(f"   • {city['label']}")
            if city.get('description'):
                print(f"     {city['description']}")
        
        if cities:
            dbpedia.save_to_json(cities, "alabama_cities.json")
        
    except Exception as e:
        logger.error(f"Error: {e}")
    
    # Example 4: Search for people (politicians)
    logger.info("\n" + "="*80)
    logger.info("Example 4: Search for Alabama politicians")
    logger.info("="*80)
    
    try:
        people = await dbpedia.find_people("Alabama mayor")
        
        print(f"\n✅ Found {len(people)} people:")
        for person in people[:10]:
            print(f"   • {person['label']}")
            if person.get('description'):
                print(f"     {person['description']}")
        
        if people:
            dbpedia.save_to_json(people, "alabama_politicians.json")
        
    except Exception as e:
        logger.error(f"Error: {e}")
    
    logger.info("\n✅ Examples complete!")
    logger.info("\n" + "="*80)
    logger.info("DBpedia Lookup API is perfect for autocomplete!")
    logger.info("Use it in your search box for instant suggestions.")
    logger.info("="*80)


if __name__ == "__main__":
    asyncio.run(example_usage())
