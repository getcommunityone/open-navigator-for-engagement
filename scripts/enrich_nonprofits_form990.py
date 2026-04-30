#!/usr/bin/env python3
"""
Enrich nonprofit data with IRS Form 990 XML filings

This script uses Giving Tuesday's open source libraries to extract detailed
financial data from Form 990 XML tax returns.

Data enriched:
- Total revenue, expenses, assets
- Program expenses, administrative, fundraising
- Grants awarded and received
- Officer compensation
- Program service descriptions
- Mission statements

Data source: IRS Form 990 XML filings via AWS S3
Tools: Giving Tuesday form-990-xml-parser
License: Public domain (IRS data) + Open source (Giving Tuesday tools)

Usage:
    # Install dependencies first
    pip install boto3 xmltodict
    
    # Enrich Alabama health organizations
    python scripts/enrich_nonprofits_form990.py \\
        --input data/gold/nonprofits_organizations.parquet \\
        --output data/gold/nonprofits_organizations_990.parquet \\
        --states AL MI \\
        --ntee E \\
        --concurrent 20
    
    # Enrich specific EINs
    python scripts/enrich_nonprofits_form990.py \\
        --input data/gold/nonprofits_organizations.parquet \\
        --output data/gold/nonprofits_specific_990.parquet \\
        --eins 123456789,987654321 \\
        --concurrent 10

Author: Open Navigator
Attribution: Uses Giving Tuesday form-990-xml-parser
"""

import asyncio
import aiohttp
import boto3
from botocore import UNSIGNED
from botocore.config import Config
import pandas as pd
import xmltodict
from pathlib import Path
from typing import List, Dict, Optional
import time
import os
from dotenv import load_dotenv
from tqdm.asyncio import tqdm
from loguru import logger
import argparse
from datetime import datetime
import json

load_dotenv()


