# Databricks notebook source
# MAGIC %md
# MAGIC # Oral Health Policy Finder - Agent Bricks Quickstart
# MAGIC 
# MAGIC This notebook demonstrates the Databricks Agent Bricks implementation of the Oral Health Policy Finder system.
# MAGIC 
# MAGIC **Features:**
# MAGIC - MLflow-based agents with automatic tracing
# MAGIC - Unity Catalog governance
# MAGIC - Model Serving deployment
# MAGIC - Agent evaluation framework
# MAGIC - Delta Lake integration
# MAGIC 
# MAGIC **Prerequisites:**
# MAGIC - Databricks Runtime 14.3 LTS ML or higher
# MAGIC - Unity Catalog enabled
# MAGIC - Model Serving permissions

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Setup and Configuration

# COMMAND ----------

# Install dependencies
%pip install -q mlflow>=2.10.0 databricks-agents>=0.1.0 langchain>=0.1.0 openai>=1.6.0

# COMMAND ----------

# Configure MLflow
import mlflow
mlflow.set_registry_uri("databricks-uc")

# Set Unity Catalog
CATALOG = "main"
SCHEMA = "agents"

# Ensure catalog and schema exist
spark.sql(f"CREATE CATALOG IF NOT EXISTS {CATALOG}")
spark.sql(f"CREATE SCHEMA IF NOT EXISTS {CATALOG}.{SCHEMA}")

