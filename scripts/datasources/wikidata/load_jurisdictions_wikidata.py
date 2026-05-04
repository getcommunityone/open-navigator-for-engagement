#!/usr/bin/env python3
"""
Load Jurisdictions from WikiData

Queries WikiData for all cities, counties, school districts, and states,
populating a jurisdictions_wikidata table with official data including:
- Official websites
- YouTube channels
- Social media (Facebook, Twitter)
- Population
- Geographic coordinates

This serves as a validation source for channel quality and provides
authoritative jurisdiction metadata.

Usage:
    # Load all dev states
    python scripts/datasources/wikidata/load_jurisdictions_wikidata.py --states AL,GA,IN,MA,WA,WI
    
    # Load specific state
    python scripts/datasources/wikidata/load_jurisdictions_wikidata.py --states AL
    
    # Load all jurisdiction types
    python scripts/datasources/wikidata/load_jurisdictions_wikidata.py --states AL --types city,county,school_district,state
"""
import os
import sys
import argparse
import asyncio
from typing import List, Dict, Optional
from datetime import datetime
import psycopg2
from psycopg2.extras import execute_batch
from loguru import logger
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from scripts.datasources.wikidata.wikidata_integration import WikidataQuery

load_dotenv()

DATABASE_URL = os.getenv('NEON_DATABASE_URL_DEV', 'postgresql://postgres:password@localhost:5433/open_navigator')

# State mapping - includes WikiData Q-codes
STATE_MAP = {
    "AL": {"name": "Alabama", "q_code": "Q173"},
    "GA": {"name": "Georgia", "q_code": "Q1428"},
    "IN": {"name": "Indiana", "q_code": "Q1415"},
    "MA": {"name": "Massachusetts", "q_code": "Q771"},
    "WA": {"name": "Washington", "q_code": "Q1223"},
    "WI": {"name": "Wisconsin", "q_code": "Q1537"}
}

# WikiData Q-codes for jurisdiction types
JURISDICTION_TYPES = {
    "city": "Q515",  # City
    "town": "Q3957",  # Town/Municipality
    "county": "Q47168",  # County of the United States
    "school_district": "Q1455778",  # School district
    "state": "Q35657"  # State of the United States
}


