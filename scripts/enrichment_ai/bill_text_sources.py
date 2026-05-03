"""
Bill Text Data Sources Configuration

⚠️ LICENSING POLICY: Only use FREE, PUBLIC DOMAIN, or OPENLY LICENSED sources
- NO commercial APIs (LegiScan, etc.)
- Only state government APIs (public domain)
- OpenStates bulk downloads (public domain)

Approved Sources:
1. OpenStates Bulk Downloads (Public Domain) - RECOMMENDED
2. OpenStates API v3 (Free, with rate limits)
3. State-specific public APIs (GA only - confirmed public)
"""

from typing import Dict, List, Optional
from enum import Enum


class BillTextSource(Enum):
    """Available bill text API sources - PUBLIC/FREE ONLY"""
    OPENSTATES_BULK = "openstates_bulk"  # Public domain bulk downloads
    OPENSTATES_API = "openstates_api"  # Free tier API
    GEORGIA_SOAP = "georgia_soap"  # GA public SOAP API
    UNAVAILABLE = "unavailable"  # No free/public API available


# State-specific API configuration
# ONLY includes states with FREE, PUBLIC APIs
STATE_BILL_TEXT_APIS: Dict[str, BillTextSource] = {
    # Georgia has a public SOAP API (confirmed public domain)
    "GA": BillTextSource.GEORGIA_SOAP,
    
    # All other states: Use OpenStates bulk downloads
    # (Public domain, no licensing restrictions)
    # Individual state APIs are often unreliable or require scraping
}


def get_bill_text_source(state: str) -> BillTextSource:
    """
    Get the recommended bill text source for a state.
    
    Args:
        state: Two-letter state code (e.g., 'AL', 'GA')
        
    Returns:
        BillTextSource enum indicating which API to use
    """
    return STATE_BILL_TEXT_APIS.get(state.upper(), BillTextSource.UNAVAILABLE)


def can_fetch_bill_text(state: str) -> bool:
    """
    Check if we can fetch bill text for this state via API.
    
    Args:
        state: Two-letter state code
        
    Returns:
        True if we have an API source, False otherwise
    """
    source = get_bill_text_source(state)
    return source != BillTextSource.UNAVAILABLE


def get_supported_states() -> List[str]:
    """
    Get list of states where we can fetch bill text via API.
    
    Returns:
        List of state codes (e.g., ['GA', 'TX', 'CA'])
    """
    return [
        state for state, source in STATE_BILL_TEXT_APIS.items()
        if source != BillTextSource.UNAVAILABLE
    ]


# API endpoints and documentation
# ONLY FREE/PUBLIC DOMAIN SOURCES
API_DOCS = {
    BillTextSource.OPENSTATES_BULK: {
        "url": "https://data.openstates.org/",
        "method": "CSV/JSON bulk downloads",
        "auth": "None (public domain)",
        "coverage": "All 50 states",
        "license": "Public Domain - no restrictions",
        "cost": "Free"
    },
    BillTextSource.OPENSTATES_API: {
        "url": "https://docs.openstates.org/api-v3/",
        "method": "GET /bills/{bill_id}",
        "auth": "API key required (free: 50k/month)",
        "coverage": "50 states (text availability varies)",
        "license": "Public Domain (with attribution)",
        "cost": "Free"
    },
    BillTextSource.GEORGIA_SOAP: {
        "url": "http://webservices.legis.ga.gov/",
        "method": "GetLegislationDetail",
        "auth": "Public (no key needed)",
        "coverage": "Georgia only",
        "license": "Public (Georgia government data)",
        "cost": "Free"
    }
}


def print_api_info():
    """Print information about available bill text APIs"""
    print("=" * 80)
    print("BILL TEXT API SOURCES")
    print("=" * 80)
    print()
    
    for source, info in API_DOCS.items():
        if source == BillTextSource.UNAVAILABLE:
            continue
            
        print(f"📡 {source.value.upper()}")
        print(f"   URL: {info['url']}")
        print(f"   Method: {info (FREE/PUBLIC DOMAIN ONLY)")
    print("=" * 80)
    print()
    
    for source, info in API_DOCS.items():
        if source == BillTextSource.UNAVAILABLE:
            continue
            
        print(f"📡 {source.value.upper()}")
        print(f"   URL: {info['url']}")
        print(f"   Method: {info['method']}")
        print(f"   Auth: {info['auth']}")
        print(f"   Coverage: {info['coverage']}")
        print(f"   License: {info['license']}")
        print(f"   Cost: {info['cost']}")
        print()
    
    print("=" * 80)
    print(f"STATES WITH DEDICATED API: {len(get_supported_states())}")
    print(f"States: {', '.join(get_supported_states()) if get_supported_states() else 'None (use OpenStates bulk)'}")
    print("=" * 80)
    print()
    print("✅ RECOMMENDED: Use OpenStates bulk downloads (public domain)")
    print("   - No rate limits")
    print("   - No API keys needed")
    print("   - Complete legislative sessions")
    print("   - Public domain license")
    print()
    print("⚠️  AVOID: Commercial APIs (LegiScan, etc.) - licensing restrictions