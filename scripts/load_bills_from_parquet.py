#!/usr/bin/env python3
"""
Load bills from existing parquet files into DuckDB
Demonstrates querying parquet files directly without copying
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scripts.legislative_analysis_intel import DuckDBLegislativeAnalyzer
from loguru import logger

logger.info("🚀 Loading bills from parquet files into DuckDB")
logger.info("=" * 60)

with DuckDBLegislativeAnalyzer() as analyzer:
    # Find what parquet files exist
    logger.info("📁 Searching for bill parquet files...")
    
    # Try different patterns
    patterns = [
        'data/gold/**/*bills*.parquet',
        'data/gold/**/*bill*.parquet',
        'data/gold/national/bills_*.parquet',
    ]
    
    found_files = False
    for pattern in patterns:
        try:
            logger.info(f"   Trying pattern: {pattern}")
            
            # Test if pattern matches any files
            test_query = f"""
                SELECT COUNT(*) as file_count
                FROM read_parquet('{pattern}', filename=true)
                LIMIT 1
            """
            result = analyzer.conn.execute(test_query).fetchone()
            
            if result and result[0] > 0:
                logger.info(f"   ✅ Found files matching: {pattern}")
                
                # Create bills table from this pattern
                analyzer.conn.execute(f"""
                    CREATE OR REPLACE TABLE bills AS
                    SELECT * FROM read_parquet('{pattern}')
                """)
                
                # Count total bills loaded
                count = analyzer.conn.execute("SELECT COUNT(*) FROM bills").fetchone()[0]
                logger.info(f"   📊 Loaded {count:,} bills into DuckDB")
                
                found_files = True
                break
                
        except Exception as e:
            logger.debug(f"   ⚠️  Pattern {pattern} didn't match: {e}")
            continue
    
    if not found_files:
        logger.warning("⚠️  No bill parquet files found")
        logger.info("   Creating demo bills table instead...")
        
        analyzer.conn.execute("""
            CREATE TABLE IF NOT EXISTS bills (
                identifier VARCHAR,
                title TEXT,
                abstract TEXT,
                classification VARCHAR,
                subject VARCHAR,
                from_organization_name VARCHAR,
                from_organization_state VARCHAR(2),
                updated_at TIMESTAMP
            )
        """)
        
        demo_bills = [
            ('HB1234', 'Water Fluoridation Act', 'Requires community water fluoridation', 'bill', 'Health', 'Alabama House', 'AL', '2026-04-01'),
            ('SB5678', 'Dental Care Access', 'Expands dental coverage for children', 'bill', 'Health', 'Georgia Senate', 'GA', '2026-04-15'),
            ('HB9012', 'School Health Programs', 'Funds oral health screenings in schools', 'bill', 'Education', 'Massachusetts House', 'MA', '2026-03-20'),
        ]
        analyzer.conn.executemany("INSERT INTO bills VALUES (?, ?, ?, ?, ?, ?, ?, ?)", demo_bills)
        logger.info("   ✅ Created 3 demo bills")
    
    # Now run stats
    logger.info("\n📊 Analyzing bill statistics...")
    stats = analyzer.analyze_bill_statistics()
    
    logger.info("\n📈 Results:")
    logger.info(f"\n🗺️  Top States by Bill Count:")
    for state_stat in stats.get('top_states', [])[:10]:
        logger.info(f"   {state_stat['state']}: {state_stat['count']:,} bills")
    
    if 'top_topics' in stats:
        logger.info(f"\n📋 Top Topics by Bill Count:")
        for topic_stat in stats.get('top_topics', [])[:10]:
            logger.info(f"   {topic_stat['topic']}: {topic_stat['count']:,} bills")
    elif 'top_subjects' in stats:
        logger.info(f"\n📋 Top Subjects by Bill Count:")
        for subject_stat in stats.get('top_subjects', [])[:10]:
            logger.info(f"   {subject_stat['subject']}: {subject_stat['count']:,} bills")

logger.info("\n✅ Analysis complete!")
