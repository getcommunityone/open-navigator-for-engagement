"""
Quick Demo: Legislative Tracking Maps

This script demonstrates how to create legislative tracking maps
for multiple social issues with minimal code.

Run:
    python examples/legislative_map_demo.py
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.legislative_tracker import LegislativeTracker
from loguru import logger


async def demo_single_issue():
    """Demo: Track fluoridation legislation."""
    logger.info("=" * 80)
    logger.info("DEMO 1: Track Fluoridation Legislation")
    logger.info("=" * 80)
    
    tracker = LegislativeTracker()
    
    # Track fluoridation bills in 2024
    logger.info("\n📊 Searching for fluoridation bills...")
    df = await tracker.track_issue("fluoridation", year=2024)
    
    # Print summary
    logger.info(f"\n✅ Found {len(df)} bills")
    logger.info(f"   Bans: {len(df[df['type'] == 'ban'])}")
    logger.info(f"   Restrictions: {len(df[df['type'] == 'restriction'])}")
    logger.info(f"   Protections: {len(df[df['type'] == 'protection'])}")
    
    # Show first 5 bills
    logger.info("\n📋 Sample Bills:")
    for _, bill in df.head(5).iterrows():
        logger.info(f"   • {bill['state_code']}: {bill['title']} ({bill['type']}, {bill['status']})")
    
    # Generate map
    logger.info("\n🗺️  Generating map visualization...")
    tracker.create_choropleth_map(df, "fluoridation")
    logger.info("✅ Map saved to data/visualizations/fluoridation_map.html")


async def demo_multiple_issues():
    """Demo: Track multiple issues at once."""
    logger.info("\n" + "=" * 80)
    logger.info("DEMO 2: Track Multiple Issues")
    logger.info("=" * 80)
    
    tracker = LegislativeTracker()
    
    # Track multiple issues
    issues = ["abortion", "marijuana", "voting"]
    
    for issue in issues:
        logger.info(f"\n📊 Tracking {issue} legislation...")
        df = await tracker.track_issue(issue, year=2024)
        
        logger.info(f"   ✅ {len(df)} bills found")
        
        # Generate map
        tracker.create_choropleth_map(df, issue)
        logger.info(f"   🗺️  Map: data/visualizations/{issue}_map.html")


async def demo_state_filtering():
    """Demo: Track legislation in specific states only."""
    logger.info("\n" + "=" * 80)
    logger.info("DEMO 3: Track Specific States")
    logger.info("=" * 80)
    
    tracker = LegislativeTracker()
    
    # Track only southern states
    southern_states = ["AL", "AR", "FL", "GA", "KY", "LA", "MS", "NC", "SC", "TN", "TX", "VA", "WV"]
    
    logger.info(f"\n📊 Tracking abortion legislation in southern states...")
    df = await tracker.track_issue("abortion", year=2024, states=southern_states)
    
    logger.info(f"   ✅ {len(df)} bills found in {len(df['state_code'].unique())} states")
    
    # Show state breakdown
    state_counts = df.groupby('state_code').size().sort_values(ascending=False)
    logger.info("\n📋 Bills by State:")
    for state, count in state_counts.items():
        logger.info(f"   {state}: {count} bills")


async def demo_custom_keywords():
    """Demo: Add custom issue with your own keywords."""
    logger.info("\n" + "=" * 80)
    logger.info("DEMO 4: Custom Issue Keywords")
    logger.info("=" * 80)
    
    tracker = LegislativeTracker()
    
    # Add custom issue: Gun Control
    tracker.issue_keywords["gun_control"] = {
        "ban": ["ban assault weapons", "prohibit firearms", "gun ban"],
        "restriction": ["background check", "waiting period", "permit requirement"],
        "protection": ["constitutional carry", "second amendment protection", "gun rights"]
    }
    
    logger.info("\n📊 Tracking gun control legislation with custom keywords...")
    df = await tracker.track_issue("gun_control", year=2024)
    
    logger.info(f"   ✅ {len(df)} bills found")
    logger.info(f"   Bans: {len(df[df['type'] == 'ban'])}")
    logger.info(f"   Restrictions: {len(df[df['type'] == 'restriction'])}")
    logger.info(f"   Protections: {len(df[df['type'] == 'protection'])}")


async def demo_data_export():
    """Demo: Export data for further analysis."""
    logger.info("\n" + "=" * 80)
    logger.info("DEMO 5: Data Export")
    logger.info("=" * 80)
    
    tracker = LegislativeTracker()
    
    # Track fluoridation
    df = await tracker.track_issue("fluoridation", year=2024)
    
    # Export to CSV (already done automatically)
    logger.info(f"\n💾 CSV saved to: data/cache/legislation/fluoridation_2024.csv")
    
    # Export state summary
    state_summary = tracker.generate_state_summary(df)
    output_file = "data/cache/legislation/fluoridation_2024_summary.csv"
    state_summary.to_csv(output_file, index=False)
    logger.info(f"💾 Summary saved to: {output_file}")
    
    # Show summary
    logger.info("\n📊 State Summary (first 10):")
    print(state_summary.head(10).to_string(index=False))


async def main():
    """Run all demos."""
    logger.info("\n" + "=" * 80)
    logger.info("LEGISLATIVE TRACKING MAPS - DEMO")
    logger.info("=" * 80)
    logger.info("\nThis demo shows how to:")
    logger.info("  1. Track legislation for specific issues")
    logger.info("  2. Track multiple issues at once")
    logger.info("  3. Filter by specific states")
    logger.info("  4. Add custom issue keywords")
    logger.info("  5. Export data for analysis")
    logger.info("\n" + "=" * 80)
    
    try:
        # Run all demos
        await demo_single_issue()
        await demo_multiple_issues()
        await demo_state_filtering()
        await demo_custom_keywords()
        await demo_data_export()
        
        logger.info("\n" + "=" * 80)
        logger.info("✅ ALL DEMOS COMPLETE")
        logger.info("=" * 80)
        logger.info("\nView generated maps:")
        logger.info("  - data/visualizations/fluoridation_map.html")
        logger.info("  - data/visualizations/abortion_map.html")
        logger.info("  - data/visualizations/marijuana_map.html")
        logger.info("  - data/visualizations/voting_map.html")
        logger.info("  - data/visualizations/gun_control_map.html")
        logger.info("\nView exported data:")
        logger.info("  - data/cache/legislation/*.csv")
        
    except Exception as e:
        logger.error(f"\n❌ Error running demos: {e}")
        logger.error("\nMake sure you have:")
        logger.error("  1. OPENSTATES_API_KEY in .env file")
        logger.error("  2. Installed requirements: pip install plotly matplotlib")
        logger.error("\nGet API key at: https://openstates.org/accounts/signup/")


if __name__ == "__main__":
    asyncio.run(main())
