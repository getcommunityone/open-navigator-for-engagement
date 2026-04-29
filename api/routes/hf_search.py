"""
HuggingFace Datasets Search API Integration

Fast server-side text search using HuggingFace's indexed datasets.
Falls back to DuckDB if dataset not indexed or search unavailable.
"""
import httpx
from typing import Optional, List, Dict, Any
from loguru import logger
import os

HF_SEARCH_API = "https://datasets-server.huggingface.co/search"
HF_ORGANIZATION = os.getenv('HF_ORGANIZATION', 'CommunityOne')
REQUEST_TIMEOUT = 5  # seconds


def is_dataset_indexed(dataset_name: str) -> bool:
    """
    Check if a dataset is indexed and searchable.
    
    Args:
        dataset_name: Full repo ID (e.g., 'CommunityOne/states-ma-contacts-local-officials')
    
    Returns:
        True if dataset supports search, False otherwise
    """
    try:
        response = httpx.get(
            "https://datasets-server.huggingface.co/is-valid",
            params={"dataset": dataset_name},
            timeout=REQUEST_TIMEOUT
        )
        if response.status_code == 200:
            data = response.json()
            return data.get("search", False)
    except Exception as e:
        logger.debug(f"Could not check if {dataset_name} is indexed: {e}")
    
    return False


def search_hf_dataset(
    dataset_name: str,
    query: str,
    config: str = "default",
    split: str = "train",
    limit: int = 100
) -> Optional[List[Dict[str, Any]]]:
    """
    Search a HuggingFace dataset using server-side indexed search.
    
    Args:
        dataset_name: Full repo ID (e.g., 'CommunityOne/states-ma-contacts')
        query: Search text (searches across all string columns)
        config: Dataset configuration name
        split: Dataset split to search
        limit: Maximum results to return
    
    Returns:
        List of matching rows, or None if search unavailable
    """
    try:
        response = httpx.get(
            HF_SEARCH_API,
            params={
                "dataset": dataset_name,
                "config": config,
                "split": split,
                "query": query,
                "offset": 0,
                "length": limit
            },
            timeout=REQUEST_TIMEOUT
        )
        
        if response.status_code == 200:
            data = response.json()
            
            # Check for errors
            if "error" in data:
                logger.debug(f"HF Search API error for {dataset_name}: {data['error']}")
                return None
            
            # Extract rows
            rows = data.get("rows", [])
            logger.info(f"✅ HF Search API: Found {len(rows)} results for '{query}' in {dataset_name}")
            
            # Convert to list of dicts (row['row'] contains actual data)
            results = [row.get("row", {}) for row in rows]
            return results
        
        elif response.status_code == 404:
            logger.debug(f"Dataset {dataset_name} not found on HuggingFace")
            return None
        
        else:
            logger.debug(f"HF Search API returned status {response.status_code}")
            return None
            
    except httpx.TimeoutException:
        logger.debug(f"HF Search API timeout for {dataset_name}")
        return None
    
    except Exception as e:
        logger.debug(f"HF Search API error: {e}")
        return None


def search_contacts_hf(query: str, state: Optional[str] = None, limit: int = 10) -> Optional[List[Dict[str, Any]]]:
    """
    Search contacts (local officials + nonprofit officers) using HF Search API.
    
    Args:
        query: Search text (name, title, jurisdiction, etc.)
        state: 2-letter state code (e.g., 'MA')
        limit: Maximum results
    
    Returns:
        List of contact dicts, or None if search unavailable
    """
    results = []
    
    # Search local officials
    if state:
        dataset = f"{HF_ORGANIZATION}/states-{state.lower()}-contacts-local-officials"
        local_results = search_hf_dataset(dataset, query, limit=limit)
        if local_results:
            for row in local_results:
                row['source'] = 'local_officials'
                results.append(row)
    
    # Search nonprofit officers
    if state and len(results) < limit:
        dataset = f"{HF_ORGANIZATION}/states-{state.lower()}-contacts-nonprofit-officers"
        nonprofit_results = search_hf_dataset(dataset, query, limit=limit - len(results))
        if nonprofit_results:
            for row in nonprofit_results:
                row['source'] = 'nonprofit_officers'
                results.append(row)
    
    return results if results else None


def search_organizations_hf(query: str, state: Optional[str] = None, limit: int = 10) -> Optional[List[Dict[str, Any]]]:
    """
    Search nonprofit organizations using HF Search API.
    
    Args:
        query: Search text (organization name, EIN, etc.)
        state: 2-letter state code
        limit: Maximum results
    
    Returns:
        List of organization dicts, or None if search unavailable
    """
    if state:
        dataset = f"{HF_ORGANIZATION}/states-{state.lower()}-nonprofits-organizations"
    else:
        dataset = f"{HF_ORGANIZATION}/national-nonprofits-organizations"
    
    return search_hf_dataset(dataset, query, limit=limit)


def search_jurisdictions_hf(query: str, jurisdiction_type: Optional[str] = None, limit: int = 10) -> Optional[List[Dict[str, Any]]]:
    """
    Search jurisdictions (cities, counties, townships, school districts) using HF Search API.
    
    Args:
        query: Search text (city name, county name, etc.)
        jurisdiction_type: 'cities', 'counties', 'townships', 'school_districts'
        limit: Maximum results
    
    Returns:
        List of jurisdiction dicts, or None if search unavailable
    """
    if jurisdiction_type:
        dataset = f"{HF_ORGANIZATION}/reference-jurisdictions-{jurisdiction_type.replace('_', '-')}"
    else:
        # Try cities first (most common)
        dataset = f"{HF_ORGANIZATION}/reference-jurisdictions-cities"
    
    return search_hf_dataset(dataset, query, limit=limit)
