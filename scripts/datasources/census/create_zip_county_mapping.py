#!/usr/bin/env python3
"""
Create ZIP code to county mapping table using HUD USPS ZIP Code Crosswalk data

Data source: HUD USPS ZIP Code Crosswalk Files
https://www.huduser.gov/portal/datasets/usps_crosswalk.html

For each ZIP code, we store:
- Primary county (highest residential ratio)
- All counties it spans (for multi-county ZIP codes)
"""
import psycopg2
from psycopg2.extras import execute_values
import pandas as pd
import requests
from io import StringIO
from loguru import logger
import sys

# Database connection
DATABASE_URL = 'postgresql://postgres:password@localhost:5433/open_navigator'

# HUD ZIP-County crosswalk (2024 Q1 - latest available)
# Note: This is a simplified approach. Full implementation would download from HUD.
# For now, we'll create from Census Bureau's ZIP-County relationship file
ZCTA_COUNTY_URL = "https://www2.census.gov/geo/docs/maps-data/data/rel2020/zcta520/tab20_zcta520_county20_natl.txt"


def create_zip_county_table():
    """Create the zip_county_mapping table"""
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    logger.info("📋 Creating zip_county_mapping table...")
    
    cur.execute("""
        DROP TABLE IF EXISTS zip_county_mapping CASCADE;
        
        CREATE TABLE zip_county_mapping (
            zip_code VARCHAR(10) NOT NULL,
            state_fips VARCHAR(2) NOT NULL,
            county_fips VARCHAR(3) NOT NULL,
            state_abbr VARCHAR(2),
            county_name VARCHAR(255),
            residential_ratio NUMERIC(5, 4) DEFAULT 1.0,
            is_primary BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT NOW(),
            PRIMARY KEY (zip_code, state_fips, county_fips)
        );
        
        CREATE INDEX idx_zip_county_zip ON zip_county_mapping(zip_code);
        CREATE INDEX idx_zip_county_state ON zip_county_mapping(state_abbr);
        CREATE INDEX idx_zip_county_primary ON zip_county_mapping(zip_code, is_primary);
    """)
    
    conn.commit()
    logger.info("✅ Table created")
    
    conn.close()


def load_census_zcta_county_data():
    """
    Load Census Bureau ZCTA to County relationship file
    This gives us ZIP Code Tabulation Areas (ZCTA) to county mappings
    """
    logger.info(f"📥 Downloading Census ZCTA-County data from {ZCTA_COUNTY_URL}")
    
    try:
        response = requests.get(ZCTA_COUNTY_URL, timeout=60)
        response.raise_for_status()
        
        # Parse the tab-delimited file
        df = pd.read_csv(StringIO(response.text), sep='|', dtype=str)
        
        logger.info(f"📊 Loaded {len(df)} ZCTA-County relationships")
        logger.info(f"Columns: {list(df.columns)}")
        
        return df
        
    except Exception as e:
        logger.error(f"❌ Failed to download Census data: {e}")
        logger.info("💡 Using simplified state-based mapping as fallback...")
        return None


def create_simplified_mapping():
    """
    Create a simplified ZIP-county mapping using state + county data we already have
    This won't be perfect but will cover most cases
    """
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    logger.info("🔧 Creating simplified ZIP-county mapping from existing data...")
    
    # Get all unique ZIP codes from nonprofits data
    states_to_process = ['AL', 'GA', 'MA', 'WA']
    
    zip_mappings = []
    
    for state in states_to_process:
        logger.info(f"Processing {state}...")
        
        # Load nonprofits locations to get ZIP codes
        try:
            import pandas as pd
            df = pd.read_parquet(f'data/gold/states/{state}/nonprofits_locations.parquet')
            
            # Get unique ZIP codes (5-digit only)
            df['zip5'] = df['zip_code'].str[:5]
            unique_zips = df['zip5'].dropna().unique()
            
            logger.info(f"  Found {len(unique_zips)} unique ZIP codes in {state}")
            
            # Get counties in this state
            cur.execute("""
                SELECT name, geoid 
                FROM jurisdictions_search 
                WHERE state = %s AND type = 'county'
            """, (state,))
            
            counties = cur.fetchall()
            logger.info(f"  Found {len(counties)} counties in {state}")
            
            # For simplicity: assign each ZIP to all counties in the state
            # with equal weight (will be refined later with actual data)
            # This is a placeholder - real implementation would use spatial join
            
            # Get state FIPS from first county GEOID (first 2 digits)
            if counties:
                state_fips = counties[0][1][:2] if counties[0][1] else '01'
                
                # For now, we'll create a basic mapping
                # In production, you'd use a proper ZIP-County crosswalk file
                logger.info(f"  Using state FIPS: {state_fips}")
            
        except Exception as e:
            logger.warning(f"  Error processing {state}: {e}")
            continue
    
    logger.info("⚠️  Simplified mapping not sufficient - need proper ZIP-County crosswalk")
    logger.info("💡 Recommend downloading HUD USPS ZIP Code Crosswalk file")
    
    conn.close()
    return zip_mappings


