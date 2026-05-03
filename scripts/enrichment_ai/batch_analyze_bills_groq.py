#!/usr/bin/env python3
"""
Batch Legislative Bill Analysis using Groq API
Analyzes bills to extract interest group positions using Groq's fast, free API.
"""

import os
import sys
import time
import json
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass
import argparse

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from loguru import logger
from groq import Groq

# Import the DuckDB analyzer from our existing module
from scripts.enrichment_ai.legislative_analysis_intel import (
    DuckDBLegislativeAnalyzer,
    InterestGroup
)

@dataclass
class AnalysisStats:
    """Track analysis statistics"""
    total_bills: int = 0
    success_count: int = 0
    error_count: int = 0
    total_groups: int = 0
    start_time: float = 0.0
    
    def add_success(self, num_groups: int):
        self.success_count += 1
        self.total_groups += num_groups
    
    def add_error(self):
        self.error_count += 1
    
    @property
    def elapsed_minutes(self) -> float:
        return (time.time() - self.start_time) / 60
    
    @property
    def avg_time_per_bill(self) -> float:
        if self.success_count == 0:
            return 0.0
        return (time.time() - self.start_time) / self.success_count


class GroqLLM:
    """Groq API wrapper for legislative analysis"""
    
    def __init__(
        self, 
        model_name: str = "llama-3.2-3b-preview",
        api_key: str = None
    ):
        """
        Initialize Groq client
        
        Args:
            model_name: Groq model to use (llama-3.2-3b-preview is fast and free)
            api_key: Groq API key (or set GROQ_API_KEY env var)
        """
        self.model_name = model_name
        self.api_key = api_key or os.getenv('GROQ_API_KEY')
        
        if not self.api_key:
            raise ValueError(
                "Groq API key required. Set GROQ_API_KEY env var or pass api_key parameter.\n"
                "Get your key at: https://console.groq.com/keys"
            )
        
        self.client = Groq(api_key=self.api_key)
        logger.info(f"🚀 Using Groq API: {self.model_name}")
        logger.info(f"   Free tier: 30 requests/min, 14,400 requests/day")
    
    def extract_interest_groups(
        self,
        bill_id: str,
        bill_title: str,
        bill_text: str,
        testimony: List[Dict] = None
    ) -> List[InterestGroup]:
        """
        Extract interest groups from bill using Groq API
        
        Args:
            bill_id: Bill identifier
            bill_title: Bill title
            bill_text: Bill text content
            testimony: Optional testimony records
            
        Returns:
            List of InterestGroup objects
        """
        # Build prompt
        prompt = self._build_prompt(bill_id, bill_title, bill_text, testimony)
        
        # Call Groq API
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert at analyzing legislative testimony to identify stakeholder groups and their positions. Always respond with valid JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=500,
                temperature=0.1
            )
            
            # Extract response
            response_text = response.choices[0].message.content
            
            # Parse response
            groups = self._parse_response(response_text, bill_id)
            
            logger.debug(f"   Extracted {len(groups)} groups")
            return groups
            
        except Exception as e:
            logger.error(f"Groq API error: {e}")
            return []
    
    def _build_prompt(
        self,
        bill_id: str,
        bill_title: str,
        bill_text: str,
        testimony: List[Dict] = None
    ) -> str:
        """Build analysis prompt"""
        
        # Truncate bill text if too long
        max_bill_length = 1000
        bill_excerpt = bill_text[:max_bill_length] if bill_text else ""
        if len(bill_text or "") > max_bill_length:
            bill_excerpt += "... [truncated]"
        
        prompt = f"""Analyze this legislative bill and identify interest groups that would likely support or oppose it.

Bill: {bill_id}
Title: {bill_title}

Bill Text:
{bill_excerpt}
"""
        
        # Add testimony if available
        if testimony and len(testimony) > 0:
            prompt += "\n\nTestimony:\n"
            for t in testimony[:5]:  # Limit to first 5 testimonies
                position = t.get('position', 'unknown')
                person = t.get('person_name', 'Unknown')
                org = t.get('organization', '')
                content = t.get('content', '')[:200]  # First 200 chars
                
                prompt += f"- {person}"
                if org:
                    prompt += f" ({org})"
                prompt += f" - {position}\n"
                if content:
                    prompt += f"  {content}...\n"
        
        prompt += """

Identify up to 5 interest groups and their likely positions. Return ONLY valid JSON in this format:
{
  "groups": [
    {
      "name": "Group Name",
      "position": "support|oppose|neutral",
      "rationale": "Brief explanation"
    }
  ]
}
"""
        
        return prompt
    
    def _parse_response(self, response_text: str, bill_id: str) -> List[InterestGroup]:
        """Parse LLM response into InterestGroup objects"""
        
        groups = []
        
        try:
            # Try to extract JSON from response
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                data = json.loads(json_str)
                
                # Extract groups
                for group_data in data.get('groups', []):
                    group = InterestGroup(
                        bill_id=bill_id,
                        group_name=group_data.get('name', ''),
                        position=group_data.get('position', 'neutral'),
                        rationale=group_data.get('rationale', ''),
                        confidence=0.8  # Groq models are pretty reliable
                    )
                    groups.append(group)
            
        except Exception as e:
            logger.warning(f"   Failed to parse response: {e}")
            logger.debug(f"   Response was: {response_text[:200]}")
        
        return groups


