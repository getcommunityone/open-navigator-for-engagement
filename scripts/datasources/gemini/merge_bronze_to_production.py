#!/usr/bin/env python3
"""
Merge Bronze AI Extractions to Production Tables

Merges AI-extracted data from Bronze tables (meeting transcript analysis)
into production search tables with deduplication and entity resolution.

Bronze Tables (Source):
- bronze_contacts
- bronze_organizations  
- bronze_bills
- bronze_decisions
- bronze_financial_items

Production Tables (Target):
- contacts_search
- organizations_nonprofit_search
- bills_search
- bills_meetings (junction)
- contacts_meeting_attendance (junction)

Usage:
    # Dry run (show what would be merged)
    python scripts/datasources/gemini/merge_bronze_to_production.py --dry-run

    # Merge contacts only
    python scripts/datasources/gemini/merge_bronze_to_production.py --entity contacts

    # Merge all entities
    python scripts/datasources/gemini/merge_bronze_to_production.py --all

    # Generate deduplication report
    python scripts/datasources/gemini/merge_bronze_to_production.py --report-duplicates
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import argparse
import uuid
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

import psycopg2
from psycopg2.extras import RealDictCursor, execute_values
from loguru import logger

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Import entity resolution
from scripts.datasources.gemini.entity_resolution import (
    ContactMatcher,
    BillMatcher,
    OrganizationMatcher
)

# Database URLs
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'password')
BRONZE_DB_URL = os.getenv('LOCAL_BRONZE_DATABASE_URL', f'postgresql://postgres:{POSTGRES_PASSWORD}@localhost:5433/open_navigator_bronze')
NEON_DB_URL = os.getenv('NEON_DATABASE_URL_DEV', f'postgresql://postgres:{POSTGRES_PASSWORD}@localhost:5433/open_navigator')


class BronzeToProductionMerger:
    """Merge bronze tables to production with entity resolution"""
    
    def __init__(self, bronze_db_url: str, production_db_url: str, dry_run: bool = False):
        self.bronze_db_url = bronze_db_url
        self.production_db_url = production_db_url
        self.dry_run = dry_run
        self.merge_run_id = uuid.uuid4()
        
        # Stats
        self.stats = {
            'contacts': {'inserted': 0, 'updated': 0, 'skipped': 0, 'needs_review': 0},
            'organizations': {'inserted': 0, 'updated': 0, 'skipped': 0, 'needs_review': 0},
            'bills': {'inserted': 0, 'updated': 0, 'skipped': 0, 'needs_review': 0},
            'bills_meetings': {'inserted': 0},
            'attendance': {'inserted': 0}
        }
    
    def merge_contacts(self):
        """Merge bronze_contacts → contacts_search"""
        logger.info("=" * 70)
        logger.info("MERGING CONTACTS")
        logger.info("=" * 70)
        
        # Fetch bronze contacts
        with psycopg2.connect(self.bronze_db_url) as bronze_conn:
            with bronze_conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT * FROM bronze_contacts
                    WHERE extracted_at > NOW() - INTERVAL '7 days'  -- Only recent extractions
                    ORDER BY extracted_at DESC
                """)
                bronze_contacts = cur.fetchall()
        
        logger.info(f"Found {len(bronze_contacts):,} bronze contacts to process")
        
        if not bronze_contacts:
            logger.warning("No bronze contacts found")
            return
        
        # Process each bronze contact
        with psycopg2.connect(self.production_db_url) as prod_conn:
            for bronze_contact in bronze_contacts:
                self._merge_single_contact(bronze_contact, prod_conn)
            
            if not self.dry_run:
                prod_conn.commit()
                logger.success(f"✅ Committed {sum(self.stats['contacts'].values())} contact operations")
        
        # Show stats
        logger.info("")
        logger.info("📊 CONTACT MERGE STATS:")
        for action, count in self.stats['contacts'].items():
            logger.info(f"  {action:15} {count:>6,}")
    
    def _merge_single_contact(self, bronze_contact: Dict, prod_conn):
        """Merge one contact with entity resolution"""
        
        # Step 1: Fetch candidates from production (same state for performance)
        with prod_conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Get state from bronze contact's jurisdiction or org
            # This is a simplification - you might need more sophisticated state extraction
            cur.execute("""
                SELECT * FROM contacts_search
                WHERE name ILIKE %s
                LIMIT 100
            """, (f"%{bronze_contact['full_name']}%",))
            prod_candidates = cur.fetchall()
        
        # Step 2: Try exact ID match (Wikidata QID, OpenStates ID)
        exact_match = ContactMatcher.match_by_id(
            dict(bronze_contact),
            [dict(c) for c in prod_candidates]
        )
        
        if exact_match:
            # Update existing record if AI has newer info
            action = self._update_contact_from_bronze(
                prod_conn,
                exact_match['id'],
                bronze_contact
            )
            self.stats['contacts'][action] += 1
            self._log_merge(
                'contact',
                bronze_contact['id'],
                exact_match['id'],
                'exact_id',
                1.0,
                action
            )
            return
        
        # Step 3: Try exact name + jurisdiction match
        name_match = ContactMatcher.match_by_name_jurisdiction(
            dict(bronze_contact),
            [dict(c) for c in prod_candidates],
            threshold=0.95
        )
        
        if name_match:
            # Decide whether to update
            action = self._decide_contact_update(
                prod_conn,
                name_match,
                bronze_contact
            )
            self.stats['contacts'][action] += 1
            self._log_merge(
                'contact',
                bronze_contact['id'],
                name_match['id'],
                'name_jurisdiction',
                0.95,
                action
            )
            return
        
        # Step 4: Try fuzzy match
        fuzzy_matches = ContactMatcher.fuzzy_match(
            dict(bronze_contact),
            [dict(c) for c in prod_candidates],
            threshold=0.85
        )
        
        if fuzzy_matches:
            # Multiple potential matches - flag for review
            best_match, score = fuzzy_matches[0]
            logger.warning(f"⚠️  Fuzzy match found for '{bronze_contact['full_name']}' → '{best_match['name']}' (score: {score:.2f})")
            
            # Insert but flag for manual review
            action = self._insert_contact_from_bronze(
                prod_conn,
                bronze_contact,
                needs_review=True
            )
            self.stats['contacts'][action] += 1
            self._log_merge(
                'contact',
                bronze_contact['id'],
                None,
                'fuzzy',
                score,
                action
            )
            return
        
        # Step 5: No match - insert as new
        action = self._insert_contact_from_bronze(
            prod_conn,
            bronze_contact,
            needs_review=False
        )
        self.stats['contacts'][action] += 1
        self._log_merge(
            'contact',
            bronze_contact['id'],
            None,
            'none',
            0.0,
            action
        )
    
    def _decide_contact_update(self, prod_conn, existing_contact: Dict, bronze_contact: Dict) -> str:
        """Decide whether to update existing contact with bronze data"""
        
        existing_datasource = existing_contact.get('datasource', 'unknown')
        existing_confidence = existing_contact.get('confidence_score', 0.5)
        
        # Don't override authoritative sources
        if existing_datasource in ['openstates_api', 'irs_990']:
            logger.debug(f"Skipping update - authoritative source: {existing_datasource}")
            return 'skipped'
        
        # Replace low-confidence records
        if existing_confidence < 0.70:
            logger.info(f"Updating low-confidence record: {existing_contact['name']}")
            self._update_contact_from_bronze(
                prod_conn,
                existing_contact['id'],
                bronze_contact
            )
            return 'updated'
        
        # Otherwise skip
        return 'skipped'
    
    def _update_contact_from_bronze(self, prod_conn, contact_id: int, bronze_contact: Dict) -> str:
        """Update existing contact with bronze data"""
        
        if self.dry_run:
            logger.info(f"[DRY RUN] Would update contact {contact_id} with bronze data")
            return 'updated'
        
        with prod_conn.cursor() as cur:
            cur.execute("""
                UPDATE contacts_search
                SET 
                    title = COALESCE(%s, title),
                    organization_name = COALESCE(%s, organization_name),
                    email = COALESCE(%s, email),
                    phone = COALESCE(%s, phone),
                    datasource = 'gemini_ai_extraction',
                    datasource_id = %s,
                    confidence_score = 0.60,
                    last_updated = NOW()
                WHERE id = %s
            """, (
                bronze_contact.get('role'),
                bronze_contact.get('org_id'),
                None,  # Email not in bronze
                None,  # Phone not in bronze
                bronze_contact.get('wikidata_qid') or bronze_contact.get('person_id'),
                contact_id
            ))
        
        return 'updated'
    
    def _insert_contact_from_bronze(self, prod_conn, bronze_contact: Dict, needs_review: bool = False) -> str:
        """Insert new contact from bronze data"""
        
        if self.dry_run:
            logger.info(f"[DRY RUN] Would insert contact: {bronze_contact['full_name']}")
            return 'needs_review' if needs_review else 'inserted'
        
        with prod_conn.cursor() as cur:
            cur.execute("""
                INSERT INTO contacts_search (
                    name, title, organization_name, organization_ein,
                    email, phone, street_address, city, state_code, state, zip_code,
                    role_type, compensation, hours_per_week,
                    datasource, datasource_id, confidence_score,
                    verified, needs_review, last_updated
                ) VALUES (
                    %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s,
                    %s, %s, %s,
                    %s, %s, %s
                )
                RETURNING id
            """, (
                bronze_contact.get('full_name'),
                bronze_contact.get('role'),
                bronze_contact.get('org_id'),
                None,  # EIN not in bronze_contacts
                None,  # Email not extracted yet
                None,  # Phone not extracted yet
                None,  # Address not in bronze
                None,  # City not in bronze
                None,  # State code - need to extract
                None,  # State name - need to extract
                None,  # ZIP not in bronze
                'government_official' if not bronze_contact.get('is_lobbyist') else 'lobbyist',
                None,  # Compensation
                None,  # Hours per week
                'gemini_ai_extraction',
                bronze_contact.get('wikidata_qid') or bronze_contact.get('person_id'),
                0.60,  # AI extraction confidence
                False,  # Not verified
                needs_review,
                datetime.now()
            ))
        
        return 'needs_review' if needs_review else 'inserted'
    
    def _log_merge(self, entity_type: str, bronze_id: int, prod_id: Optional[int], 
                   match_type: str, confidence: float, action: str):
        """Log merge operation for debugging"""
        
        if self.dry_run:
            return
        
        with psycopg2.connect(self.production_db_url) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO bronze_merge_log (
                        merge_run_id, entity_type, bronze_table, bronze_record_id,
                        production_table, production_record_id,
                        match_type, match_confidence, action_taken
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s
                    )
                """, (
                    self.merge_run_id,
                    entity_type,
                    f'bronze_{entity_type}s',
                    bronze_id,
                    f'{entity_type}s_search',
                    prod_id,
                    match_type,
                    confidence,
                    action
                ))
            conn.commit()
    
    def generate_duplicate_report(self):
        """Generate report of potential duplicates for manual review"""
        logger.info("=" * 70)
        logger.info("DUPLICATE DETECTION REPORT")
        logger.info("=" * 70)
        
        # Query contacts that need review
        with psycopg2.connect(self.production_db_url) as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT 
                        id, name, title, organization_name,
                        datasource, confidence_score, needs_review, review_notes,
                        last_updated
                    FROM contacts_search
                    WHERE needs_review = TRUE
                    ORDER BY last_updated DESC
                    LIMIT 100
                """)
                needs_review = cur.fetchall()
        
        if not needs_review:
            logger.info("✅ No contacts flagged for review")
            return
        
        logger.info(f"\n⚠️  {len(needs_review)} contacts need manual review:\n")
        
        for contact in needs_review:
            logger.info(f"ID {contact['id']}: {contact['name']}")
            logger.info(f"  Title: {contact['title']}")
            logger.info(f"  Org: {contact['organization_name']}")
            logger.info(f"  Datasource: {contact['datasource']} (confidence: {contact['confidence_score']:.2f})")
            logger.info(f"  Last updated: {contact['last_updated']}")
            logger.info("")


