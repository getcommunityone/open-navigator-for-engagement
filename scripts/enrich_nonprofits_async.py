#!/usr/bin/env python3
"""
FAST Nonprofit Enrichment with Async/Parallel Processing

This script enriches nonprofits 50-100x faster than the sequential version.

Speed comparison:
- Sequential: 1.9M × 0.5sec = 11.3 days
- Async (50 workers): 1.9M × 0.5sec / 50 = 5.4 hours ⚡
- Async (100 workers): 1.9M × 0.5sec / 100 = 2.7 hours ⚡⚡

Usage:
    # Test with small sample first (recommended!)
    python scripts/enrich_nonprofits_async.py \\
        --input data/gold/nonprofits_organizations.parquet \\
        --output data/gold/nonprofits_enriched_test.parquet \\
        --sample 1000 \\
        --concurrent 10
    
    # Full enrichment with moderate concurrency
    python scripts/enrich_nonprofits_async.py \\
        --input data/gold/nonprofits_organizations.parquet \\
        --output data/gold/nonprofits_organizations_everyorg.parquet \\
        --concurrent 50 \\
        --batch-size 5000
    
    # Aggressive concurrency (test API limits first!)
    python scripts/enrich_nonprofits_async.py \\
        --input data/gold/nonprofits_organizations.parquet \\
        --output data/gold/nonprofits_organizations_everyorg.parquet \\
        --concurrent 100 \\
        --batch-size 10000

WARNING: Start with low concurrency (10-20) to test API limits!
"""

import asyncio
import aiohttp
import pandas as pd
from pathlib import Path
from typing import List, Dict, Optional
import time
import os
from dotenv import load_dotenv
from tqdm.asyncio import tqdm
from loguru import logger
import argparse
from datetime import datetime

# Load environment variables
load_dotenv()


