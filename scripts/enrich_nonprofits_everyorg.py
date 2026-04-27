"""
Enrich nonprofit data with Every.org API

This script adds rich metadata from Every.org:
- website (organization URL)
- mission (description and descriptionLong)
- logo_url (Cloudinary CDN URL)
- cover_image_url (cover photo URL)
- profile_url (Every.org profile page)
- causes (tags array - animals, health, education, etc.)
- fundraisers (active campaigns and donation info)

API Docs: https://www.every.org/nonprofit-api
Requires: EVERYORG_API_KEY in .env file

Author: Open Navigator for Engagement
License: MIT
"""

import pandas as pd
import requests
from pathlib import Path
from loguru import logger
from typing import Optional, Dict, List
import time
from tqdm import tqdm
import sys
import os
from dotenv import load_dotenv
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Load environment variables
load_dotenv()


class EveryOrgEnricher:
    """Enrich nonprofit data using Every.org API"""
    
    def __init__(self):
        self.api_base = "https://partners.every.org/v0.2"
        self.api_key = os.getenv('EVERYORG_API_KEY')
        
        if not self.api_key:
            raise ValueError("EVERYORG_API_KEY not found in .env file")
        
        self.cache = {}
        self.request_count = 0
        self.rate_limit_delay = 0.5  # seconds between requests
        
        logger.info(f"✅ Every.org API key loaded: {self.api_key[:8]}...")
        
    def get_nonprofit_by_ein(self, ein: str) -> Optional[Dict]:
        """
        Fetch nonprofit details from Every.org API by EIN
        
        API Endpoint: GET /nonprofit/:ein
        
        Args:
            ein: Employer Identification Number (9 digits)
            
        Returns:
            Nonprofit data dict or None if not found
        """
        # Check cache first
        if ein in self.cache:
            return self.cache[ein]
        
        # Rate limiting
        if self.request_count > 0:
            time.sleep(self.rate_limit_delay)
        
        try:
            # Format EIN (remove dashes, ensure 9 digits)
            clean_ein = str(ein).replace('-', '').zfill(9)
            
            url = f"{self.api_base}/nonprofit/{clean_ein}"
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Accept': 'application/json'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            self.request_count += 1
            
            if response.status_code == 200:
                data = response.json()
                self.cache[ein] = data
                return data
            elif response.status_code == 404:
                logger.debug(f"EIN {ein} not found in Every.org")
                self.cache[ein] = None
                return None
            else:
                logger.warning(f"Every.org API error for {ein}: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error fetching {ein}: {e}")
            return None
    
    def extract_fields(self, org_data: Dict) -> Dict:
        """
        Extract enrichment fields from Every.org response
        
        Returns:
            Dict with website, mission, logo_url, cover_image_url, profile_url, causes, fundraisers
        """
        if not org_data or 'data' not in org_data:
            return {
                'website': None,
                'mission': None,
                'logo_url': None,
                'cover_image_url': None,
                'profile_url': None,
                'causes': None,
                'primary_slug': None,
                'is_disbursable': None,
            }
        
        nonprofit = org_data['data'].get('nonprofit', {})
        tags = org_data['data'].get('nonprofitTags', [])
        
        # Extract cause categories
        causes = [tag.get('tagName') for tag in tags if tag.get('tagName')]
        causes_str = ','.join(causes) if causes else None
        
        return {
            'website': nonprofit.get('websiteUrl'),
            'mission': nonprofit.get('description') or nonprofit.get('descriptionLong'),
            'logo_url': nonprofit.get('logoUrl'),
            'cover_image_url': nonprofit.get('coverImageUrl'),
            'profile_url': nonprofit.get('profileUrl'),
            'causes': causes_str,
            'primary_slug': nonprofit.get('primarySlug'),
            'is_disbursable': nonprofit.get('isDisbursable'),
        }
    
    def enrich_dataframe(
        self,
        df: pd.DataFrame,
        max_requests: Optional[int] = None,
        sample_pct: float = 0.01,
        incremental: bool = False,
        max_age_days: int = 30
    ) -> pd.DataFrame:
        """
        Enrich DataFrame with Every.org data
        
        Args:
            df: Input DataFrame with 'ein' column
            max_requests: Maximum API requests (None = use sample_pct)
            sample_pct: If max_requests is None, sample this % of data
            incremental: If True, only enrich records older than max_age_days
            max_age_days: For incremental mode, only refresh records older than this
            
        Returns:
            Enriched DataFrame
        """
        logger.info("=" * 60)
        logger.info("EVERY.ORG ENRICHMENT")
        logger.info("=" * 60)
        
        # Create copy to avoid modifying original
        enriched = df.copy()
        
        # For incremental mode, identify stale records
        if incremental and 'everyorg_last_updated' in df.columns:
            from datetime import timedelta
            cutoff_date = datetime.utcnow() - timedelta(days=max_age_days)
            
            # Find records that need updating
            stale_mask = (
                df['everyorg_last_updated'].isna() |  # Never updated
                (pd.to_datetime(df['everyorg_last_updated']) < cutoff_date)  # Older than max_age_days
            )
            stale_count = stale_mask.sum()
            total_count = len(df)
            
            logger.info(f"📊 Incremental mode: {stale_count:,} / {total_count:,} records need updating")
            logger.info(f"   Cutoff date: {cutoff_date.date()} ({max_age_days} days ago)")
            
            # Filter to stale records
            df_to_enrich = df[stale_mask]
        else:
            df_to_enrich = df
            if incremental:
                logger.warning("Incremental mode requested but no everyorg_last_updated column found")
        
        # Determine which rows to enrich
        if max_requests:
            rows_to_enrich = min(max_requests, len(df_to_enrich))
            sample = df_to_enrich.head(rows_to_enrich)
            logger.info(f"Enriching first {rows_to_enrich:,} rows (max_requests={max_requests})")
        elif sample_pct < 1.0:
            sample = df_to_enrich.sample(frac=sample_pct, random_state=42)
            logger.info(f"Enriching {len(sample):,} rows ({sample_pct*100:.1f}% sample)")
        else:
            sample = df_to_enrich
            logger.info(f"Enriching all {len(df_to_enrich):,} rows")
        
        # Initialize new columns
        enriched['website'] = None
        enriched['mission'] = None
        enriched['logo_url'] = None
        enriched['cover_image_url'] = None
        enriched['profile_url'] = None
        enriched['causes'] = None
        enriched['primary_slug'] = None
        enriched['is_disbursable'] = None
        enriched['everyorg_last_updated'] = None
        
        # Enrich each sampled row
        enriched_count = 0
        
        for idx, row in tqdm(sample.iterrows(), total=len(sample), desc="Enriching"):
            ein = str(row.get('ein', ''))
            
            if not ein or len(ein) < 9:
                continue
            
            # Fetch from Every.org
            org_data = self.get_nonprofit_by_ein(ein)
            
            if org_data:
                fields = self.extract_fields(org_data)
                
                # Update the row
                for field, value in fields.items():
                    enriched.at[idx, field] = value
                
                # Add timestamp
                enriched.at[idx, 'everyorg_last_updated'] = datetime.utcnow().isoformat()
                
                enriched_count += 1
        
        logger.success(f"Enriched {enriched_count:,} / {len(sample):,} organizations")
        logger.info(f"Total API requests: {self.request_count:,}")
        
        return enriched


