#!/usr/bin/env python3
"""
Load GSA .gov Domain Data into jurisdictions_details_search

This is an ENRICHMENT LOAD that adds official .gov domain information
from the GSA (General Services Administration) registry to existing
jurisdiction records.

Data Source: https://github.com/cisagov/dotgov-data

Columns Added:
- gov_domains: JSONB array of all .gov domains for jurisdiction
- security_contact_email: Official security contact
- gsa_organization_name: Official organization name
- gsa_domain_type: GSA classification (City, County, State, etc.)

Type: UPDATE/ENRICHMENT load (modifies existing records)
"""
import asyncio
import csv
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
from collections import defaultdict

import httpx
import psycopg2
from psycopg2.extras import execute_batch, RealDictCursor
from loguru import logger


# Database configuration
DB_CONFIG = {
    "host": "localhost",
    "port": 5433,
    "database": "open_navigator",
    "user": "postgres",
    "password": "password"
}

# GSA maintains official .gov domain list on GitHub
GSA_DOMAIN_URL = "https://raw.githubusercontent.com/cisagov/dotgov-data/main/current-full.csv"
CACHE_DIR = Path("data/cache/gsa")


def normalize_name(name: str) -> str:
    """
    Normalize jurisdiction names for matching.
    
    Examples:
        "Town of Abington" -> "abington"
        "City of Boston" -> "boston"
        "King County" -> "king county"
    """
    if not name:
        return ""
    
    # Remove common prefixes
    prefixes = ["city of ", "town of ", "village of ", "township of ", "borough of "]
    name_lower = name.lower().strip()
    
    for prefix in prefixes:
        if name_lower.startswith(prefix):
            name_lower = name_lower[len(prefix):]
    
    return name_lower.strip()


def extract_name_from_domain(domain: str, state_code: str) -> Optional[str]:
    """
    Extract city/county name from .gov domain.
    
    Examples:
        "bostonma.gov" + "MA" -> "boston"
        "boston.gov" -> "boston"
        "cityofbostonma.gov" -> "boston"
        "kingcountywa.gov" + "WA" -> "king county"
    """
    if not domain:
        return None
    
    # Remove .gov extension
    name = domain.replace('.gov', '').lower()
    
    # Remove state code suffix if present
    if state_code:
        state_lower = state_code.lower()
        if name.endswith(state_lower):
            name = name[:-len(state_lower)]
    
    # Remove common prefixes
    prefixes = ['cityof', 'townof', 'countyof', 'villageof']
    for prefix in prefixes:
        if name.startswith(prefix):
            name = name[len(prefix):]
    
    # Remove common suffixes
    suffixes = ['county', 'city', 'town', 'village']
    for suffix in suffixes:
        if name.endswith(suffix) and len(name) > len(suffix):
            # Check if it's like "kingcounty" -> "king county"
            if suffix == 'county' and not name.endswith(' county'):
                name = name[:-len(suffix)] + ' ' + suffix
                break
            elif suffix in ['city', 'town', 'village']:
                name = name[:-len(suffix)]
    
    # Clean up
    name = name.strip().replace('-', ' ').replace('_', ' ')
    
    return name if name else None


async def download_gsa_domains() -> Path:
    """
    Download latest .gov domain list from GSA.
    
    Returns:
        Path to cached CSV file
    """
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_file = CACHE_DIR / f"dotgov_domains_{datetime.now().strftime('%Y%m%d')}.csv"
    
    # Use cached if recent (< 1 day old)
    if cache_file.exists():
        age_hours = (datetime.now().timestamp() - cache_file.stat().st_mtime) / 3600
        if age_hours < 24:
            logger.info(f"Using cached GSA domain list (age: {age_hours:.1f} hours)")
            return cache_file
    
    logger.info("Downloading latest .gov domain list from GSA...")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(GSA_DOMAIN_URL)
        response.raise_for_status()
        
        cache_file.write_bytes(response.content)
        logger.success(f"Downloaded {len(response.content):,} bytes to {cache_file}")
    
    return cache_file


