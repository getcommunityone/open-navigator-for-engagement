#!/usr/bin/env python3
"""
Cleanup Non-Gold Data Files

Removes intermediate/cached files that are not in gold tables to save disk space.
Preserves:
- data/gold/*.parquet (gold tables)
- data/cache/localview/ (active LocalView data)
- .env and configuration files
- Documentation and code

Removes:
- data/bronze/ (except discovered_sources which can be regenerated)
- data/silver/ (intermediate processing)
- Temporary files in data/cache/ (except LocalView)
- Old backups and logs

Usage:
    # Dry run (show what would be deleted)
    python scripts/maintenance/cleanup_non_gold_files.py --dry-run
    
    # Actually delete files
    python scripts/maintenance/cleanup_non_gold_files.py
    
    # Aggressive cleanup (also removes bronze sources)
    python scripts/maintenance/cleanup_non_gold_files.py --aggressive
"""

import argparse
import shutil
from pathlib import Path
from typing import List, Tuple
from loguru import logger
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class DiskSpaceCleanup:
    """Clean up non-essential data files to save disk space."""
    
    def __init__(self, dry_run: bool = True, aggressive: bool = False):
        self.dry_run = dry_run
        self.aggressive = aggressive
        self.total_saved = 0
        
    def get_dir_size(self, path: Path) -> int:
        """Get total size of directory in bytes."""
        total = 0
        try:
            for item in path.rglob('*'):
                if item.is_file():
                    total += item.stat().st_size
        except PermissionError:
            pass
        return total
    
    def format_size(self, size_bytes: int) -> str:
        """Format bytes as human-readable size."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f} TB"
    
    def cleanup_directory(
        self,
        path: Path,
        description: str,
        exclude_patterns: List[str] = None
    ) -> int:
        """
        Clean up a directory.
        
        Args:
            path: Directory to clean
            description: Human-readable description
            exclude_patterns: Patterns to exclude (glob format)
            
        Returns:
            Bytes freed
        """
        if not path.exists():
            logger.info(f"Skipping {description} (doesn't exist)")
            return 0
        
        size = self.get_dir_size(path)
        
        if self.dry_run:
            logger.info(f"Would delete {description}: {self.format_size(size)}")
        else:
            logger.info(f"Deleting {description}: {self.format_size(size)}")
            try:
                shutil.rmtree(path)
                logger.success(f"Deleted {description}")
            except Exception as e:
                logger.error(f"Error deleting {description}: {e}")
                return 0
        
        return size
    
    def cleanup_files_matching(
        self,
        root: Path,
        pattern: str,
        description: str
    ) -> int:
        """Clean up files matching a pattern."""
        if not root.exists():
            return 0
        
        total_size = 0
        files = list(root.rglob(pattern))
        
        if not files:
            logger.info(f"No {description} found")
            return 0
        
        for file in files:
            if file.is_file():
                size = file.stat().st_size
                total_size += size
                
                if self.dry_run:
                    logger.debug(f"Would delete: {file} ({self.format_size(size)})")
                else:
                    try:
                        file.unlink()
                    except Exception as e:
                        logger.error(f"Error deleting {file}: {e}")
        
        if self.dry_run:
            logger.info(f"Would delete {len(files)} {description}: {self.format_size(total_size)}")
        else:
            logger.info(f"Deleted {len(files)} {description}: {self.format_size(total_size)}")
        
        return total_size
    
    def run(self):
        """Execute cleanup."""
        logger.info("=" * 80)
        if self.dry_run:
            logger.info("DRY RUN - No files will be deleted")
        else:
            logger.warning("CLEANUP - Files will be PERMANENTLY deleted")
        
        if self.aggressive:
            logger.warning("AGGRESSIVE mode enabled")
        
        logger.info("=" * 80)
        
        # 1. Clean up bronze (except discovered_sources)
        bronze_path = Path('data/bronze')
        if bronze_path.exists():
            for item in bronze_path.iterdir():
                if item.is_dir() and item.name != 'discovered_sources':
                    self.total_saved += self.cleanup_directory(
                        item,
                        f"Bronze data: {item.name}"
                    )
        
        # 2. Clean up silver (all intermediate processing)
        self.total_saved += self.cleanup_directory(
            Path('data/silver'),
            "Silver intermediate tables"
        )
        
        # 3. Clean up cache (except LocalView and active data)
        cache_path = Path('data/cache')
        if cache_path.exists():
            for item in cache_path.iterdir():
                if item.is_dir() and item.name not in ['localview', 'legislation_bulk']:
                    # Keep localview and legislation_bulk (user already cleaned postgres)
                    self.total_saved += self.cleanup_directory(
                        item,
                        f"Cache: {item.name}"
                    )
        
        # 4. Clean up old logs
        self.total_saved += self.cleanup_files_matching(
            Path('logs'),
            '*.log',
            "log files"
        )
        
        # 5. Clean up Python cache
        self.total_saved += self.cleanup_files_matching(
            Path('.'),
            '**/__pycache__',
            "Python cache directories"
        )
        
        # 6. Aggressive mode: also clean bronze/discovered_sources
        if self.aggressive:
            self.total_saved += self.cleanup_directory(
                Path('data/bronze/discovered_sources'),
                "Bronze discovered sources (aggressive)"
            )
        
        # Summary
        logger.info("=" * 80)
        if self.dry_run:
            logger.info(f"WOULD FREE: {self.format_size(self.total_saved)}")
            logger.info("Run without --dry-run to actually delete files")
        else:
            logger.success(f"FREED: {self.format_size(self.total_saved)}")
        logger.info("=" * 80)


def main():
    parser = argparse.ArgumentParser(
        description='Clean up non-essential data files to save disk space'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be deleted without actually deleting'
    )
    parser.add_argument(
        '--aggressive',
        action='store_true',
        help='Also delete bronze discovered_sources (can be regenerated)'
    )
    
    args = parser.parse_args()
    
    cleanup = DiskSpaceCleanup(dry_run=args.dry_run, aggressive=args.aggressive)
    cleanup.run()


if __name__ == '__main__':
    main()
