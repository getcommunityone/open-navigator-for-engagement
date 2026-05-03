#!/usr/bin/env python3
"""
Batch Bill Analysis using Ollama (temporary workaround for HuggingFace gating)

This script uses your locally installed Ollama models (llama3.2:latest) instead
of HuggingFace downloads. Perfect for when HF access is pending!

Usage:
    # Analyze Georgia fluoride bills with Ollama
    python scripts/enrichment_ai/batch_analyze_bills_ollama.py --state GA --topic fluorid --limit 3
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scripts.enrichment_ai.legislative_analysis_intel import (
    DuckDBLegislativeAnalyzer,
    InterestGroup,
    ANALYSIS_DIR
)
from loguru import logger
import argparse
import subprocess
import json
from typing import List
from datetime import datetime
import time


def ollama_chat(prompt: str, model: str = "llama3.2:latest") -> str:
    """
    Call Ollama via subprocess
    
    Args:
        prompt: The prompt to send
        model: Ollama model name (default: llama3.2:latest)
    
    Returns:
        Model response text
    """
    try:
        result = subprocess.run(
            ['ollama', 'run', model, prompt],
            capture_output=True,
            text=True,
            timeout=120  # 2 minute timeout per bill
        )
        return result.stdout.strip()
    except subprocess.TimeoutExpired:
        logger.error(f"Ollama timeout after 120s")
        return ""
    except Exception as e:
        logger.error(f"Ollama error: {e}")
        return ""


def extract_interest_groups_ollama(bill: dict, model: str = "llama3.2:latest") -> List[InterestGroup]:
    """
    Extract interest groups using Ollama
    
    Args:
        bill: Bill dict with 'bill_id', 'title', 'abstract'
        model: Ollama model name
    
    Returns:
        List of InterestGroup objects
    """
    
    # Build prompt
    prompt = f"""Analyze this legislative bill and extract interest groups who would support or oppose it.

Bill Title: {bill['title']}
Bill Text: {bill.get('abstract') or bill['title']}

Extract interest groups in this EXACT JSON format:
{{
  "groups": [
    {{
      "group_name": "Name of organization or group",
      "stance": "support" or "oppose" or "neutral",
      "stance_score": -1.0 to 1.0 (negative=oppose, positive=support),
      "confidence": 0.0 to 1.0,
      "testimony_excerpt": "Brief quote or reasoning"
    }}
  ]
}}

Return ONLY valid JSON, no explanation."""

    # Call Ollama
    logger.debug(f"Calling Ollama with {model}...")
    response = ollama_chat(prompt, model)
    
    if not response:
        logger.warning("Empty response from Ollama")
        return []
    
    # Parse JSON response
    try:
        # Try to extract JSON from response (in case model adds explanation)
        if '{' in response:
            json_start = response.index('{')
            json_end = response.rindex('}') + 1
            json_str = response[json_start:json_end]
            data = json.loads(json_str)
        else:
            logger.error("No JSON found in response")
            return []
        
        # Convert to InterestGroup objects
        groups = []
        for group_data in data.get('groups', []):
            group = InterestGroup(
                bill_id=bill['bill_id'],
                group_name=group_data.get('group_name', 'Unknown'),
                lobbyist=None,
                stance=group_data.get('stance', 'neutral'),
                stance_score=float(group_data.get('stance_score', 0.0)),
                testimony_excerpt=group_data.get('testimony_excerpt', ''),
                confidence=float(group_data.get('confidence', 0.5)),
                analyzed_at=datetime.now(),
                model=model
            )
            groups.append(group)
        
        return groups
        
    except json.JSONDecodeError as e:
        logger.error(f"JSON parse error: {e}")
        logger.error(f"Response was: {response[:200]}...")
        return []
    except Exception as e:
        logger.error(f"Error parsing response: {e}")
        return []


def analyze_batch_ollama(
    state: str = None,
    topic: str = None,
    limit: int = 10,
    skip_analyzed: bool = True,
    model: str = "llama3.2:latest"
):
    """
    Batch analyze bills using Ollama
    
    Args:
        state: State code filter (e.g., 'GA', 'AL')
        topic: Topic search term (e.g., 'fluorid')
        limit: Maximum bills to analyze
        skip_analyzed: Use incremental processing
        model: Ollama model name
    """
    
    logger.info("=" * 70)
    logger.info("BATCH BILL ANALYSIS WITH OLLAMA (HuggingFace Workaround)")
    logger.info("=" * 70)
    logger.info(f"State: {state or 'All'}")
    logger.info(f"Topic: {topic or 'All'}")
    logger.info(f"Limit: {limit}")
    logger.info(f"Incremental: {skip_analyzed}")
    logger.info(f"Model: {model}")
    logger.info("")
    
    # Check Ollama is running
    try:
        subprocess.run(['ollama', 'list'], capture_output=True, check=True)
    except Exception as e:
        logger.error("❌ Ollama is not running or not installed!")
        logger.error("   Start it with: ollama serve")
        logger.error(f"   Error: {e}")
        return
    
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
        
        # Process each bill
        all_results = []
        success_count = 0
        error_count = 0
        
        for i, bill in enumerate(bills, 1):
            logger.info(f"[{i}/{len(bills)}] Analyzing {bill['bill_number']}...")
            logger.info(f"   Title: {bill['title'][:70]}...")
            
            try:
                # Run AI analysis with Ollama
                start_time = time.time()
                groups = extract_interest_groups_ollama(bill, model)
                elapsed = time.time() - start_time
                
                if groups:
                    logger.info(f"   ✅ Extracted {len(groups)} interest groups ({elapsed:.1f}s)")
                    all_results.extend(groups)
                    success_count += 1
                else:
                    logger.warning(f"   ⚠️  No groups extracted ({elapsed:.1f}s)")
                    error_count += 1
                
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
        logger.info("🔍 View results:")
        logger.info(f"   python scripts/enrichment_ai/query_analysis_results.py")


def main():
    parser = argparse.ArgumentParser(
        description="Batch analyze bills using Ollama",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze Georgia fluoride bills
  python scripts/enrichment_ai/batch_analyze_bills_ollama.py --state GA --topic fluorid --limit 3
  
  # Analyze all Alabama bills
  python scripts/enrichment_ai/batch_analyze_bills_ollama.py --state AL --limit 10
  
  # Use 70B model (slower but better quality)
  python scripts/enrichment_ai/batch_analyze_bills_ollama.py --state GA --model llama3.3:70b --limit 1
        """
    )
    
    parser.add_argument('--state', help='State code (e.g., GA, AL, MA)')
    parser.add_argument('--topic', help='Topic search term (e.g., fluorid, dental)')
    parser.add_argument('--limit', type=int, default=10, help='Maximum bills to analyze (default: 10)')
    parser.add_argument('--no-incremental', action='store_true', help='Disable incremental processing')
    parser.add_argument('--model', default='llama3.2:latest', help='Ollama model (default: llama3.2:latest)')
    
    args = parser.parse_args()
    
    analyze_batch_ollama(
        state=args.state,
        topic=args.topic,
        limit=args.limit,
        skip_analyzed=not args.no_incremental,
        model=args.model
    )


if __name__ == "__main__":
    main()