def parse_gsa_csv(csv_path: Path, states: Optional[List[str]] = None) -> Dict[str, List[Dict[str, Any]]]:
    """
    Parse GSA CSV and group domains by jurisdiction.
    
    Args:
        csv_path: Path to GSA CSV file
        states: Optional list of state codes to filter (e.g., ['AL', 'MA'])
    
    Returns:
        Dictionary mapping (state_code, city_name) -> list of domain records
    """
    logger.info(f"Parsing GSA domain list from {csv_path}")
    
    jurisdiction_domains = defaultdict(list)
    total_rows = 0
    filtered_rows = 0
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            total_rows += 1
            
            domain_name = row.get('Domain name', '').strip()
            domain_type = row.get('Domain type', '').strip()
            org_name = row.get('Organization name', '').strip()
            sub_org = row.get('Suborganization name', '').strip()
            city = row.get('City', '').strip()
            state = row.get('State', '').strip()
            security_email = row.get('Security contact email', '').strip()
            
            # Filter by state if specified
            if states and state not in states:
                continue
            
            # Only process local government domains
            local_types = ['City', 'County', 'Township', 'Special District', 'School District']
            if domain_type not in local_types:
                continue
            
            filtered_rows += 1
            
            # Normalize city/county name for matching
            normalized_city = normalize_name(city)
            normalized_org = normalize_name(org_name)
            
            # Try multiple matching strategies
            match_keys = []
            
            if domain_type == 'County':
                # For counties: match by county name + state
                county_name = normalized_org if 'county' in normalized_org else normalized_city
                match_keys.append((state, county_name, 'county'))
            else:
                # For cities: match by city name + state
                match_keys.append((state, normalized_city, 'city'))
                match_keys.append((state, normalized_org, 'city'))
            
            # Store domain record under all possible match keys
            domain_record = {
                'domain_name': domain_name,
                'domain_type': domain_type,
                'organization_name': org_name,
                'suborganization_name': sub_org,
                'city': city,
                'state': state,
                'security_contact_email': security_email if security_email != '(blank)' else None
            }
            
            for match_key in match_keys:
                jurisdiction_domains[match_key].append(domain_record)
    
    logger.success(f"Parsed {total_rows:,} total domains, {filtered_rows:,} local government domains")
    logger.info(f"Grouped into {len(jurisdiction_domains):,} unique jurisdiction keys")
    
    return dict(jurisdiction_domains)


