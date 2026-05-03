"""
Google Civic Information API Integration

The Google Civic Information API is the gold standard for:
- Address-to-representative mapping
- Elected officials contact information
- Election data and polling locations
- Voter information

API Docs: https://developers.google.com/civic-information
Free Tier: 25,000 requests/day
Cost: Free for non-commercial use

SETUP:
1. Get API key: https://console.cloud.google.com/
2. Enable "Google Civic Information API"
3. Add to .env: GOOGLE_CIVIC_API_KEY=your-key

USAGE:
    from scripts.discovery.google_civic_integration import GoogleCivicAPI
    
    api = GoogleCivicAPI()
    
    # Get representatives for an address
    reps = await api.get_representatives("1600 Pennsylvania Ave NW, Washington DC")
    
    # Get upcoming elections
    elections = await api.get_elections()
    
    # Get voter info
    voter_info = await api.get_voter_info("123 Main St, Tuscaloosa, AL")
"""
import asyncio
from typing import Dict, List, Optional
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
    logger.warning("Running without Spark/settings - limited functionality")


class GoogleCivicAPI:
    """
    Integration with Google Civic Information API.
    
    Best for:
    - "Who represents this address?" queries
    - Finding all elected officials for a location
    - Election information
    - Polling locations
    """
    
    BASE_URL = "https://www.googleapis.com/civicinfo/v2"
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Google Civic API client.
        
        Args:
            api_key: Google Civic Information API key
                    If not provided, will try to get from settings.google_civic_api_key
        """
        if api_key:
            self.api_key = api_key
        elif SPARK_AVAILABLE and hasattr(settings, 'google_civic_api_key'):
            self.api_key = settings.google_civic_api_key
        else:
            self.api_key = None
            logger.warning("⚠️  GOOGLE_CIVIC_API_KEY not found")
            logger.warning("   Get one at: https://console.cloud.google.com/")
            logger.warning("   Add to .env: GOOGLE_CIVIC_API_KEY=your-key")
        
        self.cache_dir = Path("data/cache/google_civic")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    async def get_representatives(
        self,
        address: str,
        levels: Optional[List[str]] = None,
        roles: Optional[List[str]] = None
    ) -> Dict:
        """
        Get elected officials for a given address.
        
        Args:
            address: Street address (e.g., "1600 Pennsylvania Ave NW, Washington DC")
            levels: Filter by government level: ['country', 'administrativeArea1' (state), 
                   'administrativeArea2' (county), 'locality' (city), 'subLocality1' (neighborhood)]
            roles: Filter by role: ['legislatorUpperBody', 'legislatorLowerBody', 
                  'deputyHeadOfGovernment', 'headOfGovernment', 'executiveCouncil', etc.]
        
        Returns:
            Dict with 'offices' and 'officials' keys
        """
        if not self.api_key:
            raise ValueError("Google Civic API key required. Set GOOGLE_CIVIC_API_KEY in .env")
        
        params = {
            "address": address,
            "key": self.api_key
        }
        
        if levels:
            params["levels"] = levels
        if roles:
            params["roles"] = roles
        
        logger.info(f"Fetching representatives for: {address}")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.get(
                    f"{self.BASE_URL}/representatives",
                    params=params
                )
                response.raise_for_status()
                data = response.json()
                
                # Extract and format data
                officials_data = {
                    "address": address,
                    "normalized_address": data.get("normalizedInput", {}).get("line1", address),
                    "officials": [],
                    "source": "google_civic_api",
                    "fetched_at": datetime.utcnow().isoformat()
                }
                
                # Parse offices and officials
                offices = data.get("offices", [])
                officials = data.get("officials", [])
                
                for office in offices:
                    office_name = office.get("name")
                    office_level = office.get("levels", ["unknown"])[0]
                    office_roles = office.get("roles", [])
                    
                    # Get official indices for this office
                    official_indices = office.get("officialIndices", [])
                    
                    for idx in official_indices:
                        if idx < len(officials):
                            official = officials[idx]
                            
                            officials_data["officials"].append({
                                "name": official.get("name"),
                                "office": office_name,
                                "level": office_level,
                                "roles": office_roles,
                                "party": official.get("party"),
                                "phones": official.get("phones", []),
                                "urls": official.get("urls", []),
                                "emails": official.get("emails", []),
                                "photo_url": official.get("photoUrl"),
                                "address": official.get("address", [{}])[0] if official.get("address") else {},
                                "channels": official.get("channels", [])  # Social media
                            })
                
                logger.info(f"✅ Found {len(officials_data['officials'])} officials for {address}")
                return officials_data
                
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP error: {e.response.status_code} - {e.response.text}")
                raise
            except Exception as e:
                logger.error(f"Error fetching representatives: {e}")
                raise
    
    async def get_elections(self) -> Dict:
        """
        Get information about upcoming elections.
        
        Returns:
            Dict with 'elections' list
        """
        if not self.api_key:
            raise ValueError("Google Civic API key required")
        
        logger.info("Fetching upcoming elections")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.get(
                    f"{self.BASE_URL}/elections",
                    params={"key": self.api_key}
                )
                response.raise_for_status()
                data = response.json()
                
                elections_data = {
                    "elections": data.get("elections", []),
                    "source": "google_civic_api",
                    "fetched_at": datetime.utcnow().isoformat()
                }
                
                logger.info(f"✅ Found {len(elections_data['elections'])} upcoming elections")
                return elections_data
                
            except Exception as e:
                logger.error(f"Error fetching elections: {e}")
                raise
    
    async def get_voter_info(
        self,
        address: str,
        election_id: Optional[str] = None
    ) -> Dict:
        """
        Get voter information for an address.
        
        Args:
            address: Voter's address
            election_id: Specific election ID (default: next election)
        
        Returns:
            Dict with polling location, ballot info, etc.
        """
        if not self.api_key:
            raise ValueError("Google Civic API key required")
        
        params = {
            "address": address,
            "key": self.api_key
        }
        
        if election_id:
            params["electionId"] = election_id
        
        logger.info(f"Fetching voter info for: {address}")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.get(
                    f"{self.BASE_URL}/voterinfo",
                    params=params
                )
                response.raise_for_status()
                data = response.json()
                
                voter_info = {
                    "address": address,
                    "normalized_address": data.get("normalizedInput", {}).get("line1", address),
                    "election": data.get("election"),
                    "polling_locations": data.get("pollingLocations", []),
                    "early_vote_sites": data.get("earlyVoteSites", []),
                    "contests": data.get("contests", []),
                    "state": data.get("state", []),
                    "source": "google_civic_api",
                    "fetched_at": datetime.utcnow().isoformat()
                }
                
                logger.info(f"✅ Found voter info for {address}")
                return voter_info
                
            except Exception as e:
                logger.error(f"Error fetching voter info: {e}")
                raise
    
    async def get_representatives_by_division(self, ocd_id: str) -> Dict:
        """
        Get representatives for an Open Civic Data division ID.
        
        Args:
            ocd_id: OCD ID (e.g., "ocd-division/country:us/state:al/county:tuscaloosa")
        
        Returns:
            Dict with officials for that division
        """
        if not self.api_key:
            raise ValueError("Google Civic API key required")
        
        logger.info(f"Fetching representatives for OCD ID: {ocd_id}")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.get(
                    f"{self.BASE_URL}/representatives/{ocd_id}",
                    params={"key": self.api_key}
                )
                response.raise_for_status()
                return response.json()
                
            except Exception as e:
                logger.error(f"Error fetching division representatives: {e}")
                raise
    
    def save_to_json(self, data: Dict, filename: str):
        """Save data to JSON cache."""
        import json
        
        filepath = self.cache_dir / filename
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"💾 Saved to {filepath}")


# ============================================================================
# Example Usage
# ============================================================================

async def example_usage():
    """Example usage of Google Civic API."""
    
    # Initialize (will get key from settings or environment)
    api = GoogleCivicAPI()
    
    if not api.api_key:
        logger.error("❌ API key not found. Please set GOOGLE_CIVIC_API_KEY in .env")
        return
    
    # Example 1: Get representatives for Tuscaloosa City Hall
    logger.info("\n" + "="*80)
    logger.info("Example 1: Get representatives for Tuscaloosa, AL")
    logger.info("="*80)
    
    try:
        reps = await api.get_representatives("2201 University Blvd, Tuscaloosa, AL 35401")
        
        print(f"\n✅ Found {len(reps['officials'])} officials:")
        for official in reps['officials'][:10]:  # Show first 10
            print(f"\n   • {official['name']}")
            print(f"     Office: {official['office']}")
            print(f"     Level: {official['level']}")
            print(f"     Party: {official.get('party', 'N/A')}")
            if official.get('phones'):
                print(f"     Phone: {official['phones'][0]}")
            if official.get('urls'):
                print(f"     Website: {official['urls'][0]}")
        
        # Save to cache
        api.save_to_json(reps, "tuscaloosa_representatives.json")
        
    except Exception as e:
        logger.error(f"Error: {e}")
    
    # Example 2: Get upcoming elections
    logger.info("\n" + "="*80)
    logger.info("Example 2: Get upcoming elections")
    logger.info("="*80)
    
    try:
        elections = await api.get_elections()
        
        print(f"\n✅ Found {len(elections['elections'])} upcoming elections:")
        for election in elections['elections']:
            print(f"\n   • {election['name']}")
            print(f"     Date: {election['electionDay']}")
            print(f"     ID: {election['id']}")
        
        api.save_to_json(elections, "upcoming_elections.json")
        
    except Exception as e:
        logger.error(f"Error: {e}")
    
    # Example 3: Get voter info
    logger.info("\n" + "="*80)
    logger.info("Example 3: Get voter information")
    logger.info("="*80)
    
    try:
        voter_info = await api.get_voter_info("2201 University Blvd, Tuscaloosa, AL 35401")
        
        print(f"\n✅ Voter Information:")
        print(f"   Election: {voter_info['election']['name'] if voter_info.get('election') else 'None upcoming'}")
        if voter_info.get('polling_locations'):
            print(f"   Polling Locations: {len(voter_info['polling_locations'])}")
        if voter_info.get('contests'):
            print(f"   Ballot Contests: {len(voter_info['contests'])}")
        
        api.save_to_json(voter_info, "tuscaloosa_voter_info.json")
        
    except Exception as e:
        logger.error(f"Error: {e}")
    
    logger.info("\n✅ Examples complete!")


if __name__ == "__main__":
    # Run examples
    asyncio.run(example_usage())
