"""
Grants.gov API Integration

Fetch federal grant opportunities and match them to nonprofits in our database.

API Documentation: https://www.grants.gov/api
Endpoints:
- search2: Search for grant opportunities
- fetchOpportunity: Get detailed opportunity information

Key Features:
- No API key required for search2 and fetchOpportunity
- Search by keyword, funding category, agency, status
- Filter by Assistance Listing Number (ALN)

Use Cases:
1. Alert nonprofits about relevant grant opportunities
2. Track oral health funding trends
3. Match available grants to eligible organizations
4. Monitor policy changes through grant announcements
"""

import requests
import pandas as pd
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path
from loguru import logger
import time


class GrantsGovAPI:
    """Client for Grants.gov RESTful API"""
    
    BASE_URL = "https://api.grants.gov/v1/api"
    STAGING_URL = "https://api.staging.grants.gov/v1/api"
    
    def __init__(self, use_staging: bool = False):
        """
        Initialize Grants.gov API client
        
        Args:
            use_staging: Use staging environment for testing
        """
        self.base_url = self.STAGING_URL if use_staging else self.BASE_URL
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'CommunityOne/1.0 (Civic Engagement Platform)'
        })
        
    def search_opportunities(
        self,
        keyword: Optional[str] = None,
        funding_categories: Optional[str] = None,
        agencies: Optional[str] = None,
        opp_statuses: str = "forecasted|posted",
        eligibilities: Optional[str] = None,
        aln: Optional[str] = None,
        rows: int = 100,
        start_record: int = 0
    ) -> Dict:
        """
        Search for grant opportunities
        
        Args:
            keyword: Search keyword (e.g., "oral health", "dental")
            funding_categories: Funding category codes (e.g., "HL" for Health)
            agencies: Agency codes (e.g., "HHS", "HHS-NIH")
            opp_statuses: Pipe-separated statuses (forecasted|posted|closed|archived)
            eligibilities: Eligibility codes (pipe-separated)
            aln: Assistance Listing Number (formerly CFDA)
            rows: Number of results to return (default 100)
            start_record: Starting record for pagination
            
        Returns:
            API response with search results
            
        Example:
            >>> api = GrantsGovAPI()
            >>> results = api.search_opportunities(
            ...     keyword="oral health",
            ...     funding_categories="HL",
            ...     agencies="HHS",
            ...     opp_statuses="forecasted|posted"
            ... )
        """
        url = f"{self.base_url}/search2"
        
        payload = {
            "rows": rows,
            "startRecordNum": start_record,
            "oppStatuses": opp_statuses
        }
        
        # Add optional parameters
        if keyword:
            payload["keyword"] = keyword
        if funding_categories:
            payload["fundingCategories"] = funding_categories
        if agencies:
            payload["agencies"] = agencies
        if eligibilities:
            payload["eligibilities"] = eligibilities
        if aln:
            payload["aln"] = aln
            
        logger.info(f"Searching Grants.gov: {payload}")
        
        response = self.session.post(url, json=payload)
        response.raise_for_status()
        
        data = response.json()
        
        if data.get("errorcode") != 0:
            logger.error(f"API error: {data.get('msg')}")
            return data
            
        hit_count = data.get("data", {}).get("hitCount", 0)
        logger.info(f"Found {hit_count:,} opportunities")
        
        return data
    
    def fetch_opportunity(self, opportunity_id: int) -> Dict:
        """
        Get detailed information about a specific grant opportunity
        
        Args:
            opportunity_id: Opportunity ID from search results
            
        Returns:
            Detailed opportunity information
        """
        url = f"{self.base_url}/fetchOpportunity"
        payload = {"opportunityId": opportunity_id}
        
        response = self.session.post(url, json=payload)
        response.raise_for_status()
        
        data = response.json()
        
        if data.get("errorcode") != 0:
            logger.error(f"API error: {data.get('msg')}")
            
        return data
    
    def search_to_dataframe(
        self,
        keyword: Optional[str] = None,
        funding_categories: Optional[str] = None,
        agencies: Optional[str] = None,
        opp_statuses: str = "forecasted|posted",
        max_results: int = 1000
    ) -> pd.DataFrame:
        """
        Search for opportunities and return as DataFrame
        
        Args:
            keyword: Search keyword
            funding_categories: Funding category codes
            agencies: Agency codes
            opp_statuses: Opportunity statuses
            max_results: Maximum number of results to fetch
            
        Returns:
            DataFrame with opportunity information
        """
        all_opportunities = []
        start_record = 0
        rows_per_request = 100
        
        while len(all_opportunities) < max_results:
            results = self.search_opportunities(
                keyword=keyword,
                funding_categories=funding_categories,
                agencies=agencies,
                opp_statuses=opp_statuses,
                rows=rows_per_request,
                start_record=start_record
            )
            
            if results.get("errorcode") != 0:
                break
                
            data = results.get("data", {})
            hits = data.get("oppHits", [])
            
            if not hits:
                break
                
            all_opportunities.extend(hits)
            
            # Check if we've fetched all available results
            hit_count = data.get("hitCount", 0)
            if len(all_opportunities) >= hit_count:
                break
                
            start_record += rows_per_request
            time.sleep(0.5)  # Rate limiting
            
        # Convert to DataFrame
        if all_opportunities:
            df = pd.DataFrame(all_opportunities)
            logger.info(f"Fetched {len(df):,} opportunities")
            return df
        else:
            logger.warning("No opportunities found")
            return pd.DataFrame()


