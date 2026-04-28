"""
Unified Search API
LinkedIn-style search across contacts, meetings, organizations, and causes
"""
from fastapi import APIRouter, Query, HTTPException
from typing import Optional, List, Dict, Any
from pathlib import Path
import pandas as pd
import duckdb
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
    """Search local officials AND nonprofit officers using DuckDB for fast Parquet queries"""
    results = []
    
    try:
        # Initialize DuckDB connection
        conn = duckdb.connect()
        
        # Search 1: Local Officials
        if state:
            local_file_pattern = f"{GOLD_DIR}/states/{state}/contacts_local_officials.parquet"
            local_file_paths = [Path(local_file_pattern)]
        else:
            local_file_pattern = f"{GOLD_DIR}/states/*/contacts_local_officials.parquet"
            local_file_paths = list(GOLD_DIR.glob("states/*/contacts_local_officials.parquet"))[:5]
        
        logger.info(f"Searching {len(local_file_paths)} local official contact files")
        
        for file_path in local_file_paths:
            if not file_path.exists():
                continue
            
            try:
                # SQL query with relevance scoring across name, title, jurisdiction
                sql = """
                    SELECT 
                        name,
                        title,
                        jurisdiction,
                        state,
                        GREATEST(
                            CASE 
                                WHEN LOWER(name) LIKE LOWER(?) THEN 1.5
                                WHEN LOWER(name) LIKE LOWER(?) THEN 1.0
                                ELSE 0.0
                            END,
                            CASE 
                                WHEN LOWER(title) LIKE LOWER(?) THEN 1.5
                                WHEN LOWER(title) LIKE LOWER(?) THEN 1.0
                                ELSE 0.0
                            END,
                            CASE 
                                WHEN LOWER(jurisdiction) LIKE LOWER(?) THEN 1.5
                                WHEN LOWER(jurisdiction) LIKE LOWER(?) THEN 1.0
                                ELSE 0.0
                            END
                        ) as score
                    FROM read_parquet(?)
                    WHERE LOWER(name) LIKE LOWER(?) 
                       OR LOWER(title) LIKE LOWER(?) 
                       OR LOWER(jurisdiction) LIKE LOWER(?)
                    ORDER BY score DESC
                    LIMIT ?
                """
                
                query_pattern = f'%{query}%'
                query_start = f'{query}%'
                
                rows = conn.execute(sql, [
                    query_start, query_pattern,  # name scoring
                    query_start, query_pattern,  # title scoring
                    query_start, query_pattern,  # jurisdiction scoring
                    str(file_path),              # file path
                    query_pattern, query_pattern, query_pattern,  # WHERE clause
                    limit
                ]).fetchall()
                
                # Convert to SearchResult objects
                for row in rows:
                    name, title, jurisdiction, state_code, score = row
                    
                    if score > 0.3:  # Relevance threshold
                        results.append(SearchResult(
                            result_type="contact",
                            title=name if name else "Unknown",
                            subtitle=f"{title} - {jurisdiction}, {state_code}",
                            description=f"Local official in {jurisdiction}",
                            url=f"/people/{name.replace(' ', '-') if name else 'unknown'}",
                            score=score,
                            metadata={
                                "title": title,
                                "jurisdiction": jurisdiction,
                                "state": state_code,
                                "name": name
                            }
                        ))
                
            except Exception as e:
                logger.debug(f"Error searching {file_path}: {e}")
        
        # Search nonprofit officers from state directories
        nonprofit_files = []
        
        # If state specified, search that state's directory
        if state:
            state_nonprofit_file = GOLD_DIR / "states" / state / "contacts_nonprofit_officers.parquet"
            if state_nonprofit_file.exists():
                nonprofit_files.append(state_nonprofit_file)
        else:
            # Search all state directories
            for state_dir in (GOLD_DIR / "states").glob("*/"):
                state_file = state_dir / "contacts_nonprofit_officers.parquet"
                if state_file.exists():
                    nonprofit_files.append(state_file)
        
        # Also check legacy root location for backward compatibility
        legacy_file = GOLD_DIR / "contacts_nonprofit_officers.parquet"
        if legacy_file.exists():
            nonprofit_files.append(legacy_file)
        
        for nonprofit_file in nonprofit_files:
            try:
                logger.info(f"Searching nonprofit officers: {nonprofit_file}")
                
                officer_sql = """
                    SELECT 
                        name,
                        title,
                        organization_name,
                        city,
                        state,
                        compensation,
                        GREATEST(
                            CASE 
                                WHEN LOWER(name) LIKE LOWER(?) THEN 1.5
                                WHEN LOWER(name) LIKE LOWER(?) THEN 1.0
                                ELSE 0.0
                            END,
                            CASE 
                                WHEN LOWER(title) LIKE LOWER(?) THEN 1.0
                                WHEN LOWER(title) LIKE LOWER(?) THEN 0.5
                                ELSE 0.0
                            END,
                            CASE 
                                WHEN LOWER(organization_name) LIKE LOWER(?) THEN 1.0
                                WHEN LOWER(organization_name) LIKE LOWER(?) THEN 0.5
                                ELSE 0.0
                            END
                        ) AS score
                    FROM read_parquet(?)
                    WHERE (LOWER(name) LIKE LOWER(?) 
                       OR LOWER(title) LIKE LOWER(?) 
                       OR LOWER(organization_name) LIKE LOWER(?))
                """
                
                query_pattern = f'%{query}%'
                query_start = f'{query}%'
                params = [
                    query_start, query_pattern,  # name scoring
                    query_start, query_pattern,  # title scoring  
                    query_start, query_pattern,  # organization scoring
                    str(nonprofit_file),
                    query_pattern, query_pattern, query_pattern  # WHERE clause
                ]
                
                if state:
                    officer_sql += " AND LOWER(state) = LOWER(?)"
                    params.append(state)
                
                officer_sql += " ORDER BY score DESC, compensation DESC NULLS LAST LIMIT ?"
                params.append(limit)
                
                officer_rows = conn.execute(officer_sql, params).fetchall()
                
                for row in officer_rows:
                    name, title, org_name, city, state_code, compensation, score = row
                    
                    if score > 0.3:
                        comp_text = f" (${compensation:,.0f})" if compensation else ""
                        
                        results.append(SearchResult(
                            result_type="contact",
                            title=name if name else "Unknown",
                            subtitle=f"{title} - {org_name}{comp_text}",
                            description=f"Nonprofit officer in {city}, {state_code}",
                            url=f"/nonprofits?name={org_name.replace(' ', '-') if org_name else 'unknown'}",
                            score=score,
                            metadata={
                                "title": title,
                                "organization": org_name,
                                "city": city,
                                "state": state_code,
                                "compensation": compensation,
                                "contact_type": "nonprofit_officer"
                            }
                        ))
                
                logger.info(f"Found {len([r for r in results if r.metadata.get('contact_type') == 'nonprofit_officer'])} nonprofit officer results")
                
            except Exception as e:
                logger.debug(f"Error searching nonprofit officers: {e}")
        
        conn.close()
        
        # Sort all results by score and limit
        results.sort(key=lambda x: x.score, reverse=True)
        logger.info(f"DuckDB search found {len(results)} contacts for query '{query}'")
        return results[:limit]
    
    except Exception as e:
        logger.error(f"Contact search error: {e}")
        return results


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
    """Search nonprofit organizations using DuckDB for fast Parquet queries"""
    results = []
    
    try:
        # Determine file path
        if state:
            file_pattern = f"{GOLD_DIR}/states/{state}/nonprofits_organizations.parquet"
        else:
            file_pattern = f"{GOLD_DIR}/national/nonprofits_organizations.parquet"
        
        # Check if file exists
        file_path = Path(file_pattern)
        if not file_path.exists():
            logger.warning(f"File not found: {file_pattern}")
            return results
        
        # Initialize DuckDB connection
        conn = duckdb.connect()
        
        # Build WHERE clauses
        where_clauses = []
        params = []
        
        # Search query (case-insensitive LIKE) - use 'name' column
        where_clauses.append("LOWER(name) LIKE LOWER(?)")
        params.append(f'%{query}%')
        
        # State filter (if using national file)
        if state and not file_pattern.startswith(f"{GOLD_DIR}/states/"):
            where_clauses.append("state = ?")
            params.append(state)
        
        # NTEE code filter - use 'ntee_cd' column
        if ntee_code:
            where_clauses.append("ntee_cd LIKE ?")
            params.append(f'{ntee_code}%')
        
        where_sql = " AND ".join(where_clauses)
        
        # SQL query with relevance scoring - fetch all available columns for enrichment
        sql = f"""
            SELECT 
                name,
                city,
                state,
                ntee_cd,
                ein,
                revenue_amt,
                asset_amt,
                income_amt,
                CASE 
                    WHEN LOWER(name) LIKE LOWER(?) THEN 1.5
                    WHEN LOWER(name) LIKE LOWER(?) THEN 1.0
                    ELSE 0.5
                END as score
            FROM '{file_path}'
            WHERE {where_sql}
            ORDER BY score DESC, name
            LIMIT ?
        """
        
        # Execute query with parameters
        query_params = [f'{query}%', f'%{query}%'] + params + [limit]
        rows = conn.execute(sql, query_params).fetchall()
        
        # NTEE code descriptions for better context
        ntee_descriptions = {
            'E': 'Health Services',
            'E60': 'Health Support Services',
            'E61': 'Blood Supply',
            'E62': 'Emergency Medical Services',
            'E65': 'Organ & Tissue Banks',
            'E70': 'Public Health',
            'E80': 'Health Treatment - Primary Care',
            'E90': 'Nursing Services',
            'E20': 'Hospitals & Primary Medical Care',
            'E30': 'Ambulatory & Primary Health Care',
            'E32': 'Clinics & Community Health Centers',
            'P': 'Human Services',
            'B': 'Education',
            'X': 'Religion-Related',
            'A': 'Arts, Culture & Humanities',
        }
        
        # Convert to SearchResult objects
        for row in rows:
            org_name, city, state_code, ntee, ein, revenue, assets, income, score = row
            
            # Build a more informative description
            ntee_desc = None
            if ntee:
                # Try exact match first, then prefix match
                ntee_desc = ntee_descriptions.get(ntee)
                if not ntee_desc:
                    # Try first character (major category)
                    ntee_desc = ntee_descriptions.get(ntee[0]) if ntee else None
            
            description_parts = []
            if ntee_desc:
                description_parts.append(ntee_desc)
            
            # Convert financial data to numbers (handle None and string types)
            try:
                revenue_num = float(revenue) if revenue else 0
                assets_num = float(assets) if assets else 0
            except (ValueError, TypeError):
                revenue_num = 0
                assets_num = 0
            
            if revenue_num > 0:
                description_parts.append(f"Revenue: ${revenue_num:,.0f}")
            elif assets_num > 0:
                description_parts.append(f"Assets: ${assets_num:,.0f}")
            
            if not description_parts:
                description_parts.append(f"Nonprofit serving {city}")
            
            description = " • ".join(description_parts)
            
            results.append(SearchResult(
                result_type="organization",
                title=org_name if org_name else "Unknown",
                subtitle=f"{city}, {state_code}" + (f" - NTEE: {ntee}" if ntee else ""),
                description=description,
                url=f"/nonprofits-hf?search={ein}&state={state_code}",
                score=score,
                metadata={
                    "ein": ein,
                    "city": city,
                    "state": state_code,
                    "ntee_code": ntee,
                    "revenue": revenue,
                    "assets": assets,
                    "income": income
                }
            ))
        
        conn.close()
        logger.info(f"DuckDB search found {len(results)} organizations for query '{query}'")
        
    except Exception as e:
        logger.error(f"Organization search error: {e}")
    
    return results


