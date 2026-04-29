#!/usr/bin/env python3
"""
Export OpenStates data from PostgreSQL to Gold Parquet datasets

Exports data for dev states (WA, MA, AL, GA, WI) with new naming conventions:
- contacts_officials
- contacts_official_roles  
- contacts_official_contacts
- bills_bills
- bills_bill_actions
- bills_bill_sponsorships
- events_events
- events_event_participants

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
GOLD_DIR.mkdir(parents=True, exist_ok=True)


def get_state_jurisdictions(conn, states: List[str]) -> List[str]:
    """Get jurisdiction IDs for specified states."""
    cursor = conn.cursor()
    
    # Build WHERE clause for state-level jurisdictions
    conditions = " OR ".join([f"id = 'ocd-jurisdiction/country:us/state:{state.lower()}/government'" for state in states])
    
    query = f"""
        SELECT id, name, classification
        FROM opencivicdata_jurisdiction
        WHERE classification = 'state' AND ({conditions})
    """
    
    cursor.execute(query)
    jurisdictions = cursor.fetchall()
    
    state_jurs = []
    for jur_id, name, classification in jurisdictions:
        state_jurs.append(jur_id)
        logger.info(f"Found jurisdiction: {name} ({jur_id})")
    
    return state_jurs


def export_contacts_officials(conn, jurisdiction_ids: List[str]):
    """Export officials/legislators (people) from openstates_people table."""
    logger.info("Exporting contacts_officials...")
    
    # Get state codes from jurisdiction IDs
    state_codes = [state.upper() for state in DEV_STATES]
    
    query = f"""
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
        WHERE state IN ({','.join(['%s'] * len(state_codes))})
        ORDER BY state, name
    """
    
    df = pd.read_sql(query, conn, params=state_codes)
    
    output_path = GOLD_DIR / "contacts_officials.parquet"
    df.to_parquet(output_path, index=False, engine='pyarrow', compression='snappy')
    
    logger.info(f"✅ Exported {len(df):,} officials to {output_path}")
    logger.info(f"   States: {df['state'].value_counts().to_dict()}")
    
    return df


def export_bills_bills(conn, jurisdiction_ids: List[str]):
    """Export bills from opencivicdata_bill table."""
    logger.info("Exporting bills_bills...")
    
    if not jurisdiction_ids:
        logger.warning("No jurisdiction IDs provided, skipping bills export")
        return None
    
    placeholders = ','.join(['%s'] * len(jurisdiction_ids))
    
    query = f"""
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
        WHERE j.id IN ({placeholders})
        ORDER BY j.name, s.identifier, b.identifier
        LIMIT 10000
    """
    
    df = pd.read_sql(query, conn, params=jurisdiction_ids)
    
    if len(df) == 0:
        logger.warning("No bills found for specified jurisdictions")
        return None
    
    output_path = GOLD_DIR / "bills_bills.parquet"
    df.to_parquet(output_path, index=False, engine='pyarrow', compression='snappy')
    
    logger.info(f"✅ Exported {len(df):,} bills to {output_path}")
    logger.info(f"   Jurisdictions: {df['jurisdiction_name'].value_counts().head(10).to_dict()}")
    
    return df


def export_bills_bill_actions(conn, jurisdiction_ids: List[str]):
    """Export bill actions from opencivicdata_billaction table."""
    logger.info("Exporting bills_bill_actions...")
    
    if not jurisdiction_ids:
        logger.warning("No jurisdiction IDs provided, skipping bill actions export")
        return None
    
    placeholders = ','.join(['%s'] * len(jurisdiction_ids))
    
    query = f"""
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
        WHERE j.id IN ({placeholders})
        ORDER BY ba.date DESC, ba.order
        LIMIT 50000
    """
    
    df = pd.read_sql(query, conn, params=jurisdiction_ids)
    
    if len(df) == 0:
        logger.warning("No bill actions found")
        return None
    
    output_path = GOLD_DIR / "bills_bill_actions.parquet"
    df.to_parquet(output_path, index=False, engine='pyarrow', compression='snappy')
    
    logger.info(f"✅ Exported {len(df):,} bill actions to {output_path}")
    
    return df


def export_bills_bill_sponsorships(conn, jurisdiction_ids: List[str]):
    """Export bill sponsorships from opencivicdata_billsponsorship table."""
    logger.info("Exporting bills_bill_sponsorships...")
    
    if not jurisdiction_ids:
        logger.warning("No jurisdiction IDs provided, skipping sponsorships export")
        return None
    
    placeholders = ','.join(['%s'] * len(jurisdiction_ids))
    
    query = f"""
        SELECT 
            bs.id as sponsorship_id,
            bs.bill_id,
            b.identifier as bill_number,
            bs.name as sponsor_name,
            bs.entity_type,
            bs.entity_id as sponsor_id,
            bs.primary_sponsor as is_primary,
            bs.classification,
            j.name as jurisdiction_name
        FROM opencivicdata_billsponsorship bs
        JOIN opencivicdata_bill b ON bs.bill_id = b.id
        JOIN opencivicdata_legislativesession s ON b.legislative_session_id = s.id
        JOIN opencivicdata_jurisdiction j ON s.jurisdiction_id = j.id
        WHERE j.id IN ({placeholders})
        ORDER BY b.identifier, bs.primary_sponsor DESC
        LIMIT 50000
    """
    
    df = pd.read_sql(query, conn, params=jurisdiction_ids)
    
    if len(df) == 0:
        logger.warning("No sponsorships found")
        return None
    
    output_path = GOLD_DIR / "bills_bill_sponsorships.parquet"
    df.to_parquet(output_path, index=False, engine='pyarrow', compression='snappy')
    
    logger.info(f"✅ Exported {len(df):,} sponsorships to {output_path}")
    
    return df


def export_events_events(conn, jurisdiction_ids: List[str]):
    """Export events/meetings from opencivicdata_event table."""
    logger.info("Exporting events_events...")
    
    if not jurisdiction_ids:
        logger.warning("No jurisdiction IDs provided, skipping events export")
        return None
    
    placeholders = ','.join(['%s'] * len(jurisdiction_ids))
    
    query = f"""
        SELECT 
            e.id as event_id,
            e.name as event_name,
            e.description,
            e.classification,
            e.start_date,
            e.end_date,
            e.all_day,
            e.status,
            e.location_name,
            e.location_url,
            j.name as jurisdiction_name,
            j.id as jurisdiction_ocd_id,
            e.created_at,
            e.updated_at
        FROM opencivicdata_event e
        JOIN opencivicdata_jurisdiction j ON e.jurisdiction_id = j.id
        WHERE j.id IN ({placeholders})
        ORDER BY e.start_date DESC
        LIMIT 10000
    """
    
    df = pd.read_sql(query, conn, params=jurisdiction_ids)
    
    if len(df) == 0:
        logger.warning("No events found")
        return None
    
    output_path = GOLD_DIR / "events_events.parquet"
    df.to_parquet(output_path, index=False, engine='pyarrow', compression='snappy')
    
    logger.info(f"✅ Exported {len(df):,} events to {output_path}")
    logger.info(f"   Jurisdictions: {df['jurisdiction_name'].value_counts().head(10).to_dict()}")
    
    return df


def export_events_event_participants(conn, jurisdiction_ids: List[str]):
    """Export event participants from opencivicdata_eventparticipant table."""
    logger.info("Exporting events_event_participants...")
    
    if not jurisdiction_ids:
        logger.warning("No jurisdiction IDs provided, skipping event participants export")
        return None
    
    placeholders = ','.join(['%s'] * len(jurisdiction_ids))
    
    query = f"""
        SELECT 
            ep.id as participant_id,
            ep.event_id,
            e.name as event_name,
            ep.name as participant_name,
            ep.entity_type,
            ep.entity_id,
            ep.note,
            j.name as jurisdiction_name
        FROM opencivicdata_eventparticipant ep
        JOIN opencivicdata_event e ON ep.event_id = e.id
        JOIN opencivicdata_jurisdiction j ON e.jurisdiction_id = j.id
        WHERE j.id IN ({placeholders})
        ORDER BY e.start_date DESC
        LIMIT 50000
    """
    
    df = pd.read_sql(query, conn, params=jurisdiction_ids)
    
    if len(df) == 0:
        logger.warning("No event participants found")
        return None
    
    output_path = GOLD_DIR / "events_event_participants.parquet"
    df.to_parquet(output_path, index=False, engine='pyarrow', compression='snappy')
    
    logger.info(f"✅ Exported {len(df):,} event participants to {output_path}")
    
    return df


def main():
    """Main export function."""
    logger.info("=" * 80)
    logger.info("EXPORTING OPENSTATES DATA TO GOLD DATASETS")
    logger.info("=" * 80)
    logger.info(f"Dev States: {', '.join(DEV_STATES)}")
    logger.info(f"Output Directory: {GOLD_DIR}")
    logger.info("")
    
    # Connect to database
    logger.info("Connecting to PostgreSQL...")
    conn = psycopg2.connect(DB_URL)
    
    try:
        # Get jurisdiction IDs for dev states
        jurisdiction_ids = get_state_jurisdictions(conn, DEV_STATES)
        logger.info(f"Found {len(jurisdiction_ids)} jurisdictions")
        logger.info("")
        
        # Export contacts (from openstates_people table - works with state codes)
        export_contacts_officials(conn, jurisdiction_ids)
        logger.info("")
        
        # Export bills data (using jurisdiction IDs)
        export_bills_bills(conn, jurisdiction_ids)
        logger.info("")
        
        export_bills_bill_actions(conn, jurisdiction_ids)
        logger.info("")
        
        export_bills_bill_sponsorships(conn, jurisdiction_ids)
        logger.info("")
        
        # Export events data (using jurisdiction IDs)
        export_events_events(conn, jurisdiction_ids)
        logger.info("")
        
        export_events_event_participants(conn, jurisdiction_ids)
        logger.info("")
        
        logger.info("=" * 80)
        logger.info("✅ EXPORT COMPLETE!")
        logger.info("=" * 80)
        logger.info(f"Gold datasets saved to: {GOLD_DIR}")
        logger.info("")
        logger.info("Exported files:")
        for file in sorted(GOLD_DIR.glob("*.parquet")):
            size_mb = file.stat().st_size / 1024 / 1024
            logger.info(f"  {file.name}: {size_mb:.2f} MB")
        
    finally:
        conn.close()


if __name__ == "__main__":
    main()
