"""
Migration script to load data from Gold parquet files into Neon Postgres
Optimized for HuggingFace deployment - loads aggregate and search data only
"""
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional
import psycopg2
from psycopg2.extras import execute_values
import pandas as pd
from dotenv import load_dotenv
from loguru import logger

# Load environment variables
load_dotenv()

# Database connection
NEON_DATABASE_URL = os.getenv('NEON_DATABASE_URL')
if not NEON_DATABASE_URL:
    raise ValueError("NEON_DATABASE_URL not set in environment")

# Paths
GOLD_DIR = Path("data/gold")


def parse_yyyymm_date(yyyymm):
    """Convert YYYYMM format (e.g., '195504') to date object"""
    if pd.isna(yyyymm) or not yyyymm:
        return None
    try:
        yyyymm_str = str(int(yyyymm))  # Convert to string, remove decimals
        if len(yyyymm_str) == 6:
            year = int(yyyymm_str[:4])
            month = int(yyyymm_str[4:6])
            return datetime(year, month, 1).date()
    except (ValueError, TypeError):
        pass
    return None


def clean_numeric(value):
    """Convert pandas NaN/None to None, keep valid numbers"""
    if pd.isna(value) or value is None:
        return None
    try:
        # Convert to float first, then check if it's a valid number
        num = float(value)
        if pd.isna(num):
            return None
        return num
    except (ValueError, TypeError):
        return None


def get_db_connection():
    """Get database connection"""
    return psycopg2.connect(NEON_DATABASE_URL)


def execute_schema(conn):
    """Execute schema.sql to create tables"""
    schema_path = Path("neon/schema.sql")
    if not schema_path.exists():
        logger.error(f"Schema file not found: {schema_path}")
        return False
    
    logger.info("📋 Creating database schema...")
    with open(schema_path, 'r') as f:
        schema_sql = f.read()
    
    try:
        with conn.cursor() as cur:
            cur.execute(schema_sql)
        conn.commit()
        logger.success("✅ Schema created successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Schema creation failed: {e}")
        conn.rollback()
        return False


def load_stats_aggregates(conn):
    """
    Load pre-computed statistics aggregates
    This is the most critical table for fast dashboard loading
    """
    logger.info("📊 Loading statistics aggregates...")
    
    try:
        cursor = conn.cursor()
        
        # Calculate national stats
        national_stats = calculate_national_stats()
        insert_stat(cursor, **national_stats)
        
        # Calculate state-level stats for each state with data
        states_dir = GOLD_DIR / "states"
        if states_dir.exists():
            for state_dir in states_dir.iterdir():
                if state_dir.is_dir():
                    state = state_dir.name
                    logger.info(f"  Processing state: {state}")
                    state_stats = calculate_state_stats(state)
                    if state_stats:
                        insert_stat(cursor, **state_stats)
        
        conn.commit()
        
        # Get count
        cursor.execute("SELECT COUNT(*) FROM stats_aggregates")
        count = cursor.fetchone()[0]
        logger.success(f"✅ Loaded {count} statistics aggregates")
        
        record_sync(conn, 'stats_aggregates', count)
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to load stats aggregates: {e}")
        conn.rollback()
        return False


