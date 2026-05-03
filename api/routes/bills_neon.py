"""
Bills API Routes - Hybrid approach using Neon + Parquet
- Map aggregates: Neon PostgreSQL (fast, lightweight)
- Detailed bills & sessions: Parquet files (saves Neon space)
"""
from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import JSONResponse
from typing import Optional, List, Dict, Any
import asyncpg
import duckdb
import pandas as pd
from pathlib import Path
from loguru import logger
import os
from datetime import datetime, timedelta

from api.errors import ErrorDetail, parse_error

router = APIRouter(prefix="/bills", tags=["bills"])

# Database configuration (for map aggregates only)
NEON_DATABASE_URL_DEV = os.getenv("NEON_DATABASE_URL_DEV")
NEON_DATABASE_URL = os.getenv("NEON_DATABASE_URL")
DATABASE_URL = NEON_DATABASE_URL_DEV or NEON_DATABASE_URL

# Parquet configuration (for detailed bills)
GOLD_DIR = Path("data/gold")
IS_HF_SPACES = os.getenv("HF_SPACES") == "1"
HF_ORGANIZATION = os.getenv('HF_ORGANIZATION', 'CommunityOne')

if DATABASE_URL:
    logger.info(f"🗄️  Bills map using: {'DEV' if NEON_DATABASE_URL_DEV else 'PROD'} database")
    logger.info(f"📁 Bills details using: {'HuggingFace' if IS_HF_SPACES else 'local'} parquet")
else:
    logger.warning("⚠️  No database URL configured. Map endpoint will not work.")

# Connection pool
_pool = None

# Cache for map data (TTL: 5 minutes)
_map_cache = {}
_map_cache_time = None
MAP_CACHE_DURATION = timedelta(minutes=5)


def get_hf_dataset_url(dataset_name: str) -> str:
    """Convert dataset name to HuggingFace parquet URL."""
    return f"https://huggingface.co/datasets/{HF_ORGANIZATION}/{dataset_name}/resolve/main/data/train-00000-of-00001.parquet"

def get_data_source(file_path: Path, use_remote: bool = False) -> str:
    """Get data source (local path or remote URL) based on environment."""
    if not IS_HF_SPACES and not use_remote:
        return str(file_path)
    
    # Convert local path to HuggingFace dataset name
    parts = file_path.parts
    filename = parts[-1].replace('.parquet', '').replace('_', '-')
    
    # Handle nested state-specific files (if they exist)
    if 'states' in parts:
        state_idx = parts.index('states')
        state = parts[state_idx + 1].lower()
        dataset_name = f"states-{state}-{filename}"
        return get_hf_dataset_url(dataset_name)
    
    # Handle flat files in gold directory
    # Map: bills_bills.parquet -> one-bills
    dataset_mapping = {
        'bills-bills': 'one-bills',
        'bills-bill-actions': 'one-bill-actions',
        'bills-bill-sponsorships': 'one-bill-sponsorships',
        'bills-map-aggregates': 'one-bills-map-aggregates',
    }
    
    dataset_name = dataset_mapping.get(filename, filename)
    return get_hf_dataset_url(dataset_name)


async def get_pool():
    """Get or create asyncpg connection pool."""
    global _pool
    if _pool is None and DATABASE_URL:
        _pool = await asyncpg.create_pool(
            DATABASE_URL,
            min_size=1,
            max_size=10,
            command_timeout=60
        )
    return _pool


