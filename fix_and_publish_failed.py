#!/usr/bin/env python3
"""
Fix and publish the 5 failed datasets
"""
import os
from pathlib import Path
from datetime import datetime
import pandas as pd
from huggingface_hub import HfApi, create_repo
from datasets import Dataset
from loguru import logger
from dotenv import load_dotenv

load_dotenv()

HUGGINGFACE_TOKEN = os.getenv('HUGGINGFACE_TOKEN')
HF_ORGANIZATION = os.getenv('HF_ORGANIZATION', 'CommunityOne')
GOLD_DIR = Path("data/gold")


def fix_and_publish_jurisdictions():
    """Fix and publish the 4 jurisdiction files."""
    
    jurisdiction_files = [
        'data/gold/reference/jurisdictions_cities.parquet',
        'data/gold/reference/jurisdictions_counties.parquet',
        'data/gold/reference/jurisdictions_school_districts.parquet',
        'data/gold/reference/jurisdictions_townships.parquet',
    ]
    
    api = HfApi(token=HUGGINGFACE_TOKEN)
    
    for file_str in jurisdiction_files:
        file_path = Path(file_str)
        dataset_name = f"reference-{file_path.stem.replace('_', '-')}"
        repo_id = f"{HF_ORGANIZATION}/{dataset_name}"
        
        logger.info(f"📤 Processing {file_path.name}...")
        
        try:
            # Load file
            df = pd.read_parquet(file_path)
            logger.info(f"   Loaded {len(df):,} records, {len(df.columns)} columns")
            
            # FIX: Convert ALL columns to standard types
            # This fixes the Arrow dictionary/categorical issue
            for col in df.columns:
                if df[col].dtype.name == 'category':
                    logger.info(f"   Converting categorical column: {col}")
                    df[col] = df[col].astype(str)
                elif df[col].dtype == 'object':
                    # Ensure all object columns are strings
                    df[col] = df[col].astype(str)
            
            # Reset index
            df = df.reset_index(drop=True)
            
            logger.info(f"   Creating HuggingFace dataset...")
            dataset = Dataset.from_pandas(df, preserve_index=False)
            
            # Create repo
            try:
                create_repo(
                    repo_id=repo_id,
                    repo_type="dataset",
                    private=False,
                    exist_ok=True,
                    token=HUGGINGFACE_TOKEN
                )
            except Exception as e:
                logger.debug(f"   Repo may already exist: {e}")
            
            # Push to hub
            logger.info(f"   Pushing to {repo_id}...")
            dataset.push_to_hub(
                repo_id=repo_id,
                private=False,
                commit_message=f"Update {dataset_name} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                token=HUGGINGFACE_TOKEN
            )
            
            url = f"https://huggingface.co/datasets/{repo_id}"
            logger.success(f"   ✅ Published {len(df):,} records to {url}\n")
            
        except Exception as e:
            logger.error(f"   ❌ Failed: {e}\n")


def check_corrupted_meetings():
    """Check if we need the corrupted meetings.parquet file."""
    
    logger.info("🔍 Checking national/meetings.parquet...")
    
    meetings_calendar = Path('data/gold/national/meetings_calendar.parquet')
    meetings = Path('data/gold/national/meetings.parquet')
    
    if meetings_calendar.exists():
        try:
            df = pd.read_parquet(meetings_calendar)
            logger.success(f"✅ We already have national-meetings-calendar with {len(df):,} records")
            logger.info("   This contains the same data, so corrupted meetings.parquet can be deleted\n")
        except:
            pass
    
    # Try to check file
    try:
        df = pd.read_parquet(meetings)
        logger.warning(f"⚠️  meetings.parquet is actually readable! {len(df):,} records")
    except Exception as e:
        logger.error(f"❌ meetings.parquet is corrupted: {e}")
        logger.info(f"   File size: {meetings.stat().st_size / 1024 / 1024:.2f} MB")
        logger.info("   Recommend: Delete this file or regenerate it\n")


def main():
    """Fix and publish failed datasets."""
    
    if not HUGGINGFACE_TOKEN:
        logger.error("❌ HUGGINGFACE_TOKEN not set")
        return
    
    logger.info("=" * 80)
    logger.info("🔧 Fixing and Publishing Failed Datasets")
    logger.info("=" * 80)
    print()
    
    # Check the corrupted file
    check_corrupted_meetings()
    
    # Fix and publish jurisdiction files
    logger.info("📋 Publishing 4 jurisdiction reference datasets...")
    print()
    fix_and_publish_jurisdictions()
    
    # Summary
    logger.info("=" * 80)
    logger.success("✅ Done! Check your datasets at: https://huggingface.co/CommunityOne")
    logger.info("=" * 80)


if __name__ == "__main__":
    main()
