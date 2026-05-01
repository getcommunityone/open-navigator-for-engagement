#!/usr/bin/env python3
"""
Fix Alabama officials contact information by parsing source_data JSON

This script:
1. Reads the existing contacts_officials.parquet file
2. Extracts email/phone/address from the source_data JSON field
3. Adds jurisdiction_name and city_jurisdiction columns
4. Overwrites the file with enriched data

Usage:
    python scripts/fix_al_officials_contacts.py
"""

import pandas as pd
import json
import re
from pathlib import Path
from loguru import logger


def parse_jurisdiction_name(ocd_id: str) -> str:
    """Extract city/jurisdiction name from OCD ID.
    
    Examples:
        ocd-jurisdiction/country:us/state:al/place:tuscaloosa/government -> Tuscaloosa
        ocd-jurisdiction/country:us/state:al/government -> Alabama
    """
    if not ocd_id or pd.isna(ocd_id):
        return None
        
    # Extract place name from OCD ID
    match = re.search(r'/place:([^/]+)/', ocd_id)
    if match:
        place = match.group(1)
        # Convert snake_case to Title Case
        return place.replace('_', ' ').title()
    
    # Extract state if no place
    match = re.search(r'/state:([^/]+)/', ocd_id)
    if match:
        return match.group(1).upper()
    
    return None


def extract_contact_info(source_data_json: str):
    """Extract contact information from the source_data JSON field.
    
    For state legislators: checks contact_details array
    For mayors/municipal: checks offices array
    
    Returns:
        Dict with email, phone, address, city_jurisdiction
    """
    if not source_data_json or pd.isna(source_data_json):
        return pd.Series({
            'email_extracted': None,
            'phone_extracted': None,
            'address_extracted': None,
            'city_jurisdiction': None
        })
    
    try:
        data = json.loads(source_data_json) if isinstance(source_data_json, str) else source_data_json
    except (json.JSONDecodeError, TypeError):
        return pd.Series({
            'email_extracted': None,
            'phone_extracted': None,
            'address_extracted': None,
            'city_jurisdiction': None
        })
    
    email = None
    phone = None
    address = None
    city_jurisdiction = None
    
    # Try to get email from top level
    if 'email' in data:
        email = data['email']
    
    # Try contact_details (state legislators)
    contact_details = data.get('contact_details', [])
    for contact in contact_details:
        if contact.get('note') == 'Capitol Office':
            email = email or contact.get('email')
            phone = phone or contact.get('voice')
            address = address or contact.get('address')
    
    # Try offices array (mayors/municipal officials)
    offices = data.get('offices', [])
    for office in offices:
        if office.get('classification') == 'primary':
            email = email or office.get('email')
            phone = phone or office.get('voice')
            address = address or office.get('address')
    
    # Get jurisdiction/city from roles
    roles = data.get('roles', [])
    if roles:
        role = roles[0]  # Get current/first role
        jurisdiction_ocd = role.get('jurisdiction')
        if jurisdiction_ocd:
            city_jurisdiction = parse_jurisdiction_name(jurisdiction_ocd)
    
    return pd.Series({
        'email_extracted': email,
        'phone_extracted': phone,
        'address_extracted': address,
        'city_jurisdiction': city_jurisdiction
    })


def main():
    logger.info("=" * 80)
    logger.info("FIXING ALABAMA OFFICIALS CONTACT INFORMATION")
    logger.info("=" * 80)
    
    file_path = Path("data/gold/states/AL/contacts_officials.parquet")
    
    if not file_path.exists():
        logger.error(f"File not found: {file_path}")
        return
    
    # Load existing data
    logger.info(f"Loading {file_path}...")
    df = pd.read_parquet(file_path)
    logger.info(f"  Loaded {len(df)} officials")
    
    # Show current stats
    logger.info("\n📊 BEFORE:")
    logger.info(f"  With email: {df['email'].notna().sum()}")
    logger.info(f"  With phone: {df['phone'].notna().sum()}")
    logger.info(f"  With address: {df['address'].notna().sum()}")
    
    # Extract contact info from source_data
    logger.info("\n🔍 Extracting contact information from source_data JSON...")
    contact_info = df['source_data'].apply(extract_contact_info)
    
    # Update columns with extracted data (fill in nulls)
    df['email'] = df['email'].fillna(contact_info['email_extracted'])
    df['phone'] = df['phone'].fillna(contact_info['phone_extracted'])
    df['address'] = df['address'].fillna(contact_info['address_extracted'])
    df['city_jurisdiction'] = contact_info['city_jurisdiction']
    
    # Parse jurisdiction name from OCD ID
    df['jurisdiction_name'] = df['jurisdiction'].apply(parse_jurisdiction_name)
    
    # Clean up address formatting (remove semicolons)
    df['address'] = df['address'].apply(
        lambda x: x.replace(';', ', ') if x and isinstance(x, str) else x
    )
    
    # Show updated stats
    logger.info("\n📊 AFTER:")
    logger.info(f"  With email: {df['email'].notna().sum()}")
    logger.info(f"  With phone: {df['phone'].notna().sum()}")
    logger.info(f"  With address: {df['address'].notna().sum()}")
    logger.info(f"  With city_jurisdiction: {df['city_jurisdiction'].notna().sum()}")
    
    # Save updated file
    logger.info(f"\n💾 Saving updated file to {file_path}...")
    df.to_parquet(file_path, index=False, engine='pyarrow', compression='snappy')
    
    logger.info("\n✅ DONE!")
    
    # Show sample of mayors with contact info
    logger.info("\n👥 MAYORS WITH CONTACT INFO:")
    mayors = df[df['role_type'] == 'mayor'].copy()
    if len(mayors) > 0:
        cols = ['full_name', 'city_jurisdiction', 'email', 'phone']
        print(mayors[cols].to_string(index=False))
    
    logger.info("\n" + "=" * 80)


if __name__ == "__main__":
    main()