async def fetch_bills_from_parquet(
    state: str,
    q: Optional[str] = None,
    session: Optional[str] = None,
    topic: Optional[str] = None,
    chamber: Optional[str] = None,
    bill_type: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
) -> Dict[str, Any]:
    """Fetch bills from parquet files using DuckDB (detailed drill-down)."""
    try:
        # Use flat file structure (all states in one file)
        bills_file = GOLD_DIR / "bills_bills.parquet"
        
        # Get data source (local or remote HuggingFace URL)
        data_source = get_data_source(bills_file, use_remote=IS_HF_SPACES)
        
        # Connect to DuckDB
        conn = duckdb.connect()
        
        # Build SQL query - ALWAYS filter by state
        where_clauses = ["state = ?"]
        params = [state]
        
        # Topic filter (keyword search in title)
        if topic:
            topic_keywords = {
                'fluoride': 'fluorid',
                'dental': 'dental',
                'medicaid': 'medicaid',
                'oral health': 'oral|dental|teeth',
                'health': 'health',
                'education': 'education|school',
            }
            keyword = topic_keywords.get(topic.lower(), topic)
            
            # Handle multiple keywords with OR
            if '|' in keyword:
                keyword_parts = keyword.split('|')
                keyword_clauses = ["LOWER(title) LIKE LOWER(?)"] * len(keyword_parts)
                where_clauses.append(f"({' OR '.join(keyword_clauses)})")
                params.extend([f'%{kw}%' for kw in keyword_parts])
            else:
                where_clauses.append("LOWER(title) LIKE LOWER(?)")
                params.append(f'%{keyword}%')
        
        if q:
            where_clauses.append("(LOWER(title) LIKE LOWER(?) OR LOWER(bill_number) LIKE LOWER(?))")
            pattern = f'%{q}%'
            params.extend([pattern, pattern])
        
        if session:
            where_clauses.append("session = ?")
            params.append(session)
        
        # Chamber filter (based on bill number prefix)
        if chamber:
            if chamber.lower() == 'house':
                where_clauses.append("(bill_number LIKE 'HB%' OR bill_number LIKE 'HR%' OR bill_number LIKE 'HJR%' OR bill_number LIKE 'HCR%' OR bill_number LIKE 'HJM%' OR bill_number LIKE 'H %')")
            elif chamber.lower() == 'senate':
                where_clauses.append("(bill_number LIKE 'SB%' OR bill_number LIKE 'SR%' OR bill_number LIKE 'SJR%' OR bill_number LIKE 'SCR%' OR bill_number LIKE 'SJM%' OR bill_number LIKE 'S %')")
            elif chamber.lower() == 'joint':
                where_clauses.append("(bill_number LIKE '%JR%' OR bill_number LIKE '%JM%')")
        
        # Bill type filter (based on bill number pattern)
        if bill_type:
            if bill_type == 'bill':
                where_clauses.append("(bill_number LIKE 'HB%' OR bill_number LIKE 'SB%' OR bill_number LIKE 'AB%')")
            elif bill_type == 'resolution':
                where_clauses.append("(bill_number LIKE 'HR%' OR bill_number LIKE 'SR%' OR bill_number LIKE 'AR%')")
            elif bill_type == 'joint_resolution':
                where_clauses.append("(bill_number LIKE 'HJR%' OR bill_number LIKE 'SJR%' OR bill_number LIKE 'AJR%')")
            elif bill_type == 'concurrent_resolution':
                where_clauses.append("(bill_number LIKE 'HCR%' OR bill_number LIKE 'SCR%')")
            elif bill_type == 'memorial':
                where_clauses.append("(bill_number LIKE 'HJM%' OR bill_number LIKE 'SJM%')")
        
        # Status filter (based on latest_action_description)
        if status:
            status_keywords = {
                'enacted': 'Enacted',
                'passed': 'passed|Passed',
                'adopted': 'Adopted|adopted',
                'failed': 'Failed|failed',
                'introduced': 'Introduced|introduced',
                'referred': 'referred|Referred',
                'reported': 'reported|Reported'
            }
            keyword = status_keywords.get(status.lower(), status)
            
            if '|' in keyword:
                keyword_parts = keyword.split('|')
                keyword_clauses = ["LOWER(latest_action_description) LIKE LOWER(?)"] * len(keyword_parts)
                where_clauses.append(f"({' OR '.join(keyword_clauses)})")
                params.extend([f'%{kw}%' for kw in keyword_parts])
            else:
                where_clauses.append("LOWER(latest_action_description) LIKE LOWER(?)")
                params.append(f'%{keyword}%')
        
        where_clause = " AND ".join(where_clauses)
        
        # Count total
        count_sql = f"""
            SELECT COUNT(*) as total
            FROM read_parquet(?)
            WHERE {where_clause}
        """
        count_params = [data_source] + params
        total = conn.execute(count_sql, count_params).fetchone()[0]
        
        # Fetch bills
        sql = f"""
            SELECT 
                bill_id,
                bill_number,
                title,
                classification,
                session,
                session_name,
                first_action_date,
                latest_action_date,
                latest_action_description,
                jurisdiction_name
            FROM read_parquet(?)
            WHERE {where_clause}
            ORDER BY latest_action_date DESC NULLS LAST, bill_number DESC
            LIMIT ? OFFSET ?
        """
        
        query_params = [data_source] + params + [limit, offset]
        rows = conn.execute(sql, query_params).fetchall()
        
        bills = []
        for row in rows:
            bills.append({
                "bill_id": row[0],
                "bill_number": row[1],
                "title": row[2],
                "classification": list(row[3]) if row[3] else [],
                "session": row[4],
                "session_name": row[5],
                "first_action_date": str(row[6]) if row[6] else None,
                "latest_action_date": str(row[7]) if row[7] else None,
                "latest_action_description": row[8],
                "jurisdiction_name": row[9]
            })
        
        conn.close()
        
        return {
            "state": state,
            "query": q,
            "topic": topic,
            "chamber": chamber,
            "bill_type": bill_type,
            "status": status,
            "session": session,
            "bills": bills,
            "total": total,
            "limit": limit,
            "offset": offset,
            "source": "parquet"
        }
        
    except Exception as e:
        logger.error(f"Error fetching bills from parquet: {e}")
        raise