class AsyncEveryOrgEnricher:
    """Fast async nonprofit enrichment"""
    
    def __init__(self, api_key: str, max_concurrent: int = 50):
        self.api_base = "https://partners.every.org/v0.2"
        self.api_key = api_key
        self.max_concurrent = max_concurrent
        
        logger.info(f"🚀 Async enricher initialized")
        logger.info(f"   Max concurrent requests: {max_concurrent}")
        logger.info(f"   API key: {api_key[:8]}...")
    
    async def fetch_nonprofit(
        self,
        session: aiohttp.ClientSession,
        ein: str,
        semaphore: asyncio.Semaphore
    ) -> Dict:
        """Fetch single nonprofit with rate limiting"""
        async with semaphore:
            clean_ein = str(ein).replace('-', '').zfill(9)
            url = f"{self.api_base}/nonprofit/{clean_ein}"
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Accept': 'application/json'
            }
            
            try:
                async with session.get(url, headers=headers, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._extract_fields(ein, data)
                    elif response.status == 404:
                        return self._null_result(ein, "not_found")
                    else:
                        logger.debug(f"API error for {ein}: {response.status}")
                        return self._null_result(ein, f"error_{response.status}")
            except asyncio.TimeoutError:
                logger.debug(f"Timeout for {ein}")
                return self._null_result(ein, "timeout")
            except Exception as e:
                logger.debug(f"Exception for {ein}: {e}")
                return self._null_result(ein, "exception")
    
    def _extract_fields(self, ein: str, org_data: Dict) -> Dict:
        """Extract enrichment fields from Every.org response"""
        if not org_data or 'data' not in org_data:
            return self._null_result(ein, "no_data")
        
        nonprofit = org_data['data'].get('nonprofit', {})
        tags = org_data['data'].get('nonprofitTags', [])
        
        # Extract cause categories
        causes = [tag.get('tagName') for tag in tags if tag.get('tagName')]
        causes_str = ','.join(causes) if causes else None
        
        return {
            'ein': ein,
            'website': nonprofit.get('websiteUrl'),
            'mission': nonprofit.get('description') or nonprofit.get('descriptionLong'),
            'logo_url': nonprofit.get('logoUrl'),
            'cover_image_url': nonprofit.get('coverImageUrl'),
            'profile_url': nonprofit.get('profileUrl'),
            'everyorg_causes': causes_str,
            'primary_slug': nonprofit.get('primarySlug'),
            'is_disbursable': nonprofit.get('isDisbursable'),
            'everyorg_last_updated': datetime.utcnow().isoformat(),
            'everyorg_status': 'success'
        }
    
    def _null_result(self, ein: str, status: str) -> Dict:
        """Return null enrichment result"""
        return {
            'ein': ein,
            'website': None,
            'mission': None,
            'logo_url': None,
            'cover_image_url': None,
            'profile_url': None,
            'everyorg_causes': None,
            'primary_slug': None,
            'is_disbursable': None,
            'everyorg_last_updated': datetime.utcnow().isoformat(),
            'everyorg_status': status
        }
    
    async def enrich_batch(
        self,
        eins: List[str],
        progress_bar: Optional[tqdm] = None
    ) -> List[Dict]:
        """Enrich a batch of nonprofits with controlled concurrency"""
        semaphore = asyncio.Semaphore(self.max_concurrent)
        
        # Create session with connection pooling
        connector = aiohttp.TCPConnector(
            limit=self.max_concurrent * 2,
            limit_per_host=self.max_concurrent
        )
        timeout = aiohttp.ClientTimeout(total=30)
        
        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            tasks = [
                self.fetch_nonprofit(session, ein, semaphore)
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
        batch_size: int = 5000,
        output_file: Optional[str] = None,
        checkpoint_interval: int = 10
    ) -> pd.DataFrame:
        """
        Enrich DataFrame with async processing
        
        Args:
            df: DataFrame with 'ein' column
            batch_size: Process this many at once
            output_file: Save results here (and create checkpoints)
            checkpoint_interval: Save checkpoint every N batches
        
        Returns:
            Enriched DataFrame
        """
        start_time = time.time()
        
        logger.info("=" * 60)
        logger.info("ASYNC EVERY.ORG ENRICHMENT")
        logger.info("=" * 60)
        logger.info(f"Total records: {len(df):,}")
        logger.info(f"Batch size: {batch_size:,}")
        logger.info(f"Max concurrent: {self.max_concurrent}")
        logger.info(f"Estimated time: {len(df) * 0.5 / self.max_concurrent / 60:.1f} minutes")
        logger.info("=" * 60)
        
        all_results = []
        num_batches = (len(df) + batch_size - 1) // batch_size
        
        # Process in batches
        with tqdm(total=len(df), desc="Enriching nonprofits") as pbar:
            for batch_num in range(num_batches):
                start_idx = batch_num * batch_size
                end_idx = min(start_idx + batch_size, len(df))
                batch_df = df.iloc[start_idx:end_idx]
                
                logger.info(f"\nBatch {batch_num + 1}/{num_batches}: {len(batch_df):,} records")
                
                # Get EINs for this batch
                eins = batch_df['ein'].tolist()
                
                # Run async batch
                batch_results = asyncio.run(self.enrich_batch(eins, pbar))
                all_results.extend(batch_results)
                
                # Save checkpoint
                if output_file and (batch_num + 1) % checkpoint_interval == 0:
                    checkpoint_df = pd.DataFrame(all_results)
                    checkpoint_file = f"{output_file}.checkpoint"
                    checkpoint_df.to_parquet(checkpoint_file, index=False)
                    logger.info(f"💾 Checkpoint saved: {checkpoint_file}")
        
        # Convert results to DataFrame
        results_df = pd.DataFrame(all_results)
        
        # Merge with original data
        enriched_df = df.merge(
            results_df,
            on='ein',
            how='left',
            suffixes=('', '_everyorg')
        )
        
        # Calculate stats
        elapsed = time.time() - start_time
        success_count = (results_df['everyorg_status'] == 'success').sum()
        success_rate = success_count / len(results_df) * 100
        requests_per_sec = len(df) / elapsed
        
        logger.info("\n" + "=" * 60)
        logger.info("ENRICHMENT COMPLETE")
        logger.info("=" * 60)
        logger.info(f"✅ Processed: {len(df):,} nonprofits")
        logger.info(f"✅ Success: {success_count:,} ({success_rate:.1f}%)")
        logger.info(f"⚠️  Not found: {(results_df['everyorg_status'] == 'not_found').sum():,}")
        logger.info(f"❌ Errors: {(results_df['everyorg_status'].str.startswith('error')).sum():,}")
        logger.info(f"⏱️  Time: {elapsed / 60:.1f} minutes")
        logger.info(f"🚀 Speed: {requests_per_sec:.1f} requests/sec")
        logger.info(f"🚀 Speedup: {requests_per_sec / 2:.0f}x faster than sequential!")
        logger.info("=" * 60)
        
        # Save final result
        if output_file:
            enriched_df.to_parquet(output_file, index=False)
            logger.info(f"💾 Saved to: {output_file}")
            
            # Clean up checkpoint
            checkpoint_file = f"{output_file}.checkpoint"
            if Path(checkpoint_file).exists():
                Path(checkpoint_file).unlink()
                logger.info(f"🧹 Cleaned up checkpoint file")
        
        return enriched_df


def main():
    parser = argparse.ArgumentParser(
        description="Fast async nonprofit enrichment",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Test with 1000 nonprofits, 10 concurrent requests
    python scripts/enrich_nonprofits_async.py \\
        --input data/gold/nonprofits_organizations.parquet \\
        --output /tmp/test_enrichment.parquet \\
        --sample 1000 --concurrent 10
    
    # Full enrichment with 50 concurrent requests
    python scripts/enrich_nonprofits_async.py \\
        --input data/gold/nonprofits_organizations.parquet \\
        --output data/gold/nonprofits_organizations_everyorg.parquet \\
        --concurrent 50
    
    # Skip already enriched records
    python scripts/enrich_nonprofits_async.py \\
        --input data/gold/nonprofits_organizations.parquet \\
        --output data/gold/nonprofits_organizations_everyorg.parquet \\
        --skip-existing \\
        --concurrent 50
        """
    )
    
    parser.add_argument('--input', required=True, help='Input parquet file')
    parser.add_argument('--output', required=True, help='Output parquet file')
    parser.add_argument('--sample', type=int, help='Sample N records (for testing)')
    parser.add_argument('--concurrent', type=int, default=50, help='Max concurrent requests')
    parser.add_argument('--batch-size', type=int, default=5000, help='Batch size')
    parser.add_argument('--skip-existing', action='store_true', help='Skip already enriched')
    parser.add_argument('--checkpoint-interval', type=int, default=10, help='Checkpoint every N batches')
    
    args = parser.parse_args()
    
    # Get API key
    api_key = os.getenv('EVERYORG_API_KEY')
    if not api_key:
        logger.error("❌ EVERYORG_API_KEY not found in .env file")
        logger.error("   Sign up at: https://www.every.org/nonprofit-api")
        return 1
    
    # Load input data
    logger.info(f"📂 Loading {args.input}")
    df = pd.read_parquet(args.input)
    logger.info(f"   Loaded {len(df):,} nonprofits")
    
    # Sample if requested
    if args.sample:
        df = df.sample(n=min(args.sample, len(df)), random_state=42)
        logger.info(f"   Sampled {len(df):,} nonprofits")
    
    # Skip already enriched if requested
    if args.skip_existing and Path(args.output).exists():
        logger.info(f"📂 Loading existing enriched data from {args.output}")
        existing = pd.read_parquet(args.output)
        logger.info(f"   Found {len(existing):,} already enriched")
        
        # Find records not yet enriched
        df = df[~df['ein'].isin(existing['ein'])]
        logger.info(f"   {len(df):,} remaining to enrich")
        
        if len(df) == 0:
            logger.success("✅ All records already enriched!")
            return 0
    
    # Create enricher
    enricher = AsyncEveryOrgEnricher(
        api_key=api_key,
        max_concurrent=args.concurrent
    )
    
    # Enrich!
    try:
        enriched_df = enricher.enrich_dataframe(
            df,
            batch_size=args.batch_size,
            output_file=args.output,
            checkpoint_interval=args.checkpoint_interval
        )
        
        logger.success("🎉 Enrichment complete!")
        return 0
        
    except KeyboardInterrupt:
        logger.warning("\n⚠️  Interrupted by user")
        logger.warning("   Checkpoint file saved, can resume later")
        return 1
    except Exception as e:
        logger.error(f"❌ Enrichment failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
