# Databricks Agent Bricks Implementation

This directory contains the Databricks Agent Bricks (Mosaic AI Agent Framework) implementation of the Oral Health Policy Finder.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Databricks Workspace                      │
│                                                               │
│  ┌────────────────┐      ┌──────────────────┐              │
│  │ Unity Catalog  │◄─────┤  MLflow Tracking │              │
│  │  - Models      │      │  - Experiments   │              │
│  │  - Governance  │      │  - Runs          │              │
│  │  - Lineage     │      │  - Artifacts     │              │
│  └────────┬───────┘      └──────────────────┘              │
│           │                                                  │
│           ▼                                                  │
│  ┌─────────────────────────────────────────┐               │
│  │         Model Serving Endpoints          │               │
│  │  ┌──────────────┐  ┌─────────────────┐ │               │
│  │  │ Classifier   │  │ Sentiment       │ │               │
│  │  │ Agent        │  │ Analyzer        │ │               │
│  │  └──────────────┘  └─────────────────┘ │               │
│  │  Auto-scaling • Observability • A/B    │               │
│  └────────────┬────────────────────────────┘               │
│               │                                              │
└───────────────┼──────────────────────────────────────────────┘
                │
                ▼
        ┌────────────────┐
        │  REST API      │
        │  Clients       │
        └────────────────┘
```

## Components

### 1. MLflow Agent Base (`agents/mlflow_base.py`)
- `MLflowAgentBase`: Base class for all agents with MLflow Pyfunc interface
- `MLflowChainAgent`: Base for LangChain-powered agents
- Automatic tracing and observability
- Model Serving compatibility

### 2. Classifier Agent (`agents/mlflow_classifier.py`)
- Policy topic classification
- Hybrid keyword + LLM approach
- Unity Catalog registered
- Deployable to Model Serving

### 3. Deployment (`databricks/deployment.py`)
- `AgentDeploymentManager`: Handles registration and deployment
- Unity Catalog integration
- Endpoint management
- A/B testing support

### 4. Evaluation (`databricks/evaluation.py`)
- `AgentEvaluator`: Quality metrics tracking
- Automated evaluation pipelines
- Regression detection
- Version comparison

### 5. Notebooks (`databricks/notebooks/`)
- Interactive development environment
- Step-by-step deployment guide
- Evaluation examples
- Delta Lake integration

## Getting Started

### Option 1: Databricks Notebook (Recommended)

1. Import notebook to your workspace:
   ```
   databricks workspace import \
     databricks/notebooks/01_agent_bricks_quickstart.py \
     /Users/your-email@company.com/oral-health-agents
   ```

2. Attach to a cluster with:
   - DBR 14.3 LTS ML or higher
   - Unity Catalog enabled

3. Run all cells to:
   - Register agents
   - Deploy to Model Serving
   - Evaluate performance

### Option 2: Python Script

1. Set environment variables:
   ```bash
   export DATABRICKS_HOST="https://your-workspace.cloud.databricks.com"
   export DATABRICKS_TOKEN="your-token"
   export OPENAI_API_KEY="your-openai-key"
   ```

2. Register agents:
   ```bash
   source venv/bin/activate
   python -m databricks.deployment
   ```

3. Run evaluation:
   ```bash
   python -m databricks.evaluation
   ```

## Unity Catalog Structure

```
main/                          # Catalog
├── agents/                    # Schema for agent models
│   ├── policy_classifier      # Classifier agent
│   ├── sentiment_analyzer     # Sentiment agent
│   └── advocacy_writer        # Advocacy agent
└── policy_data/               # Schema for data
    ├── raw_documents          # Scraped documents
    ├── classified_documents   # Classified results
    └── advocacy_opportunities # Identified opportunities
```

## Model Serving Endpoints

### Development Endpoints
- `policy-classifier-dev`: Classifier for testing
- `sentiment-analyzer-dev`: Sentiment analysis
- `advocacy-writer-dev`: Content generation

### Production Endpoints
- `policy-classifier-prod`: Production classifier
- `multi-agent-pipeline`: Full pipeline with traffic splitting

## Deployment Workflow

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│ Development  │────►│   Staging    │────►│  Production  │
│              │     │              │     │              │
│ • Local test │     │ • A/B test   │     │ • Monitor    │
│ • Register   │     │ • Evaluate   │     │ • Scale      │
│ • Deploy dev │     │ • Approve    │     │ • Feedback   │
└──────────────┘     └──────────────┘     └──────────────┘
```

## API Usage

### Invoke via REST

