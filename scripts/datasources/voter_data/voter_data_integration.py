"""
Voter Registration Data Integration

Track voter registration and political demographics:
- Party affiliation by jurisdiction
- Voter turnout patterns
- Demographic trends
- Elected official party affiliations

Data Sources:
1. State Voter Files: Most comprehensive (state-by-state)
2. L2 Political: Commercial voter data aggregator
3. Aristotle: Commercial political data
4. VoteRef.com: Public voter lookup (manual)
5. VSEC (Voter Study Election Consortium): Research data

Note:
    Most comprehensive voter data requires:
    - State-by-state public records requests
    - Commercial vendor licenses (L2, Aristotle)
    - Academic research access (VSEC)
    
    For free/open access, we use:
    - MIT Election Data Lab
    - OpenElections project
    - Census voting statistics
"""

import requests
import pandas as pd
from typing import Dict, List, Optional
from pathlib import Path
from loguru import logger
import time


class VoterDataIntegration:
    """
    Aggregate voter and election data from public sources
    
    Note: Comprehensive voter files require commercial licenses.
    This class focuses on publicly available aggregated data.
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'CommunityOne/1.0 (Civic Engagement Platform)'
        })
    
    def get_state_party_registration(self, state_code: str) -> Optional[Dict]:
        """
        Get party registration statistics for a state
        
        Note: This requires state-specific APIs or manual data collection.
        Each state has different formats and availability.
        
        Args:
            state_code: Two-letter state code
            
        Returns:
            Party registration statistics (if available)
        """
        # Massachusetts example: https://www.sec.state.ma.us/ele/eleenr/enridx.htm
        # This would need state-specific implementations
        
        logger.info(f"Party registration data requires state-specific implementation for {state_code}")
        logger.info("Consider using commercial vendors (L2, Aristotle) for comprehensive data")
        
        return None
    
    def get_census_voting_stats(
        self,
        state_code: str,
        county_name: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Get voting statistics from Census Bureau
        
        Census provides:
        - Voting-age population
        - Registration rates
        - Turnout rates
        - Demographics of voters
        
        API: https://www.census.gov/data/developers/data-sets/acs-5year.html
        
        Args:
            state_code: Two-letter state code
            county_name: Optional county name
            
        Returns:
            DataFrame with voting statistics
        """
        logger.info(f"Census voting statistics for {state_code}")
        logger.info("This requires Census API key and specific table queries")
        
        # Placeholder - would implement Census API calls
        return pd.DataFrame()
    
    def enrich_jurisdictions_with_party_data(
        self,
        jurisdictions_df: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Enrich jurisdiction data with party affiliation estimates
        
        Args:
            jurisdictions_df: DataFrame with jurisdictions
            
        Returns:
            Enriched DataFrame
        """
        logger.info("Enriching jurisdictions with political data")
        
        # This would integrate:
        # 1. Election results (president, governor) as proxy for party lean
        # 2. Voter registration data (where available)
        # 3. Census voting statistics
        
        # Placeholder implementation
        jurisdictions_df['party_lean'] = None  # 'D', 'R', 'Swing', etc.
        jurisdictions_df['voter_registration_rate'] = None
        jurisdictions_df['voter_turnout_2024'] = None
        
        return jurisdictions_df


class ElectedOfficialsTracker:
    """Track elected officials and their party affiliations"""
    
    OPENSTATES_API = "https://v3.openstates.org"
    GOOGLE_CIVIC_API = "https://www.googleapis.com/civicinfo/v2"
    
    def __init__(
        self,
        openstates_api_key: Optional[str] = None,
        google_civic_api_key: Optional[str] = None
    ):
        """
        Initialize tracker
        
        Args:
            openstates_api_key: OpenStates API key (https://openstates.org/accounts/profile/)
            google_civic_api_key: Google Civic Information API key
        """
        self.openstates_api_key = openstates_api_key
        self.google_civic_api_key = google_civic_api_key
        self.session = requests.Session()
        
    def get_state_legislators(self, state_code: str) -> pd.DataFrame:
        """
        Get current state legislators with party affiliations
        
        Uses OpenStates API
        
        Args:
            state_code: Two-letter state code
            
        Returns:
            DataFrame with legislator information
        """
        if not self.openstates_api_key:
            logger.warning("OpenStates API key required")
            return pd.DataFrame()
        
        url = f"{self.OPENSTATES_API}/people"
        headers = {"X-API-KEY": self.openstates_api_key}
        params = {
            "jurisdiction": state_code.lower(),
            "per_page": 100
        }
        
        all_legislators = []
        
        while True:
            response = self.session.get(url, headers=headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            all_legislators.extend(data.get('results', []))
            
            # Check for next page
            if not data.get('pagination', {}).get('next'):
                break
                
            params['page'] = data['pagination'].get('page', 1) + 1
            time.sleep(0.5)
        
        df = pd.DataFrame(all_legislators)
        logger.info(f"Found {len(df):,} legislators for {state_code}")
        
        return df
    
    def get_local_officials(
        self,
        address: str
    ) -> Dict:
        """
        Get local officials for an address using Google Civic API
        
        Args:
            address: Full address or city/state
            
        Returns:
            Officials information
        """
        if not self.google_civic_api_key:
            logger.warning("Google Civic API key required")
            return {}
        
        url = f"{self.GOOGLE_CIVIC_API}/representatives"
        params = {
            "address": address,
            "key": self.google_civic_api_key
        }
        
        response = self.session.get(url, params=params)
        response.raise_for_status()
        
        return response.json()


class PoliticalContextEnricher:
    """Enrich nonprofit and jurisdiction data with political context"""
    
    def __init__(self):
        pass
    
    def add_political_context_to_nonprofits(
        self,
        nonprofits_df: pd.DataFrame,
        contributions_df: pd.DataFrame,
        legislators_df: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Enrich nonprofit data with political context
        
        Adds:
        - Officer political donations
        - Local legislator party affiliations
        - Jurisdiction political lean
        
        Args:
            nonprofits_df: Nonprofit organizations
            contributions_df: FEC political contributions
            legislators_df: State/local legislators
            
        Returns:
            Enriched DataFrame
        """
        enriched = nonprofits_df.copy()
        
        # Add political donation flag
        if not contributions_df.empty:
            politically_active_eins = contributions_df['nonprofit_ein'].unique()
            enriched['has_politically_active_leadership'] = (
                enriched['EIN'].isin(politically_active_eins)
            )
        
        # Add local legislator party context
        if not legislators_df.empty and 'STATE' in enriched.columns:
            # Group legislators by state and party
            party_by_state = legislators_df.groupby(['state', 'party']).size().unstack(fill_value=0)
            
            # Calculate party majority for each state
            for state in party_by_state.index:
                if 'Democratic' in party_by_state.columns and 'Republican' in party_by_state.columns:
                    dem_count = party_by_state.loc[state, 'Democratic']
                    rep_count = party_by_state.loc[state, 'Republican']
                    
                    if dem_count > rep_count:
                        majority = 'Democratic'
                    elif rep_count > dem_count:
                        majority = 'Republican'
                    else:
                        majority = 'Split'
                    
                    enriched.loc[enriched['STATE'] == state.upper(), 'state_legislature_control'] = majority
        
        return enriched
    
    def analyze_political_environment(
        self,
        state_code: str,
        nonprofits_df: pd.DataFrame,
        contributions_df: pd.DataFrame,
        grants_df: pd.DataFrame
    ) -> Dict:
        """
        Analyze political environment for oral health policy
        
        Args:
            state_code: State to analyze
            nonprofits_df: Nonprofit organizations
            contributions_df: Political contributions
            grants_df: Grant awards
            
        Returns:
            Analysis summary
        """
        analysis = {
            'state': state_code,
            'nonprofit_count': len(nonprofits_df),
            'politically_active_orgs': 0,
            'total_political_donations': 0,
            'total_grants_received': 0,
            'donation_to_grant_ratio': 0
        }
        
        if not contributions_df.empty:
            state_contribs = contributions_df[
                contributions_df['contributor_state'] == state_code
            ]
            analysis['politically_active_orgs'] = len(
                state_contribs['nonprofit_ein'].unique()
            )
            analysis['total_political_donations'] = (
                state_contribs['contribution_amount'].sum()
            )
        
        if not grants_df.empty:
            state_grants = grants_df[grants_df['state'] == state_code]
            analysis['total_grants_received'] = (
                state_grants['grant_amount'].sum()
            )
        
        if analysis['total_political_donations'] > 0:
            analysis['donation_to_grant_ratio'] = (
                analysis['total_grants_received'] / 
                analysis['total_political_donations']
            )
        
        return analysis


def main():
    """Example usage"""
    print("Voter Data Integration")
    print("=" * 60)
    print()
    print("Data Sources:")
    print("1. State Voter Files: Requires state-by-state requests")
    print("2. L2 Political: Commercial license required")
    print("3. Aristotle: Commercial license required")
    print("4. OpenStates: Free API for legislators (key required)")
    print("5. Google Civic API: Free API for officials (key required)")
    print()
    print("For comprehensive voter data, consider:")
    print("- Contacting state election offices")
    print("- Commercial vendors for bulk national data")
    print("- Academic partnerships (VSEC, CCES)")
    print()
    print("Free alternatives for aggregated data:")
    print("- MIT Election Data Lab")
    print("- OpenElections project")
    print("- Census voting statistics")


if __name__ == "__main__":
    main()