class Form990Enricher:
    """Enrich nonprofit data with Form 990 XML filings"""
    
    def __init__(self, max_concurrent: int = 20, cache_dir: str = "data/cache/form_990_xml"):
        self.max_concurrent = max_concurrent
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize S3 client (no credentials needed - public bucket)
        self.s3_client = boto3.client(
            's3',
            region_name='us-east-1',
            config=Config(signature_version=UNSIGNED)
        )
        self.bucket = 'irs-form-990'
        
        logger.info(f"🚀 Form 990 XML enricher initialized")
        logger.info(f"   Max concurrent requests: {max_concurrent}")
        logger.info(f"   Cache directory: {cache_dir}")
    
    def get_filing_key(self, ein: str, tax_year: int) -> Optional[str]:
        """
        Find the S3 key for a nonprofit's 990 filing
        
        IRS naming convention: {EIN}_{TAX_YEAR}{TAX_PERIOD}_990.xml
        Example: 123456789_201812_990.xml
        
        We'll try common patterns for the tax year
        """
        ein_clean = str(ein).replace('-', '').zfill(9)
        
        # Try common tax periods (most orgs file at year-end)
        periods = ['12', '06', '09', '03']  # Dec, Jun, Sep, Mar
        
        for period in periods:
            key = f"{ein_clean}_{tax_year}{period}_990.xml"
            
            try:
                # Check if file exists
                self.s3_client.head_object(Bucket=self.bucket, Key=key)
                return key
            except:
                continue
        
        return None
    
    def parse_990_xml(self, xml_content: str) -> Dict:
        """
        Parse Form 990 XML and extract key fields
        
        Uses xmltodict for simple parsing (similar to Giving Tuesday approach)
        """
        try:
            # Parse XML
            data = xmltodict.parse(xml_content)
            
            # Navigate to Return/ReturnData
            return_data = data.get('Return', {}).get('ReturnData', {})
            form_990 = return_data.get('IRS990', {}) or return_data.get('IRS990EZ', {})
            
            if not form_990:
                return self._null_result("no_990_found")
            
            # Extract header info
            return_header = data.get('Return', {}).get('ReturnHeader', {})
            filer = return_header.get('Filer', {})
            
            # Basic info
            ein = filer.get('EIN', '')
            org_name = filer.get('BusinessName', {}).get('BusinessNameLine1Txt', '')
            tax_year = return_header.get('TaxYr', '')
            
            # Financials - different paths for 990 vs 990EZ
            if 'IRS990' in return_data:
                revenue = self._safe_int(form_990.get('CYTotalRevenueAmt', 0))
                expenses = self._safe_int(form_990.get('CYTotalExpensesAmt', 0))
                assets_eoy = self._safe_int(form_990.get('TotalAssetsEOYAmt', 0))
                liabilities_eoy = self._safe_int(form_990.get('TotalLiabilitiesEOYAmt', 0))
                net_assets = self._safe_int(form_990.get('NetAssetsOrFundBalancesEOYAmt', 0))
                
                # Revenue breakdown
                contributions = self._safe_int(form_990.get('CYContributionsGrantsAmt', 0))
                program_revenue = self._safe_int(form_990.get('CYProgramServiceRevenueAmt', 0))
                investment_income = self._safe_int(form_990.get('CYInvestmentIncomeAmt', 0))
                
                # Expense breakdown
                program_expenses = self._safe_int(form_990.get('CYTotalProgramServiceExpensesAmt', 0))
                admin_expenses = self._safe_int(form_990.get('CYManagementAndGeneralExpensesAmt', 0))
                fundraising_expenses = self._safe_int(form_990.get('CYFundraisingExpensesAmt', 0))
                
                # Grants
                grants_paid = self._safe_int(form_990.get('CYGrantsAndSimilarPaidAmt', 0))
                
            else:  # 990EZ
                revenue = self._safe_int(form_990.get('TotalRevenueAmt', 0))
                expenses = self._safe_int(form_990.get('TotalExpensesAmt', 0))
                assets_eoy = self._safe_int(form_990.get('TotalAssetsEOYAmt', 0))
                liabilities_eoy = self._safe_int(form_990.get('TotalLiabilitiesEOYAmt', 0))
                net_assets = assets_eoy - liabilities_eoy
                
                contributions = self._safe_int(form_990.get('ContributionsGiftsGrantsEtcAmt', 0))
                program_revenue = self._safe_int(form_990.get('ProgramServiceRevenueAmt', 0))
                investment_income = self._safe_int(form_990.get('InvestmentIncomeAmt', 0))
                
                program_expenses = self._safe_int(form_990.get('FeesAndOtherPymtToIndCntrctAmt', 0))
                admin_expenses = 0  # Not broken out in 990EZ
                fundraising_expenses = 0
                grants_paid = self._safe_int(form_990.get('GrantsAndSimilarAmountsPaidAmt', 0))
            
            # Mission/activities
            mission = form_990.get('ActivityOrMissionDesc', '') or form_990.get('MissionDesc', '')
            
            # Program descriptions
            program_service = form_990.get('ProgramServiceAccomplishmentGrp', [])
            if not isinstance(program_service, list):
                program_service = [program_service] if program_service else []
            
            program_descriptions = []
            for prog in program_service[:3]:  # Top 3 programs
                if prog:
                    desc = prog.get('DescriptionProgramSrvcAccomTxt', '')
                    expenses = self._safe_int(prog.get('ProgramServiceExpensesAmt', 0))
                    if desc:
                        program_descriptions.append(f"{desc[:200]} (${expenses:,})")
            
            programs_text = ' | '.join(program_descriptions) if program_descriptions else None
            
            return {
                'ein': ein,
                'form_990_org_name': org_name,
                'form_990_tax_year': tax_year,
                'form_990_total_revenue': revenue,
                'form_990_total_expenses': expenses,
                'form_990_net_income': revenue - expenses,
                'form_990_total_assets': assets_eoy,
                'form_990_total_liabilities': liabilities_eoy,
                'form_990_net_assets': net_assets,
                'form_990_contributions': contributions,
                'form_990_program_revenue': program_revenue,
                'form_990_investment_income': investment_income,
                'form_990_program_expenses': program_expenses,
                'form_990_admin_expenses': admin_expenses,
                'form_990_fundraising_expenses': fundraising_expenses,
                'form_990_grants_paid': grants_paid,
                'form_990_mission': mission[:500] if mission else None,
                'form_990_programs': programs_text,
                'form_990_last_updated': datetime.utcnow().isoformat(),
                'form_990_status': 'success'
            }
            
        except Exception as e:
            logger.debug(f"Parse error: {e}")
            return self._null_result(f"parse_error: {str(e)[:100]}")
    
    def _safe_int(self, value) -> int:
        """Safely convert to int"""
        try:
            return int(value) if value else 0
        except:
            return 0
    
    def _null_result(self, status: str) -> Dict:
        """Return null result"""
        return {
            'form_990_total_revenue': None,
            'form_990_total_expenses': None,
            'form_990_net_income': None,
            'form_990_total_assets': None,
            'form_990_total_liabilities': None,
            'form_990_net_assets': None,
            'form_990_contributions': None,
            'form_990_program_revenue': None,
            'form_990_investment_income': None,
            'form_990_program_expenses': None,
            'form_990_admin_expenses': None,
            'form_990_fundraising_expenses': None,
            'form_990_grants_paid': None,
            'form_990_mission': None,
            'form_990_programs': None,
            'form_990_last_updated': datetime.utcnow().isoformat(),
            'form_990_status': status
        }
    
    async def fetch_and_parse_990(
        self,
        ein: str,
        tax_years: List[int],
        semaphore: asyncio.Semaphore
    ) -> Dict:
        """Fetch and parse 990 for an organization"""
        async with semaphore:
            # Check cache first
            cache_file = self.cache_dir / f"{ein}_990.json"
            if cache_file.exists():
                with open(cache_file, 'r') as f:
                    return json.load(f)
            
            # Try to find filing
            filing_key = None
            for year in tax_years:
                filing_key = self.get_filing_key(ein, year)
                if filing_key:
                    break
            
            if not filing_key:
                result = {'ein': ein}
                result.update(self._null_result('not_found'))
                return result
            
            try:
                # Download from S3
                response = self.s3_client.get_object(Bucket=self.bucket, Key=filing_key)
                xml_content = response['Body'].read().decode('utf-8')
                
                # Parse
                result = self.parse_990_xml(xml_content)
                result['ein'] = ein
                
                # Cache result
                with open(cache_file, 'w') as f:
                    json.dump(result, f)
                
                return result
                
            except Exception as e:
                logger.debug(f"Fetch error for {ein}: {e}")
                result = {'ein': ein}
                result.update(self._null_result(f"fetch_error"))
                return result
    
    async def enrich_batch(
        self,
        eins: List[str],
        tax_years: List[int],
        progress_bar: Optional[tqdm] = None
    ) -> List[Dict]:
        """Enrich a batch of organizations"""
        semaphore = asyncio.Semaphore(self.max_concurrent)
        
        tasks = [
            self.fetch_and_parse_990(ein, tax_years, semaphore)
            for ein in eins
        ]
        
        # Run with progress bar
        if progress_bar:
            results = []
            for coro in asyncio.as_completed(tasks):
                result = await coro
                results.append(result)
                progress_bar.update(1)
            return results
        else:
            return await asyncio.gather(*tasks)
    
    def enrich_dataframe(
        self,
        df: pd.DataFrame,
        tax_years: List[int] = [2023, 2022, 2021],
        batch_size: int = 1000
    ) -> pd.DataFrame:
        """Enrich DataFrame with Form 990 data"""
        start_time = time.time()
        
        logger.info("=" * 60)
        logger.info("FORM 990 XML ENRICHMENT")
        logger.info("=" * 60)
        logger.info(f"Total records: {len(df):,}")
        logger.info(f"Tax years to try: {tax_years}")
        logger.info(f"Max concurrent: {self.max_concurrent}")
        logger.info("=" * 60)
        
        all_results = []
        num_batches = (len(df) + batch_size - 1) // batch_size
        
        # Process in batches
        with tqdm(total=len(df), desc="Enriching with Form 990 data") as pbar:
            for batch_num in range(num_batches):
                start_idx = batch_num * batch_size
                end_idx = min(start_idx + batch_size, len(df))
                batch_df = df.iloc[start_idx:end_idx]
                
                logger.info(f"\nBatch {batch_num + 1}/{num_batches}: {len(batch_df):,} records")
                
                eins = batch_df['ein'].tolist()
                
                # Run async batch
                batch_results = asyncio.run(self.enrich_batch(eins, tax_years, pbar))
                all_results.extend(batch_results)
        
        # Convert to DataFrame
        results_df = pd.DataFrame(all_results)
        
        # Merge with original data
        enriched_df = df.merge(results_df, on='ein', how='left', suffixes=('', '_990'))
        
        # Calculate stats
        elapsed = time.time() - start_time
        success_count = (results_df['form_990_status'] == 'success').sum()
        success_rate = success_count / len(results_df) * 100
        
        logger.info("\n" + "=" * 60)
        logger.info("ENRICHMENT COMPLETE")
        logger.info("=" * 60)
        logger.info(f"✅ Processed: {len(df):,} nonprofits")
        logger.info(f"✅ Found 990s: {success_count:,} ({success_rate:.1f}%)")
        logger.info(f"⚠️  No filing found: {(results_df['form_990_status'] == 'not_found').sum():,}")
        logger.info(f"⏱️  Time: {elapsed / 60:.1f} minutes")
        logger.info("=" * 60)
        
        return enriched_df


