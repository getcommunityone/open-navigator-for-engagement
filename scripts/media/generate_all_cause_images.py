#!/usr/bin/env python3
"""
Generate images for ALL causes in the database

This script:
1. Loads all causes from gold parquet files:
   - NTEE codes (196 causes)
   - EveryOrg causes (39 causes)
2. Generates banner (1200x600) and square (400x400) images for each
3. Uses Gemini AI for intelligent color schemes
4. Organizes output by cause type

Usage:
    python scripts/media/generate_all_cause_images.py
    python scripts/media/generate_all_cause_images.py --limit 10  # Test with 10 causes
    python scripts/media/generate_all_cause_images.py --type ntee  # Only NTEE codes
    python scripts/media/generate_all_cause_images.py --type everyorg  # Only EveryOrg
"""

import os
import sys
import argparse
from pathlib import Path
from dotenv import load_dotenv
import polars as pl
from typing import List, Dict
import json

# Add parent directory to path to import the generator
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Load environment variables
load_dotenv()

# Import the image generator
from scripts.media.generate_topic_images import TopicImageGenerator


def load_ntee_causes(data_dir: str = "data/gold") -> List[Dict[str, str]]:
    """Load NTEE code causes from parquet file
    
    Returns:
        List of dicts with 'name', 'description', 'category'
    """
    ntee_path = Path(data_dir) / "causes_ntee_codes.parquet"
    
    if not ntee_path.exists():
        print(f"⚠️  NTEE codes file not found: {ntee_path}")
        return []
    
    df = pl.read_parquet(ntee_path)
    
    causes = []
    for row in df.iter_rows(named=True):
        # Use description as the cause name
        name = row['description']
        code = row['ntee_code']
        
        causes.append({
            'name': name,
            'description': f"NTEE Code {code}",
            'category': 'ntee',
            'source_id': code
        })
    
    print(f"✅ Loaded {len(causes)} NTEE causes")
    return causes


def load_everyorg_causes(data_dir: str = "data/gold") -> List[Dict[str, str]]:
    """Load EveryOrg causes from parquet file
    
    Returns:
        List of dicts with 'name', 'description', 'category'
    """
    everyorg_path = Path(data_dir) / "causes_everyorg_causes.parquet"
    
    if not everyorg_path.exists():
        print(f"⚠️  EveryOrg causes file not found: {everyorg_path}")
        return []
    
    df = pl.read_parquet(everyorg_path)
    
    causes = []
    for row in df.iter_rows(named=True):
        causes.append({
            'name': row['cause_name'],
            'description': row.get('description', ''),
            'category': 'everyorg',
            'source_id': row['cause_id']
        })
    
    print(f"✅ Loaded {len(causes)} EveryOrg causes")
    return causes