def calculate_national_stats():
    """Calculate national-level statistics"""
    stats = {
        'level': 'national',
        'state': None,
        'county': None,
        'city': None,
        'jurisdictions_count': 0,
        'school_districts_count': 0,
        'nonprofits_count': 0,
        'events_count': 0,
        'bills_count': 0,
        'contacts_count': 0,
        'total_revenue': 0,
        'total_assets': 0,
    }
    
    # Count jurisdictions
    for pattern in ['jurisdictions_cities.parquet', 'jurisdictions_counties.parquet', 
                   'jurisdictions_townships.parquet']:
        file_path = GOLD_DIR / 'reference' / pattern
        if file_path.exists():
            df = pd.read_parquet(file_path)
            stats['jurisdictions_count'] += len(df)
    
    # Count school districts
    sd_file = GOLD_DIR / 'reference' / 'jurisdictions_school_districts.parquet'
    if sd_file.exists():
        df = pd.read_parquet(sd_file)
        stats['school_districts_count'] = len(df)
    
    # Count nonprofits and sum financials
    states_dir = GOLD_DIR / "states"
    if states_dir.exists():
        for state_dir in states_dir.iterdir():
            if state_dir.is_dir():
                np_file = state_dir / "nonprofits_organizations.parquet"
                if np_file.exists():
                    df = pd.read_parquet(np_file)
                    stats['nonprofits_count'] += len(df)
                    
                    # Sum revenue/assets if available
                    if 'REVENUE' in df.columns:
                        stats['total_revenue'] += df['REVENUE'].fillna(0).sum()
                    if 'ASSETS' in df.columns:
                        stats['total_assets'] += df['ASSETS'].fillna(0).sum()
                
                # Count events
                events_file = state_dir / "events.parquet"
                if events_file.exists():
                    df = pd.read_parquet(events_file)
                    stats['events_count'] += len(df)
                
                # Count contacts
                contacts_file = state_dir / "contacts_nonprofit_officers.parquet"
                if contacts_file.exists():
                    df = pd.read_parquet(contacts_file)
                    stats['contacts_count'] += len(df)
    
    return stats


def calculate_state_stats(state: str):
    """Calculate state-level statistics"""
    stats = {
        'level': 'state',
        'state': state,
        'county': None,
        'city': None,
        'jurisdictions_count': 0,
        'school_districts_count': 0,
        'nonprofits_count': 0,
        'events_count': 0,
        'bills_count': 0,
        'contacts_count': 0,
        'total_revenue': 0,
        'total_assets': 0,
    }
    
    # Count jurisdictions in this state
    for pattern in ['jurisdictions_cities.parquet', 'jurisdictions_counties.parquet', 
                   'jurisdictions_townships.parquet']:
        file_path = GOLD_DIR / 'reference' / pattern
        if file_path.exists():
            df = pd.read_parquet(file_path)
            state_col = 'state' if 'state' in df.columns else 'STATE'
            if state_col in df.columns:
                state_df = df[df[state_col].str.upper() == state.upper()]
                stats['jurisdictions_count'] += len(state_df)
    
    # Count school districts
    sd_file = GOLD_DIR / 'reference' / 'jurisdictions_school_districts.parquet'
    if sd_file.exists():
        df = pd.read_parquet(sd_file)
        state_col = 'state' if 'state' in df.columns else 'STATE'
        if state_col in df.columns:
            state_df = df[df[state_col].str.upper() == state.upper()]
            stats['school_districts_count'] = len(state_df)
    
    # State-specific data
    state_dir = GOLD_DIR / "states" / state
    
    # Nonprofits
    np_file = state_dir / "nonprofits_organizations.parquet"
    if np_file.exists():
        df = pd.read_parquet(np_file)
        stats['nonprofits_count'] = len(df)
        
        if 'REVENUE' in df.columns:
            stats['total_revenue'] = int(df['REVENUE'].fillna(0).sum())
        if 'ASSETS' in df.columns:
            stats['total_assets'] = int(df['ASSETS'].fillna(0).sum())
    
    # Events
    events_file = state_dir / "events.parquet"
    if events_file.exists():
        df = pd.read_parquet(events_file)
        stats['events_count'] = len(df)
    
    # Contacts
    contacts_file = state_dir / "contacts_nonprofit_officers.parquet"
    if contacts_file.exists():
        df = pd.read_parquet(contacts_file)
        stats['contacts_count'] = len(df)
    
    return stats if stats['nonprofits_count'] > 0 else None


def insert_stat(cursor, level, state, county, city, **metrics):
    """Insert statistics record"""
    cursor.execute("""
        INSERT INTO stats_aggregates 
        (level, state, county, city, jurisdictions_count, school_districts_count,
         nonprofits_count, events_count, bills_count, contacts_count,
         total_revenue, total_assets, last_updated)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (level, state, county, city) 
        DO UPDATE SET
            jurisdictions_count = EXCLUDED.jurisdictions_count,
            school_districts_count = EXCLUDED.school_districts_count,
            nonprofits_count = EXCLUDED.nonprofits_count,
            events_count = EXCLUDED.events_count,
            bills_count = EXCLUDED.bills_count,
            contacts_count = EXCLUDED.contacts_count,
            total_revenue = EXCLUDED.total_revenue,
            total_assets = EXCLUDED.total_assets,
            last_updated = EXCLUDED.last_updated
    """, (
        level, state, county, city,
        metrics.get('jurisdictions_count', 0),
        metrics.get('school_districts_count', 0),
        metrics.get('nonprofits_count', 0),
        metrics.get('events_count', 0),
        metrics.get('bills_count', 0),
        metrics.get('contacts_count', 0),
        metrics.get('total_revenue', 0),
        metrics.get('total_assets', 0),
        datetime.now()
    ))