def update_jurisdictions_with_gsa_data(
    jurisdiction_domains: Dict[str, List[Dict[str, Any]]],
    states: Optional[List[str]] = None,
    dry_run: bool = False,
    create_new_records: bool = True
) -> Dict[str, int]:
    """
    Update jurisdictions_details_search with GSA domain data using multi-source matching.
    Also creates NEW records for unmatched GSA domains (townships, special districts, etc.)
    
    Matching strategy:
    1. Try exact match against jurisdictions_details_search
    2. Try match against jurisdictions_search (Census data)
    3. Try match against jurisdictions_wikidata (WikiData)
    4. Try extracting jurisdiction name from domain itself
    5. CREATE NEW records for unmatched domains (if create_new_records=True)
    
    Args:
        jurisdiction_domains: Parsed domain data grouped by jurisdiction
        states: Optional state filter
        dry_run: If True, don't actually update database
        create_new_records: If True, create new records for unmatched GSA domains
    
    Returns:
        Statistics dict
    """
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        # Fetch jurisdictions from multiple sources for better matching
        state_filter = ""
        if states:
            state_list = "', '".join(states)
            state_filter = f"AND jd.state_code IN ('{state_list}')"
        
        # Build comprehensive jurisdiction lookup with all name variants
        query = f"""
            SELECT DISTINCT
                jd.jurisdiction_id,
                jd.jurisdiction_name as details_name,
                jd.jurisdiction_type as details_type,
                jd.state_code,
                jd.state,
                js.name as census_name,
                js.type as census_type,
                jw.jurisdiction_name as wikidata_name,
                jw.jurisdiction_type as wikidata_type
            FROM jurisdictions_details_search jd
            LEFT JOIN jurisdictions_search js 
                ON jd.jurisdiction_id = js.id::text 
                AND jd.state_code = js.state_code
            LEFT JOIN jurisdictions_wikidata jw
                ON jd.state_code = jw.state_code
                AND (
                    LOWER(TRIM(jd.jurisdiction_name)) = LOWER(TRIM(jw.jurisdiction_name))
                    OR jd.jurisdiction_id = jw.jurisdiction_id
                )
            WHERE 1=1 {state_filter}
        """
        
        cur.execute(query)
        jurisdictions = cur.fetchall()
        logger.info(f"Loaded {len(jurisdictions):,} jurisdictions with name variants from database")
        
        # Match and update
        stats = {
            'total_jurisdictions': len(jurisdictions),
            'total_gsa_domains': sum(len(domains) for domains in jurisdiction_domains.values()),
            'matched': 0,
            'matched_by_details': 0,
            'matched_by_census': 0,
            'matched_by_wikidata': 0,
            'matched_by_domain': 0,
            'updated': 0,
            'created': 0,
            'no_match': 0,
            'errors': 0
        }
        
        updates = []
        match_sources = []  # Track which source matched
        matched_domain_keys = set()  # Track which domains were matched
        
        for jurisdiction in jurisdictions:
            jid = jurisdiction['jurisdiction_id']
            details_name = jurisdiction['details_name']
            census_name = jurisdiction.get('census_name')
            wikidata_name = jurisdiction.get('wikidata_name')
            details_type = jurisdiction['details_type']
            census_type = jurisdiction.get('census_type')
            wikidata_type = jurisdiction.get('wikidata_type')
            state_code = jurisdiction['state_code']
            
            matched_domains = []
            match_source = None
            
            # Strategy 1: Try matching against jurisdictions_details_search name
            if details_name:
                normalized_name = normalize_name(details_name)
                match_key = (state_code, normalized_name, details_type)
                if match_key in jurisdiction_domains:
                    matched_domains = jurisdiction_domains[match_key]
                    match_source = 'details'
                    stats['matched_by_details'] += 1
            
            # Strategy 2: Try matching against Census jurisdictions_search name
            if not matched_domains and census_name:
                normalized_name = normalize_name(census_name)
                # Try with census type
                if census_type:
                    match_key = (state_code, normalized_name, census_type)
                    if match_key in jurisdiction_domains:
                        matched_domains = jurisdiction_domains[match_key]
                        match_source = 'census'
                        stats['matched_by_census'] += 1
            
            # Strategy 3: Try matching against WikiData name
            if not matched_domains and wikidata_name:
                normalized_name = normalize_name(wikidata_name)
                # Try with wikidata type
                if wikidata_type:
                    match_key = (state_code, normalized_name, wikidata_type)
                    if match_key in jurisdiction_domains:
                        matched_domains = jurisdiction_domains[match_key]
                        match_source = 'wikidata'
                        stats['matched_by_wikidata'] += 1
            
            # Strategy 4: Try matching by extracting name from domains in this state
            if not matched_domains:
                # Get all domain records for this state
                for key, domains in jurisdiction_domains.items():
                    key_state, key_name, key_type = key
                    if key_state != state_code:
                        continue
                    
                    # Try extracting jurisdiction name from each domain
                    for domain_rec in domains:
                        domain_name = domain_rec.get('domain_name', '')
                        extracted_name = extract_name_from_domain(domain_name, state_code)
                        
                        if extracted_name:
                            # Check if extracted name matches any of our name variants
                            names_to_check = [
                                normalize_name(details_name) if details_name else None,
                                normalize_name(census_name) if census_name else None,
                                normalize_name(wikidata_name) if wikidata_name else None
                            ]
                            
                            for name_variant in names_to_check:
                                if name_variant and extracted_name == name_variant:
                                    matched_domains = [domain_rec]
                                    match_source = 'domain_extraction'
                                    stats['matched_by_domain'] += 1
                                    break
                            
                            if matched_domains:
                                break
                    
                    if matched_domains:
                        break
            
            if not matched_domains:
                stats['no_match'] += 1
                continue
            
            stats['matched'] += 1
            match_sources.append(match_source)
            
            # Extract data from matched domains
            domain_names = [d['domain_name'] for d in matched_domains]
            
            # Mark these domain records as matched
            for d in matched_domains:
                matched_domain_keys.add(d['domain_name'])
            
            # Use first domain's metadata (they should be consistent)
            first_domain = matched_domains[0]
            security_email = first_domain.get('security_contact_email')
            org_name = first_domain.get('organization_name')
            domain_type = first_domain.get('domain_type')
            
            # Also update website_url if not already set (use first domain as primary)
            primary_domain = f"https://{domain_names[0]}" if domain_names else None
            
            updates.append({
                'jurisdiction_id': jid,
                'gov_domains': json.dumps(domain_names),
                'security_contact_email': security_email,
                'gsa_organization_name': org_name,
                'gsa_domain_type': domain_type,
                'primary_domain': primary_domain,
                'gsa_last_updated': datetime.now()
            })
            
            if len(updates) % 100 == 0:
                logger.info(f"Processed {len(updates):,} matches...")
        
        logger.success(f"Matched {len(updates):,} jurisdictions with GSA domain data")
        
        if dry_run:
            logger.warning("DRY RUN - No database updates performed")
            logger.info("Sample matches (first 10):")
            for i, update in enumerate(updates[:10]):
                source = match_sources[i] if i < len(match_sources) else 'unknown'
                logger.info(f"  [{source}] {update['jurisdiction_id']}: {update['gov_domains']}")
        else:
            # Perform batch update
            update_query = """
                UPDATE jurisdictions_details_search
                SET 
                    gov_domains = %s::jsonb,
                    security_contact_email = %s,
                    gsa_organization_name = %s,
                    gsa_domain_type = %s,
                    gsa_last_updated = %s,
                    website_url = COALESCE(website_url, %s)
                WHERE jurisdiction_id = %s
            """
            
            batch_data = [
                (
                    u['gov_domains'],
                    u['security_contact_email'],
                    u['gsa_organization_name'],
                    u['gsa_domain_type'],
                    u['gsa_last_updated'],
                    u['primary_domain'],
                    u['jurisdiction_id']
                )
                for u in updates
            ]
            
            execute_batch(cur, update_query, batch_data, page_size=500)
            conn.commit()
            
            stats['updated'] = len(updates)
            logger.success(f"Updated {stats['updated']:,} jurisdictions in database")
        
        # Step 2: Create NEW records for unmatched GSA domains
        if create_new_records:
            logger.info("=" * 80)
            logger.info("PHASE 2: Creating new records for unmatched GSA domains...")
            logger.info("=" * 80)
            
            # Use the matched_domain_keys set that was populated during Phase 1
            # Find unmatched domain records
            new_records = []
            for (state_code, normalized_name, jtype), domain_list in jurisdiction_domains.items():
                for domain_rec in domain_list:
                    domain_name = domain_rec['domain_name']
                    
                    # Skip if already matched
                    if domain_name in matched_domain_keys:
                        continue
                    
                    # Create new jurisdiction record
                    org_name = domain_rec.get('organization_name', '')
                    city = domain_rec.get('city', '')
                    domain_type = domain_rec.get('domain_type', '')
                    security_email = domain_rec.get('security_contact_email')
                    
                    # Generate jurisdiction_id (use domain name as base)
                    jurisdiction_id = f"gsa_{domain_name.replace('.gov', '').replace('.', '_')}"
                    
                    # Determine jurisdiction name (prefer org name, fallback to city)
                    jurisdiction_name = org_name or city or domain_name.replace('.gov', '').title()
                    
                    new_records.append({
                        'jurisdiction_id': jurisdiction_id,
                        'jurisdiction_name': jurisdiction_name,
                        'jurisdiction_type': domain_type.lower() if domain_type else 'other',
                        'state_code': state_code,
                        'state': domain_rec.get('state', state_code),
                        'gov_domains': json.dumps([domain_name]),
                        'security_contact_email': security_email,
                        'gsa_organization_name': org_name,
                        'gsa_domain_type': domain_type,
                        'website_url': f"https://{domain_name}",
                        'status': 'gsa_only',  # Mark as GSA-sourced
                        'gsa_last_updated': datetime.now()
                    })
            
            logger.info(f"Found {len(new_records):,} unmatched GSA domains to add as new records")
            
            if dry_run:
                logger.warning("DRY RUN - Would create new records (first 10):")
                for rec in new_records[:10]:
                    logger.info(f"  NEW: {rec['jurisdiction_id']} ({rec['jurisdiction_type']}) - {rec['jurisdiction_name']}")
            else:
                if new_records:
                    # Insert new records
                    insert_query = """
                        INSERT INTO jurisdictions_details_search (
                            jurisdiction_id,
                            jurisdiction_name,
                            jurisdiction_type,
                            state_code,
                            state,
                            gov_domains,
                            security_contact_email,
                            gsa_organization_name,
                            gsa_domain_type,
                            website_url,
                            status,
                            gsa_last_updated
                        ) VALUES (
                            %s, %s, %s, %s, %s, %s::jsonb, %s, %s, %s, %s, %s, %s
                        )
                        ON CONFLICT (jurisdiction_id) DO UPDATE SET
                            gov_domains = EXCLUDED.gov_domains,
                            security_contact_email = EXCLUDED.security_contact_email,
                            gsa_organization_name = EXCLUDED.gsa_organization_name,
                            gsa_domain_type = EXCLUDED.gsa_domain_type,
                            website_url = EXCLUDED.website_url,
                            gsa_last_updated = EXCLUDED.gsa_last_updated
                    """
                    
                    batch_data = [
                        (
                            rec['jurisdiction_id'],
                            rec['jurisdiction_name'],
                            rec['jurisdiction_type'],
                            rec['state_code'],
                            rec['state'],
                            rec['gov_domains'],
                            rec['security_contact_email'],
                            rec['gsa_organization_name'],
                            rec['gsa_domain_type'],
                            rec['website_url'],
                            rec['status'],
                            rec['gsa_last_updated']
                        )
                        for rec in new_records
                    ]
                    
                    execute_batch(cur, insert_query, batch_data, page_size=500)
                    conn.commit()
                    
                    stats['created'] = len(new_records)
                    logger.success(f"Created {stats['created']:,} new jurisdiction records from GSA domains")
        
        return stats
        
    except Exception as e:
        conn.rollback()
        logger.error(f"Error updating jurisdictions: {e}")
        stats['errors'] += 1
        raise
    finally:
        cur.close()
        conn.close()


