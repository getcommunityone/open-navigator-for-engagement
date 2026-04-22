"""
FastAPI application optimized for Databricks Apps deployment.
Serves React frontend and provides REST API for agent interactions.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path
from fastapi import FastAPI, HTTPException, Query, BackgroundTasks
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from loguru import logger
import os

from agents.orchestrator import OrchestratorAgent
from pipeline.delta_lake import DeltaLakePipeline
from config import settings

# Initialize FastAPI app
app = FastAPI(
    title="Oral Health Policy Pulse",
    description="AI-powered advocacy opportunity finder",
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
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

# Pydantic models
class WorkflowRequest(BaseModel):
    """Request to start a new analysis workflow."""
    targets: List[Dict[str, str]]
    topics: Optional[List[str]] = None

class OpportunityFilter(BaseModel):
    """Filter criteria for advocacy opportunities."""
    state: Optional[str] = None
    topic: Optional[str] = None
    urgency: Optional[str] = None
    min_confidence: Optional[float] = 0.7


# API Routes
@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


@app.get("/api/dashboard")
async def get_dashboard_stats():
    """Get dashboard statistics and recent opportunities."""
    try:
        # Query Delta Lake for stats
        stats = await pipeline.get_dashboard_stats()
        return stats
    except Exception as e:
        logger.error(f"Dashboard stats error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/opportunities")
async def get_opportunities(
    state: Optional[str] = Query(None),
    topic: Optional[str] = Query(None),
    urgency: Optional[str] = Query(None),
    limit: int = Query(100, le=1000)
):
    """Get advocacy opportunities with optional filters."""
    try:
        opportunities = await pipeline.query_opportunities(
            state=state,
            topic=topic,
            urgency=urgency,
            limit=limit
        )
        return {"opportunities": opportunities, "count": len(opportunities)}
    except Exception as e:
        logger.error(f"Query opportunities error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/documents")
async def get_documents(
    search: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, le=100)
):
    """Get analyzed documents with pagination."""
    try:
        offset = (page - 1) * limit
        documents = await pipeline.query_documents(
            search=search,
            limit=limit,
            offset=offset
        )
        total = await pipeline.count_documents(search=search)
        return {
            "documents": documents,
            "page": page,
            "limit": limit,
            "total": total,
            "total_pages": (total + limit - 1) // limit
        }
    except Exception as e:
        logger.error(f"Query documents error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/workflow/start")
async def start_workflow(request: WorkflowRequest, background_tasks: BackgroundTasks):
    """Start a new analysis workflow."""
    try:
        workflow_id = f"workflow_{datetime.utcnow().timestamp()}"
        
        # Start workflow in background
        background_tasks.add_task(
            orchestrator.execute_pipeline,
            workflow_id=workflow_id,
            targets=request.targets,
            topics=request.topics
        )
        
        return {
            "workflow_id": workflow_id,
            "status": "started",
            "message": "Workflow started successfully"
        }
    except Exception as e:
        logger.error(f"Workflow start error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/workflow/{workflow_id}/status")
async def get_workflow_status(workflow_id: str):
    """Get status of a running workflow."""
    try:
        status = await orchestrator.get_workflow_status(workflow_id)
        return status
    except Exception as e:
        logger.error(f"Workflow status error: {e}")
        raise HTTPException(status_code=404, detail="Workflow not found")


@app.post("/api/advocacy/email/{opportunity_id}")
async def generate_advocacy_email(opportunity_id: str):
    """Generate advocacy email for an opportunity."""
    try:
        opportunity = await pipeline.get_opportunity(opportunity_id)
        if not opportunity:
            raise HTTPException(status_code=404, detail="Opportunity not found")
        
        email_content = await orchestrator.generate_advocacy_email(opportunity)
        return {"content": email_content}
    except Exception as e:
        logger.error(f"Generate email error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/settings")
async def get_settings():
    """Get current system settings."""
    return {
        "target_states": settings.target_states or [],
        "policy_topics": settings.policy_topics,
        "min_confidence": 0.7,
        "email_notifications": False,
        "notification_email": ""
    }


@app.put("/api/settings")
async def update_settings(new_settings: Dict[str, Any]):
    """Update system settings."""
    try:
        # In production, this would update configuration in Unity Catalog
        logger.info(f"Settings update requested: {new_settings}")
        return {"message": "Settings updated successfully"}
    except Exception as e:
        logger.error(f"Settings update error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/agents/status")
async def get_agents_status():
    """Get status of all agents."""
    try:
        return {
            "agents": [
                {"name": "Scraper", "status": "active", "uptime": "24h"},
                {"name": "Classifier", "status": "active", "uptime": "24h"},
                {"name": "Sentiment Analyzer", "status": "active", "uptime": "24h"},
                {"name": "Advocacy Writer", "status": "active", "uptime": "24h"}
            ]
        }
    except Exception as e:
        logger.error(f"Agent status error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Serve React frontend
static_dir = Path(__file__).parent / "static"
if static_dir.exists():
    # Mount static files (JS, CSS, images)
    app.mount("/assets", StaticFiles(directory=static_dir / "assets"), name="assets")
    
    # Serve index.html for all non-API routes (SPA routing)
    @app.get("/{full_path:path}")
    async def serve_react_app(full_path: str):
        """Serve React app for all non-API routes."""
        if full_path.startswith("api/"):
            raise HTTPException(status_code=404, detail="API endpoint not found")
        
        index_file = static_dir / "index.html"
        if index_file.exists():
            return FileResponse(index_file)
        else:
            raise HTTPException(status_code=404, detail="Frontend not built")


@app.on_event("startup")
async def startup_event():
    """Initialize system on startup."""
    logger.info("Starting Oral Health Policy Pulse application...")
    
    # Initialize Delta Lake if not exists
    try:
        await pipeline.initialize_tables()
        logger.info("Delta Lake tables initialized")
    except Exception as e:
        logger.warning(f"Delta Lake initialization skipped: {e}")
    
    logger.info("Application started successfully")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("Shutting down application...")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
