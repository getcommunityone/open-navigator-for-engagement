"""
FastAPI application for the Oral Health Policy Pulse system.

Provides REST API endpoints for:
- Initiating policy analysis workflows
- Querying advocacy opportunities
- Retrieving generated materials
- Accessing visualizations
- System status and monitoring
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, date
from fastapi import FastAPI, HTTPException, Query, BackgroundTasks
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.docs import get_swagger_ui_html
from pydantic import BaseModel, Field
from loguru import logger
import os

from agents.orchestrator import OrchestratorAgent
from agents.scraper import ScraperAgent
from agents.parser import ParserAgent
from agents.classifier import ClassifierAgent
from agents.sentiment import SentimentAnalyzerAgent
from agents.advocacy import AdvocacyWriterAgent
from pipeline.delta_lake import DeltaLakePipeline
from visualization.heatmap import AdvocacyHeatmap
from config import settings

# Initialize FastAPI app
app = FastAPI(
    title="Open Navigator for Engagement API",
    description="Multi-agent system for analyzing local government oral health policy discussions",
    version="1.0.0",
    docs_url=None,  # Disable default docs to use custom
    redoc_url="/redoc",  # Keep ReDoc at /redoc
    openapi_tags=[
        {
            "name": "auth",
            "description": "Authentication and user management"
        },
        {
            "name": "workflows",
            "description": "Policy analysis workflows"
        },
        {
            "name": "opportunities",
            "description": "Advocacy opportunities"
        }
    ]
)

# Custom OpenAPI schema with logo
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    from fastapi.openapi.utils import get_openapi
    
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    
    # Add custom logo
    openapi_schema["info"]["x-logo"] = {
        "url": "/static/communityone_logo.svg",
        "altText": "CommunityOne Logo"
    }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for logo
static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend", "public")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
else:
    logger.warning(f"Static directory not found: {static_dir}")

# Include authentication routes
from api.routes import auth as auth_routes
from api.database import init_db

app.include_router(auth_routes.router)

# Custom Swagger UI with logo
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    """Custom Swagger UI with CommunityOne logo"""
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=f"{app.title} - API Documentation",
        swagger_favicon_url="/static/communityone_logo_64.png",
        swagger_ui_parameters={
            "defaultModelsExpandDepth": -1,
            "docExpansion": "list",
            "filter": True,
            "syntaxHighlight.theme": "monokai"
        }
    )

# Initialize database on startup
@app.on_event("startup")
async def init_database():
    """Initialize authentication database"""
    try:
        init_db()
        logger.info("✅ Authentication database initialized")
    except Exception as e:
        logger.warning(f"⚠️  Database initialization skipped: {e}")

# Initialize components
orchestrator = OrchestratorAgent()
pipeline = DeltaLakePipeline()
heatmap_generator = AdvocacyHeatmap()


# Pydantic models for API
class ScrapeTarget(BaseModel):
    """Configuration for a scraping target."""
    url: str
    municipality: str
    state: str
    platform: str = "generic"


class WorkflowRequest(BaseModel):
    """Request to start a new analysis workflow."""
    scrape_targets: List[ScrapeTarget]
    date_range: Optional[Dict[str, str]] = None
    description: Optional[str] = None


class WorkflowResponse(BaseModel):
    """Response for workflow operations."""
    workflow_id: str
    status: str
    message: str


class OpportunityFilter(BaseModel):
    """Filters for querying opportunities."""
    state: Optional[str] = None
    municipality: Optional[str] = None
    topic: Optional[str] = None
    urgency: Optional[str] = None
    min_date: Optional[date] = None
    max_date: Optional[date] = None


class OpportunityResponse(BaseModel):
    """Response containing advocacy opportunities."""
    opportunities: List[Dict[str, Any]]
    total_count: int
    filters_applied: Dict[str, Any]


class SystemStatus(BaseModel):
    """System status information."""
    status: str
    active_workflows: int
    agent_status: Dict[str, Any]
    last_update: datetime


# API Endpoints

@app.get("/", response_class=HTMLResponse)
async def root():
    """Root endpoint with API information."""
    html_content = """
    <!DOCTYPE html>
    <html>
        <head>
            <title>Open Navigator for Engagement API</title>
            <style>
                body { 
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                    max-width: 900px; 
                    margin: 50px auto; 
                    padding: 20px;
                    line-height: 1.6;
                }
                .header {
                    display: flex;
                    align-items: center;
                    gap: 20px;
                    margin-bottom: 30px;
                    border-bottom: 2px solid #1976d2;
                    padding-bottom: 20px;
                }
                .logo {
                    width: 80px;
                    height: 80px;
                }
                h1 { 
                    color: #1976d2;
                    margin: 0;
                }
                .tagline {
                    color: #666;
                    font-size: 1.1em;
                }
                .endpoint { 
                    background: linear-gradient(135deg, #f5f5f5 0%, #e8f4f8 100%);
                    padding: 15px;
                    margin: 10px 0;
                    border-radius: 8px;
                    border-left: 4px solid #1976d2;
                }
                .endpoint strong {
                    color: #1976d2;
                }
                code { 
                    background: #e0e0e0;
                    padding: 3px 8px;
                    border-radius: 4px;
                    font-family: 'Courier New', monospace;
                }
                .docs-link {
                    display: inline-block;
                    background: #1976d2;
                    color: white;
                    padding: 12px 24px;
                    text-decoration: none;
                    border-radius: 6px;
                    margin-top: 20px;
                    transition: background 0.3s;
                }
                .docs-link:hover {
                    background: #1565c0;
                }
            </style>
        </head>
        <body>
            <div class="header">
                <img src="/static/communityone_logo.svg" alt="CommunityOne Logo" class="logo">
                <div>
                    <h1>Open Navigator for Engagement API</h1>
                    <p class="tagline">Multi-agent system for analyzing local government policy discussions</p>
                </div>
            </div>
            
            <h2>🔑 Key Endpoints:</h2>
            <div class="endpoint">
                <strong>POST /workflow/start</strong> - Start a new analysis workflow
            </div>
            <div class="endpoint">
                <strong>GET /opportunities</strong> - Query advocacy opportunities
            </div>
            <div class="endpoint">
                <strong>GET /heatmap</strong> - Get advocacy heatmap visualization
            </div>
            <div class="endpoint">
                <strong>GET /status</strong> - System status and health
            </div>
            <div class="endpoint">
                <strong>POST /auth/login/{provider}</strong> - OAuth login (HuggingFace, Google, Facebook, GitHub)
            </div>
            
            <a href="/docs" class="docs-link">📚 View Full API Documentation</a>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@app.post("/workflow/start", response_model=WorkflowResponse)
async def start_workflow(
    request: WorkflowRequest,
    background_tasks: BackgroundTasks
):
    """
    Start a new policy analysis workflow.
    
    This initiates the full multi-agent pipeline:
    1. Scrape meeting minutes from specified sources
    2. Parse and structure the data
    3. Classify by oral health topics
    4. Analyze sentiment and policy stance
    5. Generate advocacy materials
    """
    try:
        # Register agents with orchestrator
        orchestrator.register_agent(ScraperAgent())
        orchestrator.register_agent(ParserAgent())
        orchestrator.register_agent(ClassifierAgent())
        orchestrator.register_agent(SentimentAnalyzerAgent())
        orchestrator.register_agent(AdvocacyWriterAgent())
        
        # Convert targets to dict format
        targets = [target.dict() for target in request.scrape_targets]
        
        # Start workflow in background
        background_tasks.add_task(
            orchestrator.execute_pipeline,
            targets,
            request.date_range
        )
        
        return WorkflowResponse(
            workflow_id="wf-" + datetime.utcnow().strftime("%Y%m%d-%H%M%S"),
            status="started",
            message=f"Workflow started with {len(targets)} targets"
        )
        
    except Exception as e:
        logger.error(f"Error starting workflow: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/workflow/{workflow_id}/status")
async def get_workflow_status(workflow_id: str):
    """Get the status of a specific workflow."""
    # Query workflow status from orchestrator
    # This is a placeholder - would query actual workflow state
    return {
        "workflow_id": workflow_id,
        "status": "running",
        "stage": "classification",
        "progress": 0.6
    }


@app.get("/opportunities", response_model=OpportunityResponse)
async def get_opportunities(
    state: Optional[str] = Query(None, description="Filter by state code"),
    municipality: Optional[str] = Query(None, description="Filter by municipality"),
    topic: Optional[str] = Query(None, description="Filter by policy topic"),
    urgency: Optional[str] = Query(None, description="Filter by urgency level"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum results to return")
):
    """
    Query advocacy opportunities.
    
    Returns a list of identified opportunities for advocacy action
    based on the specified filters.
    """
    try:
        # Query from Delta Lake
        opportunities = pipeline.query_opportunities_by_state(state, urgency)
        
        # Apply additional filters
        if municipality:
            opportunities = [
                opp for opp in opportunities
                if opp.get("municipality", "").lower() == municipality.lower()
            ]
        
        if topic:
            opportunities = [
                opp for opp in opportunities
                if opp.get("topic") == topic
            ]
        
        # Limit results
        opportunities = opportunities[:limit]
        
        return OpportunityResponse(
            opportunities=opportunities,
            total_count=len(opportunities),
            filters_applied={
                "state": state,
                "municipality": municipality,
                "topic": topic,
                "urgency": urgency
            }
        )
        
    except Exception as e:
        logger.error(f"Error querying opportunities: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# React frontend endpoints with /api/ prefix
@app.get("/api/opportunities")
async def get_api_opportunities(
    state: Optional[str] = Query(None),
    topic: Optional[str] = Query(None),
    urgency: Optional[str] = Query(None),
    limit: int = Query(100)
):
    """API endpoint for React frontend opportunities page."""
    try:
        opportunities = pipeline.query_opportunities_by_state(state, urgency)
        
        if topic:
            opportunities = [o for o in opportunities if o.get("topic") == topic]
        
        return {"opportunities": opportunities[:limit]}
    except Exception as e:
        logger.error(f"Error: {e}")
        return {"opportunities": []}


@app.get("/api/documents")
async def get_api_documents(
    search: Optional[str] = Query(None),
    page: int = Query(1),
    limit: int = Query(20)
):
    """API endpoint for React frontend documents page."""
    try:
        # Get all opportunities (documents)
        documents = pipeline.query_opportunities_by_state(None, None)
        
        # Apply search filter
        if search:
            search_lower = search.lower()
            documents = [
                d for d in documents
                if search_lower in d.get("title", "").lower() or
                   search_lower in d.get("municipality", "").lower() or
                   search_lower in d.get("content", "").lower()
            ]
        
        # Paginate
        start = (page - 1) * limit
        end = start + limit
        
        return {
            "documents": documents[start:end],
            "total": len(documents),
            "page": page,
            "limit": limit
        }
    except Exception as e:
        logger.error(f"Error: {e}")
        return {"documents": [], "total": 0}


@app.get("/opportunities/{opportunity_id}")
async def get_opportunity_detail(opportunity_id: str):
    """Get detailed information about a specific opportunity."""
    # Query specific opportunity
    document = pipeline.get_document_by_id(opportunity_id)
    
    if not document:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    
    return document


@app.get("/opportunities/{opportunity_id}/materials")
async def get_advocacy_materials(opportunity_id: str):
    """Get generated advocacy materials for an opportunity."""
    # Query materials from Delta Lake
    # This is a placeholder
    return {
        "opportunity_id": opportunity_id,
        "materials": {
            "email": {
                "subject": "Support Oral Health Policy",
                "body": "..."
            },
            "talking_points": [],
            "social_media": {}
        }
    }


@app.get("/heatmap", response_class=HTMLResponse)
async def get_heatmap(
    urgency: Optional[str] = Query(None, description="Filter by urgency level")
):
    """
    Get interactive heatmap visualization.
    
    Returns an HTML page with an interactive map showing
    advocacy opportunities across the country.
    """
    try:
        # Query opportunities
        opportunities = pipeline.query_opportunities_by_state(None, urgency)
        
        # Generate map
        m = heatmap_generator.create_folium_map(
            opportunities,
            title="Open Navigator for Engagement - Advocacy Heatmap"
        )
        
        # Return HTML
        return HTMLResponse(content=m._repr_html_())
        
    except Exception as e:
        logger.error(f"Error generating heatmap: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/dashboard")
async def get_dashboard():
    """
    Get complete dashboard data including statistics and visualizations.
    """
    try:
        # Query all opportunities
        opportunities = pipeline.query_opportunities_by_state(None, None)
        
        # Generate dashboard
        dashboard = heatmap_generator.create_dashboard(opportunities)
        
        # Convert visualizations to JSON-serializable format
        return {
            "statistics": dashboard["statistics"],
            "topic_distribution": dashboard["topic_distribution"].to_json(),
            "timeline": dashboard["timeline"].to_json()
        }
        
    except Exception as e:
        logger.error(f"Error generating dashboard: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/dashboard")
async def get_api_dashboard():
    """
    Get dashboard statistics for React frontend.
    Returns data in format expected by frontend Dashboard component.
    """
    try:
        # Query all opportunities
        opportunities = pipeline.query_opportunities_by_state(None, None)
        
        # Count topics
        topics_count = {}
        for opp in opportunities:
            topic = opp.get("topic", "unknown")
            topics_count[topic] = topics_count.get(topic, 0) + 1
        
        # Get unique states
        states = set(opp.get("state") for opp in opportunities if opp.get("state"))
        
        # Get recent opportunities (last 10)
        recent = sorted(
            opportunities,
            key=lambda x: x.get("meeting_date", ""),
            reverse=True
        )[:10]
        
        return {
            "total_documents": len(opportunities),
            "total_opportunities": len(opportunities),
            "states_monitored": len(states),
            "topics": topics_count,
            "recent_opportunities": recent
        }
        
    except Exception as e:
        logger.error(f"Error generating API dashboard: {e}")
        # Return mock data if there's an error
        return {
            "total_documents": 0,
            "total_opportunities": 0,
            "states_monitored": 0,
            "topics": {},
            "recent_opportunities": []
        }


@app.get("/topics")
async def get_topics():
    """Get list of all policy topics being tracked."""
    return {
        "topics": settings.policy_topics,
        "count": len(settings.policy_topics)
    }


@app.get("/states")
async def get_states():
    """Get list of all states with active opportunities."""
    # Query distinct states from database
    states = ["CA", "NY", "TX", "FL", "IL"]  # Placeholder
    
    return {
        "states": states,
        "count": len(states)
    }


@app.get("/status", response_model=SystemStatus)
async def get_system_status():
    """Get current system status and health."""
    try:
        agent_status = orchestrator.get_all_agent_states()
        
        return SystemStatus(
            status="operational",
            active_workflows=len(orchestrator.active_workflows),
            agent_status=agent_status,
            last_update=datetime.utcnow()
        )
        
    except Exception as e:
        logger.error(f"Error getting system status: {e}")
        return SystemStatus(
            status="error",
            active_workflows=0,
            agent_status={},
            last_update=datetime.utcnow()
        )


@app.get("/nonprofits")
async def search_nonprofits(
    location: str = Query("Tuscaloosa, AL", description="City, State format"),
    keyword: Optional[str] = Query(None, description="Service keyword (e.g., 'dental', 'health')"),
    state: Optional[str] = Query(None, description="2-letter state code (e.g., 'AL')"),
    ntee_code: Optional[str] = Query(None, description="NTEE code (e.g., 'E' for health)"),
    source: Optional[str] = Query(None, description="Data source: 'propublica', 'everyorg', 'all'")
):
    """
    Search for nonprofits using free open data APIs.
    
    Integrates data from:
    - ProPublica Nonprofit Explorer (financial data, NTEE codes)
    - Every.org (mission statements, logos)
    - IRS TEOS (official tax-exempt status)
    
    Example: /nonprofits?location=Tuscaloosa,AL&keyword=dental&ntee_code=E
    """
    try:
        from discovery.nonprofit_discovery import NonprofitDiscovery
        
        discovery = NonprofitDiscovery()
        results = []
        
        # Parse location for state/city
        location_parts = location.split(',')
        city = location_parts[0].strip() if len(location_parts) > 0 else None
        state_from_location = location_parts[1].strip() if len(location_parts) > 1 else None
        state_code = state or state_from_location or "AL"
        
        # Determine which sources to query
        sources_to_query = ['propublica', 'everyorg'] if source == 'all' or not source else [source]
        
        # Query ProPublica
        if 'propublica' in sources_to_query:
            try:
                propublica_results = discovery.search_propublica(
                    state=state_code,
                    city=city,
                    ntee_code=ntee_code
                )
                results.extend(propublica_results)
                logger.info(f"ProPublica: Found {len(propublica_results)} organizations")
            except Exception as e:
                logger.warning(f"ProPublica search failed: {e}")
        
        # Query Every.org
        if 'everyorg' in sources_to_query:
            try:
                causes = []
                if keyword:
                    # Map keywords to causes
                    keyword_lower = keyword.lower()
                    if 'health' in keyword_lower or 'dental' in keyword_lower or 'medical' in keyword_lower:
                        causes.append('health')
                    if 'education' in keyword_lower or 'school' in keyword_lower:
                        causes.append('education')
                
                everyorg_results = discovery.search_everyorg(
                    location=location,
                    causes=causes if causes else None
                )
                results.extend(everyorg_results)
                logger.info(f"Every.org: Found {len(everyorg_results)} organizations")
            except Exception as e:
                logger.warning(f"Every.org search failed: {e}")
        
        # Filter by keyword if provided
        if keyword and results:
            keyword_lower = keyword.lower()
            filtered_results = []
            for org in results:
                # Search in name, description, mission, ntee_description
                searchable_text = ' '.join([
                    str(org.get('name', '')),
                    str(org.get('description', '')),
                    str(org.get('mission', '')),
                    str(org.get('ntee_description', ''))
                ]).lower()
                
                if keyword_lower in searchable_text:
                    filtered_results.append(org)
            
            results = filtered_results
        
        return {
            "location": location,
            "keyword": keyword,
            "state": state_code,
            "ntee_code": ntee_code,
            "count": len(results),
            "nonprofits": results,
            "data_sources": {
                "propublica": "https://projects.propublica.org/nonprofits/api",
                "everyorg": "https://www.every.org/nonprofit-api",
                "irs_teos": "https://www.irs.gov/charities-non-profits/tax-exempt-organization-search-bulk-data-downloads"
            }
        }
        
    except Exception as e:
        logger.error(f"Nonprofit search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/nonprofits")
async def search_nonprofits_api(
    location: str = Query("Tuscaloosa, AL", description="City, State format"),
    keyword: Optional[str] = Query(None, description="Service keyword (e.g., 'dental', 'health')"),
    state: Optional[str] = Query(None, description="2-letter state code (e.g., 'AL')"),
    ntee_code: Optional[str] = Query(None, description="NTEE code (e.g., 'E' for health)"),
    source: Optional[str] = Query(None, description="Data source: 'propublica', 'everyorg', 'all'")
):
    """
    Search for nonprofits using free open data APIs (API-prefixed endpoint for frontend).
    
    This is a duplicate of /nonprofits with /api prefix for frontend routing.
    """
    return await search_nonprofits(location, keyword, state, ntee_code, source)


@app.get("/data/status")
async def get_data_ingestion_status():
    """
    Get status of reference data ingestions.
    
    Shows Census jurisdictions, NCES school districts, and nonprofit cache status.
    """
    try:
        from pathlib import Path
        from datetime import datetime
        
        status = {
            "census": {
                "jurisdictions": 90000,
                "counties": 3144,
                "municipalities": 19500,
                "status": "Check data/bronze/census_jurisdictions"
            },
            "nces": {
                "school_districts": 13000,
                "status": "Check data/bronze/nces_school_districts"
            },
            "nonprofits": {
                "total_available": 3000000,
                "cached_searches": 0,
                "cache_path": "data/cache/nonprofits"
            },
            "meetings": {
                "meetingbank": 1366,
                "city_scrapers": "100-500",
                "open_states": "50+"
            }
        }
        
        # Check cache directories
        cache_dir = Path("data/cache/nonprofits")
        if cache_dir.exists():
            cached_files = list(cache_dir.glob("*.json"))
            status["nonprofits"]["cached_searches"] = len(cached_files)
        
        return status
        
    except Exception as e:
        logger.error(f"Data status error: {e}")
        return {"error": str(e)}


@app.post("/data/ingest/nonprofits")
async def bulk_ingest_nonprofits(
    state: str = Query(..., description="State code (e.g., AL)"),
    ntee_code: Optional[str] = Query("E", description="NTEE code (default: E for Health)")
):
    """
    Bulk ingest nonprofit data for a state.
    
    Caches ProPublica API results for offline use.
    """
    try:
        from discovery.nonprofit_discovery import NonprofitDiscovery
        
        discovery = NonprofitDiscovery()
        orgs = discovery.search_propublica(state=state, ntee_code=ntee_code)
        
        return {
            "message": f"Ingested {len(orgs)} nonprofits for {state}",
            "state": state,
            "ntee_code": ntee_code,
            "count": len(orgs),
            "cache_location": "data/cache/nonprofits"
        }
        
    except Exception as e:
        logger.error(f"Nonprofit ingestion error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }


@app.post("/admin/initialize")
async def initialize_system():
    """Initialize Delta Lake tables and system components."""
    try:
        pipeline.initialize_tables()
        
        return {
            "status": "success",
            "message": "System initialized successfully"
        }
        
    except Exception as e:
        logger.error(f"Error initializing system: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Startup event
@app.post("/api/debate-grade")
async def grade_decision_with_debate_framework(
    document_id: Optional[str] = Query(None, description="Document ID to grade"),
    text: Optional[str] = Query(None, description="Text to grade directly"),
    title: Optional[str] = Query("", description="Document title")
):
    """
    Grade a government decision using debate framework (Harms/Solvency/Topicality).
    
    Translates debate concepts for laypeople:
    - Harms → "The Problem": Why is this a crisis?
    - Solvency → "The Fix": How does this solution work?
    - Topicality → "The Scope": Does the government have authority?
    
    Example: /api/debate-grade?text=The city council approved funding for dental screening...
    """
    try:
        from agents.debate_grader import DebateGraderAgent
        
        grader = DebateGraderAgent()
        
        # Get document content
        if document_id:
            document = pipeline.get_document_by_id(document_id)
            if not document:
                raise HTTPException(status_code=404, detail="Document not found")
        elif text:
            document = {
                "content": text,
                "title": title,
                "id": "custom_text"
            }
        else:
            raise HTTPException(status_code=400, detail="Provide either document_id or text")
        
        # Grade the document
        grade = await grader._grade_document(document)
        
        return {
            "document_id": document.get("id"),
            "title": document.get("title", ""),
            "debate_grade": grade,
            "explanation": {
                "harms": "This measures how well the decision identifies and documents the problem using data and evidence",
                "solvency": "This measures how clearly the solution is defined and whether it will actually fix the problem",
                "topicality": "This measures whether the government body has the legal authority to take this action"
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Debate grading error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/debate-grade/batch")
async def grade_decisions_batch(
    state: Optional[str] = Query(None, description="Filter by state"),
    topic: Optional[str] = Query(None, description="Filter by topic"),
    limit: int = Query(50, description="Number of documents to grade")
):
    """
    Grade multiple government decisions using debate framework.
    
    Returns aggregate insights about decision quality across dimensions.
    """
    try:
        from agents.debate_grader import DebateGraderAgent
        from agents.base import AgentMessage, MessageType, AgentRole
        
        grader = DebateGraderAgent()
        
        # Get documents to grade
        documents = pipeline.query_opportunities_by_state(state, None)
        
        if topic:
            documents = [d for d in documents if d.get("topic") == topic]
        
        documents = documents[:limit]
        
        # Create message and process
        message = AgentMessage(
            message_id=f"batch_grade_{datetime.utcnow().timestamp()}",
            sender=AgentRole.ORCHESTRATOR,
            recipient=AgentRole.DEBATE_GRADER,
            message_type=MessageType.COMMAND,
            payload={"documents": documents}
        )
        
        result = await grader.process(message)
        graded_documents = result[0].payload.get("documents", [])
        insights = result[0].payload.get("insights", {})
        
        return {
            "graded_count": len(graded_documents),
            "documents": graded_documents,
            "insights": insights,
            "explanation": {
                "average_scores": "Average scores across all three debate dimensions (out of 5)",
                "strongest_dimension": "Which dimension governments perform best on",
                "weakest_dimension": "Which dimension needs the most improvement"
            }
        }
        
    except Exception as e:
        logger.error(f"Batch debate grading error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.on_event("startup")
async def startup_event():
    """Initialize system on startup."""
    logger.info("Starting Oral Health Policy Pulse API")
    logger.info(f"Configuration: {settings.catalog_name}.{settings.schema_name}")


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("Shutting down Oral Health Policy Pulse API")


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        app,
        host=settings.api_host,
        port=settings.api_port,
        workers=settings.api_workers
    )
