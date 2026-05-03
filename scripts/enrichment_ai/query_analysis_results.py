#!/usr/bin/env python3
"""
Query Analysis Results from Parquet Files

Shows how to query the analysis results using DuckDB.
Results are stored in Parquet for portability and speed.

Usage:
    # Show recent analysis
    python scripts/enrichment_ai/query_analysis_results.py
    
    # Filter by state
    python scripts/enrichment_ai/query_analysis_results.py --state GA
    
    # Find specific groups
    python scripts/enrichment_ai/query_analysis_results.py --group "Dental"
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import duckdb
import argparse
from scripts.enrichment_ai.legislative_analysis_intel import ANALYSIS_DIR
from loguru import logger


def query_results(state: str = None, group_filter: str = None, limit: int = 20):
    """Query analysis results from Parquet"""
    
    analysis_file = ANALYSIS_DIR / "interest_groups_analysis.parquet"
    
    if not analysis_file.exists():
        logger.error(f"❌ No analysis results found at: {analysis_file}")
        logger.info("\n💡 Run batch analysis first:")
        logger.info("   python scripts/enrichment_ai/batch_analyze_bills.py --state GA --topic fluorid --limit 5")
        return
    
    conn = duckdb.connect()
    
    # Build query
    where_clauses = []
    if state:
        where_clauses.append(f"bill_id LIKE '%{state.lower()}%'")
    if group_filter:
        where_clauses.append(f"LOWER(group_name) LIKE '%{group_filter.lower()}%'")
    
    where_sql = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""
    
    # Summary stats
    logger.info("=" * 70)
    logger.info("ANALYSIS RESULTS SUMMARY")
    logger.info("=" * 70)
    
    summary = conn.execute(f"""
        SELECT 
            COUNT(DISTINCT bill_id) as bills_analyzed,
            COUNT(*) as total_groups,
            COUNT(DISTINCT group_name) as unique_organizations,
            MIN(analyzed_at) as first_analysis,
            MAX(analyzed_at) as last_analysis
        FROM read_parquet('{analysis_file}')
    """).fetchone()
    
    logger.info(f"Bills analyzed:       {summary[0]}")
    logger.info(f"Interest groups:      {summary[1]}")
    logger.info(f"Unique organizations: {summary[2]}")
    logger.info(f"First analysis:       {summary[3]}")
    logger.info(f"Last analysis:        {summary[4]}")
    
    # Stance distribution
    logger.info("\n📊 Stance Distribution:")
    stances = conn.execute(f"""
        SELECT stance, COUNT(*) as count
        FROM read_parquet('{analysis_file}')
        GROUP BY stance
        ORDER BY count DESC
    """).fetchall()
    
    for stance, count in stances:
        logger.info(f"   {stance:12s}: {count}")
    
    # Recent results
    logger.info(f"\n🔍 Recent Analysis (limit {limit}):")
    if state:
        logger.info(f"   Filtered by state: {state}")
    if group_filter:
        logger.info(f"   Filtered by group: {group_filter}")
    logger.info("")
    
    results = conn.execute(f"""
        SELECT 
            bill_id,
            group_name,
            lobbyist,
            stance,
            stance_score,
            LEFT(testimony_excerpt, 60) as excerpt,
            confidence,
            analyzed_at
        FROM read_parquet('{analysis_file}')
        {where_sql}
        ORDER BY analyzed_at DESC
        LIMIT {limit}
    """).fetchall()
    
    if not results:
        logger.info("   No results found")
        return
    
    for row in results:
        bill_id, group, lobbyist, stance, score, excerpt, conf, analyzed_at = row
        
        logger.info(f"📋 {bill_id}")
        logger.info(f"   Organization: {group}")
        if lobbyist:
            logger.info(f"   Lobbyist:     {lobbyist}")
        logger.info(f"   Stance:       {stance} (score: {score:.2f})")
        logger.info(f"   Excerpt:      \"{excerpt}...\"")
        logger.info(f"   Confidence:   {conf:.0%}")
        logger.info(f"   Analyzed:     {analyzed_at}")
        logger.info("")
    
    # Export option
    logger.info("=" * 70)
    logger.info("💾 EXPORT OPTIONS")
    logger.info("=" * 70)
    logger.info("\nPython (Pandas):")
    logger.info(f"""
import pandas as pd
df = pd.read_parquet('{analysis_file}')
print(df.head())
df.to_csv('analysis_results.csv', index=False)
""")
    
    logger.info("\nDuckDB CLI:")
    logger.info(f"""
duckdb -c "COPY (SELECT * FROM read_parquet('{analysis_file}')) TO 'results.csv' (HEADER, DELIMITER ',')"
""")
    
    logger.info("\nSQL Query:")
    logger.info(f"""
SELECT bill_id, group_name, stance, stance_score
FROM read_parquet('{analysis_file}')
WHERE stance = 'oppose'
ORDER BY stance_score
LIMIT 10
""")


def main():
    parser = argparse.ArgumentParser(description="Query analysis results from Parquet")
    parser.add_argument('--state', help='Filter by state code (e.g., GA, AL)')
    parser.add_argument('--group', help='Filter by group name (partial match)')
    parser.add_argument('--limit', type=int, default=20, help='Number of results to show')
    
    args = parser.parse_args()
    
    query_results(
        state=args.state,
        group_filter=args.group,
        limit=args.limit
    )


if __name__ == "__main__":
    main()