def analyze_batch(
    state: str = None,
    topic: str = None,
    limit: int = 10,
    skip_analyzed: bool = True,
    model: str = "llama-3.2-3b-preview"
):
    """
    Analyze a batch of bills using Groq API
    
    Args:
        state: Filter by state (e.g., 'AL', 'MA')
        topic: Filter by topic keywords (e.g., 'fluoride', 'dental')
        limit: Maximum number of bills to analyze
        skip_analyzed: Skip bills that have already been analyzed
        model: Groq model name
    """
    
    stats = AnalysisStats(start_time=time.time())
    
    logger.info("=" * 70)
    logger.info("BATCH BILL ANALYSIS WITH GROQ API")
    logger.info("=" * 70)
    logger.info(f"State: {state}")
    logger.info(f"Topic: {topic}")
    logger.info(f"Limit: {limit}")
    logger.info(f"Incremental: {skip_analyzed}")
    logger.info(f"Model: {model}")
    logger.info("")
    logger.info(f"💰 Cost: FREE (Groq free tier)")
    logger.info(f"⏱️  Estimated time: {limit * 2 / 60:.1f} minutes (~2 sec/bill)")
    logger.info("")
    
    # Connect to DuckDB
    analyzer = DuckDBLegislativeAnalyzer()
    analyzer.connect()
    
    # Load bill and testimony data
    logger.info("📊 Loading bill data...")
    analyzer.create_bills_table()
    analyzer.create_testimony_table()
    
    # Load bill texts if available (optional - provides richer context)
    bill_texts_available = False
    bill_texts_path = Path(__file__).parent.parent.parent / "data" / "gold" / "bills_bill_text.parquet"
    if bill_texts_path.exists():
        logger.info("📄 Loading bill texts (full PDF/HTML content)...")
        analyzer.conn.execute(f"""
            CREATE OR REPLACE TABLE bill_texts AS
            SELECT * FROM read_parquet('{bill_texts_path}')
            WHERE extraction_status = 'success'
        """)
        text_count = analyzer.conn.execute("SELECT COUNT(*) FROM bill_texts").fetchone()[0]
        logger.info(f"   ✅ Loaded {text_count:,} bill texts")
        bill_texts_available = True
    else:
        logger.info("   ⚠️  Bill texts not found (will use title + abstract instead)")
        logger.info(f"   💡 Run: python scripts/data/scrape_bill_texts.py --state {state or 'AL'} --limit 10")
    
    # Find bills to analyze
    logger.info("\n🔍 Finding bills to analyze...")
    
    where_clauses = []
    if state:
        where_clauses.append(f"state = '{state}'")
    if topic:
        where_clauses.append(f"(LOWER(title) LIKE '%{topic.lower()}%' OR LOWER(abstract) LIKE '%{topic.lower()}%' OR LOWER(latest_action) LIKE '%{topic.lower()}%')")
    
    where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"
    
    # Build query with optional bill texts join
    if bill_texts_available:
        select_clause = """
            SELECT b.bill_id, b.state, b.title, 
                   COALESCE(b.abstract, '') as abstract,
                   COALESCE(b.latest_action, '') as latest_action,
                   b.session,
                   COALESCE(bt.text, '') as bill_text,
                   bt.text_hash
            FROM bills b
            LEFT JOIN bill_texts bt ON b.bill_id = bt.bill_id
        """
    else:
        select_clause = """
            SELECT bill_id, state, title, 
                   COALESCE(abstract, '') as abstract,
                   COALESCE(latest_action, '') as latest_action,
                   session,
                   '' as bill_text,
                   NULL as text_hash
            FROM bills
        """
    
    # Check which bills need analysis
    if skip_analyzed:
        # Check if analysis table exists
        table_exists = analyzer.conn.execute(
            "SELECT count(*) FROM information_schema.tables WHERE table_name = 'analysis'"
        ).fetchone()[0] > 0
        
        if table_exists:
            if bill_texts_available:
                query = f"""
                {select_clause}
                LEFT JOIN analysis a ON b.bill_id = a.bill_id
                WHERE {where_sql}
                  AND a.bill_id IS NULL
                LIMIT {limit}
                """
            else:
                query = f"""
                SELECT b.* FROM ({select_clause}) b
                LEFT JOIN analysis a ON b.bill_id = a.bill_id
                WHERE {where_sql}
                  AND a.bill_id IS NULL
                LIMIT {limit}
                """
        else:
            logger.info("   No previous analysis found, analyzing all matching bills")
            query = f"""
            {select_clause}
            WHERE {where_sql}
            LIMIT {limit}
            """
    else:
        query = f"""
        {select_clause}
        WHERE {where_sql}
        LIMIT {limit}
        """
    
    bills = analyzer.conn.execute(query).fetchall()
    stats.total_bills = len(bills)
    
    logger.info(f"📋 Found {stats.total_bills} bills to analyze")
    logger.info("")
    
    if stats.total_bills == 0:
        logger.warning("No bills found matching criteria")
        analyzer.close()
        return
    
    # Initialize Groq LLM
    logger.info("🚀 Connecting to Groq API...")
    llm = GroqLLM(model_name=model)
    logger.info("✅ API connected")
    logger.info("")
    
    # Process each bill
    all_results = []
    
    for i, bill in enumerate(bills, 1):
        bill_id = bill[0]
        state = bill[1]
        title = bill[2]
        abstract = bill[3] or ""
        latest_action = bill[4] or ""
        session = bill[5] or ""
        scraped_bill_text = bill[6] or "" if len(bill) > 6 else ""
        text_hash = bill[7] if len(bill) > 7 else None
        
        # Use scraped bill text if available, otherwise combine metadata
        if scraped_bill_text and len(scraped_bill_text) > 100:
            # Full bill text available!
            bill_text = f"{title}\n\n{scraped_bill_text[:5000]}"  # Limit to 5000 chars for API
            logger.info(f"[{i}/{stats.total_bills}] Analyzing {bill_id}...")
            logger.info(f"   Title: {title[:70]}...")
            logger.info(f"   ✨ Using full bill text ({len(scraped_bill_text):,} chars, hash: {text_hash[:8]}...)")
        else:
            # Fallback to metadata
            bill_text = f"{title}\n\n"
            if abstract:
                bill_text += f"Summary: {abstract}\n\n"
            if latest_action:
                bill_text += f"Latest Action: {latest_action}\n"
            if session:
                bill_text += f"Session: {session}\n"
            
            logger.info(f"[{i}/{stats.total_bills}] Analyzing {bill_id}...")
            logger.info(f"   Title: {title[:70]}...")
            logger.info(f"   ⚠️  No full text available (using metadata only)")
        
        # Get testimony for this bill
        testimony_query = f"""
        SELECT speaker_name, '' as organization, '' as position, testimony_text as content
        FROM testimony
        WHERE bill_id = '{bill_id}'
        LIMIT 10
        """
        try:
            testimony_rows = analyzer.conn.execute(testimony_query).fetchall()
            testimony = [
                {
                    'person_name': t[0],
                    'organization': t[1],
                    'position': t[2],
                    'content': t[3]
                }
                for t in testimony_rows
            ]
        except Exception as e:
            logger.warning(f"   No testimony found: {e}")
            testimony = []
        
        # Extract interest groups
        groups = llm.extract_interest_groups(
            bill_id=bill_id,
            bill_title=title,
            bill_text=bill_text,
            testimony=testimony
        )
        
        if groups:
            logger.info(f"   ✅ Found {len(groups)} groups:")
            for g in groups:
                logger.info(f"      - {g.group_name}: {g.position}")
            stats.add_success(len(groups))
            all_results.extend(groups)
        else:
            logger.warning(f"   ⚠️  No groups found")
            stats.add_error()
        
        # Rate limiting: Groq free tier = 30 req/min
        # Sleep 2 seconds between requests to stay under limit
        if i < stats.total_bills:
            time.sleep(2)
    
    # Save results
    logger.info("")
    logger.info("=" * 70)
    logger.info("📊 BATCH ANALYSIS COMPLETE")
    logger.info("=" * 70)
    logger.info(f"✅ Success: {stats.success_count}/{stats.total_bills} bills")
    logger.info(f"❌ Errors: {stats.error_count}")
    logger.info(f"📝 Total groups extracted: {stats.total_groups}")
    logger.info(f"⏱️  Total time: {stats.elapsed_minutes:.1f} minutes")
    logger.info(f"⚡ Average: {stats.avg_time_per_bill:.1f} sec/bill")
    
    if all_results:
        # Save to parquet
        output_path = Path(__file__).parent.parent.parent / "data" / "gold" / "analysis"
        output_path.mkdir(parents=True, exist_ok=True)
        output_file = output_path / "interest_groups_analysis.parquet"
        
        analyzer.save_analysis_results(all_results, str(output_file))
        logger.info(f"💾 Results saved to: {output_file}")
    
    logger.info("")
    
    analyzer.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Analyze legislative bills using Groq API'
    )
    parser.add_argument('--state', type=str, help='State abbreviation (e.g., AL, MA)')
    parser.add_argument('--topic', type=str, help='Topic keywords (e.g., fluoride)')
    parser.add_argument('--limit', type=int, default=10, help='Max bills to analyze')
    parser.add_argument('--no-incremental', action='store_true', 
                        help='Re-analyze already analyzed bills')
    parser.add_argument('--model', type=str, 
                        default='llama-3.2-3b-preview',
                        help='Groq model name')
    
    args = parser.parse_args()
    
    analyze_batch(
        state=args.state,
        topic=args.topic,
        limit=args.limit,
        skip_analyzed=not args.no_incremental,
        model=args.model
    )
