"""
Enrich nonprofit data with ProPublica Nonprofit Explorer API

This script adds missing fields to the IRS EO-BMF data:
- filing_type (e.g., "990", "990EZ", "990PF") - from filings_with_data
- asset_code (asset size category 0-9) - from organization
- income_code (income size category 0-9) - from organization
- ntee_description (human-readable NTEE description) - from lookup table

NOTE: ProPublica API does NOT provide website or mission statement fields.
For those, you need to parse Form 990 XML files or use other APIs (Every.org, Charity Navigator).

Author: Open Navigator for Engagement
License: MIT
"""

import pandas as pd
import requests
from pathlib import Path
from loguru import logger
from typing import Optional, Dict
import time
from tqdm import tqdm
import sys
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class ProPublicaEnricher:
    """Enrich nonprofit data using ProPublica API"""
    
    def __init__(self):
        self.api_base = "https://projects.propublica.org/nonprofits/api/v2"
        self.cache = {}
        self.request_count = 0
        self.rate_limit_delay = 1.0  # seconds between requests
        
    def get_organization(self, ein: str) -> Optional[Dict]:
        """
        Fetch organization details from ProPublica API
        
        Args:
            ein: Employer Identification Number (9 digits)
            
        Returns:
            Organization data dict or None if not found
        """
        # Check cache first
        if ein in self.cache:
            return self.cache[ein]
        
        # Rate limiting
        if self.request_count > 0:
            time.sleep(self.rate_limit_delay)
        
        try:
            url = f"{self.api_base}/organizations/{ein}.json"
            response = requests.get(url, timeout=10)
            self.request_count += 1
            
            if response.status_code == 200:
                data = response.json()
                self.cache[ein] = data
                return data
            elif response.status_code == 404:
                logger.debug(f"EIN {ein} not found in ProPublica")
                self.cache[ein] = None
                return None
            else:
                logger.warning(f"ProPublica API error for {ein}: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error fetching {ein}: {e}")
            return None
    
    def extract_fields(self, org_data: Dict) -> Dict:
        """
        Extract enrichment fields from ProPublica response
        
        ProPublica provides:
        - asset_code, income_code: In organization object (0-9 size category)
        - filing_type: In filings_with_data (0=990, 1=990EZ, 2=990PF)
        
        NOTE: ProPublica does NOT provide website or mission fields.
        Those require parsing Form 990 XML files or using other APIs.
        
        Returns:
            Dict with filing_type, asset_code, income_code
        """
        if not org_data or 'organization' not in org_data:
            return {
                'filing_type': None,
                'asset_code': None,
                'income_code': None,
            }
        
        org = org_data['organization']
        
        # Get latest filing type if available
        filing_type = None
        if 'filings_with_data' in org_data and org_data['filings_with_data']:
            latest_filing = org_data['filings_with_data'][0]
            formtype = latest_filing.get('formtype')
            # Map numeric formtype to string
            formtype_map = {0: '990', 1: '990EZ', 2: '990PF'}
            filing_type = formtype_map.get(formtype, str(formtype))
        
        # asset_code and income_code are in organization object
        # These are size categories (0-9)
        asset_code = org.get('asset_code')
        income_code = org.get('income_code')
        
        # Convert 0 to None (0 means "not reported" or "very small")
        if asset_code == 0:
            asset_code = None
        if income_code == 0:
            income_code = None
        
        return {
            'filing_type': filing_type,
            'asset_code': asset_code,
            'income_code': income_code,
        }
    
    def enrich_dataframe(
        self,
        df: pd.DataFrame,
        max_requests: Optional[int] = None,
        sample_pct: float = 0.01
    ) -> pd.DataFrame:
        """
        Enrich DataFrame with ProPublica data
        
        Args:
            df: Input DataFrame with 'ein' column
            max_requests: Maximum API requests (None = all)
            sample_pct: If max_requests is None, sample this % of data
            
        Returns:
            Enriched DataFrame
        """
        logger.info("=" * 60)
        logger.info("PROPUBLICA ENRICHMENT")
        logger.info("=" * 60)
        
        # Create copy to avoid modifying original
        enriched = df.copy()
        
        # Determine which rows to enrich
        if max_requests:
            rows_to_enrich = min(max_requests, len(df))
            sample = df.head(rows_to_enrich)
            logger.info(f"Enriching first {rows_to_enrich:,} rows (max_requests={max_requests})")
        elif sample_pct < 1.0:
            sample = df.sample(frac=sample_pct, random_state=42)
            logger.info(f"Enriching {len(sample):,} rows ({sample_pct*100:.1f}% sample)")
        else:
            sample = df
            logger.info(f"Enriching all {len(df):,} rows")
        
        # Initialize new columns
        enriched['filing_type'] = None
        enriched['asset_code'] = None
        enriched['income_code'] = None
        enriched['propublica_last_updated'] = None
        
        # Enrich each sampled row
        enriched_count = 0
        
        for idx, row in tqdm(sample.iterrows(), total=len(sample), desc="Enriching"):
            ein = str(row.get('ein', ''))
            
            if not ein or len(ein) < 9:
                continue
            
            # Fetch from ProPublica
            org_data = self.get_organization(ein)
            
            if org_data:
                fields = self.extract_fields(org_data)
                
                # Update the row
                for field, value in fields.items():
                    enriched.at[idx, field] = value
                
                # Add timestamp
                enriched.at[idx, 'propublica_last_updated'] = datetime.utcnow().isoformat()
                
                enriched_count += 1
        
        logger.success(f"Enriched {enriched_count:,} / {len(sample):,} organizations")
        logger.info(f"Total API requests: {self.request_count:,}")
        
        return enriched


