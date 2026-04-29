#!/usr/bin/env python3
"""
Export OpenStates data from PostgreSQL to Gold Parquet datasets

Exports data for dev states (WA, MA, AL, GA, WI) with new naming conventions:
- contacts_officials
- bills_bills
- bills_bill_actions
- bills_bill_sponsorships
- events_events
- events_event_participants

Files are saved to: data/gold/states/{STATE}/

Usage:
    python scripts/export_openstates_to_gold.py
"""

import psycopg2
import pandas as pd
from pathlib import Path
from loguru import logger
from typing import List

# Dev states for initial export
DEV_STATES = ['WA', 'MA', 'AL', 'GA', 'WI']

# Database connection
DB_URL = "postgresql://postgres:postgres@localhost:5433/openstates"

# Output directory
GOLD_DIR = Path("data/gold")
STATES_DIR = GOLD_DIR / "states"
STATES_DIR.mkdir(parents=True, exist_ok=True)


def get_state_jurisdiction(conn, state: str) -> str:
    """Get jurisdiction ID for a specific state."""
    cursor = conn.cursor()
    
    jur_id = f"ocd-jurisdiction/country:us/state:{state.lower()}/government"
    
    query = """
        SELECT id, name, classification
        FROM opencivicdata_jurisdiction
        WHERE id = %s
    """
    
    cursor.execute(query, (jur_id,))
    result = cursor.fetchone()
    
    if result:
        logger.info(f"Found jurisdiction: {result[1]} ({result[0]})")
        return result[0]
    else:
        logger.warning(f"Jurisdiction not found for state: {state}")
        return None


def export_contacts_officials(conn, state: str, state_dir: Path):
    """Export officials/legislators (people) from openstates_people table."""
    logger.info(f"  Exporting contacts_officials for {state}...")
    
    query = """
        SELECT 
            id as official_id,
            name as full_name,
            state,
            party,
            role_type,
            district,
            jurisdiction,
            email,
            phone,
            address,
            image as photo_url,
            data::text as source_data
        FROM openstates_people
        WHERE state = %s
        ORDER BY name
    """
    
    df = pd.read_sql(query, conn, params=(state,))
    
    if len(df) == 0:
        logger.warning(f"  No officials found for {state}")
        return None
    
    output_path = state_dir / "contacts_officials.parquet"
    df.to_parquet(output_path, index=False, engine='pyarrow', compression='snappy')
    
    logger.info(f"  ✅ Exported {len(df):,} officials")
    
    return df


def export_bills_bills(conn, state: str, jurisdiction_id: str, state_dir: Path):
    """Export bills from opencivicdata_bill table."""
    logger.info(f"  Exporting bills_bills for {state}...")
    
    if not jurisdiction_id:
        logger.warning(f"  No jurisdiction ID for {state}, skipping bills export")
        return None
    
    query = """
        SELECT 
            b.id as bill_id,
            b.identifier as bill_number,
            b.title,
            b.classification,
            b.from_organization_id,
            b.legislative_session_id,
            s.identifier as session,
            s.name as session_name,
            j.name as jurisdiction_name,
            j.id as jurisdiction_ocd_id,
            b.first_action_date,
            b.latest_action_date,
            b.latest_action_description,
            b.created_at,
            b.updated_at
        FROM opencivicdata_bill b
        JOIN opencivicdata_legislativesession s ON b.legislative_session_id = s.id
        JOIN opencivicdata_jurisdiction j ON s.jurisdiction_id = j.id
        WHERE j.id = %s
        ORDER BY s.identifier, b.identifier
    """
    
    df = pd.read_sql(query, conn, params=(jurisdiction_id,))
    
    if len(df) == 0:
        logger.warning(f"  No bills found for {state}")
        return None
    
    output_path = state_dir / "bills_bills.parquet"
    df.to_parquet(output_path, index=False, engine='pyarrow', compression='snappy')
    
    logger.info(f"  ✅ Exported {len(df):,} bills")
    
    return df