def populate_from_census_data(df):
    """Populate zip_county_mapping from Census ZCTA data"""
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    logger.info("📊 Processing Census ZCTA-County data...")
    
    # Use correct FIPS to state abbreviation mapping
    # Source: https://www.census.gov/library/reference/code-lists/ansi.html
    state_mapping = {
        '01': 'AL', '02': 'AK', '04': 'AZ', '05': 'AR', '06': 'CA',
        '08': 'CO', '09': 'CT', '10': 'DE', '11': 'DC', '12': 'FL',
        '13': 'GA', '15': 'HI', '16': 'ID', '17': 'IL', '18': 'IN',
        '19': 'IA', '20': 'KS', '21': 'KY', '22': 'LA', '23': 'ME',
        '24': 'MD', '25': 'MA', '26': 'MI', '27': 'MN', '28': 'MS',
        '29': 'MO', '30': 'MT', '31': 'NE', '32': 'NV', '33': 'NH',
        '34': 'NJ', '35': 'NM', '36': 'NY', '37': 'NC', '38': 'ND',
        '39': 'OH', '40': 'OK', '41': 'OR', '42': 'PA', '44': 'RI',
        '45': 'SC', '46': 'SD', '47': 'TN', '48': 'TX', '49': 'UT',
        '50': 'VT', '51': 'VA', '53': 'WA', '54': 'WV', '55': 'WI',
        '56': 'WY', '72': 'PR'
    }
    
    logger.info(f"Using official FIPS-to-state mapping ({len(state_mapping)} states)")
    
    # Process the Census data
    # Expected columns: GEOID_ZCTA5_20, GEOID_COUNTY_20, ...
    records = []
    
    for _, row in df.iterrows():
        zcta = row.get('GEOID_ZCTA5_20', '')
        county_geoid = row.get('GEOID_COUNTY_20', '')
        
        if not zcta or not county_geoid or len(county_geoid) < 5:
            continue
        
        state_fips = county_geoid[:2]
        county_fips = county_geoid[2:5]
        
        state_abbr = state_mapping.get(state_fips)
        
        if not state_abbr:
            continue
        
        # Get county name from Census data or construct from GEOID
        cur.execute("""
            SELECT name FROM jurisdictions_search
            WHERE type = 'county' AND geoid = %s
        """, (county_geoid,))
        
        result = cur.fetchone()
        county_name = result[0] if result else row.get('NAMELSAD_COUNTY_20', None)
        
        records.append((
            zcta,
            state_fips,
            county_fips,
            state_abbr,
            county_name,
            1.0,  # residential_ratio - default to 1.0
            True  # is_primary - will update later for multi-county ZIPs
        ))
    
    if records:
        logger.info(f"💾 Inserting {len(records)} ZIP-county mappings...")
        
        insert_query = """
            INSERT INTO zip_county_mapping 
            (zip_code, state_fips, county_fips, state_abbr, county_name, residential_ratio, is_primary)
            VALUES %s
            ON CONFLICT (zip_code, state_fips, county_fips) DO NOTHING
        """
        
        execute_values(cur, insert_query, records)
        conn.commit()
        
        logger.info(f"✅ Inserted {len(records)} mappings")
    
    conn.close()


def mark_primary_counties():
    """
    For ZIP codes spanning multiple counties, mark the one with highest
    residential ratio as primary
    """
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    logger.info("🎯 Marking primary counties for multi-county ZIP codes...")
    
    # Reset all to non-primary first
    cur.execute("UPDATE zip_county_mapping SET is_primary = FALSE")
    
    # Mark primary (highest residential ratio) for each ZIP
    cur.execute("""
        WITH ranked AS (
            SELECT zip_code, state_fips, county_fips,
                   ROW_NUMBER() OVER (
                       PARTITION BY zip_code 
                       ORDER BY residential_ratio DESC, county_fips
                   ) as rank
            FROM zip_county_mapping
        )
        UPDATE zip_county_mapping z
        SET is_primary = TRUE
        FROM ranked r
        WHERE z.zip_code = r.zip_code
          AND z.state_fips = r.state_fips
          AND z.county_fips = r.county_fips
          AND r.rank = 1
    """)
    
    conn.commit()
    logger.info(f"✅ Marked primary counties")
    
    # Show stats
    cur.execute("""
        SELECT 
            COUNT(DISTINCT zip_code) as total_zips,
            COUNT(DISTINCT CASE WHEN is_primary THEN zip_code END) as zips_with_primary,
            COUNT(*) as total_mappings
        FROM zip_county_mapping
    """)
    
    total_zips, zips_primary, total_mappings = cur.fetchone()
    logger.info(f"📊 Stats:")
    logger.info(f"  Total ZIP codes: {total_zips:,}")
    logger.info(f"  ZIP codes with primary county: {zips_primary:,}")
    logger.info(f"  Total ZIP-county mappings: {total_mappings:,}")
    logger.info(f"  Multi-county ZIPs: {total_mappings - total_zips:,}")
    
    conn.close()


if __name__ == '__main__':
    logger.info("🗺️  Creating ZIP Code to County Mapping")
    logger.info("=" * 60)
    
    # Step 1: Create table
    create_zip_county_table()
    
    # Step 2: Load Census data
    census_df = load_census_zcta_county_data()
    
    if census_df is not None:
        # Step 3: Populate from Census data
        populate_from_census_data(census_df)
        
        # Step 4: Mark primary counties
        mark_primary_counties()
        
        logger.info("\n✅ ZIP-County mapping complete!")
    else:
        logger.warning("\n⚠️  Could not load Census data")
        logger.info("Alternative: Use HUD USPS ZIP Code Crosswalk file")
        logger.info("Download from: https://www.huduser.gov/portal/datasets/usps_crosswalk.html")
