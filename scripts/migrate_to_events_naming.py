#!/usr/bin/env python3
"""
Migrate old naming conventions to new events_ and contacts_ naming.

OLD NAMING → NEW NAMING:
- meetings.parquet → events_events.parquet
- meetings_calendar.parquet → events_events.parquet (merged)
- meetings_transcripts.parquet → events_event_documents.parquet
- meetings_topics.parquet → events_event_agenda_items.parquet
- meetings_demographics.parquet → events_event_participants.parquet
- meetings_decisions.parquet → events_event_bills.parquet
- contacts_meeting_attendance.parquet → events_event_participants.parquet (merged)

This script will:
1. Find all old-named files in data/gold/
2. Rename them to new naming convention
3. Backup old files before renaming
4. Generate a migration report
"""

import shutil
from pathlib import Path
from datetime import datetime
import logging
import sys

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)
logger = logging.getLogger(__name__)

# Renaming map
RENAME_MAP = {
    "meetings.parquet": "events.parquet",
    "meetings_calendar.parquet": "events.parquet",  # Will be merged if both exist
    "meetings_transcripts.parquet": "event_documents.parquet",
    "meetings_topics.parquet": "event_agenda_items.parquet",
    "meetings_demographics.parquet": "event_participants.parquet",
    "meetings_decisions.parquet": "event_bills.parquet",
    "contacts_meeting_attendance.parquet": "event_participants.parquet",  # Merge with participants
    # Rename old events_event_* to new event_* naming
    "events_events.parquet": "events.parquet",
    "events_event_documents.parquet": "event_documents.parquet",
    "events_event_participants.parquet": "event_participants.parquet",
    "events_event_agenda_items.parquet": "event_agenda_items.parquet",
    "events_event_bills.parquet": "event_bills.parquet",
    "events_event_media.parquet": "event_media.parquet",
}


def backup_file(file_path: Path) -> Path:
    """Create a backup of the file with timestamp."""
    file_path = file_path.resolve()  # Convert to absolute path
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = file_path.parent / ".migration_backup"
    backup_dir.mkdir(exist_ok=True)
    
    backup_path = backup_dir / f"{file_path.stem}_{timestamp}.parquet"
    shutil.copy2(file_path, backup_path)
    try:
        print(f"   📦 Backed up to: {backup_path.relative_to(Path.cwd())}")
    except ValueError:
        print(f"   📦 Backed up to: {backup_path}")
    return backup_path


def cleanup_backups(directory: Path, dry_run: bool = False):
    """Remove all .migration_backup directories."""
    backup_dirs = list(directory.rglob(".migration_backup"))
    
    if not backup_dirs:
        print("No backup directories found")
        return 0
    
    print(f"\nFound {len(backup_dirs)} backup directories:")
    for backup_dir in backup_dirs:
        try:
            print(f"  📦 {backup_dir.relative_to(Path.cwd())}")
        except ValueError:
            print(f"  📦 {backup_dir}")
        if backup_dir.is_dir():
            file_count = len(list(backup_dir.glob("*.parquet")))
            print(f"     ({file_count} files)")
    
    if dry_run:
        print("\n[DRY RUN] Would delete these backup directories")
        return len(backup_dirs)
    
    print("\n⚠️  This will permanently delete all backup files!")
    response = input("Are you sure you want to continue? (yes/no): ")
    
    if response.lower() != "yes":
        print("Cancelled - no backups were deleted")
        return 0
    
    deleted = 0
    for backup_dir in backup_dirs:
        try:
            shutil.rmtree(backup_dir)
            try:
                print(f"✅ Deleted: {backup_dir.relative_to(Path.cwd())}")
            except ValueError:
                print(f"✅ Deleted: {backup_dir}")
            deleted += 1
        except Exception as e:
            print(f"❌ Error deleting {backup_dir}: {e}")
    
    return deleted