async def fetch_sessions_from_parquet(state: str) -> Dict[str, Any]:
    """Fetch sessions from parquet files using DuckDB."""
    try:
        # Use flat file structure (all states in one file)
        bills_file = GOLD_DIR / "bills_bills.parquet"
        
        # Get data source
        data_source = get_data_source(bills_file, use_remote=IS_HF_SPACES)
        
        # Connect to DuckDB
        conn = duckdb.connect()
        
        # Aggregate sessions - filter by state
        sql = """
            SELECT 
                session,
                MAX(session_name) as session_name,
                MIN(first_action_date) as start_date,
                MAX(latest_action_date) as end_date,
                COUNT(*) as bill_count
            FROM read_parquet(?)
            WHERE state = ?
            GROUP BY session, session_name
            ORDER BY session DESC
        """
        
        rows = conn.execute(sql, [data_source, state]).fetchall()
        
        sessions = []
        for row in rows:
            sessions.append({
                "session": row[0],
                "session_name": row[1],
                "start_date": str(row[2]) if row[2] else None,
                "end_date": str(row[3]) if row[3] else None,
                "bill_count": row[4]
            })
        
        conn.close()
        
        return {
            "state": state,
            "sessions": sessions,
            "total_sessions": len(sessions),
            "source": "parquet"
        }
        
    except Exception as e:
        logger.error(f"Error fetching sessions from parquet: {e}")
        raise


async def fetch_map_data_from_neon(
    topic: Optional[str] = None,
    session: Optional[str] = None
) -> Dict[str, Any]:
    """Fetch map aggregates from Neon PostgreSQL."""
    pool = await get_pool()
    
    # Use cache if available
    global _map_cache, _map_cache_time
    cache_key = f"{topic or 'all'}_{session or 'all'}"
    
    now = datetime.now()
    if _map_cache_time and (now - _map_cache_time) < MAP_CACHE_DURATION:
        if cache_key in _map_cache:
            logger.debug(f"🚀 Map cache hit for {cache_key}")
            return _map_cache[cache_key]
    
    async with pool.acquire() as conn:
        # For now, we only support topic='all' (no topic filtering yet)
        # Session filtering would require aggregating bills on-the-fly
        
        sql = """
            SELECT 
                state_code,
                topic,
                total_bills,
                type_bill,
                type_resolution,
                type_concurrent_resolution,
                type_joint_resolution,
                type_constitutional_amendment,
                status_enacted,
                status_failed,
                status_pending,
                primary_type,
                primary_status,
                map_category,
                sample_bills,
                last_updated
            FROM bills_map_aggregates
            WHERE topic = $1
        """
        
        requested_topic = topic.lower() if topic else 'all'
        rows = await conn.fetch(sql, requested_topic)
        
        # If topic-specific data not found, return empty (don't fallback)
        if not rows:
            logger.warning(f"📊 No pre-computed data for topic '{requested_topic}'")
            return {
                "topic": requested_topic,
                "session": session,
                "states": {},
                "total_states": 0,
                "message": f"No data available for topic '{requested_topic}'. Try 'all' or pre-compute aggregates for this topic.",
                "source": "neon"
            }
        
        state_data = {}
        for row in rows:
            state_code = row['state_code']
            
            # Parse sample bills JSON
            sample_bills = row['sample_bills'] or []
            if isinstance(sample_bills, str):
                import json
                sample_bills = json.loads(sample_bills)
            
            state_data[state_code] = {
                "state": state_code,
                "total_bills": row['total_bills'],
                "type_counts": {
                    "bill": row['type_bill'],
                    "resolution": row['type_resolution'],
                    "concurrent_resolution": row['type_concurrent_resolution'],
                    "joint_resolution": row['type_joint_resolution'],
                    "constitutional_amendment": row['type_constitutional_amendment']
                },
                "status_counts": {
                    "enacted": row['status_enacted'] or 0,
                    "failed": row['status_failed'] or 0,
                    "pending": row['status_pending'] or 0
                },
                "primary_type": row['primary_type'],
                "primary_status": row['primary_status'],
                "map_category": row['map_category'],
                "sample_bills": sample_bills,
                "last_updated": row['last_updated'].isoformat() if row['last_updated'] else None
            }
        
        # Build dynamic legend based on actual data
        unique_types = set()
        for state in state_data.values():
            if state['primary_type']:
                unique_types.add(state['primary_type'])
        
        # Map types to user-friendly names
        type_labels = {
            'mandate': 'Mandate',
            'removal': 'Removal',
            'study': 'Study',
            'funding': 'Funding',
            'coverage_expansion': 'Coverage Expansion',
            'screening': 'Screening',
            'provider_access': 'Provider Access',
            'expansion': 'Expansion',
            'coverage': 'Coverage',
            'reimbursement': 'Reimbursement',
            'eligibility': 'Eligibility',
            'requirement': 'Requirement',
            'curriculum': 'Curriculum',
            'reform': 'Reform',
            'protection': 'Protection',
            'restriction': 'Restriction',
            'other': 'Other'
        }
        
        legend_types = {t: type_labels.get(t, t.replace('_', ' ').title()) for t in unique_types}
        
        result = {
            "topic": requested_topic,
            "session": session,
            "states": state_data,
            "total_states": len(state_data),
            "legend": {
                "types": legend_types,
                "statuses": {
                    "enacted": "Enacted",
                    "failed": "Failed",
                    "pending": "Pending"
                }
            },
            "cached": True,
            "source": "neon"
        }
        
        # Update cache
        _map_cache[cache_key] = result
        _map_cache_time = now
        
        return result