def main():
    parser = argparse.ArgumentParser(
        description='Generate images for ALL causes in the database'
    )
    parser.add_argument(
        '--type',
        choices=['all', 'ntee', 'everyorg'],
        default='all',
        help='Which causes to generate (default: all)'
    )
    parser.add_argument(
        '--limit',
        type=int,
        help='Limit number of causes (for testing)'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        default='data/media/causes',
        help='Output directory for images'
    )
    parser.add_argument(
        '--api-key',
        type=str,
        help='Google Gemini API key (or use GEMINI_API_KEY env var)'
    )
    parser.add_argument(
        '--skip-existing',
        action='store_true',
        help='Skip causes that already have generated images'
    )
    
    args = parser.parse_args()
    
    # Load causes based on type
    all_causes = []
    
    if args.type in ['all', 'ntee']:
        ntee_causes = load_ntee_causes()
        all_causes.extend(ntee_causes)
    
    if args.type in ['all', 'everyorg']:
        everyorg_causes = load_everyorg_causes()
        all_causes.extend(everyorg_causes)
    
    if not all_causes:
        print("❌ No causes found!")
        return 1
    
    print(f"\n📊 Total causes to process: {len(all_causes)}")
    
    # Apply limit if specified
    if args.limit:
        all_causes = all_causes[:args.limit]
        print(f"   (Limited to {args.limit} for testing)")
    
    # Initialize generator
    try:
        generator = TopicImageGenerator(
            api_key=args.api_key,
            output_dir=args.output_dir
        )
    except ValueError as e:
        print(f"\n❌ {e}")
        print("\n💡 To use this script:")
        print("   1. Get a Gemini API key: https://makersuite.google.com/app/apikey")
        print("   2. Add to .env file: GEMINI_API_KEY=your_key_here")
        print("   3. Or pass with --api-key flag")
        return 1
    
    # Generate images for each cause
    results = []
    skipped = 0
    failed = []
    
    print(f"\n🚀 Generating images for {len(all_causes)} causes...\n")
    print("=" * 80)
    
    for i, cause in enumerate(all_causes, 1):
        cause_name = cause['name']
        category = cause['category']
        
        # Create filename prefix
        prefix = f"{category}_{cause['source_id']}"
        
        # Check if already exists
        if args.skip_existing:
            banner_path = Path(args.output_dir) / f"{prefix}_banner.png"
            square_path = Path(args.output_dir) / f"{prefix}_square.png"
            
            if banner_path.exists() and square_path.exists():
                print(f"[{i}/{len(all_causes)}] ⏭️  Skipping (exists): {cause_name}")
                skipped += 1
                continue
        
        print(f"\n[{i}/{len(all_causes)}] Processing: {cause_name}")
        print(f"   Category: {category} | ID: {cause['source_id']}")
        print("-" * 80)
        
        try:
            result = generator.generate_images(cause_name, prefix=prefix)
            result['cause_info'] = cause
            results.append(result)
            
            # Progress indicator
            completed = len(results)
            total = len(all_causes) - skipped
            pct = (completed / total * 100) if total > 0 else 0
            print(f"   ✅ Success! ({completed}/{total} = {pct:.1f}% complete)")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            failed.append({
                'cause': cause_name,
                'category': category,
                'error': str(e)
            })
            continue
    
    # Summary
    print("\n" + "=" * 80)
    print("🎉 IMAGE GENERATION COMPLETE!")
    print("=" * 80)
    print(f"✅ Successfully generated: {len(results)} causes")
    
    if skipped > 0:
        print(f"⏭️  Skipped (existing):     {skipped} causes")
    
    if failed:
        print(f"❌ Failed:                 {len(failed)} causes")
        print("\nFailed causes:")
        for f in failed:
            print(f"   - {f['cause']} ({f['category']}): {f['error']}")
    
    print(f"\n📁 Images saved to: {args.output_dir}")
    
    # Save comprehensive metadata
    metadata = {
        'generated_at': pl.datetime('now').strftime('%Y-%m-%d %H:%M:%S'),
        'total_causes': len(all_causes),
        'successful': len(results),
        'skipped': skipped,
        'failed': len(failed),
        'cause_type': args.type,
        'results': results,
        'failed_causes': failed
    }
    
    metadata_path = Path(args.output_dir) / 'all_causes_metadata.json'
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"📄 Metadata saved to: {metadata_path}")
    
    # Generate summary by category
    ntee_count = sum(1 for r in results if r['cause_info']['category'] == 'ntee')
    everyorg_count = sum(1 for r in results if r['cause_info']['category'] == 'everyorg')
    
    print("\n📊 Breakdown by category:")
    if ntee_count > 0:
        print(f"   - NTEE codes:    {ntee_count} images")
    if everyorg_count > 0:
        print(f"   - EveryOrg:      {everyorg_count} images")
    
    # Success rate
    success_rate = (len(results) / len(all_causes) * 100) if all_causes else 0
    print(f"\n🎯 Success rate: {success_rate:.1f}%")
    
    # Next steps
    print("\n" + "=" * 80)
    print("📋 NEXT STEPS:")
    print("=" * 80)
    print("\n1. Copy images to frontend:")
    print(f"   mkdir -p frontend/public/images/causes")
    print(f"   cp {args.output_dir}/*.png frontend/public/images/causes/")
    
    print("\n2. Create API endpoint to serve cause metadata")
    print("   (shows which causes have images)")
    
    print("\n3. Update homepage to use database-driven causes:")
    print("   const { data: causes } = useQuery('trending-causes', ...")
    
    return 0 if not failed else 1


if __name__ == '__main__':
    sys.exit(main())