def main():
    """Main enrichment workflow"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Enrich nonprofit data with Every.org API"
    )
    parser.add_argument(
        "--input",
        default="data/gold/nonprofits_organizations.parquet",
        help="Input Parquet file"
    )
    parser.add_argument(
        "--output",
        default="data/gold/nonprofits_organizations_everyorg.parquet",
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
        "--full",
        action="store_true",
        help="Enrich all records (ignores sample-pct)"
    )
    parser.add_argument(
        "--incremental",
        action="store_true",
        help="Only enrich records older than --max-age-days"
    )
    parser.add_argument(
        "--max-age-days",
        type=int,
        default=30,
        help="For incremental mode, refresh records older than N days (default: 30)"
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
    
    # Enrich with Every.org
    enricher = EveryOrgEnricher()
    
    if args.full:
        df = enricher.enrich_dataframe(
            df,
            sample_pct=1.0,
            incremental=args.incremental,
            max_age_days=args.max_age_days
        )
    else:
        df = enricher.enrich_dataframe(
            df,
            max_requests=args.max_requests,
            sample_pct=args.sample_pct,
            incremental=args.incremental,
            max_age_days=args.max_age_days
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
    
    for field in ['website', 'mission', 'logo_url', 'cover_image_url', 'profile_url', 'causes']:
        if field in df.columns:
            non_null = df[field].notna().sum()
            pct = (non_null / len(df)) * 100
            logger.info(f"{field:20s}: {non_null:7,} / {len(df):7,} ({pct:5.1f}%)")
    
    # Show sample enriched records
    logger.info("")
    logger.info("=== SAMPLE ENRICHED RECORDS ===")
    enriched_sample = df[df['website'].notna()].head(3)
    
    for idx, row in enriched_sample.iterrows():
        logger.info(f"\n{row['organization_name']}")
        logger.info(f"  EIN: {row['ein']}")
        logger.info(f"  Website: {row['website']}")
        logger.info(f"  Mission: {str(row['mission'])[:80]}...")
        logger.info(f"  Causes: {row['causes']}")
        logger.info(f"  Profile: {row['profile_url']}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