```bash
curl -X POST https://your-workspace.cloud.databricks.com/serving-endpoints/policy-classifier-prod/invocations \
  -H "Authorization: Bearer $DATABRICKS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "dataframe_records": [{
      "document_id": "doc_001",
      "title": "City Council Meeting",
      "content": "Discussion on water fluoridation..."
    }]
  }'
```

### Invoke via Python SDK

```python
from databricks.sdk import WorkspaceClient

w = WorkspaceClient()

response = w.serving_endpoints.query(
    name="policy-classifier-prod",
    dataframe_records=[{
        "document_id": "doc_001",
        "title": "City Council Meeting",
        "content": "Discussion on water fluoridation..."
    }]
)

print(response.predictions[0])
```

## Monitoring & Observability

### MLflow Tracing
- Automatic trace capture for all agent calls
- LLM request/response logging
- Latency tracking
- Cost estimation

### View Traces
```python
import mlflow

# Get traces for a run
traces = mlflow.get_traces(
    experiment_id="your-experiment-id",
    filter_string="attributes.agent_role = 'classifier'"
)

for trace in traces:
    print(f"Trace ID: {trace.request_id}")
    print(f"Latency: {trace.execution_time_ms}ms")
    print(f"Status: {trace.status}")
```

### Endpoint Metrics
- Request rate
- Latency (P50, P95, P99)
- Error rate
- Token usage
- Cost per request

## Evaluation

### Automated Evaluation
```python
from databricks.evaluation import AgentEvaluator

evaluator = AgentEvaluator("policy_classifier")

metrics = evaluator.evaluate_classifier(
    model_uri="models:/main.agents.policy_classifier/1",
    test_documents=test_docs,
    ground_truth=labels
)

print(f"Accuracy: {metrics.accuracy:.2%}")
print(f"F1 Score: {metrics.f1_score:.2%}")
```

### A/B Testing
```python
comparison = evaluator.compare_versions(
    version_a="1",
    version_b="2",
    eval_data=eval_df
)

# Automatically promote if v2 is better
if comparison["improvements"]["accuracy"]["improvement_pct"] > 5:
    # Promote to production
    manager.deploy_agent(
        agent_name="policy_classifier",
        endpoint_name="policy-classifier-prod",
        version="2"
    )
```

## Best Practices

1. **Version Control**: Always register new versions to Unity Catalog
2. **Evaluate First**: Run evaluation before deploying to production
3. **Monitor Continuously**: Set up alerts for drift and errors
4. **Use Feedback**: Collect corrections and retrain regularly
5. **Scale Gradually**: Start with small workloads, scale up
6. **Cost Optimization**: Use scale-to-zero for dev/staging endpoints

## Cost Considerations

| Component | Estimated Cost |
|-----------|---------------|
| Model Serving (Small, scale-to-zero) | ~$0.10-0.50/hour active |
| MLflow Tracking | Included |
| Unity Catalog | Included |
| LLM API calls | $0.002-0.03 per request |

**Cost Optimization Tips:**
- Use keyword classification before LLM
- Enable scale-to-zero for dev endpoints
- Batch requests when possible
- Cache frequent queries
- Monitor token usage

## Troubleshooting

### Issue: Agent fails to load
```python
# Check model status
from mlflow.tracking import MlflowClient

client = MlflowClient()
versions = client.search_model_versions(
    filter_string="name='main.agents.policy_classifier'"
)
print(versions[0].status)
```

### Issue: Endpoint is slow
- Check workload size (upgrade from Small to Medium)
- Enable auto-scaling
- Review LLM prompt length
- Add caching layer

### Issue: High error rate
- Check MLflow traces for specific errors
- Verify input schema matches signature
- Review LLM API rate limits
- Check Unity Catalog permissions

## Next Steps

1. **Deploy More Agents**: Add sentiment analyzer and advocacy writer
2. **Create Workflows**: Use Databricks Workflows for scheduled processing
3. **Add Feedback Loop**: Store corrections in Delta Lake
4. **Set Up Alerts**: Monitor for drift and errors
5. **Scale Production**: Process thousands of documents

## Resources

- [Databricks Agent Framework Docs](https://docs.databricks.com/en/generative-ai/agent-framework/index.html)
- [MLflow Agent Deployment](https://mlflow.org/docs/latest/llms/deployments/index.html)
- [Unity Catalog AI](https://docs.databricks.com/en/generative-ai/unity-catalog-ai.html)
- [Model Serving Guide](https://docs.databricks.com/en/machine-learning/model-serving/index.html)
