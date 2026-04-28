"""
Unified Search API
LinkedIn-style search across contacts, meetings, organizations, and causes
"""
from fastapi import APIRouter, Query, HTTPException
from typing import Optional, List, Dict, Any
from pathlib import Path
import pandas as pd
from loguru import logger
import re

router = APIRouter(prefix="/api/search", tags=["search"])

# Paths to gold datasets
GOLD_DIR = Path("data/gold")

class SearchResult:
    """Unified search result"""
    
    def __init__(self, 
                 result_type: str,
                 title: str,
                 subtitle: str,
                 description: str,
                 url: str,
                 score: float,
                 metadata: Dict[str, Any]):
        self.result_type = result_type
        self.title = title
        self.subtitle = subtitle
        self.description = description
        self.url = url
        self.score = score
        self.metadata = metadata
    
    def to_dict(self):
        return {
            "type": self.result_type,
            "title": self.title,
            "subtitle": self.subtitle,
            "description": self.description,
            "url": self.url,
            "score": self.score,
            "metadata": self.metadata
        }


def calculate_relevance_score(text: str, query: str) -> float:
    """Calculate relevance score for text matching query"""
    if not text or not query:
        return 0.0
    
    text_lower = text.lower()
    query_lower = query.lower()
    
    # Exact match gets highest score
    if query_lower in text_lower:
        score = 1.0
        # Boost if it's at the start
        if text_lower.startswith(query_lower):
            score += 0.5
        return min(score, 2.0)
    
    # Partial word matches
    query_words = query_lower.split()
    text_words = text_lower.split()
    
    matches = sum(1 for qw in query_words if any(qw in tw for tw in text_words))
    return matches / len(query_words) if query_words else 0.0


def search_contacts(query: str, state: Optional[str] = None, limit: int = 10) -> List[SearchResult]:
    """Search local officials"""
    results = []
    
    try:
        # Search state files first
        if state:
            contact_files = list(GOLD_DIR.glob(f"states/{state}/contacts_local_officials.parquet"))
        else:
            contact_files = list(GOLD_DIR.glob("states/*/contacts_local_officials.parquet"))
        
        for file_path in contact_files[:5]:  # Limit to 5 states for performance
            try:
                df = pd.read_parquet(file_path)
                state_code = file_path.parent.name
                
                # Search in name, title, jurisdiction
                for _, row in df.iterrows():
                    name = str(row.get('official_name', ''))
                    title = str(row.get('title', ''))
                    jurisdiction = str(row.get('jurisdiction_name', ''))
                    
                    score = max(
                        calculate_relevance_score(name, query),
                        calculate_relevance_score(title, query),
                        calculate_relevance_score(jurisdiction, query)
                    )
                    
                    if score > 0.3:  # Relevance threshold
                        results.append(SearchResult(
                            result_type="contact",
                            title=name,
                            subtitle=f"{title} - {jurisdiction}, {state_code}",
                            description=f"Local official in {jurisdiction}",
                            url=f"/people?official={row.get('official_id', '')}",
                            score=score,
                            metadata={
                                "title": title,
                                "jurisdiction": jurisdiction,
                                "state": state_code,
                                "official_id": row.get('official_id', '')
                            }
                        ))
            except Exception as e:
                logger.debug(f"Error searching {file_path}: {e}")
    
    except Exception as e:
        logger.error(f"Contact search error: {e}")
    
    # Sort by score and limit
    results.sort(key=lambda x: x.score, reverse=True)
    return results[:limit]