def main():
    parser = argparse.ArgumentParser(
        description='Merge Bronze AI extractions to Production tables'
    )
    
    parser.add_argument(
        '--entity',
        type=str,
        choices=['contacts', 'organizations', 'bills', 'all'],
        default='all',
        help='Which entity type to merge'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be merged without committing'
    )
    
    parser.add_argument(
        '--report-duplicates',
        action='store_true',
        help='Generate duplicate detection report'
    )
    
    parser.add_argument(
        '--bronze-db',
        type=str,
        default=BRONZE_DB_URL,
        help='Bronze database URL'
    )
    
    parser.add_argument(
        '--production-db',
        type=str,
        default=NEON_DB_URL,
        help='Production database URL'
    )
    
    args = parser.parse_args()
    
    logger.info("=" * 70)
    logger.info("BRONZE → PRODUCTION MERGE")
    logger.info("=" * 70)
    logger.info(f"Entity: {args.entity}")
    logger.info(f"Dry run: {args.dry_run}")
    logger.info(f"Bronze DB: {args.bronze_db[:50]}...")
    logger.info(f"Production DB: {args.production_db[:50]}...")
    logger.info("")
    
    merger = BronzeToProductionMerger(
        bronze_db_url=args.bronze_db,
        production_db_url=args.production_db,
        dry_run=args.dry_run
    )
    
    try:
        if args.report_duplicates:
            merger.generate_duplicate_report()
            return 0
        
        if args.entity in ['contacts', 'all']:
            merger.merge_contacts()
        
        if args.entity in ['organizations', 'all']:
            logger.info("\n⏳ Organizations merge not yet implemented")
        
        if args.entity in ['bills', 'all']:
            logger.info("\n⏳ Bills merge not yet implemented")
        
        logger.info("")
        logger.info("=" * 70)
        logger.info("✅ MERGE COMPLETE")
        logger.info("=" * 70)
        
        return 0
        
    except Exception as e:
        logger.error(f"✗ Merge failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