def load_nonprofits_search(conn, limit_states: Optional[list] = None):
    """
    Load nonprofits into search table
    Args:
        limit_states: List of state codes to load (e.g., ['MA', 'CA']) or None for all
    """
    logger.info("🏢 Loading nonprofits search data...")
    
    states_to_load = limit_states or []
    
    # If no limit, scan all states
    if not limit_states:
        states_dir = GOLD_DIR / "states"
        if states_dir.exists():
            states_to_load = [d.name for d in states_dir.iterdir() if d.is_dir()]
    
    total_loaded = 0
    cursor = conn.cursor()
    
    for state in states_to_load:
        np_file = GOLD_DIR / "states" / state / "nonprofits_organizations.parquet"
        if not np_file.exists():
            logger.warning(f"  No nonprofits file for {state}")
            continue
        
        logger.info(f"  Loading nonprofits from {state}...")
        df = pd.read_parquet(np_file)
        
        # Prepare data for insertion (use lowercase column names)
        # Filter out rows with null EIN
        df_valid = df[df['ein'].notna()].copy()
        
        records = []
        for _, row in df_valid.iterrows():
            # Convert ruling date from YYYYMM to proper date
            ruling_date = parse_yyyymm_date(row.get('ruling'))
            
            record = (
                row.get('ein'),
                row.get('name', ''),
                row.get('street', ''),
                row.get('city', ''),
                state,  # Use the state variable directly
                row.get('zip', ''),
                '',  # county - not in source data
                row.get('ntee_cd', ''),
                None,  # ntee_description - join later
                row.get('subsection', ''),
                row.get('affiliation', ''),
                row.get('classification', ''),
                clean_numeric(row.get('form_990_total_revenue')),  # Clean numeric fields
                clean_numeric(row.get('form_990_total_assets')),
                clean_numeric(row.get('income_amt')),
                ruling_date,  # Converted ruling date
                row.get('foundation', ''),
                row.get('pf_filing_req_cd', ''),
                clean_numeric(row.get('acct_pd')),
                row.get('asset_cd', ''),
                row.get('income_cd', ''),
                row.get('filing_req_cd', ''),
                row.get('status', ''),  # Use 'status' for exempt_org_status_cd
                clean_numeric(row.get('tax_period')),
                clean_numeric(row.get('asset_amt')),
                clean_numeric(row.get('income_amt')),
                clean_numeric(row.get('revenue_amt')),  # Use revenue_amt
                'irs_bmf',
                datetime.now()
            )
            records.append(record)
        
        # Batch insert
        if records:
            execute_values(cursor, """
                INSERT INTO nonprofits_search 
                (ein, name, street_address, city, state, zip_code, county,
                 ntee_code, ntee_description, subsection_code, affiliation_code, classification_code,
                 revenue, assets, income, ruling_date, foundation_code, pf_filing_requirement_code,
                 accounting_period, asset_code, income_code, filing_requirement_code,
                 exempt_organization_status_code, tax_period, asset_amount, income_amount,
                 form_990_revenue_amount, source, last_updated)
                VALUES %s
                ON CONFLICT (ein) DO UPDATE SET
                    name = EXCLUDED.name,
                    city = EXCLUDED.city,
                    state = EXCLUDED.state,
                    revenue = EXCLUDED.revenue,
                    assets = EXCLUDED.assets,
                    last_updated = EXCLUDED.last_updated
            """, records)
            
            total_loaded += len(records)
            logger.info(f"    Loaded {len(records)} nonprofits from {state}")
    
    conn.commit()
    logger.success(f"✅ Loaded {total_loaded} nonprofits into search table")
    record_sync(conn, 'nonprofits_search', total_loaded)
    return True