@router.get("")
async def get_bills(
    state: str = Query(..., description="State abbreviation (e.g., MA, AL)"),
    q: Optional[str] = Query(None, description="Search query (bill number or title)"),
    session: Optional[str] = Query(None, description="Legislative session"),
    topic: Optional[str] = Query(None, description="Policy topic (e.g., fluoride, dental, medicaid)"),
    chamber: Optional[str] = Query(None, description="Legislative chamber (house, senate, joint)"),
    bill_type: Optional[str] = Query(None, description="Bill type (bill, resolution, joint_resolution, concurrent_resolution, memorial)"),
    status: Optional[str] = Query(None, description="Bill status (enacted, passed, adopted, failed, introduced, referred, reported)"),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0)
):
    """
    Search legislative bills using parquet files (detailed drill-down).
    
    **Examples:**
    - `/api/bills?state=AL&q=dental` - Search Alabama bills for "dental"
    - `/api/bills?state=AL&session=2024rs` - Get all 2024 regular session bills
    - `/api/bills?state=AL&topic=fluoride` - Get fluoride-related Alabama bills
    - `/api/bills?state=AL&chamber=house` - Get House bills only
    - `/api/bills?state=AL&bill_type=bill` - Get only bills (not resolutions)
    - `/api/bills?state=AL&status=enacted` - Get enacted bills only
    - `/api/bills?state=AL&limit=50` - Browse recent Alabama bills
    """
    try:
        result = await fetch_bills_from_parquet(
            state=state.upper(),
            q=q,
            session=session,
            topic=topic,
            chamber=chamber,
            bill_type=bill_type,
            status=status,
            limit=limit,
            offset=offset
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Bills query error for state={state}: {e}")
        
        error_detail = parse_error(e, context={
            "state": state,
            "query": q,
            "session": session
        })
        
        return JSONResponse(
            status_code=500,
            content=error_detail.model_dump()
        )


@router.get("/sessions")
async def get_sessions(
    state: str = Query(..., description="State abbreviation (e.g., MA, AL)")
):
    """
    Get legislative sessions for a state using parquet files.
    
    **Examples:**
    - `/api/bills/sessions?state=MA` - Get all Massachusetts sessions
    """
    try:
        result = await fetch_sessions_from_parquet(state=state.upper())
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Sessions query error for state={state}: {e}")
        
        error_detail = parse_error(e, context={
            "state": state
        })
        
        return JSONResponse(
            status_code=500,
            content=error_detail.model_dump()
        )


@router.get("/map")
async def get_bill_map_data(
    topic: Optional[str] = Query(None, description="Topic to filter (e.g., dental, health, education)"),
    session: Optional[str] = Query(None, description="Legislative session")
):
    """
    Get aggregated bill data for choropleth map using Neon PostgreSQL.
    
    Returns pre-computed state-level aggregates for instant visualization.
    
    **Examples:**
    - `/api/bills/map` - Get national bill map data
    - `/api/bills/map?topic=dental` - Map dental legislation (not yet implemented)
    """
    try:
        if not DATABASE_URL:
            raise HTTPException(status_code=503, detail="Database not configured")
        
        result = await fetch_map_data_from_neon(topic=topic, session=session)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Map data query error: {e}")
        
        error_detail = parse_error(e, context={
            "topic": topic,
            "session": session
        })
        
        return JSONResponse(
            status_code=500,
            content=error_detail.model_dump()
        )
