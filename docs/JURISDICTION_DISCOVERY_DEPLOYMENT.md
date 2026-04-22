# Jurisdiction Discovery - Deployment Options

You have **three deployment options** for running the jurisdiction discovery system:

## Option 1: Local CLI (Recommended for Testing)

Run discovery directly from your local machine or development environment.

### Advantages
- ✅ Fastest setup
- ✅ No cloud costs
- ✅ Easy debugging
- ✅ Full control

### Usage

```bash
# Basic discovery
python main.py discover-jurisdictions --limit 100

# Filter by state
python main.py discover-jurisdictions --state CA

# Full production run
python main.py discover-jurisdictions

# View statistics
python main.py discovery-stats

# Start batch scraping
python main.py scrape-batch --source discovered --limit 50
```

### When to Use
- Testing and development
- Small-scale discovery (single state or limited jurisdictions)
- One-time manual runs
- Debugging issues

---

## Option 2: Databricks Notebook (Recommended for Production)

Run discovery in a Databricks notebook with full Spark capabilities.

### Advantages
- ✅ Leverage Spark for parallel processing
- ✅ Built-in monitoring and logging
- ✅ Schedule with Databricks Workflows
- ✅ Access to large compute resources

### Setup

1. **Upload Notebook**
   ```bash
   databricks workspace import \
     notebooks/Jurisdiction_Discovery.py \
     /Users/your-email@company.com/Jurisdiction_Discovery \
     --language PYTHON
   ```

2. **Create Cluster**
   - Runtime: 14.3 LTS or higher
   - Node type: Standard_DS3_v2
   - Workers: 2-4
   - Libraries: Install from requirements.txt

3. **Configure Secrets**
   ```bash
   databricks secrets create-scope oral-health-app
   databricks secrets put-secret oral-health-app google-search-api-key
   databricks secrets put-secret oral-health-app google-search-engine-id
   databricks secrets put-secret oral-health-app bing-search-api-key
   ```

4. **Run Notebook**
   - Attach to cluster
   - Execute all cells
   - Monitor progress in real-time

### When to Use
- Production discovery runs
- Processing 10,000+ jurisdictions
- Need for parallel processing
- Scheduled/automated discovery

### Scheduling

Create a Databricks Workflow:

```python
# In Databricks UI: Workflows → Create Job
{
  "name": "Monthly Jurisdiction Discovery",
  "tasks": [{
    "task_key": "discover_jurisdictions",
    "notebook_task": {
      "notebook_path": "/Users/your-email/Jurisdiction_Discovery",
      "base_parameters": {
        "discovery_limit": "null",  # Full discovery
        "state_filter": "null"
      }
    },
    "existing_cluster_id": "your-cluster-id"
  }],
  "schedule": {
    "quartz_cron_expression": "0 0 1 * *",  # Monthly on 1st
    "timezone_id": "America/Los_Angeles"
  }
}
```

---

## Option 3: AgentBricks Model Serving (Recommended for API Integration)

Deploy discovery as a Databricks Model Serving endpoint for API-based access.

### Advantages
- ✅ REST API endpoint
- ✅ Integration with other agents
- ✅ Auto-scaling
- ✅ Built-in monitoring and tracing
- ✅ Version control

### Setup

1. **Deploy Agent**
   ```python
   from discovery.mlflow_discovery_agent import deploy_discovery_agent
   
   endpoint_url = deploy_discovery_agent(
       endpoint_name="jurisdiction-discovery",
       workload_size="Small"  # Small, Medium, or Large
   )
   ```

   Or via CLI:
   ```bash
   python -m discovery.mlflow_discovery_agent
   ```

2. **Endpoint URL**
   ```
   https://your-workspace.cloud.databricks.com/serving-endpoints/jurisdiction-discovery/invocations
   ```

### API Usage

**Discover Jurisdictions:**
```python
import requests

response = requests.post(
    f"{endpoint_url}",
    headers={"Authorization": f"Bearer {databricks_token}"},
    json={
        "dataframe_records": [{
            "action": "discover",
            "params": {
                "limit": 100,
                "state": "CA"
            }
        }]
    }
)

result = response.json()
# {
#   "status": "success",
#   "data": {
#     "bronze_records": 90735,
#     "urls_discovered": 87,
#     "scraping_targets": 65
#   }
# }
```

