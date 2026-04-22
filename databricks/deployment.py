"""
Deployment scripts for Databricks Agent Bricks.

Handles:
- Unity Catalog registration
- Model Serving deployment
- Endpoint management
- Version promotion
"""
import os
from typing import Optional, List
import mlflow
from mlflow.tracking import MlflowClient
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.serving import (
    ServedEntityInput,
    EndpointCoreConfigInput,
    TrafficConfig,
    Route
)
from databricks.sdk.service.catalog import (
    ModelVersionInfoStatus
)
from loguru import logger

from config import settings


class AgentDeploymentManager:
    """
    Manages deployment of agents to Databricks Model Serving.
    
    Workflow:
    1. Register agent to Unity Catalog
    2. Create/update serving endpoint
    3. Monitor deployment status
    4. Promote versions (dev -> staging -> prod)
    """
    
    def __init__(self):
        """Initialize deployment manager."""
        self.client = MlflowClient()
        self.w = WorkspaceClient(
            host=settings.databricks_host,
            token=settings.databricks_token
        )
        self.catalog = settings.catalog_name
        self.schema = settings.schema_name
        
    def register_agent(
        self,
        agent_class,
        agent_name: str,
        description: str,
        tags: Optional[dict] = None
    ) -> str:
        """
        Register an agent to Unity Catalog.
        
        Args:
            agent_class: Agent class to instantiate
            agent_name: Name for the registered model (e.g., "policy_classifier")
            description: Model description
            tags: Optional tags for the model
            
        Returns:
            Model version string
        """
        full_model_name = f"{self.catalog}.{self.schema}.{agent_name}"
        
        logger.info(f"Registering agent: {full_model_name}")
        
        # Instantiate agent
        agent = agent_class()
        
        # Log to MLflow and register
        with mlflow.start_run(run_name=f"register_{agent_name}") as run:
            # Log agent metadata
            mlflow.log_param("agent_name", agent_name)
            mlflow.log_param("catalog", self.catalog)
            mlflow.log_param("schema", self.schema)
            
            if tags:
                mlflow.set_tags(tags)
            
            # Get example for signature
            example_input = agent._get_example_input()
            example_output = agent.predict(None, example_input)
            signature = mlflow.models.infer_signature(example_input, example_output)
            
            # Log model
            model_info = mlflow.pyfunc.log_model(
                artifact_path="agent",
                python_model=agent,
                signature=signature,
                registered_model_name=full_model_name,
                pip_requirements=self._get_requirements(agent_class)
            )
            
            run_id = run.info.run_id
        
        # Get version number
        latest_version = self.client.get_latest_versions(full_model_name)[0]
        version = latest_version.version
        
        # Update model description
        if description:
            self.client.update_registered_model(
                name=full_model_name,
                description=description
            )
        
        logger.info(f"✅ Registered {full_model_name} version {version}")
        
        return version
    
    def deploy_agent(
        self,
        agent_name: str,
        endpoint_name: str,
        version: Optional[str] = None,
        workload_size: str = "Small",
        scale_to_zero: bool = True,
        min_replicas: int = 1,
        max_replicas: int = 10
    ) -> str:
        """
        Deploy agent to Model Serving endpoint.
        
        Args:
            agent_name: Registered model name
            endpoint_name: Serving endpoint name
            version: Model version (defaults to latest)
            workload_size: Endpoint size (Small, Medium, Large)
            scale_to_zero: Enable scale-to-zero
            min_replicas: Minimum replicas
            max_replicas: Maximum replicas
            
        Returns:
            Endpoint URL
        """
        full_model_name = f"{self.catalog}.{self.schema}.{agent_name}"
        
        # Get version if not specified
        if version is None:
            latest_version = self.client.get_latest_versions(full_model_name)[0]
            version = latest_version.version
        
        logger.info(f"Deploying {full_model_name} v{version} to {endpoint_name}")
        
        # Configure served entity
        served_entity = ServedEntityInput(
            entity_name=full_model_name,
            entity_version=version,
            workload_size=workload_size,
            scale_to_zero_enabled=scale_to_zero,
            min_replicas=min_replicas if not scale_to_zero else 0,
            max_replicas=max_replicas
        )
        
        # Create or update endpoint
        try:
            endpoint = self.w.serving_endpoints.create_and_wait(
                name=endpoint_name,
                config=EndpointCoreConfigInput(
                    served_entities=[served_entity]
                )
            )
            logger.info(f"✅ Created endpoint: {endpoint_name}")
            
        except Exception as e:
            if "already exists" in str(e).lower():
                # Update existing endpoint
                endpoint = self.w.serving_endpoints.update_config_and_wait(
                    name=endpoint_name,
                    served_entities=[served_entity]
                )
                logger.info(f"✅ Updated endpoint: {endpoint_name}")
            else:
                raise
        
        # Return invocation URL
        endpoint_url = f"{settings.databricks_host}/serving-endpoints/{endpoint_name}/invocations"
        logger.info(f"   Endpoint URL: {endpoint_url}")
        
        return endpoint_url
    
    def create_multi_agent_endpoint(
        self,
        endpoint_name: str,
        agents: List[tuple],  # [(agent_name, version, traffic_percentage)]
        workload_size: str = "Medium"
    ) -> str:
        """
        Create endpoint serving multiple agents with traffic splitting.
        
        Args:
            endpoint_name: Endpoint name
            agents: List of (agent_name, version, traffic_percentage) tuples
            workload_size: Endpoint size
            
        Returns:
            Endpoint URL
        """
        logger.info(f"Creating multi-agent endpoint: {endpoint_name}")
        
        # Build served entities
        served_entities = []
        for agent_name, version, traffic_pct in agents:
            full_model_name = f"{self.catalog}.{self.schema}.{agent_name}"
            
            served_entities.append(
                ServedEntityInput(
                    entity_name=full_model_name,
                    entity_version=version,
                    workload_size=workload_size,
                    scale_to_zero_enabled=True
                )
            )
        
        # Create endpoint
        endpoint = self.w.serving_endpoints.create_and_wait(
            name=endpoint_name,
            config=EndpointCoreConfigInput(
                served_entities=served_entities
            )
        )
        
        logger.info(f"✅ Created multi-agent endpoint with {len(agents)} agents")
        
        return f"{settings.databricks_host}/serving-endpoints/{endpoint_name}/invocations"
    
    def test_endpoint(self, endpoint_name: str, test_input: dict) -> dict:
        """
        Test a deployed endpoint.
        
        Args:
            endpoint_name: Endpoint name
            test_input: Test input data
            
        Returns:
            Prediction result
        """
        import requests
        
        url = f"{settings.databricks_host}/serving-endpoints/{endpoint_name}/invocations"
        
        headers = {
            "Authorization": f"Bearer {settings.databricks_token}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(
            url,
            headers=headers,
            json={"dataframe_records": [test_input]}
        )
        
        response.raise_for_status()
        return response.json()
    
    def get_endpoint_status(self, endpoint_name: str) -> dict:
        """Get endpoint status and metrics."""
        endpoint = self.w.serving_endpoints.get(name=endpoint_name)
        
        return {
            "name": endpoint.name,
            "state": endpoint.state.config_update if endpoint.state else "Unknown",
            "served_entities": [
                {
                    "name": entity.name,
                    "version": entity.entity_version,
                    "state": entity.state
                }
                for entity in (endpoint.config.served_entities or [])
            ]
        }
    
    def _get_requirements(self, agent_class) -> List[str]:
        """Get pip requirements for an agent."""
        return [
            "mlflow>=2.10.0",
            "databricks-agents>=0.1.0",
            "langchain>=0.1.0",
            "openai>=1.6.0",
            "anthropic>=0.8.0",
            "pydantic>=2.5.0",
            "loguru>=0.7.0"
        ]


