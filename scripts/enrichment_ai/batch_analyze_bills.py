#!/usr/bin/env python3
"""
Batch Bill Analysis with Incremental Processing

This script:
1. Finds bills that haven't been analyzed yet
2. Runs Llama AI analysis to extract interest groups
3. Saves results to Parquet (incremental appends)
4. Supports resume after failures

Usage:
    # Analyze Georgia fluoride bills
    python scripts/enrichment_ai/batch_analyze_bills.py --state GA --topic fluorid --limit 10
    
    # Analyze all Alabama bills (will take a while!)
    python scripts/enrichment_ai/batch_analyze_bills.py --state AL --limit 100
    
    # Re-analyze everything (skip incremental check)
    python scripts/enrichment_ai/batch_analyze_bills.py --state GA --no-incremental
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scripts.enrichment_ai.legislative_analysis_intel import (
    DuckDBLegislativeAnalyzer,
    IntelOptimizedLLM,
    InterestGroup,
    ANALYSIS_DIR
)
from loguru import logger
import argparse
from typing import List
import time


def analyze_batch(
    state: str = None,
    topic: str = None,
    limit: int = 10,
    skip_analyzed: bool = True,
    model: str = "meta-llama/Llama-3.2-3B-Instruct"
):
    """
    Batch analyze bills and save results to Parquet
    
    Args:
        state: State code filter (e.g., 'GA', 'AL')
        topic: Topic search term (e.g., 'fluorid')
        limit: Maximum bills to analyze
        skip_analyzed: Use incremental processing
        model: LLM model to use
    """
    
    logger.info("=" * 70)
    logger.info("BATCH BILL ANALYSIS WITH INCREMENTAL PROCESSING")
    logger.info("=" * 70)
    logger.info(f"State: {state or 'All'}")
    logger.info(f"Topic: {topic or 'All'}")
    logger.info(f"Limit: {limit}")
    logger.info(f"Incremental: {skip_analyzed}")
    logger.info(f"Model: {model}")
    logger.info("")
    
    # Initialize
    with DuckDBLegislativeAnalyzer() as analyzer:
        # Create tables
        logger.info("📊 Loading bill data...")
        analyzer.create_bills_table()
        analyzer.create_testimony_table()
        
        # Get bills to analyze (incremental!)
        logger.info(f"\n🔍 Finding bills to analyze...")
        bills = analyzer.get_bills_to_analyze(
            state=state,
            topic_filter=topic,
            limit=limit,
            skip_analyzed=skip_analyzed
        )
        
        if not bills:
            logger.info("✅ No bills to analyze (all done or no matches)")
            logger.info(f"\n💡 Tip: Check existing results at:")
            logger.info(f"   {ANALYSIS_DIR / 'interest_groups_analysis.parquet'}")
            return
        
        logger.info(f"📋 Found {len(bills)} bills to analyze")
        logger.info("")
        
        # Initialize LLM
        logger.info("🤖 Loading AI model...")
        llm = IntelOptimizedLLM(model_name=model)
        llm.load_model(use_openvino=False)  # Use transformers for now
        logger.info("✅ Model loaded")
        logger.info("")
        
        # Process each bill
        all_results = []
        success_count = 0
        error_count = 0
        
        for i, bill in enumerate(bills, 1):
            logger.info(f"[{i}/{len(bills)}] Analyzing {bill['bill_number']}...")
            logger.info(f"   Title: {bill['title'][:70]}...")
            
            try:
                # Get testimony (if available)
                testimony = analyzer.get_all_testimony_for_bill(bill['bill_id'])
                
                if not testimony:
                    # Create mock testimony for demo
                    testimony = [{
                        'speaker': 'Sample Speaker',
                        'organization': 'Sample Organization',
                        'text': bill.get('abstract') or bill['title'],
                        'stance': 'support',
                        'timestamp': '2026-01-01'
                    }]
                
                # Build bill context
                bill_context = {
                    'id': bill['bill_number'],
                    'title': bill['title'],
                    'abstract': bill.get('abstract') or bill['title']
                }
                
                # Run AI analysis
                start_time = time.time()
                groups = llm.extract_interest_groups(bill_context, testimony)
                elapsed = time.time() - start_time
                
                logger.info(f"   ✅ Extracted {len(groups)} interest groups ({elapsed:.1f}s)")
                
                # Add bill_id to results
                for group in groups:
                    group.bill_id = bill['bill_id']
                
                all_results.extend(groups)
                success_count += 1
                
                # Save incrementally every 5 bills (in case of crash)
                if len(all_results) >= 5:
                    logger.info(f"\n💾 Saving intermediate results ({len(all_results)} groups)...")
                    analyzer.save_analysis_results(all_results, append=True)
                    all_results = []  # Clear after save
                    logger.info("   ✅ Saved to Parquet")
                    logger.info("")
                
            except Exception as e:
                logger.error(f"   ❌ Analysis failed: {e}")
                error_count += 1
                continue
        
        # Save any remaining results
        if all_results:
            logger.info(f"\n💾 Saving final results ({len(all_results)} groups)...")
            output_file = analyzer.save_analysis_results(all_results, append=True)
            logger.info(f"   ✅ Saved to {output_file}")
        
        # Summary
        logger.info("")
        logger.info("=" * 70)
        logger.info("BATCH ANALYSIS COMPLETE")
        logger.info("=" * 70)
        logger.info(f"✅ Success: {success_count} bills")
        logger.info(f"❌ Errors:  {error_count} bills")
        logger.info(f"📊 Results saved to: {ANALYSIS_DIR / 'interest_groups_analysis.parquet'}")
        logger.info("")
        logger.info("🔍 Query results with DuckDB:")
        logger.info(f"""
import duckdb
conn = duckdb.connect()
results = conn.execute('''
    SELECT bill_id, group_name, stance, stance_score
    FROM read_parquet('{ANALYSIS_DIR / 'interest_groups_analysis.parquet'}')
    ORDER BY analyzed_at DESC
    LIMIT 10
''').fetchdf()
print(results)
""")
        logger.info("")
        logger.info("💡 Next run will skip already-analyzed bills (incremental!)")


def main():
    parser = argparse.ArgumentParser(
        description="Batch analyze bills with incremental processing",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze Georgia fluoride bills
  python scripts/enrichment_ai/batch_analyze_bills.py --state GA --topic fluorid --limit 10
  
  # Analyze all Alabama bills
  python scripts/enrichment_ai/batch_analyze_bills.py --state AL --limit 50
  
  # Re-analyze (skip incremental check)
  python scripts/enrichment_ai/batch_analyze_bills.py --state GA --no-incremental
        """
    )
    
    parser.add_argument('--state', help='State code (e.g., GA, AL, MA)')
    parser.add_argument('--topic', help='Topic search term (e.g., fluorid, dental)')
    parser.add_argument('--limit', type=int, default=10, help='Maximum bills to analyze (default: 10)')
    parser.add_argument('--no-incremental', action='store_true', help='Disable incremental processing')
    parser.add_argument('--model', default='meta-llama/Llama-3.2-3B-Instruct', help='LLM model to use')
    
    args = parser.parse_args()
    
    analyze_batch(
        state=args.state,
        topic=args.topic,
        limit=args.limit,
        skip_analyzed=not args.no_incremental,
        model=args.model
    )


if __name__ == "__main__":
    main()