print(f"✅ Using Unity Catalog: {CATALOG}.{SCHEMA}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Test Policy Classifier Agent Locally

# COMMAND ----------

# Import agent
import sys
sys.path.append("/Workspace/Repos/your-repo/open-navigator")

from agents.mlflow_classifier import PolicyClassifierAgent

# Initialize agent
agent = PolicyClassifierAgent()

# Test with sample document
test_input = {
    "document_id": "test_001",
    "title": "City Council Meeting - Water Infrastructure",
    "content": """
    The city council voted 5-2 to approve fluoridation of the municipal water supply.
    The program will begin next quarter with monitoring by the health department.
    Expected to benefit approximately 50,000 residents.
    """
}

# Get prediction
result = agent.predict(None, test_input)

print("Classification Result:")
print(f"  Topic: {result['primary_topic']}")
print(f"  Confidence: {result['confidence']:.2%}")
print(f"  Method: {result['method']}")
print(f"  Reasoning: {result['reasoning']}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Register Agent to Unity Catalog

# COMMAND ----------

from databricks.deployment import AgentDeploymentManager

# Initialize deployment manager
manager = AgentDeploymentManager()

# Register agent
version = manager.register_agent(
    agent_class=PolicyClassifierAgent,
    agent_name="policy_classifier",
    description="Classifies government meeting documents for oral health policy topics",
    tags={
        "team": "advocacy",
        "domain": "oral_health",
        "framework": "databricks-agent-bricks"
    }
)

print(f"✅ Registered policy_classifier version {version}")
print(f"   Model: {CATALOG}.{SCHEMA}.policy_classifier")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. Deploy to Model Serving

# COMMAND ----------

# Deploy agent to serving endpoint
endpoint_url = manager.deploy_agent(
    agent_name="policy_classifier",
    endpoint_name="policy-classifier-dev",
    version=version,
    workload_size="Small",
    scale_to_zero=True
)

print(f"✅ Deployed to Model Serving")
print(f"   Endpoint: policy-classifier-dev")
print(f"   URL: {endpoint_url}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 5. Test Deployed Endpoint

# COMMAND ----------

import requests
import os

# Test endpoint
endpoint_name = "policy-classifier-dev"
databricks_host = dbutils.notebook.entry_point.getDbutils().notebook().getContext().apiUrl().get()
databricks_token = dbutils.notebook.entry_point.getDbutils().notebook().getContext().apiToken().get()

url = f"{databricks_host}/serving-endpoints/{endpoint_name}/invocations"

headers = {
    "Authorization": f"Bearer {databricks_token}",
    "Content-Type": "application/json"
}

test_payload = {
    "dataframe_records": [
        {
            "document_id": "endpoint_test_001",
            "title": "School Board Meeting",
            "content": "Discussion of new dental screening program for elementary students"
        }
    ]
}

response = requests.post(url, headers=headers, json=test_payload)
result = response.json()

print("Endpoint Response:")
print(result)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 6. Evaluate Agent Performance

# COMMAND ----------

from databricks.evaluation import AgentEvaluator
import pandas as pd

# Create evaluation dataset
eval_data = pd.DataFrame([
    {
        "document_id": "eval_001",
        "title": "Water Board Meeting",
        "content": "Approved fluoride addition to water supply",
        "ground_truth": "water_fluoridation"
    },
    {
        "document_id": "eval_002",
        "title": "School Board Session",
        "content": "New dental screening program for students",
        "ground_truth": "school_dental_screening"
    },
    {
        "document_id": "eval_003",
        "title": "Budget Review",
        "content": "General fund allocation discussion",
        "ground_truth": "not_oral_health_related"
    }
])

# Evaluate
evaluator = AgentEvaluator("policy_classifier")
metrics = evaluator.evaluate_classifier(
    model_uri=f"models:/{CATALOG}.{SCHEMA}.policy_classifier/{version}",
    test_documents=eval_data[["document_id", "title", "content"]].to_dict('records'),
    ground_truth=eval_data["ground_truth"].tolist()
)

print(f"\n📊 Evaluation Metrics:")
print(f"  Accuracy: {metrics.accuracy:.2%}")
print(f"  Precision: {metrics.precision:.2%}")
print(f"  Recall: {metrics.recall:.2%}")
print(f"  F1 Score: {metrics.f1_score:.2%}")
print(f"  Avg Latency: {metrics.avg_latency_ms:.0f}ms")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 7. Query Results from Delta Lake

# COMMAND ----------

# Create sample data in Delta Lake
spark.sql(f"""
CREATE TABLE IF NOT EXISTS {CATALOG}.{SCHEMA}.classified_documents (
    document_id STRING,
    municipality STRING,
    state STRING,
    meeting_date TIMESTAMP,
    primary_topic STRING,
    confidence DOUBLE,
    relevant_excerpts ARRAY<STRING>,
    classification_timestamp TIMESTAMP
)
USING DELTA
PARTITIONED BY (state)
""")

# Query documents by topic
df = spark.sql(f"""
SELECT 
    state,
    primary_topic,
    COUNT(*) as document_count,
    AVG(confidence) as avg_confidence
FROM {CATALOG}.{SCHEMA}.classified_documents
WHERE primary_topic != 'not_oral_health_related'
GROUP BY state, primary_topic
ORDER BY document_count DESC
""")

display(df)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 8. Create Advocacy Heatmap

# COMMAND ----------

# Query advocacy opportunities
opportunities = spark.sql(f"""
SELECT 
    state,
    municipality,
    primary_topic,
    confidence,
    relevant_excerpts
FROM {CATALOG}.{SCHEMA}.classified_documents
WHERE 
    primary_topic IN ('water_fluoridation', 'school_dental_screening', 'low_income_dental_funding')
    AND confidence > 0.7
ORDER BY confidence DESC
LIMIT 100
""")

# Convert to pandas for visualization
pdf = opportunities.toPandas()

print(f"Found {len(pdf)} advocacy opportunities")
display(pdf.head(10))

# COMMAND ----------

# MAGIC %md
# MAGIC ## 9. Monitor Agent Performance

# COMMAND ----------

# Get endpoint metrics
status = manager.get_endpoint_status("policy-classifier-dev")

print(f"Endpoint Status:")
print(f"  Name: {status['name']}")
print(f"  State: {status['state']}")
print(f"\nServed Entities:")
for entity in status['served_entities']:
    print(f"  - {entity['name']} v{entity['version']}: {entity['state']}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 10. A/B Test Model Versions

# COMMAND ----------

# Compare two versions (if you have multiple)
# comparison = evaluator.compare_versions(
#     version_a="1",
#     version_b="2",
#     eval_data=eval_data
# )
# 
# print("Version Comparison:")
# for metric, data in comparison["improvements"].items():
#     print(f"  {metric}: {data['improvement_pct']:.1f}% improvement")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Next Steps
# MAGIC 
# MAGIC 1. **Scale Up**: Process thousands of documents using Spark
# MAGIC 2. **Add Monitoring**: Set up alerts for model drift
# MAGIC 3. **Feedback Loop**: Collect user corrections in Delta Lake
# MAGIC 4. **Multi-Agent**: Deploy sentiment and advocacy writer agents
# MAGIC 5. **Production**: Promote to production endpoint with traffic splitting
# MAGIC 
# MAGIC **Resources:**
# MAGIC - [Databricks Agent Framework Docs](https://docs.databricks.com/en/generative-ai/agent-framework/index.html)
# MAGIC - [MLflow Guide](https://mlflow.org/docs/latest/index.html)
# MAGIC - [Unity Catalog](https://docs.databricks.com/en/data-governance/unity-catalog/index.html)
