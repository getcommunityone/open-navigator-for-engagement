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
from pydantic import BaseModel, Field
from loguru import logger

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
    title="Oral Health Policy Pulse API",
    description="Multi-agent system for analyzing local government oral health policy discussions",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
            <title>Oral Health Policy Pulse API</title>
            <style>
                body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
                h1 { color: #1976d2; }
                .endpoint { background: #f5f5f5; padding: 10px; margin: 10px 0; border-radius: 5px; }
                code { background: #e0e0e0; padding: 2px 5px; border-radius: 3px; }
            </style>
        </head>
        <body>
            <h1>🦷 Oral Health Policy Pulse API</h1>
            <p>Multi-agent system for analyzing local government oral health policy discussions.</p>
            
            <h2>Key Endpoints:</h2>
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
            
            <p>View full API documentation at <a href="/docs">/docs</a></p>
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
            title="Oral Health Policy Advocacy Heatmap"
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
