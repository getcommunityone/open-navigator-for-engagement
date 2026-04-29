"""
Bills API Routes - Legislative bill data from OpenStates
"""
from fastapi import APIRouter, Query, HTTPException
from typing import Optional, List, Dict
import duckdb
from pathlib import Path
from loguru import logger
import re

router = APIRouter(prefix="/api/bills", tags=["bills"])

GOLD_DIR = Path("data/gold")


def classify_bill_type(title: str, classification: list) -> str:
    """
    Classify bill into ban, restriction, protection, or other.
    
    Uses keyword matching on title and classification.
    """
    title_lower = title.lower()
    
    # Ban keywords
    ban_keywords = [
        'prohibit', 'ban', 'forbid', 'unlawful', 'illegal', 
        'criminalize', 'outlaw', 'prevent', 'bar from'
    ]
    
    # Restriction keywords
    restriction_keywords = [
        'restrict', 'limit', 'regulate', 'require', 'mandate',
        'control', 'impose', 'condition', 'constraint'
    ]
    
    # Protection keywords
    protection_keywords = [
        'protect', 'preserve', 'safeguard', 'ensure', 'guarantee',
        'expand', 'increase', 'enhance', 'support', 'fund'
    ]
    
    # Check for bans first (strongest signal)
    if any(keyword in title_lower for keyword in ban_keywords):
        return 'ban'
    
    # Check for protections
    if any(keyword in title_lower for keyword in protection_keywords):
        return 'protection'
    
    # Check for restrictions
    if any(keyword in title_lower for keyword in restriction_keywords):
        return 'restriction'
    
    # Default
    return 'other'


def determine_bill_status(latest_action: str, latest_date: str) -> str:
    """
    Determine if bill was enacted, failed, or is pending.
    """
    if not latest_action:
        return 'pending'
    
    action_lower = latest_action.lower()
    
    # Enacted/Passed
    if any(word in action_lower for word in ['signed', 'enacted', 'approved', 'passed both', 'became law']):
        return 'enacted'
    
    # Failed
    if any(word in action_lower for word in ['failed', 'defeated', 'rejected', 'died', 'withdrawn', 'vetoed']):
        return 'failed'
    
    # Pending (default)
    return 'pending'


@router.get("")
async def search_bills(
    q: Optional[str] = Query(None, description="Search query for bill title or number"),
    state: Optional[str] = Query("AL", description="State code (e.g., AL, GA, MA)"),
    session: Optional[str] = Query(None, description="Legislative session (e.g., 2024rs)"),
    limit: int = Query(20, ge=1, le=100, description="Maximum results"),
    offset: int = Query(0, ge=0, description="Number of results to skip")
):
    """
    Search legislative bills from OpenStates data.
    
    **Examples:**
    - `/api/bills?state=AL&q=dental` - Search Alabama bills for "dental"
    - `/api/bills?state=AL&session=2024rs` - Get all 2024 regular session bills
    - `/api/bills?state=AL&limit=50` - Browse recent Alabama bills
    """
    try:
        # Build file path
        bills_file = GOLD_DIR / "states" / state / "bills_bills.parquet"
        
        if not bills_file.exists():
            raise HTTPException(
                status_code=404, 
                detail=f"No bills data found for state: {state}"
            )
        
        # Connect to DuckDB
        conn = duckdb.connect()
        
        # Build SQL query
        where_clauses = []
        params = []
        
        if q:
            where_clauses.append("(LOWER(title) LIKE LOWER(?) OR LOWER(bill_number) LIKE LOWER(?))")
            pattern = f'%{q}%'
            params.extend([pattern, pattern])
        
        if session:
            where_clauses.append("session = ?")
            params.append(session)
        
        where_clause = " AND ".join(where_clauses) if where_clauses else "1=1"
        
        # Count total
        count_sql = f"""
            SELECT COUNT(*) as total
            FROM read_parquet(?)
            WHERE {where_clause}
        """
        count_params = [str(bills_file)] + params
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
        
        query_params = [str(bills_file)] + params + [limit, offset]
        rows = conn.execute(sql, query_params).fetchall()
        
        bills = []
        for row in rows:
            bills.append({
                "bill_id": row[0],
                "bill_number": row[1],
                "title": row[2],
                "classification": row[3],
                "session": row[4],
                "session_name": row[5],
                "first_action_date": row[6],
                "latest_action_date": row[7],
                "latest_action": row[8],
                "jurisdiction": row[9]
            })
        
        conn.close()
        
        return {
            "total": total,
            "bills": bills,
            "pagination": {
                "limit": limit,
                "offset": offset,
                "has_more": offset + len(bills) < total
            },
            "filters": {
                "state": state,
                "query": q,
                "session": session
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Bills search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions")
async def get_sessions(
    state: str = Query("AL", description="State code")
):
    """Get available legislative sessions for a state."""
    try:
        bills_file = GOLD_DIR / "states" / state / "bills_bills.parquet"
        
        if not bills_file.exists():
            raise HTTPException(
                status_code=404,
                detail=f"No bills data found for state: {state}"
            )
        
        conn = duckdb.connect()
        
        sql = """
            SELECT DISTINCT 
                session,
                session_name,
                MIN(first_action_date) as start_date,
                MAX(latest_action_date) as end_date,
                COUNT(*) as bill_count
            FROM read_parquet(?)
            GROUP BY session, session_name
            ORDER BY session DESC
        """
        
        rows = conn.execute(sql, [str(bills_file)]).fetchall()
        
        sessions = []
        for row in rows:
            sessions.append({
                "session": row[0],
                "session_name": row[1],
                "start_date": row[2],
                "end_date": row[3],
                "bill_count": row[4]
            })
        
        conn.close()
        
        return {
            "state": state,
            "sessions": sessions,
            "total_sessions": len(sessions)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Sessions fetch error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