def rename_file(old_path: Path, new_name: str, dry_run: bool = False, skip_backup: bool = False) -> bool:
    """Rename a file to new naming convention."""
    old_path = old_path.resolve()  # Convert to absolute path
    new_path = old_path.parent / new_name
    
    print(f"\n🔄 {old_path.relative_to(Path.cwd())}")
    print(f"   → {new_path.relative_to(Path.cwd())}")
    
    if new_path.exists():
        print(f"   ⚠️  Target already exists: {new_path.name}")
        print(f"   Consider merging or manually resolving")
        return False
    
    if dry_run:
        print("   [DRY RUN] Would rename this file")
        return True
    
    # Create backup unless skipped
    if not skip_backup:
        backup_file(old_path)
    else:
        print("   ⏭️  Skipping backup (--no-backup)")
    
    # Rename
    old_path.rename(new_path)
    print(f"   ✅ Renamed successfully")
    return True


def scan_directory(directory: Path, dry_run: bool = False, skip_backup: bool = False):
    """Scan a directory for old-named files."""
    renamed_count = 0
    skipped_count = 0
    
    for old_name, new_name in RENAME_MAP.items():
        # Find all occurrences of this old filename
        old_files = list(directory.rglob(old_name))
        
        for old_file in old_files:
            # Skip backup directories
            if ".migration_backup" in str(old_file):
                continue
                
            success = rename_file(old_file, new_name, dry_run=dry_run, skip_backup=skip_backup)
            if success:
                renamed_count += 1
            else:
                skipped_count += 1
    
    return renamed_count, skipped_count


def main():
    """Main migration function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Migrate to new events_ naming convention")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be renamed without actually renaming"
    )
    parser.add_argument(
        "--directory",
        type=str,
        default="data/gold",
        help="Directory to scan for files (default: data/gold)"
    )
    parser.add_argument(
        "--no-backup",
        action="store_true",
        help="Skip creating backups (NOT RECOMMENDED unless you have external backups)"
    )
    parser.add_argument(
        "--cleanup-backups",
        action="store_true",
        help="Remove all .migration_backup directories"
    )
    
    args = parser.parse_args()
    
    gold_dir = Path(args.directory)
    
    if not gold_dir.exists():
        print(f"❌ Directory not found: {gold_dir}")
        sys.exit(1)
    
    # Handle cleanup mode
    if args.cleanup_backups:
        print("=" * 80)
        print("🗑️  Cleanup Backup Directories")
        print("=" * 80)
        print(f"Scanning: {gold_dir.absolute()}")
        
        deleted = cleanup_backups(gold_dir, dry_run=args.dry_run)
        
        print("")
        print("=" * 80)
        if args.dry_run:
            print(f"Would delete {deleted} backup directories")
        else:
            print(f"✅ Deleted {deleted} backup directories")
        print("=" * 80)
        return
    
    print("=" * 80)
    if args.dry_run:
        print("🔍 DRY RUN: File Naming Migration")
    else:
        print("🔄 File Naming Migration")
    print("=" * 80)
    print(f"Scanning: {gold_dir.absolute()}")
    
    if args.no_backup:
        print("⚠️  Backups DISABLED - files will be renamed without backup!")
    
    print("")
    
    print("Renaming map:")
    for old, new in RENAME_MAP.items():
        print(f"  {old} → {new}")
    print("")
    
    # Scan and rename
    renamed, skipped = scan_directory(gold_dir, dry_run=args.dry_run, skip_backup=args.no_backup)
    
    print("")
    print("=" * 80)
    print("Migration Summary")
    print("=" * 80)
    print(f"✅ Renamed: {renamed} files")
    print(f"⚠️  Skipped: {skipped} files (target exists or error)")
    
    if args.dry_run:
        print("")
        print("This was a DRY RUN. No files were actually renamed.")
        print("Run without --dry-run to perform the migration.")
    else:
        print("")
        print("✅ Migration complete!")
        if not args.no_backup:
            print("Backups are stored in .migration_backup directories")
            print("Run with --cleanup-backups to remove them after verification")
    
    print("")


if __name__ == "__main__":
    main()