def search_meetings(query: str, state: Optional[str] = None, limit: int = 10) -> List[SearchResult]:
    """Search meeting transcripts and agendas"""
    results = []
    
    try:
        # Search state meeting files
        if state:
            meeting_files = list(GOLD_DIR.glob(f"states/{state}/meetings.parquet"))
        else:
            meeting_files = list(GOLD_DIR.glob("states/*/meetings.parquet"))
        
        for file_path in meeting_files[:5]:  # Limit for performance
            try:
                df = pd.read_parquet(file_path)
                state_code = file_path.parent.name
                
                # Search in title, body, jurisdiction
                for _, row in df.iterrows():
                    title = str(row.get('title', ''))
                    body = str(row.get('body', ''))[:500]  # First 500 chars
                    jurisdiction = str(row.get('jurisdiction_name', ''))
                    meeting_date = str(row.get('meeting_date', ''))
                    
                    score = max(
                        calculate_relevance_score(title, query),
                        calculate_relevance_score(body, query) * 0.8,  # Body matches slightly lower
                        calculate_relevance_score(jurisdiction, query) * 0.6
                    )
                    
                    if score > 0.3:
                        # Extract snippet around query
                        snippet = body[:200] + "..." if len(body) > 200 else body
                        
                        results.append(SearchResult(
                            result_type="meeting",
                            title=title,
                            subtitle=f"{jurisdiction}, {state_code} - {meeting_date}",
                            description=snippet,
                            url=f"/documents?meeting_id={row.get('meeting_id', '')}",
                            score=score,
                            metadata={
                                "jurisdiction": jurisdiction,
                                "state": state_code,
                                "date": meeting_date,
                                "meeting_id": row.get('meeting_id', '')
                            }
                        ))
            except Exception as e:
                logger.debug(f"Error searching {file_path}: {e}")
    
    except Exception as e:
        logger.error(f"Meeting search error: {e}")
    
    results.sort(key=lambda x: x.score, reverse=True)
    return results[:limit]


def search_organizations(query: str, state: Optional[str] = None, ntee_code: Optional[str] = None, limit: int = 10) -> List[SearchResult]:
    """Search nonprofit organizations"""
    results = []
    
    try:
        # Search state organization files
        if state:
            org_files = list(GOLD_DIR.glob(f"states/{state}/nonprofits_organizations.parquet"))
        else:
            # Search national file for better performance
            org_files = list(GOLD_DIR.glob("national/nonprofits_organizations.parquet"))
        
        for file_path in org_files[:1]:  # Limit to 1 file for performance
            try:
                df = pd.read_parquet(file_path)
                
                # Filter by NTEE code if provided
                if ntee_code:
                    df = df[df['ntee_code'].str.startswith(ntee_code, na=False)]
                
                # Filter by state if provided and using national file
                if state and 'state' in df.columns:
                    df = df[df['state'] == state]
                
                # Limit to first 1000 rows for performance
                df = df.head(1000)
                
                # Search in name, mission, programs
                for _, row in df.iterrows():
                    name = str(row.get('name', ''))
                    city = str(row.get('city', ''))
                    state_code = str(row.get('state', ''))
                    ntee = str(row.get('ntee_code', ''))
                    
                    score = calculate_relevance_score(name, query)
                    
                    if score > 0.3:
                        results.append(SearchResult(
                            result_type="organization",
                            title=name,
                            subtitle=f"{city}, {state_code} - {ntee}",
                            description=f"Nonprofit organization serving {city}",
                            url=f"/nonprofits?ein={row.get('ein', '')}",
                            score=score,
                            metadata={
                                "ein": row.get('ein', ''),
                                "city": city,
                                "state": state_code,
                                "ntee_code": ntee
                            }
                        ))
            except Exception as e:
                logger.debug(f"Error searching {file_path}: {e}")
    
    except Exception as e:
        logger.error(f"Organization search error: {e}")
    
    results.sort(key=lambda x: x.score, reverse=True)
    return results[:limit]