class JurisdictionsWikiDataLoader:
    """Load jurisdiction data from WikiData into PostgreSQL."""
    
    def __init__(self, database_url: str):
        self.conn = psycopg2.connect(database_url)
        self.wikidata = WikidataQuery()
        
        # Create table
        self._create_table()
    
    def _create_table(self):
        """Create jurisdictions_wikidata table."""
        cursor = self.conn.cursor()
        
        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS jurisdictions_wikidata (
                    id SERIAL PRIMARY KEY,
                    
                    -- Identifiers
                    wikidata_id VARCHAR(20) UNIQUE NOT NULL,
                    jurisdiction_id VARCHAR(50),  -- Link to jurisdictions_details_search
                    jurisdiction_name VARCHAR(200) NOT NULL,
                    state_code VARCHAR(2) NOT NULL,
                    state VARCHAR(50) NOT NULL,
                    jurisdiction_type VARCHAR(50) NOT NULL,  -- city, county, school_district, state
                    
                    -- Official links
                    official_website TEXT,
                    youtube_channel_id VARCHAR(50),
                    youtube_channel_url TEXT,
                    facebook_username VARCHAR(100),
                    facebook_url TEXT,
                    twitter_username VARCHAR(100),
                    twitter_url TEXT,
                    
                    -- Demographics
                    population INTEGER,
                    area_sq_km FLOAT,
                    
                    -- Geographic
                    latitude FLOAT,
                    longitude FLOAT,
                    
                    -- Metadata
                    confidence_score FLOAT DEFAULT 1.0,
                    fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    notes TEXT
                );
            """)
            
            # Create indexes
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_wikidata_state ON jurisdictions_wikidata(state_code);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_wikidata_type ON jurisdictions_wikidata(jurisdiction_type);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_wikidata_youtube ON jurisdictions_wikidata(youtube_channel_id);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_wikidata_jurisdiction_id ON jurisdictions_wikidata(jurisdiction_id);")
            
            self.conn.commit()
            logger.success("✓ Created jurisdictions_wikidata table")
            
        except Exception as e:
            self.conn.rollback()
            logger.warning(f"Table creation note: {e}")
        finally:
            cursor.close()
    
    async def query_all_jurisdictions_in_state(self, state_code: str, types: List[str]) -> List[Dict]:
        """Query WikiData for all jurisdiction types in a state using efficient VALUES query."""
        state_info = STATE_MAP.get(state_code)
        if not state_info:
            logger.error(f"Unknown state code: {state_code}")
            return []
        
        state_name = state_info["name"]
        state_q_code = state_info["q_code"]
        
        # Build VALUES clause for jurisdiction types
        type_q_codes = []
        type_map = {}
        
        if 'state' in types:
            # State query is separate
            pass
        
        if 'city' in types or 'town' in types:
            type_q_codes.append(f"wd:{JURISDICTION_TYPES['city']}")
            type_map[JURISDICTION_TYPES['city']] = 'city'
            type_q_codes.append(f"wd:{JURISDICTION_TYPES['town']}")
            type_map[JURISDICTION_TYPES['town']] = 'city'
        
        if 'county' in types:
            type_q_codes.append(f"wd:{JURISDICTION_TYPES['county']}")
            type_map[JURISDICTION_TYPES['county']] = 'county'
        
        if 'school_district' in types:
            type_q_codes.append(f"wd:{JURISDICTION_TYPES['school_district']}")
            type_map[JURISDICTION_TYPES['school_district']] = 'school_district'
        
        if not type_q_codes:
            return []
        
        values_clause = " ".join(type_q_codes)
        
        query = f"""
        SELECT DISTINCT 
            ?item ?itemLabel ?type ?typeLabel
            ?website ?population ?area
            ?facebook ?twitter ?youtube
            ?lat ?lon
        WHERE {{
          # Define the types we are looking for
          VALUES ?type {{ {values_clause} }}
          
          # Item is an instance of one of these types
          ?item wdt:P31 ?type.
          
          # Located in the state (transitive - includes cities in counties in state)
          ?item wdt:P131* wd:{state_q_code}.
          
          # Optional: official website
          OPTIONAL {{ ?item wdt:P856 ?website . }}
          
          # Optional: population
          OPTIONAL {{ ?item wdt:P1082 ?population . }}
          
          # Optional: area
          OPTIONAL {{ ?item wdt:P2046 ?area . }}
          
          # Optional: social media
          OPTIONAL {{ ?item wdt:P2013 ?facebook . }}
          OPTIONAL {{ ?item wdt:P2002 ?twitter . }}
          OPTIONAL {{ ?item wdt:P2397 ?youtube . }}
          
          # Optional: coordinates
          OPTIONAL {{ ?item p:P625/psv:P625/wikibase:geoLatitude ?lat . }}
          OPTIONAL {{ ?item p:P625/psv:P625/wikibase:geoLongitude ?lon . }}
          
          SERVICE wikibase:label {{ bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }}
        }}
        """
        
        logger.info(f"Querying WikiData for {', '.join(types)} in {state_name}...")
        results = await self.wikidata.execute_sparql(query)
        
        jurisdictions = []
        for result in results:
            wikidata_id = result.get("item", "").split("/")[-1]
            type_id = result.get("type", "").split("/")[-1]
            youtube_channel_id = result.get("youtube")
            
            # Map type ID to our jurisdiction type
            jurisdiction_type = type_map.get(type_id, 'unknown')
            
            jurisdictions.append({
                'wikidata_id': wikidata_id,
                'jurisdiction_name': result.get("itemLabel", ""),
                'state_code': state_code,
                'state': state_name,
                'jurisdiction_type': jurisdiction_type,
                'official_website': result.get("website"),
                'youtube_channel_id': youtube_channel_id,
                'youtube_channel_url': f"https://www.youtube.com/channel/{youtube_channel_id}" if youtube_channel_id else None,
                'facebook_username': result.get("facebook"),
                'facebook_url': f"https://www.facebook.com/{result.get('facebook')}" if result.get('facebook') else None,
                'twitter_username': result.get("twitter"),
                'twitter_url': f"https://twitter.com/{result.get('twitter')}" if result.get('twitter') else None,
                'population': int(result.get("population")) if result.get("population") else None,
                'area_sq_km': float(result.get("area")) if result.get("area") else None,
                'latitude': float(result.get("lat")) if result.get("lat") else None,
                'longitude': float(result.get("lon")) if result.get("lon") else None,
            })
        
        logger.success(f"✓ Found {len(jurisdictions)} jurisdictions in {state_name}")
        return jurisdictions
    
    async def query_state_info(self, state_code: str) -> List[Dict]:
        """Query WikiData for state government info."""
        state_info = STATE_MAP.get(state_code)
        if not state_info:
            return []
        
        state_name = state_info["name"]
        state_q_code = state_info["q_code"]
        
        query = f"""
        SELECT DISTINCT 
            ?item ?itemLabel 
            ?website ?population ?area
            ?facebook ?twitter ?youtube
            ?lat ?lon
        WHERE {{
          # Direct reference to the state
          BIND(wd:{state_q_code} AS ?item)
          
          OPTIONAL {{ ?item wdt:P856 ?website . }}
          OPTIONAL {{ ?item wdt:P1082 ?population . }}
          OPTIONAL {{ ?item wdt:P2046 ?area . }}
          OPTIONAL {{ ?item wdt:P2013 ?facebook . }}
          OPTIONAL {{ ?item wdt:P2002 ?twitter . }}
          OPTIONAL {{ ?item wdt:P2397 ?youtube . }}
          OPTIONAL {{ ?item p:P625/psv:P625/wikibase:geoLatitude ?lat . }}
          OPTIONAL {{ ?item p:P625/psv:P625/wikibase:geoLongitude ?lon . }}
          
          SERVICE wikibase:label {{ bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }}
        }}
        """
        
        logger.info(f"Querying WikiData for state: {state_name}...")
        results = await self.wikidata.execute_sparql(query)
        
        if not results:
            logger.warning(f"No WikiData entry found for {state_name}")
            return []
        
        result = results[0]
        youtube_channel_id = result.get("youtube")
        
        return [{
            'wikidata_id': state_q_code,
            'jurisdiction_name': state_name,
            'state_code': state_code,
            'state': state_name,
            'jurisdiction_type': 'state',
            'official_website': result.get("website"),
            'youtube_channel_id': youtube_channel_id,
            'youtube_channel_url': f"https://www.youtube.com/channel/{youtube_channel_id}" if youtube_channel_id else None,
            'facebook_username': result.get("facebook"),
            'facebook_url': f"https://www.facebook.com/{result.get('facebook')}" if result.get('facebook') else None,
            'twitter_username': result.get("twitter"),
            'twitter_url': f"https://twitter.com/{result.get('twitter')}" if result.get('twitter') else None,
            'population': int(result.get("population")) if result.get("population") else None,
            'area_sq_km': float(result.get("area")) if result.get("area") else None,
            'latitude': float(result.get("lat")) if result.get("lat") else None,
            'longitude': float(result.get("lon")) if result.get("lon") else None,
        }]
    
    def insert_jurisdictions(self, jurisdictions: List[Dict]):
        """Insert jurisdictions into database."""
        if not jurisdictions:
            return
        
        cursor = self.conn.cursor()
        
        insert_query = """
            INSERT INTO jurisdictions_wikidata (
                wikidata_id, jurisdiction_name, state_code, state, jurisdiction_type,
                official_website, youtube_channel_id, youtube_channel_url,
                facebook_username, facebook_url, twitter_username, twitter_url,
                population, area_sq_km, latitude, longitude,
                confidence_score, fetched_at
            ) VALUES (
                %(wikidata_id)s, %(jurisdiction_name)s, %(state_code)s, %(state)s, %(jurisdiction_type)s,
                %(official_website)s, %(youtube_channel_id)s, %(youtube_channel_url)s,
                %(facebook_username)s, %(facebook_url)s, %(twitter_username)s, %(twitter_url)s,
                %(population)s, %(area_sq_km)s, %(latitude)s, %(longitude)s,
                1.0, CURRENT_TIMESTAMP
            )
            ON CONFLICT (wikidata_id) DO UPDATE SET
                official_website = COALESCE(EXCLUDED.official_website, jurisdictions_wikidata.official_website),
                youtube_channel_id = COALESCE(EXCLUDED.youtube_channel_id, jurisdictions_wikidata.youtube_channel_id),
                youtube_channel_url = COALESCE(EXCLUDED.youtube_channel_url, jurisdictions_wikidata.youtube_channel_url),
                facebook_username = COALESCE(EXCLUDED.facebook_username, jurisdictions_wikidata.facebook_username),
                facebook_url = COALESCE(EXCLUDED.facebook_url, jurisdictions_wikidata.facebook_url),
                twitter_username = COALESCE(EXCLUDED.twitter_username, jurisdictions_wikidata.twitter_username),
                twitter_url = COALESCE(EXCLUDED.twitter_url, jurisdictions_wikidata.twitter_url),
                population = COALESCE(EXCLUDED.population, jurisdictions_wikidata.population),
                area_sq_km = COALESCE(EXCLUDED.area_sq_km, jurisdictions_wikidata.area_sq_km),
                latitude = COALESCE(EXCLUDED.latitude, jurisdictions_wikidata.latitude),
                longitude = COALESCE(EXCLUDED.longitude, jurisdictions_wikidata.longitude),
                last_updated = CURRENT_TIMESTAMP
        """
        
        try:
            execute_batch(cursor, insert_query, jurisdictions, page_size=100)
            self.conn.commit()
            logger.success(f"✓ Inserted {len(jurisdictions)} jurisdictions")
        except Exception as e:
            self.conn.rollback()
            logger.error(f"Error inserting jurisdictions: {e}")
            raise
        finally:
            cursor.close()
    
    async def load_state(self, state_code: str, types: List[str]):
        """Load all jurisdiction types for a state."""
        state_info = STATE_MAP.get(state_code, {})
        state_name = state_info.get('name', state_code)
        
        logger.info("")
        logger.info("=" * 80)
        logger.info(f"LOADING WIKIDATA FOR {state_name}")
        logger.info("=" * 80)
        
        all_jurisdictions = []
        
        # Load state info separately
        if 'state' in types:
            state_data = await self.query_state_info(state_code)
            all_jurisdictions.extend(state_data)
            if state_data:
                self.insert_jurisdictions(state_data)
        
        # Load other jurisdiction types in one efficient query
        other_types = [t for t in types if t != 'state']
        if other_types:
            jurisdictions = await self.query_all_jurisdictions_in_state(state_code, other_types)
            all_jurisdictions.extend(jurisdictions)
            if jurisdictions:
                self.insert_jurisdictions(jurisdictions)
        
        # Summary
        with_youtube = sum(1 for j in all_jurisdictions if j.get('youtube_channel_id'))
        with_website = sum(1 for j in all_jurisdictions if j.get('official_website'))
        
        logger.info("")
        logger.success(f"✓ Loaded {len(all_jurisdictions)} jurisdictions for {state_code}")
        logger.info(f"  With YouTube channels: {with_youtube}")
        logger.info(f"  With official websites: {with_website}")
    
    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Load jurisdictions from WikiData')
    
    parser.add_argument(
        '--states',
        type=str,
        required=True,
        help='Comma-separated list of state codes (e.g., AL,MA,WI)'
    )
    
    parser.add_argument(
        '--types',
        type=str,
        default='city,county,state',
        help='Comma-separated jurisdiction types (default: city,county,state)'
    )
    
    args = parser.parse_args()
    
    # Parse states and types
    states = [s.strip().upper() for s in args.states.split(',')]
    types = [t.strip().lower() for t in args.types.split(',')]
    
    # Load data
    loader = JurisdictionsWikiDataLoader(DATABASE_URL)
    
    try:
        for state in states:
            await loader.load_state(state, types)
        
        # Final summary
        cursor = loader.conn.cursor()
        cursor.execute("""
            SELECT 
                jurisdiction_type,
                COUNT(*) as count,
                COUNT(*) FILTER (WHERE youtube_channel_id IS NOT NULL) as with_youtube,
                COUNT(*) FILTER (WHERE official_website IS NOT NULL) as with_website
            FROM jurisdictions_wikidata
            GROUP BY jurisdiction_type
            ORDER BY count DESC
        """)
        
        logger.info("")
        logger.info("=" * 80)
        logger.info("FINAL SUMMARY")
        logger.info("=" * 80)
        
        for row in cursor.fetchall():
            jtype, count, youtube, website = row
            logger.info(f"{jtype:15s}: {count:4d} total, {youtube:3d} with YouTube, {website:3d} with website")
        
        cursor.close()
        
    finally:
        loader.close()


if __name__ == '__main__':
    asyncio.run(main())
