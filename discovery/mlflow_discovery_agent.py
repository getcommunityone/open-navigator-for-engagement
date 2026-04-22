"""
MLflow-based Jurisdiction Discovery Agent for Databricks Agent Bricks.

Deploys the jurisdiction discovery pipeline as a Model Serving endpoint,
enabling:
- API-based discovery requests
- Scheduled batch discovery jobs
- Integration with other agents
- Observability and tracing
"""
from typing import Any, Dict, List, Optional, Union
import mlflow
from mlflow.models import infer_signature
import pandas as pd
from datetime import datetime
from loguru import logger
import asyncio

from agents.mlflow_base import MLflowAgentBase
from agents.base import AgentRole
from discovery.discovery_pipeline import DiscoveryPipeline
from config import settings


class MLflowDiscoveryAgent(MLflowAgentBase):
    """
    Jurisdiction Discovery Agent for AgentBricks deployment.
    
    Input format:
    {
        "action": "discover" | "stats" | "targets",
        "params": {
            "limit": int,           # Optional: limit jurisdictions
            "state": str,           # Optional: filter by state
            "type": str,            # Optional: filter by type
            "priority_min": int     # Optional: min priority for targets
        }
    }
    
    Output format:
    {
        "status": "success" | "error",
        "data": {...},
        "metadata": {
            "timestamp": str,
            "elapsed_seconds": float
        }
    }
    """
    
    def __init__(self):
        """Initialize Discovery Agent."""
        super().__init__(
            agent_id="jurisdiction_discovery_agent",
            role=AgentRole.SCRAPER  # Closest role
        )
        self.pipeline = None
        
    def load_context(self, context):
        """Load agent context from MLflow."""
        super().load_context(context)
        logger.info("Discovery Agent loaded and ready")
        
    def _initialize_pipeline(self):
        """Lazy initialization of discovery pipeline."""
        if self.pipeline is None:
            self.pipeline = DiscoveryPipeline()
            
    def _process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process discovery request.
        
        Args:
            request: Discovery request with action and params
            
        Returns:
            Discovery results
        """
        action = request.get("action", "discover")
        params = request.get("params", {})
        
        start_time = datetime.now()
        
        try:
            self._initialize_pipeline()
            
            if action == "discover":
                # Run discovery pipeline
                result = asyncio.run(
                    self.pipeline.run_full_pipeline(
                        discovery_limit=params.get("limit"),
                        state_filter=params.get("state"),
                        type_filter=params.get("type")
                    )
                )
                
                return {
                    "status": "success",
                    "data": result,
                    "metadata": {
                        "timestamp": datetime.now().isoformat(),
                        "elapsed_seconds": (datetime.now() - start_time).total_seconds()
                    }
                }
                
            elif action == "stats":
                # Get discovery statistics
                from pyspark.sql import SparkSession
                from pyspark.sql.functions import col, count, avg
                
                spark = SparkSession.builder.getOrCreate()
                
                # Bronze stats
                bronze_df = spark.read.format("delta").load(
                    f"{settings.delta_lake_path}/bronze/jurisdictions/unified"
                )
                total_jurisdictions = bronze_df.count()
                by_type = {
                    row["jurisdiction_type"]: row["count"]
                    for row in bronze_df.groupBy("jurisdiction_type").count().collect()
                }
                
                # Silver stats
                silver_df = spark.read.format("delta").load(
                    f"{settings.delta_lake_path}/silver/discovered_urls"
                )
                urls_discovered = silver_df.count()
                homepages_found = silver_df.filter(col("homepage_url").isNotNull()).count()
                minutes_found = silver_df.filter(col("minutes_url").isNotNull()).count()
                
                # Gold stats
                gold_df = spark.read.format("delta").load(
                    f"{settings.delta_lake_path}/gold/scraping_targets"
                )
                scraping_targets = gold_df.count()
                
                return {
                    "status": "success",
                    "data": {
                        "bronze": {
                            "total_jurisdictions": total_jurisdictions,
                            "by_type": by_type
                        },
                        "silver": {
                            "urls_discovered": urls_discovered,
                            "homepages_found": homepages_found,
                            "minutes_found": minutes_found,
                            "success_rate": homepages_found / urls_discovered if urls_discovered > 0 else 0
                        },
                        "gold": {
                            "scraping_targets": scraping_targets
                        }
                    },
                    "metadata": {
                        "timestamp": datetime.now().isoformat(),
                        "elapsed_seconds": (datetime.now() - start_time).total_seconds()
                    }
                }
                
            elif action == "targets":
                # Get scraping targets
                from pyspark.sql import SparkSession
                from pyspark.sql.functions import col
                
                spark = SparkSession.builder.getOrCreate()
                
                gold_df = spark.read.format("delta").load(
                    f"{settings.delta_lake_path}/gold/scraping_targets"
                )
                
                # Apply filters
                priority_min = params.get("priority_min", 100)
                gold_df = gold_df.filter(col("priority_score") >= priority_min)
                
                if params.get("state"):
                    gold_df = gold_df.filter(col("state") == params["state"])
                    
                if params.get("limit"):
                    gold_df = gold_df.limit(params["limit"])
                
                targets = [
                    {
                        "jurisdiction_id": row.jurisdiction_id,
                        "jurisdiction_name": row.jurisdiction_name,
                        "state": row.state,
                        "homepage_url": row.homepage_url,
                        "minutes_url": row.minutes_url,
                        "cms_platform": row.cms_platform,
                        "priority_score": row.priority_score
                    }
                    for row in gold_df.collect()
                ]
                
                return {
                    "status": "success",
                    "data": {
                        "targets": targets,
                        "count": len(targets)
                    },
                    "metadata": {
                        "timestamp": datetime.now().isoformat(),
                        "elapsed_seconds": (datetime.now() - start_time).total_seconds()
                    }
                }
                
            else:
                return {
                    "status": "error",
                    "error": f"Unknown action: {action}",
                    "metadata": {
                        "timestamp": datetime.now().isoformat()
                    }
                }
                
        except Exception as e:
            logger.error(f"Discovery request failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "metadata": {
                    "timestamp": datetime.now().isoformat(),
                    "elapsed_seconds": (datetime.now() - start_time).total_seconds()
                }
            }
    
    def _get_example_input(self) -> Dict[str, Any]:
        """Get example input for model signature."""
        return {
            "action": "discover",
            "params": {
                "limit": 100,
                "state": "CA"
            }
        }


def deploy_discovery_agent(
    endpoint_name: str = "jurisdiction-discovery",
    workload_size: str = "Small"
) -> str:
    """
    Deploy Discovery Agent to Databricks Model Serving.
    
    Args:
        endpoint_name: Name for the serving endpoint
        workload_size: Small, Medium, or Large
        
    Returns:
        Endpoint URL
    """
    from databricks.sdk import WorkspaceClient
    from databricks.sdk.service.serving import (
        ServedEntityInput,
        EndpointCoreConfigInput
    )
    
    logger.info(f"Deploying Discovery Agent to Model Serving: {endpoint_name}")
    
    # Register model to Unity Catalog
    agent = MLflowDiscoveryAgent()
    full_model_name = f"{settings.catalog_name}.{settings.schema_name}.jurisdiction_discovery"
    
    with mlflow.start_run(run_name="register_discovery_agent") as run:
        mlflow.log_param("endpoint_name", endpoint_name)
        mlflow.log_param("workload_size", workload_size)
        
        # Get signature
        example_input = agent._get_example_input()
        example_output = agent._process_request(example_input)
        signature = infer_signature(example_input, example_output)
        
        # Log model
        model_info = mlflow.pyfunc.log_model(
            artifact_path="discovery_agent",
            python_model=agent,
            signature=signature,
            registered_model_name=full_model_name,
            pip_requirements=[
                "pyspark==3.5.0",
                "delta-spark==3.0.0",
                "httpx==0.27.0",
                "beautifulsoup4==4.12.2",
                "loguru==0.7.2"
            ]
        )
        
        model_version = model_info.registered_model_version
    
    # Create serving endpoint
    w = WorkspaceClient(
        host=settings.databricks_host,
        token=settings.databricks_token
    )
    
    try:
        # Check if endpoint exists
        endpoint = w.serving_endpoints.get(name=endpoint_name)
        logger.info(f"Updating existing endpoint: {endpoint_name}")
        
        w.serving_endpoints.update_config(
            name=endpoint_name,
            served_entities=[
                ServedEntityInput(
                    entity_name=full_model_name,
                    entity_version=model_version,
                    workload_size=workload_size,
                    scale_to_zero_enabled=True
                )
            ]
        )
        
    except Exception:
        # Create new endpoint
        logger.info(f"Creating new endpoint: {endpoint_name}")
        
        w.serving_endpoints.create(
            name=endpoint_name,
            config=EndpointCoreConfigInput(
                served_entities=[
                    ServedEntityInput(
                        entity_name=full_model_name,
                        entity_version=model_version,
                        workload_size=workload_size,
                        scale_to_zero_enabled=True
                    )
                ]
            )
        )
    
    # Wait for endpoint to be ready
    logger.info("Waiting for endpoint to be ready...")
    w.serving_endpoints.wait_get_serving_endpoint_not_updating(name=endpoint_name)
    
    endpoint_url = f"{settings.databricks_host}/serving-endpoints/{endpoint_name}/invocations"
    logger.success(f"✅ Discovery Agent deployed: {endpoint_url}")
    
    return endpoint_url


if __name__ == "__main__":
    # Deploy the agent
    endpoint_url = deploy_discovery_agent()
    print(f"\n🚀 Discovery Agent deployed!")
    print(f"   Endpoint: {endpoint_url}")
    print(f"\n   Example usage:")
    print(f"""
    import requests
    
    response = requests.post(
        "{endpoint_url}",
        headers={{"Authorization": f"Bearer {{databricks_token}}"}},
        json={{
            "dataframe_records": [{{
                "action": "discover",
                "params": {{"limit": 100, "state": "CA"}}
            }}]
        }}
    )
    """)