class NTEEDescriptionMapper:
    """Map NTEE codes to human-readable descriptions"""
    
    # NTEE Major Categories
    MAJOR_CATEGORIES = {
        'A': 'Arts, Culture & Humanities',
        'B': 'Education',
        'C': 'Environment',
        'D': 'Animal-Related',
        'E': 'Health Care',
        'F': 'Mental Health & Crisis Intervention',
        'G': 'Voluntary Health Associations & Medical Disciplines',
        'H': 'Medical Research',
        'I': 'Crime & Legal-Related',
        'J': 'Employment',
        'K': 'Food, Agriculture & Nutrition',
        'L': 'Housing & Shelter',
        'M': 'Public Safety, Disaster Preparedness & Relief',
        'N': 'Recreation & Sports',
        'O': 'Youth Development',
        'P': 'Human Services',
        'Q': 'International, Foreign Affairs & National Security',
        'R': 'Civil Rights, Social Action & Advocacy',
        'S': 'Community Improvement & Capacity Building',
        'T': 'Philanthropy, Voluntarism & Grantmaking Foundations',
        'U': 'Science & Technology',
        'V': 'Social Science',
        'W': 'Public & Societal Benefit',
        'X': 'Religion-Related',
        'Y': 'Mutual & Membership Benefit',
        'Z': 'Unknown',
    }
    
    # Common subcategories (add more as needed)
    SUBCATEGORIES = {
        'E20': 'Hospitals & Primary Care Facilities',
        'E30': 'Ambulatory & Community Health Care',
        'E40': 'Reproductive Health Care',
        'E50': 'Rehabilitative Care',
        'E60': 'Health Support Services',
        'E70': 'Public Health',
        'E80': 'Health Organizations - General & Financing',
        'P20': 'Human Service Organizations - Multipurpose',
        'P30': 'Children & Youth Services',
        'P40': 'Family Services',
        'P50': 'Personal Social Services',
        'P60': 'Emergency Assistance',
        'P70': 'Residential & Custodial Care',
        'P80': 'Services to Promote Independence',
        'X20': 'Christian',
        'X21': 'Protestant',
        'X22': 'Roman Catholic',
        'X30': 'Jewish',
        'X40': 'Islamic',
        'X50': 'Buddhist',
        'X70': 'Hindu',
        'X80': 'Religious Media & Communications',
    }
    
    @classmethod
    def get_description(cls, ntee_code: str) -> str:
        """
        Get human-readable description for NTEE code
        
        Args:
            ntee_code: NTEE code (e.g., "E30", "P80")
            
        Returns:
            Description string or None
        """
        if not ntee_code:
            return None
        
        ntee = str(ntee_code).strip().upper()
        
        # Check for exact match in subcategories
        if ntee in cls.SUBCATEGORIES:
            return cls.SUBCATEGORIES[ntee]
        
        # Check for major category (first letter)
        major_code = ntee[0] if ntee else ''
        if major_code in cls.MAJOR_CATEGORIES:
            return cls.MAJOR_CATEGORIES[major_code]
        
        return None
    
    @classmethod
    def add_descriptions(cls, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add ntee_description column to DataFrame
        
        Args:
            df: DataFrame with 'ntee_code' column
            
        Returns:
            DataFrame with added 'ntee_description' column
        """
        logger.info("Adding NTEE descriptions...")
        
        df['ntee_description'] = df['ntee_code'].apply(cls.get_description)
        
        described_count = df['ntee_description'].notna().sum()
        logger.success(f"Added descriptions for {described_count:,} / {len(df):,} organizations")
        
        return df


def main():
    """Main enrichment workflow"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Enrich nonprofit data with ProPublica API"
    )
    parser.add_argument(
        "--input",
        default="data/gold/nonprofits_organizations.parquet",
        help="Input Parquet file"
    )
    parser.add_argument(
        "--output",
        default="data/gold/nonprofits_organizations_enriched.parquet",
        help="Output Parquet file"
    )
    parser.add_argument(
        "--max-requests",
        type=int,
        help="Maximum API requests (default: 1%% sample)"
    )
    parser.add_argument(
        "--sample-pct",
        type=float,
        default=0.01,
        help="Sample percentage (0.01 = 1%%)"
    )
    parser.add_argument(
        "--ntee-only",
        action="store_true",
        help="Only add NTEE descriptions (no API calls)"
    )
    
    args = parser.parse_args()
    
    # Load input data
    input_path = Path(args.input)
    if not input_path.exists():
        logger.error(f"Input file not found: {input_path}")
        return 1
    
    logger.info(f"Loading {input_path}...")
    df = pd.read_parquet(input_path)
    logger.info(f"Loaded {len(df):,} organizations")
    
    # Add NTEE descriptions
    df = NTEEDescriptionMapper.add_descriptions(df)
    
    # Enrich with ProPublica (unless --ntee-only)
    if not args.ntee_only:
        enricher = ProPublicaEnricher()
        df = enricher.enrich_dataframe(
            df,
            max_requests=args.max_requests,
            sample_pct=args.sample_pct
        )
    
    # Save enriched data
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(output_path, index=False)
    logger.success(f"Saved enriched data: {output_path}")
    
    # Show summary
    logger.info("")
    logger.info("=" * 60)
    logger.info("ENRICHMENT SUMMARY")
    logger.info("=" * 60)
    
    for field in ['ntee_description', 'filing_type', 'asset_code', 'income_code']:
        if field in df.columns:
            non_null = df[field].notna().sum()
            pct = (non_null / len(df)) * 100
            logger.info(f"{field:20s}: {non_null:7,} / {len(df):7,} ({pct:5.1f}%)")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
