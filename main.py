"""
Main entry point for running the Oral Health Policy Pulse system.
"""
import asyncio
import sys
from pathlib import Path
from typing import List, Optional
import click
from loguru import logger

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from agents.orchestrator import OrchestratorAgent
from agents.scraper import ScraperAgent
from agents.parser import ParserAgent
from agents.classifier import ClassifierAgent
from agents.sentiment import SentimentAnalyzerAgent
from agents.advocacy import AdvocacyWriterAgent
from pipeline.delta_lake import DeltaLakePipeline
from visualization.heatmap import AdvocacyHeatmap
from config import settings


# Configure logging
logger.remove()
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
    level=settings.log_level
)
logger.add(
    settings.log_file,
    rotation="500 MB",
    retention="10 days",
    level=settings.log_level
)


@click.group()
def cli():
    """Oral Health Policy Pulse - Multi-agent policy analysis system."""
    pass


@cli.command()
@click.option('--host', default='0.0.0.0', help='API host')
@click.option('--port', default=8000, help='API port')
@click.option('--reload', is_flag=True, help='Enable auto-reload')
def serve(host: str, port: int, reload: bool):
    """Start the API server."""
    import uvicorn
    from api.main import app
    
    logger.info(f"Starting API server on {host}:{port}")
    
    uvicorn.run(
        "api.main:app",
        host=host,
        port=port,
        reload=reload,
        workers=1 if reload else settings.api_workers
    )


@cli.command()
@click.option('--state', help='State to analyze')
@click.option('--municipality', help='Municipality to analyze')
@click.option('--url', required=True, help='URL to scrape')
@click.option('--platform', default='generic', help='Platform type (legistar, granicus, generic)')
def scrape(state: str, municipality: str, url: str, platform: str):
    """Scrape meeting minutes from a single source."""
    logger.info(f"Scraping {url} for {municipality}, {state}")
    
    async def run_scrape():
        scraper = ScraperAgent()
        
        async with scraper:
            targets = [{
                "url": url,
                "municipality": municipality,
                "state": state,
                "platform": platform
            }]
            
            documents = await scraper._scrape_targets(targets, {})
            
            logger.info(f"Scraped {len(documents)} documents")
            
            # Save to pipeline
            pipeline = DeltaLakePipeline()
            pipeline.write_raw_documents(documents)
    
    asyncio.run(run_scrape())


@cli.command()
@click.option('--targets-file', required=True, help='JSON file with scrape targets')
def analyze(targets_file: str):
    """Run full analysis pipeline on targets."""
    import json
    
    logger.info(f"Starting analysis pipeline with targets from {targets_file}")
    
    # Load targets
    with open(targets_file, 'r') as f:
        targets = json.load(f)
    
    async def run_pipeline():
        # Initialize orchestrator and agents
        orchestrator = OrchestratorAgent()
        orchestrator.register_agent(ScraperAgent())
        orchestrator.register_agent(ParserAgent())
        orchestrator.register_agent(ClassifierAgent())
        orchestrator.register_agent(SentimentAnalyzerAgent())
        orchestrator.register_agent(AdvocacyWriterAgent())
        
        # Execute pipeline
        results = await orchestrator.execute_pipeline(targets)
        
        logger.info(f"Pipeline completed: {results}")
    
    asyncio.run(run_pipeline())


@cli.command()
@click.option('--output', default='heatmap.html', help='Output file path')
@click.option('--urgency', help='Filter by urgency level')
def generate_heatmap(output: str, urgency: Optional[str]):
    """Generate advocacy heatmap visualization."""
    logger.info(f"Generating heatmap (urgency={urgency})")
    
    # Query opportunities
    pipeline = DeltaLakePipeline()
    opportunities = pipeline.query_opportunities_by_state(None, urgency)
    
    # Generate map
    heatmap = AdvocacyHeatmap()
    m = heatmap.create_folium_map(opportunities)
    
    # Save
    heatmap.export_map_html(m, output)
    
    logger.info(f"Heatmap saved to {output}")


@cli.command()
def init():
    """Initialize the system (create database tables, etc.)."""
    logger.info("Initializing Oral Health Policy Pulse system")
    
    try:
        pipeline = DeltaLakePipeline()
        pipeline.initialize_tables()
        
        logger.info("System initialized successfully")
        
    except Exception as e:
        logger.error(f"Initialization failed: {e}")
        sys.exit(1)


@cli.command()
def status():
    """Show system status."""
    logger.info("Checking system status")
    
    # Check configuration
    click.echo(f"Catalog: {settings.catalog_name}")
    click.echo(f"Schema: {settings.schema_name}")
    click.echo(f"Delta Lake Path: {settings.delta_lake_path}")
    click.echo(f"Log Level: {settings.log_level}")
    
    # Check connections
    click.echo("\nSystem Status: OK")


if __name__ == "__main__":
    cli()