**Get Statistics:**
```python
response = requests.post(
    f"{endpoint_url}",
    headers={"Authorization": f"Bearer {databricks_token}"},
    json={
        "dataframe_records": [{
            "action": "stats",
            "params": {}
        }]
    }
)
```

**Get Scraping Targets:**
```python
response = requests.post(
    f"{endpoint_url}",
    headers={"Authorization": f"Bearer {databricks_token}"},
    json={
        "dataframe_records": [{
            "action": "targets",
            "params": {
                "priority_min": 150,
                "state": "CA",
                "limit": 50
            }
        }]
    }
)

targets = response.json()["data"]["targets"]
```

### When to Use
- API-based workflows
- Integration with other services
- Need for programmatic access
- Multi-agent orchestration
- Production serving with SLA requirements

### Monitoring

View endpoint metrics in Databricks:
- **Serving Endpoints** → `jurisdiction-discovery`
- Monitor latency, throughput, errors
- View MLflow traces for each request

---

## Comparison Matrix

| Feature | Local CLI | Databricks Notebook | AgentBricks Serving |
|---------|-----------|---------------------|---------------------|
| **Setup Time** | 5 minutes | 15 minutes | 30 minutes |
| **Cost** | Free | $2-4/hour | $0.50-2/hour* |
| **Scalability** | Limited | High | Auto-scale |
| **API Access** | ❌ | ❌ | ✅ |
| **Scheduling** | ❌ | ✅ | ✅ (via API) |
| **Monitoring** | Basic logs | Full dashboards | MLflow tracing |
| **Parallel Processing** | Limited | ✅ | ✅ |
| **Best For** | Testing | Production batch | Production API |

*With scale-to-zero enabled

---

## Recommended Workflow

### Phase 1: Testing (Local CLI)
```bash
# Test with small sample
python main.py discover-jurisdictions --limit 100 --state CA
python main.py discovery-stats
```

### Phase 2: Production Discovery (Databricks Notebook)
```bash
# Upload and run notebook for full discovery
databricks workspace import notebooks/Jurisdiction_Discovery.py /Users/.../Discovery
# Run notebook with limit=null for full discovery
```

### Phase 3: Ongoing Operations (AgentBricks)
```python
# Deploy as serving endpoint for API access
deploy_discovery_agent()

# Schedule monthly re-discovery via API
# Integrate with scraper agents
```

---

## Cost Optimization

### Local CLI
- **Compute**: Free (local machine)
- **Search APIs**: $78 for 30k jurisdictions (mix Google free tier + Bing)
- **Total**: ~$78

### Databricks Notebook
- **Compute**: ~$4/hour × 5 hours = $20
- **Search APIs**: $78
- **Total**: ~$98 (one-time)
- **Monthly re-discovery**: ~$20 (fewer API calls, cached data)

### AgentBricks Serving
- **Model Serving**: $0.50-2/hour with scale-to-zero
- **Per-request**: ~$0.01/request
- **Monthly**: ~$10-20 for periodic discovery + API access
- **Total**: ~$10-20/month (ongoing)

### Recommended Strategy
1. Use **Local CLI** for testing ($0)
2. Use **Databricks Notebook** for initial full discovery ($98)
3. Deploy **AgentBricks** for ongoing operations ($10-20/month)
4. Schedule monthly re-discovery via AgentBricks API

---

## Next Steps

Choose your deployment path:

**For Testing:**
```bash
python main.py discover-jurisdictions --limit 100
```

**For Production Batch:**
1. Upload notebook to Databricks
2. Run full discovery
3. Schedule monthly re-runs

**For API Integration:**
```bash
python -m discovery.mlflow_discovery_agent
```

Then start scraping:
```bash
python main.py scrape-batch --source discovered --limit 50
```

---

All three options are production-ready and can be used interchangeably based on your needs! 🚀