def deploy_all_agents():
    """
    Deploy all agents to Databricks Model Serving.
    
    Usage:
        python -m databricks.deployment
    """
    from agents.mlflow_classifier import PolicyClassifierAgent
    
    manager = AgentDeploymentManager()
    
    # Register and deploy classifier
    print("\n📦 Deploying Policy Classifier Agent...")
    version = manager.register_agent(
        agent_class=PolicyClassifierAgent,
        agent_name="policy_classifier",
        description="Classifies government meeting documents for oral health policy topics",
        tags={"team": "advocacy", "domain": "oral_health"}
    )
    
    endpoint_url = manager.deploy_agent(
        agent_name="policy_classifier",
        endpoint_name="policy-classifier-prod",
        version=version,
        workload_size="Small",
        scale_to_zero=True
    )
    
    print(f"\n✅ Deployment Complete!")
    print(f"   Endpoint: {endpoint_url}")
    print(f"\n🧪 Test with:")
    print(f"""
    curl -X POST {endpoint_url} \\
      -H "Authorization: Bearer $DATABRICKS_TOKEN" \\
      -H "Content-Type: application/json" \\
      -d '{{"dataframe_records": [{{"document_id": "test", "title": "Meeting", "content": "Fluoride discussion..."}}]}}'
    """)
    
    # Test endpoint
    print("\n🧪 Testing endpoint...")
    result = manager.test_endpoint(
        endpoint_name="policy-classifier-prod",
        test_input={
            "document_id": "test_001",
            "title": "City Council Meeting",
            "content": "Discussion on water fluoridation program"
        }
    )
    print(f"   Result: {result}")


if __name__ == "__main__":
    deploy_all_agents()
