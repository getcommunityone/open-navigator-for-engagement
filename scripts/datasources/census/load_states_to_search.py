#!/usr/bin/env python3
"""
Load US States into jurisdictions_search table.

This script populates jurisdictions_search with state-level records,
enabling state matching in the master data management system.

Data source: Census Bureau FIPS codes + jurisdictions_wikidata
"""

import psycopg2
from psycopg2.extras import execute_values

# All 50 states + DC + PR with FIPS codes
US_STATES = [
    ('AL', 'Alabama', '01'),
    ('AK', 'Alaska', '02'),
    ('AZ', 'Arizona', '04'),
    ('AR', 'Arkansas', '05'),
    ('CA', 'California', '06'),
    ('CO', 'Colorado', '08'),
    ('CT', 'Connecticut', '09'),
    ('DE', 'Delaware', '10'),
    ('DC', 'District of Columbia', '11'),
    ('FL', 'Florida', '12'),
    ('GA', 'Georgia', '13'),
    ('HI', 'Hawaii', '15'),
    ('ID', 'Idaho', '16'),
    ('IL', 'Illinois', '17'),
    ('IN', 'Indiana', '18'),
    ('IA', 'Iowa', '19'),
    ('KS', 'Kansas', '20'),
    ('KY', 'Kentucky', '21'),
    ('LA', 'Louisiana', '22'),
    ('ME', 'Maine', '23'),
    ('MD', 'Maryland', '24'),
    ('MA', 'Massachusetts', '25'),
    ('MI', 'Michigan', '26'),
    ('MN', 'Minnesota', '27'),
    ('MS', 'Mississippi', '28'),
    ('MO', 'Missouri', '29'),
    ('MT', 'Montana', '30'),
    ('NE', 'Nebraska', '31'),
    ('NV', 'Nevada', '32'),
    ('NH', 'New Hampshire', '33'),
    ('NJ', 'New Jersey', '34'),
    ('NM', 'New Mexico', '35'),
    ('NY', 'New York', '36'),
    ('NC', 'North Carolina', '37'),
    ('ND', 'North Dakota', '38'),
    ('OH', 'Ohio', '39'),
    ('OK', 'Oklahoma', '40'),
    ('OR', 'Oregon', '41'),
    ('PA', 'Pennsylvania', '42'),
    ('PR', 'Puerto Rico', '72'),
    ('RI', 'Rhode Island', '44'),
    ('SC', 'South Carolina', '45'),
    ('SD', 'South Dakota', '46'),
    ('TN', 'Tennessee', '47'),
    ('TX', 'Texas', '48'),
    ('UT', 'Utah', '49'),
    ('VT', 'Vermont', '50'),
    ('VA', 'Virginia', '51'),
    ('WA', 'Washington', '53'),
    ('WV', 'West Virginia', '54'),
    ('WI', 'Wisconsin', '55'),
    ('WY', 'Wyoming', '56'),
]


def get_connection():
    """Create database connection."""
    return psycopg2.connect(
        host="localhost",
        port=5433,
        database="open_navigator",
        user="postgres",
        password="password"
    )


def load_states_to_jurisdictions_search():
    """Load all US states into jurisdictions_search table."""
    conn = get_connection()
    cur = conn.cursor()
    
    print(f"Loading {len(US_STATES)} states into jurisdictions_search...")
    
    # Prepare records for bulk insert
    records = []
    for state_code, state_name, fips_code in US_STATES:
        # GEOID for states is the 2-digit FIPS code
        geoid = fips_code
        
        records.append((
            state_name,           # name
            'state',              # type
            state_code,           # state_code
            state_name,           # state (same as name for states)
            None,                 # county (NULL for states)
            geoid,                # geoid (2-digit FIPS)
            fips_code,            # fips_code
            None,                 # population (can enrich later)
            None,                 # area_sq_miles (can enrich later)
            'census_fips'         # source
        ))
    
    # Insert with ON CONFLICT to handle duplicates
    insert_query = """
        INSERT INTO jurisdictions_search (
            name,
            type,
            state_code,
            state,
            county,
            geoid,
            fips_code,
            population,
            area_sq_miles,
            source
        ) VALUES %s
        ON CONFLICT (name, type, state_code, county) DO UPDATE
        SET geoid = EXCLUDED.geoid,
            fips_code = EXCLUDED.fips_code,
            source = EXCLUDED.source
        RETURNING id
    """
    
    execute_values(cur, insert_query, records, page_size=1000)
    inserted_ids = cur.fetchall()
    
    conn.commit()
    
    print(f"✅ Successfully loaded {len(inserted_ids)} states")
    
    # Verify insertion
    cur.execute("""
        SELECT state_code, name, geoid, fips_code
        FROM jurisdictions_search
        WHERE type = 'state'
        ORDER BY state_code
    """)
    
    states = cur.fetchall()
    print(f"\nVerification: {len(states)} states in jurisdictions_search:")
    for state_code, name, geoid, fips in states[:5]:
        print(f"  {state_code}: {name} (GEOID: {geoid}, FIPS: {fips})")
    if len(states) > 5:
        print(f"  ... and {len(states) - 5} more")
    
    cur.close()
    conn.close()


if __name__ == "__main__":
    load_states_to_jurisdictions_search()
