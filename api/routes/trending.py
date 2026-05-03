"""
Trending causes/topics API endpoints

Serves database-driven causes for homepage and other features.
"""
from fastapi import APIRouter, Query
from typing import List, Optional
from pydantic import BaseModel
import polars as pl
from pathlib import Path
from loguru import logger

router = APIRouter(prefix="/api/trending", tags=["trending"])


class CauseItem(BaseModel):
    """A trending cause/topic"""
    name: str
    icon: str
    category: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    popularity_rank: Optional[int] = None


class TrendingResponse(BaseModel):
    """Response with trending causes"""
    causes: List[CauseItem]
    total: int


def get_everyorg_causes(limit: int = 20) -> List[CauseItem]:
    """Load EveryOrg causes (popular, curated categories)"""
    try:
        path = Path("data/gold/causes_everyorg_causes.parquet")
        if not path.exists():
            logger.warning(f"EveryOrg causes file not found: {path}")
            return []
        
        df = pl.read_parquet(path)
        
        # Sort by popularity rank
        df = df.sort("popularity_rank")
        
        # Take top N
        df = df.head(limit)
        
        causes = []
        for row in df.iter_rows(named=True):
            # Check if image exists
            cause_id = row['cause_id']
            image_url = f"/images/causes/everyorg_{cause_id}_square.png"
            
            causes.append(CauseItem(
                name=row['cause_name'],
                icon=row.get('icon', '📌'),
                category=row.get('category', 'general'),
                description=row.get('description', ''),
                image_url=image_url,
                popularity_rank=row.get('popularity_rank')
            ))
        
        return causes
    
    except Exception as e:
        logger.error(f"Error loading EveryOrg causes: {e}")
        return []


def get_ntee_causes(limit: int = 20, level: Optional[int] = None) -> List[CauseItem]:
    """Load NTEE code causes (IRS nonprofit categories)
    
    Args:
        limit: Max number to return
        level: NTEE level (1=major groups like Health, 2=subcategories)
    """
    try:
        path = Path("data/gold/causes_ntee_codes.parquet")
        if not path.exists():
            logger.warning(f"NTEE codes file not found: {path}")
            return []
        
        df = pl.read_parquet(path)
        
        # Filter by level if specified
        if level is not None:
            df = df.filter(pl.col('level') == level)
        
        # Major groups first (level 1), then by code
        df = df.sort(['level', 'ntee_code'])
        
        # Take top N
        df = df.head(limit)
        
        causes = []
        for row in df.iter_rows(named=True):
            # Map NTEE codes to icons (simplified)
            code = row['ntee_code']
            icon_map = {
                'A': '🎨',  # Arts
                'B': '📚',  # Education
                'C': '🌍',  # Environment
                'D': '🐾',  # Animal
                'E': '⚕️',  # Health
                'F': '🏥',  # Mental Health
                'G': '🏛️',  # Diseases
                'H': '🏥',  # Medical Research
                'I': '🔬',  # Crime/Legal
                'J': '👥',  # Employment
                'K': '🍽️',  # Food/Nutrition
                'L': '🏠',  # Housing
                'M': '🛡️',  # Public Safety
                'N': '🎯',  # Recreation
                'O': '⚖️',  # Youth Development
                'P': '👶',  # Human Services
                'Q': '🌐',  # International
                'R': '🏛️',  # Civil Rights
                'S': '🤝',  # Community Improvement
                'T': '💼',  # Philanthropy
                'U': '🔬',  # Science
                'V': '⚡',  # Social Science
                'W': '📢',  # Public Affairs
                'X': '🏛️',  # Religion
                'Y': '🏛️',  # Mutual Benefit
                'Z': '🔤',  # Unknown
            }
            
            icon = icon_map.get(code[0] if code else 'Z', '📌')
            
            # Check if image exists
            image_url = f"/images/causes/ntee_{code}_square.png"
            
            causes.append(CauseItem(
                name=row['description'],
                icon=icon,
                category=row.get('ntee_type', 'ntee'),
                description=f"NTEE Code {code}",
                image_url=image_url,
                popularity_rank=None
            ))
        
        return causes
    
    except Exception as e:
        logger.error(f"Error loading NTEE causes: {e}")
        return []


@router.get("", response_model=TrendingResponse)
async def get_trending_causes(
    source: str = Query("everyorg", description="Source: 'everyorg', 'ntee', or 'mixed'"),
    limit: int = Query(12, ge=1, le=100, description="Max number of causes to return"),
    level: Optional[int] = Query(None, description="NTEE level filter (1 or 2)")
) -> TrendingResponse:
    """
    Get trending causes for homepage
    
    Returns popular causes from database, with generated images.
    
    **Sources:**
    - `everyorg`: Curated popular causes (39 total)
    - `ntee`: IRS nonprofit categories (196 total)  
    - `mixed`: Mix of both (6 from each)
    
    **Examples:**
    - `/api/trending?source=everyorg&limit=12` - Top 12 popular causes
    - `/api/trending?source=ntee&level=1` - Major NTEE categories
    - `/api/trending?source=mixed` - Mix of both sources
    """
    causes = []
    
    if source == "everyorg":
        causes = get_everyorg_causes(limit=limit)
    
    elif source == "ntee":
        causes = get_ntee_causes(limit=limit, level=level)
    
    elif source == "mixed":
        # Mix: 50% from each source
        half = limit // 2
        everyorg = get_everyorg_causes(limit=half)
        ntee = get_ntee_causes(limit=half, level=1)  # Only major groups
        
        # Interleave them
        causes = []
        for i in range(max(len(everyorg), len(ntee))):
            if i < len(everyorg):
                causes.append(everyorg[i])
            if i < len(ntee):
                causes.append(ntee[i])
    
    else:
        # Default to everyorg
        causes = get_everyorg_causes(limit=limit)
    
    return TrendingResponse(
        causes=causes,
        total=len(causes)
    )


@router.get("/stats")
async def get_trending_stats():
    """Get stats about available causes"""
    try:
        everyorg_path = Path("data/gold/causes_everyorg_causes.parquet")
        ntee_path = Path("data/gold/causes_ntee_codes.parquet")
        
        everyorg_count = 0
        ntee_count = 0
        
        if everyorg_path.exists():
            df = pl.read_parquet(everyorg_path)
            everyorg_count = len(df)
        
        if ntee_path.exists():
            df = pl.read_parquet(ntee_path)
            ntee_count = len(df)
        
        # Count generated images
        images_dir = Path("data/media/causes")
        images_count = 0
        if images_dir.exists():
            images_count = len(list(images_dir.glob("*_square.png")))
        
        return {
            "everyorg_causes": everyorg_count,
            "ntee_causes": ntee_count,
            "total_causes": everyorg_count + ntee_count,
            "generated_images": images_count
        }
    
    except Exception as e:
        logger.error(f"Error getting trending stats: {e}")
        return {
            "everyorg_causes": 0,
            "ntee_causes": 0,
            "total_causes": 0,
            "generated_images": 0,
            "error": str(e)
        }