def load_reference_data(conn):
    """Load reference tables (causes, NTEE codes)"""
    logger.info("📚 Loading reference data...")
    
    cursor = conn.cursor()
    total = 0
    
    # Load NTEE codes
    ntee_file = GOLD_DIR / "reference" / "causes_ntee_codes.parquet"
    if ntee_file.exists():
        df = pd.read_parquet(ntee_file)
        # Use actual column names: ntee_code, description, parent_code
        records = [(row['ntee_code'], row.get('description', ''), None, None, 'irs', datetime.now()) 
                   for _, row in df.iterrows()]
        
        execute_values(cursor, """
            INSERT INTO reference_ntee_codes (code, description, category, subcategory, source, last_updated)
            VALUES %s
            ON CONFLICT (code) DO UPDATE SET description = EXCLUDED.description
        """, records)
        
        total += len(records)
        logger.info(f"  Loaded {len(records)} NTEE codes")
    
    # Load causes
    causes_file = GOLD_DIR / "reference" / "causes_everyorg_causes.parquet"
    if causes_file.exists():
        df = pd.read_parquet(causes_file)
        # Use actual column names: cause_id, cause_name, description
        records = [(row['cause_id'], row['cause_name'], row.get('description'), None, 'everyorg', datetime.now())
                   for _, row in df.iterrows()]
        
        execute_values(cursor, """
            INSERT INTO reference_causes (cause_slug, cause_name, description, parent_category, source, last_updated)
            VALUES %s
            ON CONFLICT (cause_slug) DO UPDATE SET cause_name = EXCLUDED.cause_name
        """, records)
        
        total += len(records)
        logger.info(f"  Loaded {len(records)} causes")
    
    conn.commit()
    logger.success(f"✅ Loaded {total} reference records")
    return True


def record_sync(conn, table_name: str, records_synced: int, status: str = 'success', error: Optional[str] = None):
    """Record sync status"""
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO last_sync (table_name, last_sync_time, records_synced, sync_status, error_message)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (table_name) DO UPDATE SET
            last_sync_time = EXCLUDED.last_sync_time,
            records_synced = EXCLUDED.records_synced,
            sync_status = EXCLUDED.sync_status,
            error_message = EXCLUDED.error_message
    """, (table_name, datetime.now(), records_synced, status, error))
    conn.commit()


def main():
    """Main migration function"""
    logger.info("🚀 Starting Neon migration...")
    logger.info(f"📁 Gold directory: {GOLD_DIR.absolute()}")
    
    try:
        conn = get_db_connection()
        logger.success("✅ Connected to Neon database")
        
        # Step 1: Create schema
        if not execute_schema(conn):
            return 1
        
        # Step 2: Load aggregates (critical for dashboard)
        if not load_stats_aggregates(conn):
            return 1
        
        # Step 3: Load reference data
        if not load_reference_data(conn):
            return 1
        
        # Step 4: Load nonprofit search data (start with MA as example)
        logger.info("⚠️  Loading only MA nonprofits (full load would be 3M+ records)")
        logger.info("   To load all states, modify limit_states parameter")
        if not load_nonprofits_search(conn, limit_states=['MA']):
            return 1
        
        # Show summary
        cursor = conn.cursor()
        cursor.execute("SELECT table_name, records_synced, last_sync_time FROM last_sync ORDER BY table_name")
        logger.info("\n📊 Migration Summary:")
        logger.info("=" * 60)
        for row in cursor.fetchall():
            logger.info(f"  {row[0]:<30} {row[1]:>10,} records  ({row[2]})")
        logger.info("=" * 60)
        
        conn.close()
        logger.success("\n🎉 Migration completed successfully!")
        logger.info("\n💡 Next steps:")
        logger.info("  1. Test queries: SELECT * FROM stats_aggregates LIMIT 5;")
        logger.info("  2. Update API routes to use Neon")
        logger.info("  3. Add NEON_DATABASE_URL to HuggingFace Secrets")
        
        return 0
        
    except Exception as e:
        logger.error(f"\n❌ Migration failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return 1


if __name__ == "__main__":
    sys.exit(main())