async def main(states: Optional[str] = None, dry_run: bool = False, create_new: bool = True):
    """
    Main entry point for GSA domain enrichment.
    
    Args:
        states: Comma-separated state codes (e.g., "AL,GA,MA")
        dry_run: If True, don't update database
        create_new: If True, create new records for unmatched GSA domains
    """
    logger.info("=" * 80)
    logger.info("GSA .gov Domain Enrichment Load")
    logger.info("=" * 80)
    
    # Parse state filter
    state_list = None
    if states:
        state_list = [s.strip().upper() for s in states.split(',')]
        logger.info(f"Filtering to states: {', '.join(state_list)}")
    
    # Step 1: Download GSA data
    csv_path = await download_gsa_domains()
    
    # Step 2: Parse and group by jurisdiction
    jurisdiction_domains = parse_gsa_csv(csv_path, states=state_list)
    
    # Step 3: Match and update jurisdictions (+ create new records)
    stats = update_jurisdictions_with_gsa_data(
        jurisdiction_domains,
        states=state_list,
        dry_run=dry_run,
        create_new_records=create_new
    )
    
    # Print summary
    logger.info("=" * 80)
    logger.info("ENRICHMENT SUMMARY")
    logger.info("=" * 80)
    logger.info(f"Total GSA domains processed: {stats.get('total_gsa_domains', 0):,}")
    logger.info(f"Total existing jurisdictions checked: {stats['total_jurisdictions']:,}")
    logger.info("")
    logger.info("PHASE 1: Enriched existing jurisdictions")
    logger.info(f"  Matched with GSA domains: {stats['matched']:,}")
    logger.info(f"    - Via jurisdictions_details_search: {stats['matched_by_details']:,}")
    logger.info(f"    - Via jurisdictions_search (Census): {stats['matched_by_census']:,}")
    logger.info(f"    - Via jurisdictions_wikidata: {stats['matched_by_wikidata']:,}")
    logger.info(f"    - Via domain name extraction: {stats['matched_by_domain']:,}")
    logger.info(f"  Updated in database: {stats['updated']:,}")
    logger.info(f"  No match found: {stats['no_match']:,}")
    logger.info(f"  Match rate: {stats['matched']/stats['total_jurisdictions']*100:.1f}%")
    logger.info("")
    logger.info("PHASE 2: Created new jurisdiction records")
    logger.info(f"  New records from unmatched GSA domains: {stats.get('created', 0):,}")
    logger.info("")
    logger.info("TOTAL IMPACT")
    logger.info(f"  Total jurisdictions with GSA data: {stats['updated'] + stats.get('created', 0):,}")
    
    if stats['errors']:
        logger.warning(f"Errors encountered: {stats['errors']}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Load GSA .gov domains into jurisdictions_details_search")
    parser.add_argument(
        '--states',
        type=str,
        help='Comma-separated state codes (e.g., AL,GA,MA,WA,WI)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be updated without actually updating'
    )
    parser.add_argument(
        '--no-create-new',
        action='store_true',
        help='Only enrich existing jurisdictions, do not create new records'
    )
    
    args = parser.parse_args()
    
    asyncio.run(main(
        states=args.states, 
        dry_run=args.dry_run,
        create_new=not args.no_create_new
    ))
