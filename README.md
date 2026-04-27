---
title: Open Navigator for Engagement
emoji: 🦷
colorFrom: blue
colorTo: green
sdk: docker
app_port: 7860
pinned: false
---

# Open Navigator for Engagement

> *AI-powered community impact and engagement finder with React + FastAPI web interface*

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![React](https://img.shields.io/badge/React-18.2-61DAFB.svg)](https://reactjs.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-009688.svg)](https://fastapi.tiangolo.com)

## � Quick Links

**[⚛️ Open Navigator →](https://www.communityone.com)** - **LIVE APPLICATION** (search, filters, heatmap, data exploration)

**[📖 Documentation →](https://www.communityone.com/docs)** - Complete guides, architecture, and feature details

The documentation site includes:
- Features and capabilities
- Data sources and integrations
- Architecture and deployment options
- Policy topics and advocacy tools
- API reference and examples

---

## Quick Start

### Three Services

This project runs three separate services:

| Service | Port (Local) | Live URL | Description |
|---------|------|----------|-------------|
| **⚛️ Open Navigator** 🚀 | 5173 | [www.communityone.com](https://www.communityone.com) | **MAIN APPLICATION** - Search, filters, heatmap, data exploration |
| **📚 Documentation** | 3000 | [www.communityone.com/docs](https://www.communityone.com/docs) | Docusaurus site with complete guides and tutorials |
| **🔥 API Backend** | 8000 | [www.communityone.com/api](https://www.communityone.com/api) | FastAPI server with AI agents |

> **💡 LIVE DEMO:** Visit **[www.communityone.com](https://www.communityone.com)** to use the application!
> 
> **💻 LOCAL DEV:** After running `./start-all.sh`, visit **http://localhost:5173**

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker (optional)
- OpenAI API key

### Installation

**Option 1: Start Everything at Once (Recommended)**

```bash
# Clone repository
git clone https://github.com/getcommunityone/open-navigator-for-engagement.git
cd oral-health-policy-pulse

# Install dependencies
./install.sh                          # Python backend
cd frontend && npm install && cd ..   # React app
cd website && npm install && cd ..    # Documentation

# Start all services in tmux
./start-all.sh
```

**Option 2: Using Makefile**

```bash
# Install
make install
make install-frontend
make install-docs

# Start all services
make start-all

# Or individually:
make dev           # API only
make dev-frontend  # React app only
make dev-docs      # Docs only
```

**Option 3: Manual Setup**

```bash
# Python backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# React app
cd frontend && npm install && cd ..

# Documentation
cd website && npm install && cd ..

# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Start services (separate terminals)
source .venv/bin/activate && python main.py serve  # Terminal 1
cd frontend && npm run dev                          # Terminal 2
cd website && npm start                             # Terminal 3
```

### Access Points

**🌐 LIVE APPLICATION:**
- **🚀 Open Navigator:** https://www.communityone.com - Main application
- 📚 **Documentation:** https://www.communityone.com/docs - Guides and API reference
- 🔥 **API Docs:** https://www.communityone.com/api/docs - FastAPI interactive documentation

**💻 LOCAL DEVELOPMENT:**
- **🚀 Main App:** http://localhost:5173
- 📚 **Documentation:** http://localhost:3000
- 🔥 **API Docs:** http://localhost:8000/docs

### Stop Services

```bash
./stop-all.sh
# or
make stop-all
```

---

## Usage

### Command Line Interface

Always activate the virtual environment first:

```bash
source .venv/bin/activate
```

**API Server**

```bash
python main.py serve --host 0.0.0.0 --port 8000
```

**Jurisdiction Discovery**

```bash
# Test run
python main.py discover-jurisdictions --limit 100

# Single state
python main.py discover-jurisdictions --state CA

# Full discovery (~30k jurisdictions)
python main.py discover-jurisdictions

# View statistics
python main.py discovery-stats
```

**Data Ingestion**

```bash
# Census data (90,000+ jurisdictions)
python -m discovery.census_ingestion

# NCES school districts (13,000+)
python -m discovery.nces_ingestion

# Pre-built meeting datasets
python discovery/meetingbank_ingestion.py
python discovery/city_scrapers_urls.py
python discovery/openstates_sources.py

# LocalView (requires Dataverse API key)
python discovery/localview_ingestion.py
```

**Scraping & Analysis**

```bash
# Scrape batch from discovered sites
python main.py scrape-batch --source discovered --limit 50

# Scrape single source
python main.py scrape --url "https://city.legistar.com" \
                      --state "CA" \
                      --municipality "San Francisco"

# Run analysis pipeline
python main.py analyze --targets-file examples/targets.json

# Generate heatmap
python main.py generate-heatmap --output heatmap.html
```

**Publishing Datasets**

```bash
# Publish to HuggingFace (requires HUGGINGFACE_TOKEN in .env)
python main.py publish-to-hf --dataset all
python main.py publish-to-hf --dataset discovered-urls
python main.py publish-to-hf --dataset census --sample
```

### API Usage

**Start a workflow:**

```bash
curl -X POST "http://localhost:8000/workflow/start" \
     -H "Content-Type: application/json" \
     -d '{
       "scrape_targets": [
         {
           "url": "https://example-city.legistar.com",
           "municipality": "Example City",
           "state": "CA",
           "platform": "legistar"
         }
       ]
     }'
```

**Query opportunities:**

```bash
curl "http://localhost:8000/opportunities?state=CA&urgency=critical"
```

**Get heatmap:**

```bash
curl "http://localhost:8000/heatmap" > heatmap.html
```

### Python API

```python
import asyncio
from agents.orchestrator import OrchestratorAgent
from agents.scraper import ScraperAgent
from agents.parser import ParserAgent
from agents.classifier import ClassifierAgent

# Initialize orchestrator
orchestrator = OrchestratorAgent()

# Register agents
orchestrator.register_agent(ScraperAgent())
orchestrator.register_agent(ParserAgent())
orchestrator.register_agent(ClassifierAgent())

# Execute pipeline
targets = [
    {
        "url": "https://city.legistar.com",
        "municipality": "Example City",
        "state": "CA",
        "platform": "legistar"
    }
]

results = await orchestrator.execute_pipeline(targets)
```

---

## Project Structure

```
oral-health-policy-pulse/
├── agents/                 # Multi-agent AI system
├── api/                   # FastAPI application
├── frontend/             # React application (Open Navigator)
├── website/              # Docusaurus documentation
├── discovery/            # Data discovery modules
├── extraction/           # Document extraction
├── pipeline/             # Data pipeline components
├── visualization/        # Heatmap and charts
├── config/               # Configuration
├── tests/                # Test suite
├── main.py              # CLI entry point
└── requirements.txt     # Python dependencies
```

---

## Deployment Options

### 1. 🤗 Hugging Face Spaces (Recommended)

Deploy all three apps (Documentation, Frontend, API) to a single Docker Space:

**Quick start (first time):**
```bash
# Add your HF username to .env
echo "HF_USERNAME=your_hf_username" >> .env

# Run the interactive setup wizard (login, verify env vars, deploy)
./setup-huggingface.sh
```

**Redeploy after changes:**
```bash
./deploy-huggingface.sh
# or pass username as argument:
./deploy-huggingface.sh YOUR_HF_USERNAME
```

The script will:
1. Authenticate with Hugging Face (`huggingface-cli login`)
2. Create or update the Space
3. Push code to `https://huggingface.co/spaces/YOUR_USERNAME/open-navigator-for-engagement`
4. Build takes ~10-15 minutes

**After deployment, configure your Space:**
- Settings → Resource configuration → Select **CPU Basic** (~$22/month, required for Docker)
- Settings → Variables & Secrets → Add `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `HUGGINGFACE_TOKEN`

See [Hugging Face Spaces Deployment Guide](website/docs/deployment/huggingface-spaces.md) for the complete walkthrough.

### 2. Databricks Apps (Enterprise)

```bash
export DATABRICKS_HOST=https://your-workspace.cloud.databricks.com
export DATABRICKS_TOKEN=dapi...
export OPENAI_API_KEY=sk-...

./scripts/deploy-databricks-app.sh
```

See [DATABRICKS_APP_GUIDE.md](DATABRICKS_APP_GUIDE.md) for details.

### 3. Docker (Local / Self-hosted)

```bash
docker-compose up -d
```

Starts:
- API server (port 8000)
- Qdrant vector database (port 6333)
- Jupyter notebook (port 8888)

### 4. Local Development

See [Quick Start](#quick-start) above.

---

## Testing

```bash
# Run all tests
pytest

# With coverage
pytest --cov=agents --cov=pipeline --cov=visualization

# Specific test file
pytest tests/test_agents.py
```

---

## Configuration

Create `.env` file:

```bash
# OpenAI
OPENAI_API_KEY=sk-...

# Databricks (optional)
DATABRICKS_HOST=https://your-workspace.cloud.databricks.com
DATABRICKS_TOKEN=dapi...

# HuggingFace (optional)
HUGGINGFACE_TOKEN=hf_...

# Dataverse (optional)
DATAVERSE_API_KEY=...
```

---

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

---

## Documentation

- **[Full Documentation](http://localhost:3000)** - Complete guides and API reference
- **[Architecture](http://localhost:3000/docs/architecture)** - System architecture overview
- **[Quick Start](http://localhost:3000/docs/quickstart)** - Detailed setup instructions
- **[Quick Reference](http://localhost:3000/docs/quick-reference)** - Command reference card
- **[Deployment](http://localhost:3000/docs/deployment/databricks-apps)** - Production deployment guides
- **[Case Studies](http://localhost:3000/docs/case-studies/tuscaloosa-complete)** - Real-world examples
- [CONTRIBUTING.md](CONTRIBUTING.md) - How to contribute

---

## Citations

This project uses several open datasets and research contributions. **Please see [CITATIONS.md](CITATIONS.md) for complete citation information.**

**Key Dataset:**
- **MeetingBank**: Hu et al., "MeetingBank: A Benchmark Dataset for Meeting Summarization", ACL 2023
  - Used for meeting discovery and analysis
  - 1,366 city council meetings from 6 U.S. cities
  - See [CITATIONS.md](CITATIONS.md) for full citation and BibTeX

---

## License

MIT License - see [LICENSE](LICENSE) file for details.

---

## Support

- GitHub Issues: [github.com/getcommunityone/open-navigator-for-engagement/issues](https://github.com/getcommunityone/open-navigator-for-engagement/issues)
- Email: support@communityone.com

---

**Note**: This system is designed to support advocacy efforts. All generated content should be reviewed by humans before use.