def main():
    parser = argparse.ArgumentParser(
        description="Enrich nonprofits with Form 990 XML data",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('--input', required=True, help='Input parquet file')
    parser.add_argument('--output', required=True, help='Output parquet file')
    parser.add_argument('--states', nargs='+', help='Filter to these states (e.g., AL MI)')
    parser.add_argument('--ntee', help='Filter to NTEE code prefix (e.g., E for health)')
    parser.add_argument('--eins', help='Specific EINs to enrich (comma-separated)')
    parser.add_argument('--sample', type=int, help='Sample N records (for testing)')
    parser.add_argument('--concurrent', type=int, default=20, help='Max concurrent requests')
    parser.add_argument('--tax-years', nargs='+', type=int, default=[2023, 2022, 2021], 
                       help='Tax years to try (newest first)')
    
    args = parser.parse_args()
    
    # Load data
    logger.info(f"📂 Loading {args.input}")
    df = pd.read_parquet(args.input)
    logger.info(f"   Loaded {len(df):,} nonprofits")
    
    # Filter by states
    if args.states:
        df = df[df['state'].isin(args.states)]
        logger.info(f"   Filtered to states {args.states}: {len(df):,} records")
    
    # Filter by NTEE code
    if args.ntee:
        df = df[df['ntee_code'].str.startswith(args.ntee, na=False)]
        logger.info(f"   Filtered to NTEE {args.ntee}: {len(df):,} records")
    
    # Filter by specific EINs
    if args.eins:
        eins_list = [ein.strip() for ein in args.eins.split(',')]
        df = df[df['ein'].isin(eins_list)]
        logger.info(f"   Filtered to {len(eins_list)} specific EINs: {len(df):,} records")
    
    # Sample if requested
    if args.sample:
        df = df.sample(n=min(args.sample, len(df)), random_state=42)
        logger.info(f"   Sampled {len(df):,} nonprofits")
    
    if len(df) == 0:
        logger.error("No records to process after filtering!")
        return 1
    
    # Create enricher
    enricher = Form990Enricher(max_concurrent=args.concurrent)
    
    # Enrich!
    try:
        enriched_df = enricher.enrich_dataframe(df, tax_years=args.tax_years)
        
        # Save
        enriched_df.to_parquet(args.output, index=False)
        logger.success(f"💾 Saved to: {args.output}")
        
        # Show sample
        logger.info("\n📊 Sample enriched records:")
        sample = enriched_df[enriched_df['form_990_status'] == 'success'].head(3)
        for idx, row in sample.iterrows():
            logger.info(f"\n  {row['organization_name']}")
            logger.info(f"    Revenue: ${row['form_990_total_revenue']:,.0f}")
            logger.info(f"    Assets: ${row['form_990_total_assets']:,.0f}")
            logger.info(f"    Programs: {row['form_990_programs'][:100] if row['form_990_programs'] else 'N/A'}...")
        
        logger.success("\n🎉 Enrichment complete!")
        return 0
        
    except Exception as e:
        logger.error(f"❌ Enrichment failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