def export_bills_bill_actions(conn, state: str, jurisdiction_id: str, state_dir: Path):
    """Export bill actions from opencivicdata_billaction table."""
    logger.info(f"  Exporting bills_bill_actions for {state}...")
    
    if not jurisdiction_id:
        logger.warning(f"  No jurisdiction ID for {state}, skipping bill actions export")
        return None
    
    query = """
        SELECT 
            ba.id as action_id,
            ba.bill_id,
            b.identifier as bill_number,
            ba.description,
            ba.date as action_date,
            ba.classification,
            ba.organization_id,
            ba.order as sequence_order,
            j.name as jurisdiction_name
        FROM opencivicdata_billaction ba
        JOIN opencivicdata_bill b ON ba.bill_id = b.id
        JOIN opencivicdata_legislativesession s ON b.legislative_session_id = s.id
        JOIN opencivicdata_jurisdiction j ON s.jurisdiction_id = j.id
        WHERE j.id = %s
        ORDER BY ba.date DESC, ba.order
    """
    
    df = pd.read_sql(query, conn, params=(jurisdiction_id,))
    
    if len(df) == 0:
        logger.warning(f"  No bill actions found for {state}")
        return None
    
    output_path = state_dir / "bills_bill_actions.parquet"
    df.to_parquet(output_path, index=False, engine='pyarrow', compression='snappy')
    
    logger.info(f"  ✅ Exported {len(df):,} bill actions")
    
    return df


def export_bills_bill_sponsorships(conn, state: str, jurisdiction_id: str, state_dir: Path):
    """Export bill sponsorships from opencivicdata_billsponsorship table."""
    logger.info(f"  Exporting bills_bill_sponsorships for {state}...")
    
    if not jurisdiction_id:
        logger.warning(f"  No jurisdiction ID for {state}, skipping sponsorships export")
        return None
    
    query = """
        SELECT 
            bs.id as sponsorship_id,
            bs.bill_id,
            b.identifier as bill_number,
            bs.name as sponsor_name,
            bs.entity_type,
            bs.person_id,
            bs.organization_id,
            bs.primary as is_primary,
            bs.classification,
            j.name as jurisdiction_name
        FROM opencivicdata_billsponsorship bs
        JOIN opencivicdata_bill b ON bs.bill_id = b.id
        JOIN opencivicdata_legislativesession s ON b.legislative_session_id = s.id
        JOIN opencivicdata_jurisdiction j ON s.jurisdiction_id = j.id
        WHERE j.id = %s
        ORDER BY b.identifier, bs.primary DESC
    """
    
    df = pd.read_sql(query, conn, params=(jurisdiction_id,))
    
    if len(df) == 0:
        logger.warning(f"  No sponsorships found for {state}")
        return None
    
    output_path = state_dir / "bills_bill_sponsorships.parquet"
    df.to_parquet(output_path, index=False, engine='pyarrow', compression='snappy')
    
    logger.info(f"  ✅ Exported {len(df):,} sponsorships")
    
    return df


def export_events_events(conn, state: str, jurisdiction_id: str, state_dir: Path):
    """Export events/meetings from opencivicdata_event table."""
    logger.info(f"  Exporting events_events for {state}...")
    
    if not jurisdiction_id:
        logger.warning(f"  No jurisdiction ID for {state}, skipping events export")
        return None
    
    query = """
        SELECT 
            e.id as event_id,
            e.name as event_name,
            e.description,
            e.classification,
            e.start_date,
            e.end_date,
            e.all_day,
            e.status,
            e.location_id,
            j.name as jurisdiction_name,
            j.id as jurisdiction_ocd_id,
            e.created_at,
            e.updated_at
        FROM opencivicdata_event e
        JOIN opencivicdata_jurisdiction j ON e.jurisdiction_id = j.id
        WHERE j.id = %s
        ORDER BY e.start_date DESC
    """
    
    df = pd.read_sql(query, conn, params=(jurisdiction_id,))
    
    if len(df) == 0:
        logger.warning(f"  No events found for {state}")
        return None
    
    output_path = state_dir / "events_events.parquet"
    df.to_parquet(output_path, index=False, engine='pyarrow', compression='snappy')
    
    logger.info(f"  ✅ Exported {len(df):,} events")
    
    return df