def search_causes(query: str, limit: int = 10) -> List[SearchResult]:
    """Search causes and NTEE categories"""
    results = []
    
    try:
        # Search NTEE codes
        ntee_file = GOLD_DIR / "reference" / "causes_ntee_codes.parquet"
        logger.info(f"Searching causes in: {ntee_file}, exists: {ntee_file.exists()}")
        
        if ntee_file.exists():
            df = pd.read_parquet(ntee_file)
            logger.info(f"Loaded {len(df)} NTEE codes, columns: {df.columns.tolist()}")
            
            for _, row in df.iterrows():
                code = str(row.get('ntee_code', ''))
                description = str(row.get('description', ''))
                ntee_type = str(row.get('ntee_type', ''))
                
                score = max(
                    calculate_relevance_score(description, query),
                    calculate_relevance_score(code, query)
                )
                
                if score > 0.3:
                    results.append(SearchResult(
                        result_type="cause",
                        title=description,
                        subtitle=f"NTEE Code: {code}",
                        description=f"Category type: {ntee_type}",
                        url=f"/nonprofits?ntee_code={code}",
                        score=score,
                        metadata={
                            "ntee_code": code,
                            "ntee_type": ntee_type
                        }
                    ))
            
            logger.info(f"Found {len(results)} cause results for query '{query}'")
    
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
            contact_results = search_contacts(q, state, limit=max(3, limit // 2))
            all_results.extend(contact_results)
        
        if 'meetings' in requested_types:
            meeting_results = search_meetings(q, state, limit=max(3, limit // 2))
            all_results.extend(meeting_results)
        
        if 'organizations' in requested_types:
            org_results = search_organizations(q, state, ntee_code, limit=max(3, limit))
            all_results.extend(org_results)
        
        if 'causes' in requested_types:
            cause_results = search_causes(q, limit=max(3, limit // 2))
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