class GrantMatcher:
    """Match grant opportunities to nonprofits"""
    
    def __init__(self, grants_api: GrantsGovAPI):
        self.api = grants_api
        
    def find_oral_health_grants(
        self,
        opp_statuses: str = "forecasted|posted"
    ) -> pd.DataFrame:
        """
        Find all oral health related grant opportunities
        
        Returns:
            DataFrame with oral health grants
        """
        keywords = [
            "oral health",
            "dental",
            "fluoridation",
            "tooth decay",
            "dental care",
            "dental hygiene",
            "dentistry"
        ]
        
        all_grants = []
        
        for keyword in keywords:
            logger.info(f"Searching for: {keyword}")
            
            df = self.api.search_to_dataframe(
                keyword=keyword,
                funding_categories="HL",  # Health category
                opp_statuses=opp_statuses,
                max_results=500
            )
            
            if not df.empty:
                df['search_keyword'] = keyword
                all_grants.append(df)
            
            time.sleep(1)  # Rate limiting
            
        if all_grants:
            combined = pd.concat(all_grants, ignore_index=True)
            # Remove duplicates by opportunity ID
            combined = combined.drop_duplicates(subset=['id'])
            logger.info(f"Found {len(combined):,} unique oral health grants")
            return combined
        else:
            return pd.DataFrame()
    
    def match_grants_to_state(
        self,
        state_code: str,
        grants_df: pd.DataFrame,
        nonprofits_df: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Match grants to nonprofits in a specific state
        
        Args:
            state_code: Two-letter state code (e.g., "MA")
            grants_df: DataFrame with grant opportunities
            nonprofits_df: DataFrame with nonprofit organizations
            
        Returns:
            DataFrame with grant matches
        """
        # Filter nonprofits to state
        state_nonprofits = nonprofits_df[nonprofits_df['STATE'] == state_code].copy()
        
        logger.info(f"Matching {len(grants_df):,} grants to {len(state_nonprofits):,} nonprofits in {state_code}")
        
        # Create cross-join of all grants with all nonprofits
        # (In practice, you'd filter by eligibility criteria, NTEE codes, etc.)
        matches = []
        
        for _, grant in grants_df.iterrows():
            match_record = {
                'state': state_code,
                'opportunity_id': grant.get('id'),
                'opportunity_number': grant.get('opportunityNumber'),
                'opportunity_title': grant.get('opportunityTitle'),
                'agency': grant.get('agencyCode'),
                'agency_name': grant.get('agencyName'),
                'posted_date': grant.get('openDate'),
                'close_date': grant.get('closeDate'),
                'status': grant.get('opportunityStatus'),
                'aln': grant.get('cfdaList', [{}])[0].get('cfdaNumber') if grant.get('cfdaList') else None,
                'eligible_nonprofit_count': len(state_nonprofits),  # Placeholder - need to check actual eligibility
                'last_updated': datetime.now().isoformat()
            }
            matches.append(match_record)
            
        return pd.DataFrame(matches)
    
    def save_opportunities_by_state(
        self,
        grants_df: pd.DataFrame,
        output_dir: Path = Path("data/gold/grants")
    ):
        """
        Save grant opportunities organized by state
        
        Args:
            grants_df: DataFrame with grant opportunities
            output_dir: Output directory for grant data
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save all opportunities
        all_path = output_dir / "federal_grant_opportunities.parquet"
        grants_df.to_parquet(all_path, index=False)
        logger.info(f"Saved {len(grants_df):,} opportunities to {all_path}")
        
        # Also save by agency for easier filtering
        if 'agencyCode' in grants_df.columns:
            for agency in grants_df['agencyCode'].dropna().unique():
                agency_df = grants_df[grants_df['agencyCode'] == agency]
                agency_path = output_dir / f"opportunities_{agency.replace('-', '_')}.parquet"
                agency_df.to_parquet(agency_path, index=False)
                logger.info(f"Saved {len(agency_df):,} {agency} opportunities to {agency_path}")


def main():
    """Example usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Fetch federal grant opportunities from Grants.gov")
    parser.add_argument("--keyword", help="Search keyword")
    parser.add_argument("--funding-category", help="Funding category code (e.g., HL for Health)")
    parser.add_argument("--agency", help="Agency code (e.g., HHS)")
    parser.add_argument("--oral-health", action="store_true", help="Search for oral health grants")
    parser.add_argument("--output", type=Path, default=Path("data/gold/grants"), help="Output directory")
    parser.add_argument("--staging", action="store_true", help="Use staging environment")
    
    args = parser.parse_args()
    
    # Initialize API client
    api = GrantsGovAPI(use_staging=args.staging)
    matcher = GrantMatcher(api)
    
    if args.oral_health:
        # Find all oral health grants
        grants_df = matcher.find_oral_health_grants()
        
        if not grants_df.empty:
            # Save results
            matcher.save_opportunities_by_state(grants_df, args.output)
            
            # Display summary
            print(f"\n{'='*60}")
            print(f"Found {len(grants_df):,} oral health grant opportunities")
            print(f"{'='*60}\n")
            
            if 'agencyCode' in grants_df.columns:
                print("By Agency:")
                print(grants_df['agencyCode'].value_counts())
            
            if 'opportunityStatus' in grants_df.columns:
                print("\nBy Status:")
                print(grants_df['opportunityStatus'].value_counts())
                
    else:
        # Custom search
        results_df = api.search_to_dataframe(
            keyword=args.keyword,
            funding_categories=args.funding_category,
            agencies=args.agency,
            max_results=1000
        )
        
        if not results_df.empty:
            output_file = args.output / "grant_opportunities.parquet"
            args.output.mkdir(parents=True, exist_ok=True)
            results_df.to_parquet(output_file, index=False)
            print(f"Saved {len(results_df):,} opportunities to {output_file}")


if __name__ == "__main__":
    main()