def export_events_event_participants(conn, state: str, jurisdiction_id: str, state_dir: Path):
    """Export event participants from opencivicdata_eventparticipant table."""
    logger.info(f"  Exporting events_event_participants for {state}...")
    
    if not jurisdiction_id:
        logger.warning(f"  No jurisdiction ID for {state}, skipping event participants export")
        return None
    
    query = """
        SELECT 
            ep.id as participant_id,
            ep.event_id,
            e.name as event_name,
            ep.name as participant_name,
            ep.entity_type,
            ep.person_id,
            ep.organization_id,
            ep.note,
            j.name as jurisdiction_name
        FROM opencivicdata_eventparticipant ep
        JOIN opencivicdata_event e ON ep.event_id = e.id
        JOIN opencivicdata_jurisdiction j ON e.jurisdiction_id = j.id
        WHERE j.id = %s
        ORDER BY e.start_date DESC
    """
    
    df = pd.read_sql(query, conn, params=(jurisdiction_id,))
    
    if len(df) == 0:
        logger.warning(f"  No event participants found for {state}")
        return None
    
    output_path = state_dir / "events_event_participants.parquet"
    df.to_parquet(output_path, index=False, engine='pyarrow', compression='snappy')
    
    logger.info(f"  ✅ Exported {len(df):,} event participants")
    
    return df


def main():
    """Main export function - exports each state to its own directory."""
    logger.info("=" * 80)
    logger.info("EXPORTING OPENSTATES DATA TO GOLD DATASETS")
    logger.info("=" * 80)
    logger.info(f"Dev States: {', '.join(DEV_STATES)}")
    logger.info(f"Output Directory: {STATES_DIR}")
    logger.info("")
    
    # Connect to database
    logger.info("Connecting to PostgreSQL...")
    conn = psycopg2.connect(DB_URL)
    
    try:
        # Export each state separately
        for state in DEV_STATES:
            logger.info(f"\n{'=' * 60}")
            logger.info(f"Processing state: {state}")
            logger.info('=' * 60)
            
            # Create state directory
            state_dir = STATES_DIR / state
            state_dir.mkdir(exist_ok=True)
            
            # Get jurisdiction ID for this state
            jurisdiction_id = get_state_jurisdiction(conn, state)
            
            if not jurisdiction_id:
                logger.warning(f"Skipping {state} - no jurisdiction found")
                continue
            
            # Export all datasets for this state
            export_contacts_officials(conn, state, state_dir)
            export_bills_bills(conn, state, jurisdiction_id, state_dir)
            export_bills_bill_actions(conn, state, jurisdiction_id, state_dir)
            export_bills_bill_sponsorships(conn, state, jurisdiction_id, state_dir)
            export_events_events(conn, state, jurisdiction_id, state_dir)
            export_events_event_participants(conn, state, jurisdiction_id, state_dir)
            
            # Show summary for this state
            logger.info(f"\n  State {state} files:")
            for file in sorted(state_dir.glob("*.parquet")):
                if file.name.startswith(('bills_', 'contacts_', 'events_')):
                    size_mb = file.stat().st_size / 1024 / 1024
                    logger.info(f"    {file.name}: {size_mb:.2f} MB")
        
        logger.info("\n" + "=" * 80)
        logger.info("✅ EXPORT COMPLETE!")
        logger.info("=" * 80)
        logger.info(f"Gold datasets saved to: {STATES_DIR}")
        logger.info("")
        logger.info("Exported states:")
        for state in DEV_STATES:
            state_dir = STATES_DIR / state
            if state_dir.exists():
                leg_files = [f for f in state_dir.glob("*.parquet") 
                           if f.name.startswith(('bills_', 'contacts_', 'events_'))]
                logger.info(f"  {state}: {len(leg_files)} legislative files")
        
    finally:
        conn.close()


if __name__ == "__main__":
    main()