def search_causes(query: str, limit: int = 10) -> List[SearchResult]:
    """Search causes and NTEE categories"""
    results = []
    
    try:
        # Search NTEE codes
        ntee_file = GOLD_DIR / "reference" / "causes_ntee_codes.parquet"
        if ntee_file.exists():
            df = pd.read_parquet(ntee_file)
            
            for _, row in df.iterrows():
                code = str(row.get('ntee_code', ''))
                description = str(row.get('description', ''))
                category = str(row.get('category', ''))
                
                score = max(
                    calculate_relevance_score(description, query),
                    calculate_relevance_score(category, query)
                )
                
                if score > 0.3:
                    results.append(SearchResult(
                        result_type="cause",
                        title=description,
                        subtitle=f"NTEE Code: {code} - {category}",
                        description=f"Nonprofit category: {category}",
                        url=f"/nonprofits?ntee_code={code}",
                        score=score,
                        metadata={
                            "ntee_code": code,
                            "category": category
                        }
                    ))
    
    except Exception as e:
        logger.error(f"Cause search error: {e}")
    
    results.sort(key=lambda x: x.score, reverse=True)
    return results[:limit]


@router.get("/")
async def unified_search(
    q: str = Query(..., min_length=2, description="Search query"),
    types: Optional[str] = Query(None, description="Comma-separated result types: contacts,meetings,organizations,causes"),
    state: Optional[str] = Query(None, description="Filter by state (2-letter code)"),
    ntee_code: Optional[str] = Query(None, description="Filter organizations by NTEE code"),
    limit: int = Query(20, ge=1, le=100, description="Maximum results per type")
):
    """
    Unified search across all data types
    
    Search for contacts, meetings, organizations, and causes in one query.
    
    **Examples:**
    - `/api/search?q=dental` - Search everything for "dental"
    - `/api/search?q=budget&types=meetings` - Search only meetings
    - `/api/search?q=health&state=AL` - Search in Alabama only
    - `/api/search?q=education&types=organizations,causes` - Search orgs and causes
    """
    try:
        # Parse requested types
        if types:
            requested_types = [t.strip() for t in types.split(',')]
        else:
            requested_types = ['contacts', 'meetings', 'organizations', 'causes']
        
        all_results = []
        
        # Search each requested type
        if 'contacts' in requested_types:
            contact_results = search_contacts(q, state, limit=limit // 4)
            all_results.extend(contact_results)
        
        if 'meetings' in requested_types:
            meeting_results = search_meetings(q, state, limit=limit // 4)
            all_results.extend(meeting_results)
        
        if 'organizations' in requested_types:
            org_results = search_organizations(q, state, ntee_code, limit=limit // 2)
            all_results.extend(org_results)
        
        if 'causes' in requested_types:
            cause_results = search_causes(q, limit=limit // 4)
            all_results.extend(cause_results)
        
        # Sort all results by score
        all_results.sort(key=lambda x: x.score, reverse=True)
        
        # Group by type for response
        grouped_results = {
            'contacts': [r.to_dict() for r in all_results if r.result_type == 'contact'][:limit],
            'meetings': [r.to_dict() for r in all_results if r.result_type == 'meeting'][:limit],
            'organizations': [r.to_dict() for r in all_results if r.result_type == 'organization'][:limit],
            'causes': [r.to_dict() for r in all_results if r.result_type == 'cause'][:limit],
        }
        
        # Calculate total results
        total_results = sum(len(v) for v in grouped_results.values())
        
        return {
            "query": q,
            "total_results": total_results,
            "results": grouped_results,
            "filters": {
                "state": state,
                "ntee_code": ntee_code,
                "types": requested_types
            }
        }
    
    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/suggest")
async def search_suggestions(
    q: str = Query(..., min_length=1, description="Partial search query"),
    limit: int = Query(5, ge=1, le=20, description="Maximum suggestions")
):
    """
    Get search suggestions/autocomplete
    
    Returns quick suggestions as user types
    """
    try:
        suggestions = []
        
        # Common search terms
        common_terms = [
            "dental health", "oral health", "affordable housing", "public transit",
            "school funding", "budget", "water quality", "parks", "zoning",
            "police", "fire department", "mental health", "food assistance",
            "senior services", "youth programs", "employment", "job training"
        ]
        
        # Filter suggestions
        q_lower = q.lower()
        suggestions = [term for term in common_terms if q_lower in term.lower()]
        
        return {
            "query": q,
            "suggestions": suggestions[:limit]
        }
    
    except Exception as e:
        logger.error(f"Suggestion error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
