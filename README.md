# 🦷 Open Navigator for Engagement

> *AI-powered advocacy opportunity finder with React + FastAPI web interface*

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![React](https://img.shields.io/badge/React-18.2-61DAFB.svg)](https://reactjs.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-009688.svg)](https://fastapi.tiangolo.com)
[![Databricks](https://img.shields.io/badge/Databricks-Apps-FF3621.svg)](https://www.databricks.com)
[![Docusaurus](https://img.shields.io/badge/Docusaurus-3.10-green.svg)](https://docusaurus.io)

## 📚 Documentation

**[📖 Read the full documentation →](http://localhost:3000)** (Start with `cd website && npm start`)

**[⚛️ Launch Open Navigator →](http://localhost:5173)** (Start with `cd frontend && npm run dev`)

> **Architecture Note**: This project has **three separate services**:
> - 📚 **Documentation Site** (port 3000) - Guides, API docs, getting started
> - ⚛️ **Open Navigator** (port 5173) - **Main application** with search, filters, heatmap, data exploration
> - 🔥 **API Backend** (port 8000) - Data processing and AI agents
>
> See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed explanation.

This README provides a quick overview. For comprehensive guides, API reference, and tutorials, visit the **Docusaurus documentation site** in the `website/` directory. For the **actual application interface with search, filters, and data exploration**, use **Open Navigator** in the `frontend/` directory.

## Overview

The **Open Navigator for Engagement** is a full-stack AI application that analyzes thousands of **municipal meeting minutes and financial documents** across the country to identify policy opportunities for oral health advocacy. It features a **modern React web interface**, **FastAPI backend**, and **multi-agent AI system** powered by Databricks.

### What It Analyzes

**📄 Meeting Minutes & Transcripts**
- **Government**: City council meetings, school board sessions, health department discussions, public hearings, budget meetings, committee sessions
- **Nonprofit**: Board meetings, committee meetings, public forums, community listening sessions
- Automatically scraped from 90,000+ local government websites and nonprofit public records

**💰 Financial Documents**
- **Government**: Municipal budgets and amendments, school district financial reports, department expenditures, revenue allocations, funding proposals
- **Nonprofit**: IRS Form 990 filings (revenue, expenses, executive compensation), annual reports, financial statements, grant allocations, program budgets
- Correlates spending with meeting rhetoric to reveal true priorities for both government agencies and nonprofit organizations

**✨ New in v2.0:**
- 🎨 **React Frontend** - Modern, responsive UI with interactive visualizations
- 🚀 **Databricks Apps** - One-click deployment to Databricks workspace
- 📊 **Real-Time Platform** - Live analytics and opportunity tracking
- 🗺️ **Interactive Heatmap** - Geographic visualization of advocacy opportunities
- 📧 **Automated Generation** - AI-powered advocacy emails and materials

### Key Features

- 🤖 **Multi-Agent Architecture**: Coordinated agents for scraping, parsing, classification, sentiment analysis, and advocacy generation
- 🔍 **Jurisdiction Discovery**: Automatically identifies 90,000+ local government websites using Census Bureau data
- 🏛️ **Massive Scale**: Handles millions of meeting minutes and financial documents using Delta Lake on Databricks
- 💰 **Budget-to-Minutes Analysis**: Correlates meeting rhetoric with actual spending to reveal true priorities
- 📊 **Financial Document Extraction**: Automatically parses budgets, expenditure reports, and funding allocations
- 🗺️ **Advocacy Heatmap**: Visual representation of policy opportunities across the country
- 📧 **Automated Materials**: Generates personalized emails, talking points, and social media content
- 📈 **Real-Time Analytics**: Identifies windows of opportunity for policy change based on both discussion and funding
- 🎯 **Topic-Focused**: Monitors water fluoridation, school dental programs, Medicaid dental, and more

## 💰 Free Nonprofit Data Sources

Access comprehensive nonprofit data without expensive subscriptions. The platform integrates with **100% free** open data APIs to discover and track organizations already providing services that governments claim are "impossible."

### Why This Matters

**Direct Community Impact:**
- **Discover Local Solutions** - Find nonprofits and community organizations already providing dental care, health screenings, and education programs in your area
- **Connect Citizens to Services** - Provide direct pathways for people to access care, volunteer, or donate to organizations making a difference
- **Partnership Opportunities** - Identify potential partners for advocacy campaigns, service expansion, or collaborative initiatives
- **Resource Mapping** - Understand the full landscape of oral health services available in each community

**Government Accountability & Advocacy:**
- **Challenge "Impossibility" Claims** - When officials say "We can't do dental screenings - legal liability," show the nonprofits already doing it successfully
- **Expose Resource Gaps** - Reveal where government funding falls short and community organizations are filling the void
- **Opportunity Cost Analysis** - Compare government spending priorities with nonprofit service provision ("City spent $200K on landscaping while nonprofits struggle to fund children's dental care")
- **Policy Precedents** - Demonstrate proven models that government could replicate or support

**Strategic Advocacy:**
- **Evidence-Based Campaigns** - Ground advocacy in real data about who's serving communities and what's working
- **Coalition Building** - Identify natural allies and stakeholders for policy campaigns
- **Alternative Pathways** - When government action stalls, direct people to existing nonprofit solutions
- **Mobilization** - Turn "government should do X" into "help organization Y expand what they're already doing"

**Nonprofit Accountability & Advocacy:**
- **Mission Alignment Analysis** - Compare nonprofit board meeting minutes with actual programs and spending (same Budget-to-Minutes framework)
- **Financial Transparency** - Analyze Form 990 data alongside stated priorities to verify resource allocation
- **Service Verification** - Ensure nonprofits claiming to serve specific populations are actually delivering
- **Impact Assessment** - Track whether nonprofits meeting discussions about new programs lead to actual service expansion
- **Donor Intelligence** - Help funders verify that nonprofits are focusing resources where they say they are
- **Board Accountability** - Monitor whether nonprofit boards address the issues they claim to prioritize

### Integrated Data Sources

#### 1. 🏆 ProPublica Nonprofit Explorer API (Primary Source)

**Best overall free source** for IRS Form 990 financial data.

- **Coverage**: 3+ million organizations, 10+ years of filings
- **Data**: Revenue, expenses, assets, executive compensation, NTEE codes
- **Rate Limits**: Free, unlimited (be respectful: ~1 req/sec suggested)
- **API Docs**: [ProPublica Nonprofit Explorer API](https://projects.propublica.org/nonprofits/api)

```python
# Example: Search health nonprofits in Tuscaloosa
from discovery.nonprofit_discovery import NonprofitDiscovery
discovery = NonprofitDiscovery()
health_orgs = discovery.search_propublica(
    state="AL", city="Tuscaloosa", ntee_code="E"  # E = Health
)
```

#### 2. 📋 IRS Tax Exempt Organization Search (TEOS)

**Official source of truth** for all U.S. nonprofits and churches.

- **Coverage**: Every registered tax-exempt organization
- **Data**: Legal status, Pub 78 verification (deductibility), raw financial extracts
- **Format**: Bulk data downloads (CSV/JSON)
- **Resource**: [IRS Bulk Data Downloads](https://www.irs.gov/charities-non-profits/tax-exempt-organization-search-bulk-data-downloads)

#### 3. 🌟 Every.org Charity API

**Best for human-readable** mission statements and visual assets.

- **Coverage**: Verified nonprofits with enhanced metadata
- **Data**: Mission statements, logos, cover images, cause categories
- **Best Feature**: "Browse by Cause" - easier discovery than raw IRS codes
- **API Docs**: [Every.org Charity API](https://www.every.org/nonprofit-api)

```python
# Example: Find nonprofits by cause
nonprofits = discovery.search_everyorg(
    location="Tuscaloosa, AL",
    causes=["health", "education"]
)
```

#### 4. 🔍 Findhelp.org (Aunt Bertha)

**Most comprehensive local services directory** for food, health, housing.

- **Coverage**: 400,000+ community programs across the U.S.
- **Data**: Services provided, eligibility criteria, contact info, hours
- **Best Use**: Search "dental" + location to find active providers
- **Resource**: [Findhelp.org](https://www.findhelp.org/)
- **Note**: API access varies; web scraping is an option for small-scale use

#### 5. 📞 211 Directory

**Regional social services directory** available in most U.S. regions.

- **Coverage**: Local United Way and community service referrals
- **Data**: Service descriptions, contact information, hours of operation
- **Access**: State/region-specific (e.g., [Alabama 211](https://www.211connects.org/))
- **Note**: Each region has different systems; scraping may be required

### Nonprofit Data Ingestion

The system can **bulk ingest nonprofit data** into the Delta Lake for analysis:

```bash
# Ingest nonprofits for specific location
python -c "
from discovery.nonprofit_discovery import NonprofitDiscovery
discovery = NonprofitDiscovery()

# Bulk search and cache
orgs = discovery.search_propublica(state='AL', ntee_code='E')
print(f'Cached {len(orgs)} health nonprofits in Alabama')
"
```

**API Access:**
```bash
# Search nonprofits
GET /api/nonprofits?location=Tuscaloosa,AL&keyword=dental

# Trigger bulk ingestion (admin)
POST /api/data/ingest/nonprofits
{
  "state": "AL",
  "ntee_codes": ["E", "E20", "E30"],
  "cache_only": false
}
```

See [`discovery/nonprofit_discovery.py`](discovery/nonprofit_discovery.py) for implementation and [`discovery/README_NONPROFIT_DISCOVERY.md`](discovery/README_NONPROFIT_DISCOVERY.md) for documentation.

## 📊 Reference Data & Jurisdiction Discovery

The platform ingests comprehensive reference datasets to identify and enrich 90,000+ government jurisdictions nationwide. All data sources are **100% free and public**.

### Census Bureau Data Ingestion

**Source:** [U.S. Census Bureau Government Integrated Directory (GID)](https://www.census.gov/programs-surveys/gid.html)

Provides complete listings of all government entities with standardized FIPS codes, geographic coordinates, and population data.

**Coverage:**
- 🏛️ **3,144 Counties** - All U.S. counties with FIPS, lat/lon, population
- 🏘️ **19,500+ Municipalities** - Cities, towns, villages, boroughs
- 📍 **36,000+ Townships** - County subdivisions, census divisions
- 🏫 **13,000+ School Districts** - Elementary, secondary, and unified districts

**Data Files:** Census Gazetteer 2024
```bash
# Ingest all Census jurisdiction data
python -c "
from discovery.census_ingestion import CensusGovernmentIngestion
ingestor = CensusGovernmentIngestion()

# Download and process all jurisdiction types
await ingestor.ingest_all_jurisdictions()
# Saved to: data/bronze/census_jurisdictions/
"
```

**Implementation:** [`discovery/census_ingestion.py`](discovery/census_ingestion.py)

### NCES School District Data

**Source:** [NCES Common Core of Data (CCD)](https://nces.ed.gov/ccd/)

Complete directory of all U.S. school districts with contact information and enrollment data.

**Coverage:**
- 13,000+ school districts nationwide
- District names, addresses, phone numbers
- NCES IDs for standardized identification
- Enrollment counts and demographic data
- Website URLs (when available)

```bash
# Ingest NCES school district data
python -c "
from discovery.nces_ingestion import NCESSchoolDistrictIngestion
ingestor = NCESSchoolDistrictIngestion()

districts = await ingestor.download_and_process()
# Saved to: data/bronze/nces_school_districts/
"
```

**Why This Matters:** School boards control dental screening programs, nutrition policy, and health education. This provides complete contact info for all 13,000+ districts.

**Implementation:** [`discovery/nces_ingestion.py`](discovery/nces_ingestion.py)

### Harvard Dataverse Integration

**Source:** [Harvard Dataverse](https://dataverse.harvard.edu/)

Academic research datasets including LocalView (1,000+ municipalities with video archives).

**Available Datasets:**
- 📹 **LocalView** - Municipal meeting videos and transcripts from 1,000+ cities
- 🎓 **Research Collections** - Curated government datasets from Harvard, MIT, etc.

```bash
# Configure Dataverse API access (optional but recommended)
echo "DATAVERSE_API_KEY=your-api-key" >> .env

# Ingest LocalView dataset
python discovery/localview_ingestion.py
```

**Implementation:** [`discovery/dataverse_client.py`](discovery/dataverse_client.py) and [`discovery/localview_ingestion.py`](discovery/localview_ingestion.py)

### Pre-Built Meeting & Video Datasets

**Already Integrated Sources:**

1. **MeetingBank** (1,366 meetings from 6 cities)
   - Full transcripts, human-written summaries
   - YouTube/Vimeo video URLs extracted
   - Run: `python discovery/meetingbank_ingestion.py`

2. **City Scrapers** (100-500 validated agency URLs)
   - Curated from 5 major cities
   - Includes Granicus video pages
   - Run: `python discovery/city_scrapers_urls.py`

3. **Open States** (50+ state legislature channels)
   - YouTube/Vimeo sources via API
   - Run: `python discovery/openstates_sources.py`

**All ingested data flows to Delta Lake** for unified querying and analysis.

### Complete Data Ingestion Pipeline

```bash
# Full ingestion workflow (run once to populate reference data)
cd /home/developer/projects/oral-health-policy-pulse
source .venv/bin/activate

# 1. Census jurisdictions (90,000+ entities)
python -m discovery.census_ingestion

# 2. NCES school districts (13,000+)
python -m discovery.nces_ingestion

# 3. Pre-built meeting datasets
python discovery/meetingbank_ingestion.py
python discovery/city_scrapers_urls.py
python discovery/openstates_sources.py

# 4. LocalView (requires Dataverse API key)
python discovery/localview_ingestion.py

# 5. Nonprofit organizations (on-demand by location)
python -c "
from discovery.nonprofit_discovery import NonprofitDiscovery
discovery = NonprofitDiscovery()
orgs = discovery.search_propublica(state='AL', ntee_code='E')
"
```

**Result:** Comprehensive reference database of:
- ✅ 90,000+ government jurisdictions with geo-coordinates
- ✅ 13,000+ school districts with contact info
- ✅ 3,000+ meeting video URLs from pre-built datasets
- ✅ 3,000,000+ nonprofit organizations (searchable on-demand)

### API Endpoints for Data Management

```bash
# Check ingestion status
GET /api/data/status

# Trigger specific ingestion (admin only)
POST /api/data/ingest/census
POST /api/data/ingest/nces
POST /api/data/ingest/nonprofits

# Query ingested jurisdictions
GET /api/jurisdictions?state=AL&type=municipality
GET /api/school-districts?state=AL&limit=100
```

**All reference data stored in Delta Lake** with medallion architecture:
- **Bronze**: Raw downloaded data
- **Silver**: Cleaned and standardized
- **Gold**: Enriched with URLs and analysis

## Architecture

### Deployment Architecture

```
┌─────────────────────────────────────────────────────────┐
│              Databricks Workspace (Cloud)                │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │   React + FastAPI Databricks App                 │  │
│  │                                                   │  │
│  │   ┌──────────────┐      ┌──────────────────┐    │  │
│  │   │   React UI   │ ───▶ │  FastAPI Backend │    │  │
│  │   │ (Dashboard,  │      │  (REST API +     │    │  │
│  │   │  Heatmap,    │      │   Multi-Agent    │    │  │
│  │   │  Docs, etc.) │      │   Orchestration) │    │  │
│  │   └──────────────┘      └──────────────────┘    │  │
│  └───────────────────┬──────────────────────────────┘  │
│                      │                                  │
│  ┌───────────────────▼─────────────────────────────┐   │
│  │      Unity Catalog & Delta Lake                 │   │
│  │  • Meeting minutes & transcripts                │   │
│  │  • Budget documents & financial data            │   │
│  │  • Policy classifications & sentiment           │   │
│  │  • Advocacy opportunities & analytics           │   │
│  └─────────────────────────────────────────────────┘   │
│                                                          │
│  ┌─────────────────────────────────────────────────┐   │
│  │         Model Serving (AI Agents)                │   │
│  │  • Policy Classifier                            │   │
│  │  • Sentiment Analyzer                           │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

**🎯 Three Deployment Options:**

1. **Databricks Apps (Recommended)** - Full-stack web app hosted in Databricks
2. **Standalone Mode** - Local development with custom agents
3. **Docker** - Containerized deployment

See [`DATABRICKS_APP_GUIDE.md`](DATABRICKS_APP_GUIDE.md) for full deployment guide.

### Multi-Agent System

```
┌─────────────────────────────────────────────────────────────┐
│                    ORCHESTRATOR AGENT                        │
│              Coordinates entire workflow                     │
└────────────────────┬────────────────────────────────────────┘
                     │
        ┌────────────┼────────────┬──────────────┐
        ▼            ▼            ▼              ▼
   ┌─────────┐  ┌─────────┐  ┌──────────┐  ┌──────────┐
   │ SCRAPER │  │ PARSER  │  │CLASSIFIER│  │SENTIMENT │
   │  AGENT  │──▶  AGENT  │──▶  AGENT   │──▶  AGENT   │
   └────────Deploy to Databricks Apps (Production)**

```bash
# Set credentials
export DATABRICKS_HOST=https://your-workspace.cloud.databricks.com
export DATABRICKS_TOKEN=dapi...
export OPENAI_API_KEY=sk-...

# Deploy (builds frontend + backend)
./scripts/deploy-databricks-app.sh

# Access at: https://your-workspace.cloud.databricks.com/apps/oral-health-policy-pulse
```

**Option 2: Local Development**

```bash
# Setup environment
./scripts/setup-local.sh

# Terminal 1 - Backend
source venv/bin/activate
uvicorn api.app:app --reload

# Terminal 2 - Frontend
cd frontend
npm run dev

# Open: http://localhost:3000
```

**Option 3: Automated Installation (Legacy Standalone Mode───────┘
                                                  │
                                                  ▼
                                           ┌──────────┐
                                           │ADVOCACY  │
                                           │  AGENT   │
                                           └──────────┘
```

### Data Pipeline

```
┌─────────────────────────────────────────────────────────────┐
│                    DATA INGESTION                            │
├─────────────────────────────────────────────────────────────┤
│  Meeting Minutes          │  Financial Documents            │
│  • City Council           │  • Municipal Budgets            │
│  • School Boards          │  • Expenditure Reports          │
│  • Public Hearings        │  • Revenue Allocations          │
│  • Committee Sessions     │  • Department Spending          │
└──────────┬────────────────┴────────────┬───────────────────┘
           │                             │
           ▼                             ▼
      Scraping & OCR                Scraping & OCR
           │                             │
           ▼                             ▼
      Text Parsing                  Budget Extraction
           │                             │
           ▼                             ▼
      Classification              Line Item Analysis
           │                             │
           ▼                             ▼
    Sentiment Analysis            Budget-to-Minutes
           │                      Delta Analysis
           └──────────┬────────────────┘
                      ▼
              Delta Lake Storage
                      │
           ┌──────────┼──────────┐
           ▼          ▼          ▼
      Heatmap   Dashboard   Advocacy
                            Materials
```

## Installation

### Prerequisites

- Python 3.11+
- Node.js 18+ (for React dashboard and Docusaurus documentation)
- Docker (optional, for containerized deployment)
- Databricks workspace (for production lakehouse)
- OpenAI API key (for LLM capabilities)

Note: `./install.sh` now attempts to install `tesseract-ocr` automatically (Linux via `apt-get`, macOS via `brew`) so OCR parsing works out of the box.

### Documentation Site

This project uses **Docusaurus** for comprehensive documentation:

```bash
# Navigate to the documentation site
cd website

# Install dependencies
npm install

# Start the documentation server
npm start

# Open http://localhost:3000
```

The documentation site includes:
- Complete project documentation
- API reference
- Integration guides
- Data source documentation
- Interactive examples

### Quick Start

**🚀 Fastest Way: Start All Services at Once (Recommended)**

```bash
# Clone the repository
git clone https://github.com/getcommunityone/oral-health-policy-pulse.git
cd oral-health-policy-pulse

# Install dependencies
./install.sh                    # Python backend
cd frontend && npm install && cd ..      # Open Navigator
cd website && npm install && cd ..       # Documentation site

# Start everything with one command
./start-all.sh
```

This launches all three services in a tmux session:
- 📚 **Documentation**: http://localhost:3000 (Docusaurus site)
- ⚛️ **Open Navigator**: http://localhost:5173 (React app)
- 🔥 **API**: http://localhost:8000 (FastAPI backend)

**Using Makefile (Alternative)**

```bash
# Install all dependencies
make install
make install-frontend
make install-docs

# Start everything
make start-all

# Or start services individually:
make dev           # API only
make dev-frontend  # Dashboard only
make dev-docs      # Documentation only
```

**Manual Installation (Traditional)**

```bash
# Clone the repository
git clone https://github.com/getcommunityone/oral-health-policy-pulse.git
cd oral-health-policy-pulse

# Install Python backend
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Install Open Navigator
cd frontend && npm install && cd ..

# Install documentation site
cd website && npm install && cd ..

# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Start services (in separate terminals)
# Terminal 1: API
source .venv/bin/activate && python main.py serve

# Terminal 2: Open Navigator
cd frontend && npm run dev

# Terminal 3: Documentation
cd website && npm start
```

Visit:
- `http://localhost:3000` - Documentation and project overview
- `http://localhost:5173` - Open Navigator
- `http://localhost:8000/docs` - API documentation

> **💡 Tip:** Use `./start-all.sh` for the best development experience. It manages all services in tmux, making it easy to switch between terminals and see logs.
>
> **Stop all services:** `./stop-all.sh` or `make stop-all`

For detailed installation instructions and troubleshooting, see [QUICKSTART.md](QUICKSTART.md).

### Docker Deployment

```bash
docker-compose up -d
```

This starts:
- API server on port 8000
- Qdrant vector database on port 6333
- Jupyter notebook on port 8888

## Usage

### Command Line Interface

**Important:** Always activate the virtual environment first:
```bash
source venv/bin/activate
```

Then run commands:

```bash
# Start the API server
python main.py serve --host 0.0.0.0 --port 8000

# Discover local government websites (NEW!)
python main.py discover-jurisdictions --limit 100        # Test run
python main.py discover-jurisdictions --state CA          # Single state
python main.py discover-jurisdictions                     # Full discovery (~30k jurisdictions)

# View discovery statistics
python main.py discovery-stats

# Scrape discovered sites in batch
python main.py scrape-batch --source discovered --limit 50 --priority 150

# Publish datasets to HuggingFace Hub (requires HUGGINGFACE_TOKEN in .env)
python main.py publish-to-hf --dataset all                # Publish all datasets
python main.py publish-to-hf --dataset discovered-urls    # Publish specific dataset
python main.py publish-to-hf --dataset census --sample    # Test with sample data
python main.py publish-to-hf --dataset all --private      # Make datasets private

# Scrape a single source (legacy)
python main.py scrape --url "https://city.legistar.com" \
                      --state "CA" \
                      --municipality "San Francisco" \
                      --platform "legistar"

# Run analysis pipeline
python main.py analyze --targets-file examples/targets.json

# Generate heatmap
python main.py generate-heatmap --output heatmap.html --urgency critical

# Check system status
python main.py status
```

**Or use Make commands:**

```bash
make run          # Start API server
make dev          # Start with auto-reload
make example      # Run example workflow
make heatmap      # Generate example heatmap
make test         # Run tests
make clean        # Clean up environment
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
       ],
       "date_range": {
         "start": "2024-01-01",
         "end": "2024-12-31"
       }
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
from agents.sentiment import SentimentAnalyzerAgent
from agents.advocacy import AdvocacyWriterAgent

# Initialize orchestrator
orchestrator = OrchestratorAgent()

# Register agents
orchestrator.register_agent(ScraperAgent())
orchestrator.register_agent(ParserAgent())
orchestrator.register_agent(ClassifierAgent())
orchestrator.register_agent(SentimentAnalyzerAgent())
orchestrator.register_agent(AdvocacyWriterAgent())

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

## Data Sources

### Jurisdiction Discovery System

The system automatically discovers and tracks **90,000+ local government units** across the United States using **official, free, public datasets**:

**Data Sources (All Free!):**
- 🏛️ **CISA .gov Domain Master List** - 15,000+ validated .gov domains ([cisagov/dotgov-data](https://github.com/cisagov/dotgov-data))
- 📊 **Census Bureau Gazetteer Files 2024** - 85,302 individual jurisdictions with names, FIPS codes ([Census.gov](https://www.census.gov/geographies/reference-files/time-series/geo/gazetteer-files.html))
- 🎓 **NCES Common Core of Data** - 13,000+ school districts ([NCES](https://nces.ed.gov/ccd/))
- 🎯 **MeetingBank (HuggingFace)** - 1,366 city council meetings with transcripts & summaries ([huggingface.co/datasets/huuuyeah/meetingbank](https://huggingface.co/datasets/huuuyeah/meetingbank))
- 📚 **LocalView (Harvard)** - 1,000+ municipalities with meeting videos & transcripts ([Harvard Dataverse](https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/NJTBEM))
- 🏛️ **Council Data Project** - 20+ cities with full pipelines, transcripts, voting records ([councildataproject.org](https://councildataproject.org))

**Discovery Methods:**
- ✅ **GSA Domain Matching**: Direct lookup in CISA registry (confidence: 0.95-1.0)
- ✅ **Pattern Generation**: Test common government URL patterns (confidence: 0.6-0.9)
- ✅ **Web Crawling**: Verify URLs and discover minutes pages
- ✅ **Non-.gov Coverage**: Includes .org, .net, .us domains

**Benefits:**
- 🆓 **Zero API costs** (no search API fees)
- 🔒 **Authoritative sources** (official government registries)
- ♻️ **Sustainable** (vendor-neutral, future-proof)
- 📊 **High accuracy** (70-95% discovery rate)

**Pipeline Architecture:**
```
Bronze (Raw Data) → Silver (URL Discovery) → Gold (Scraping Targets)
```

**Deployment Options:**
1. **Local CLI** - Quick testing (`python main.py discover-jurisdictions --limit 100`)
2. **Databricks Notebook** - Production batch processing
3. **Scheduled Jobs** - Monthly re-discovery

See [DATA_SOURCES.md](docs/DATA_SOURCES.md) for complete source documentation and [JURISDICTION_DISCOVERY_DEPLOYMENT.md](docs/JURISDICTION_DISCOVERY_DEPLOYMENT.md) for deployment guide.

### Meeting Minutes & Transcript Sources

The system collects meeting data from multiple sources:

**Pre-Existing Datasets (Download & Use):**
- 📚 **MeetingBank** - 1,366 meetings from 6 major cities with full transcripts, human-written summaries, **YouTube/Vimeo video URLs**, and academic benchmark quality ([HuggingFace](https://huggingface.co/datasets/huuuyeah/meetingbank))
  - ✅ **NOW EXTRACTS VIDEO URLs**: YouTube IDs, Vimeo links, Archive.org videos from urls dictionary
- 🎓 **LocalView** - 1,000+ municipalities with meeting videos, automated transcripts, continuous collection ([Harvard Dataverse](https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/NJTBEM))
- 🏛️ **Council Data Project** - 20+ cities with full data pipelines: transcripts, videos, voting records, legislation tracking ([councildataproject.org](https://councildataproject.org))
- 📹 **City Scrapers** - 100-500 validated agency URLs with video links from 5 cities (Chicago, Pittsburgh, Detroit, Cleveland, LA) ([cityscrapers.org](https://cityscrapers.org))
  - ✅ **NEW INTEGRATION**: Extracts start_urls from GitHub spider files, includes Granicus video pages with YouTube embeds
- 🏛️ **Open States** - 50+ state legislature YouTube channels, expanding to local jurisdictions ([openstates.org](https://openstates.org))
  - ✅ **NEW INTEGRATION**: API integration extracts YouTube/Vimeo sources from jurisdiction metadata

**Public Website Scrapers (Free Access):**
- **Legistar** (FREE public data): Meeting management platform used by ~1,000-3,000 cities. All meeting data is publicly accessible (e.g., chicago.legistar.com)
- **Granicus** (FREE public data): Government meeting platform (ViewPublisher, MetaViewer). Public meetings are freely accessible
- **CivicPlus** (FREE public data): Municipal website platform with public meeting sections
- **Municode** (FREE public data): Municipal code and meeting platform with public access
- **Generic Municipal Websites** (FREE public data): Custom scrapers for .gov sites
- **PDF Documents** (FREE public data): Extract text from publicly posted meeting minutes

⚠️ **Important**: All these are FREE public data sources. Municipalities pay for these platforms, but the meeting data is publicly accessible by law. We don't pay for any data access.

**Strategy**: Download existing datasets first (2,000-10,000 URLs from MeetingBank/LocalView/CDP), then scrape public platforms to fill gaps. Total cost: $0.

**📊 NEW: All Three Video URL Sources Now Integrated!**
- ✅ MeetingBank: 1,366 meetings with YouTube/Vimeo URLs extracted
- ✅ City Scrapers: 100-500 agency URLs from GitHub repos
- ✅ Open States: 50+ legislative video channels via API

**To run the integrations:**
```bash
cd /home/developer/projects/oral-health-policy-pulse
source venv/bin/activate

# Install dependencies
pip install datasets requests

# Run each integration
python discovery/meetingbank_ingestion.py
python discovery/city_scrapers_urls.py
python discovery/openstates_sources.py  # Optional: add OPENSTATES_API_KEY to .env first
```

See [`docs/INTEGRATION_STATUS.md`](docs/INTEGRATION_STATUS.md) for complete integration details, [`docs/URL_DATASETS_CONFIRMED.md`](docs/URL_DATASETS_CONFIRMED.md) for URL analysis, [`docs/HUGGINGFACE_DATASETS_ANALYSIS.md`](docs/HUGGINGFACE_DATASETS_ANALYSIS.md) for HuggingFace datasets, and [`docs/VIDEO_URL_SOURCES.md`](docs/VIDEO_URL_SOURCES.md) for video URL integration guide.

### Financial Documents & Budget Sources

The system analyzes **government and nonprofit financial documents** to correlate rhetoric (meeting minutes) with reality (actual spending):

**Government Budget Documents (Free Public Data):**
- 💰 **City & County Budgets** - Annual budgets, mid-year amendments, departmental allocations
- 📊 **School District Financials** - K-12 budgets, per-pupil spending, categorical funding
- 🏥 **Health Department Budgets** - Public health spending, program-specific allocations
- 📈 **Budget Amendments** - Real-time changes that reveal shifting priorities
- 📉 **Expenditure Reports** - Actual spending vs. budgeted amounts

**Nonprofit Financial Documents (Free Public Data):**
- 📋 **IRS Form 990** - Complete financial picture (revenue, expenses, assets, executive compensation, program service accomplishments)
- 💼 **Annual Reports** - Mission statements, program descriptions, financial summaries
- 📊 **Audited Financial Statements** - When publicly available
- 🎯 **Grant Reports** - Foundations often require public reporting
- 📈 **Program Budgets** - Allocation across different service areas

**Key Data Sources:**
- 🏛️ **Municipal Finance Officer Association (GFOA)** - Standardized budget formats from 17,000+ governments
- 🎓 **NCES Common Core of Data (CCD)** - School district financial data for all 13,000+ U.S. districts ([NCES Data](https://nces.ed.gov/ccd/))
- 📚 **U.S. Census Annual Survey of State & Local Government Finances** - Comprehensive revenue/expenditure data ([Census Finance Data](https://www.census.gov/programs-surveys/gov-finances.html))
- 🏙️ **Comprehensive Annual Financial Reports (CAFRs)** - Detailed municipal financial statements (publicly posted on .gov sites)
- 📄 **OpenGov Platforms** - Many cities use OpenGov, OpenBudget, or similar transparency portals
- 💰 **ProPublica Nonprofit Explorer** - 3M+ Form 990 filings with 10+ years of history
- 🏛️ **IRS TEOS** - Official source for all nonprofit financial data
- 🌟 **GuideStar/Candid** - Enhanced nonprofit profiles (some data requires subscription, but core 990s are free)

**Budget-to-Minutes Analysis Framework:**

The system implements **political economy forensics** by correlating discussion with funding for both **government agencies and nonprofit organizations**:

```
Meeting Rhetoric          Budget Reality          Analysis
──────────────────────────────────────────────────────────────
"Critical priority"   →   +5% increase      =   ✅ Aligned
"Essential program"   →   Flat funding       =   ⚠️ Lip Service  
Rarely discussed      →   +25% increase     =   🔍 Hidden Priority
Heavy debate          →   -15% cut          =   ❌ Performative Talk
```

**What It Reveals:**
- 🎭 **Performative Politics/Messaging**: Programs praised in meetings but defunded in budgets (government) or Form 990s showing minimal spending on stated mission (nonprofits)
- 🔦 **Hidden Priorities**: Quiet budget increases for politically sensitive items or nonprofit executive compensation growing while program spending stagnates
- 💡 **Advocacy Opportunities**: Gaps between stated values and actual resource allocation in both sectors
- 📊 **Opportunity Costs**: "We funded X instead of Y" comparisons for advocacy messaging

**Example Use Cases:**

*Government Accountability:*
```
City Council: "School dental programs are a top priority"
Budget Reality: Dental program funding decreased 20%
Alternative Spending: New city hall landscaping increased 150%

→ Advocacy Message: "City spent $200K on landscaping while cutting 
   children's dental screenings. 800 kids now without care."
```

*Nonprofit Accountability:*
```
Nonprofit Board Minutes: "Expanding access to underserved communities is our core mission"
Form 990 Reality: Only 12% of budget spent on direct services, 45% on administration
Board Discussions: Zero mentions of service expansion in past 6 months

→ Donor Alert: "Organization claims to prioritize underserved communities 
   but allocates <15% to programs. Board hasn't discussed service expansion 
   in 6+ months despite $2M annual revenue."
```

**Implementation:**
See [`extraction/budget_analyzer.py`](extraction/budget_analyzer.py) for budget extraction logic and [`docs/ACCOUNTABILITY_DASHBOARD_STRATEGY.md`](docs/ACCOUNTABILITY_DASHBOARD_STRATEGY.md) for analysis methodology.

⚠️ **All Public Data**: 
- **Government**: Budget documents are legally required to be publicly accessible. The system scrapes PDF budgets from .gov websites and standardizes them for analysis.
- **Nonprofits**: IRS Form 990 filings are public records. Tax-exempt organizations must make their 990s available upon request, and they're freely accessible via ProPublica and IRS databases.
- **Total Cost**: $0 - All data sources are free and publicly available.

## Policy Topics Monitored

- 💧 **Water Fluoridation**: Community water fluoridation initiatives
- 🏫 **School Dental Screening**: School-based dental health programs
- 🏥 **Medicaid Dental**: Medicaid dental coverage expansion
- 🏢 **Dental Clinic Funding**: Community dental clinic funding
- 👨‍👩‍👧‍👦 **Community Dental Programs**: Outreach and education programs
- 👶 **Children's Dental Health**: Pediatric oral health initiatives

## Advocacy Heatmap

The system generates an interactive map showing:

- **Geographic Distribution**: Where policies are being discussed
- **Urgency Levels**: Color-coded by action urgency (critical, high, medium, low)
- **Topic Concentration**: What topics are dominant in each region
- **Timeline View**: When opportunities are emerging
- **Clickable Details**: Full context for each opportunity

### Urgency Levels

- 🔴 **Critical**: Vote imminent, immediate action required
- 🟠 **High**: Active debate, high engagement needed
- 🟡 **Medium**: Moderate discussion, monitoring recommended
- 🟢 **Low**: Early stage, awareness building

## Generated Advocacy Materials

For each identified opportunity, the system generates:

1. **Personalized Emails**
   - Subject line optimized for the situation
   - Context-aware body with key arguments
   - Call to action based on urgency

2. **Talking Points**
   - Bullet-point format for meetings
   - Evidence-based arguments
   - Local context integration

3. **Social Media Content**
   - Platform-specific formats (Twitter, Facebook, Instagram)
   - Hashtag recommendations
   - Shareable graphics (future)

4. **Policy Briefs**
   - Summary of the issue
   - Key benefits and evidence
   - Recommendations for action

## Delta Lake Schema

### Tables

- `raw_documents`: Scraped meeting minutes
- `parsed_documents`: Structured document data
- `classified_documents`: Topic classifications
- `sentiment_analysis`: Stance and debate intensity
- `advocacy_opportunities`: Identified opportunities
- `advocacy_materials`: Generated content

All tables use Delta Lake format with:
- Partitioning for performance
- Change data feed for auditing
- Auto-optimization enabled

## Testing

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_agents.py

# Run with coverage
pytest --cov=agents --cov=pipeline --cov=visualization
```

## Examples

See the `examples/` directory for:

- `example_workflow.py`: Complete end-to-end workflow
- `notebooks/example_analysis.py`: Databricks notebook example

## Project Structure

```
oral-health-policy-pulse/
├── agents/                 # Multi-agent system components
│   ├── base.py            # Base agent class
│   ├── orchestrator.py    # Workflow orchestration
│   ├── scraper.py         # Web scraping agent
│   ├── parser.py          # Document parsing agent
│   ├── classifier.py      # Topic classification agent
│   ├── sentiment.py       # Sentiment analysis agent
│   └── advocacy.py        # Advocacy generation agent
├── api/                   # FastAPI application
│   ├── app.py            # Main application (Databricks Apps)
│   └── main.py           # API endpoints (Standalone mode)
├── frontend/             # Open Navigator (React + Vite + TypeScript)
│   ├── src/
│   │   ├── pages/        # Analytics, Heatmap, Nonprofits, etc.
│   │   └── components/   # Shared UI components
│   └── package.json
├── website/              # Docusaurus Documentation Site ⭐ NEW
│   ├── docs/            # Documentation markdown files
│   ├── blog/            # Blog posts
│   ├── src/
│   │   └── pages/       # Custom pages (home, dashboard redirect)
│   ├── docusaurus.config.ts
│   └── package.json
├── discovery/            # Data discovery modules
│   ├── census_ingestion.py
│   ├── nces_ingestion.py
│   ├── nonprofit_discovery.py
│   └── ...
├── extraction/           # Document extraction
│   ├── budget_analyzer.py
│   ├── summarizer.py
│   └── ...
├── pipeline/             # Data pipeline components
│   └── delta_lake.py    # Delta Lake integration
├── visualization/        # Visualization components
│   └── heatmap.py       # Heatmap generation
├── config/               # Configuration
│   └── settings.py      # Application settings
├── docs/                # Markdown documentation (legacy)
├── tests/                # Test suite
├── examples/             # Example scripts
├── notebooks/            # Analysis notebooks
├── main.py              # CLI entry point
├── requirements.txt     # Python dependencies
├── Dockerfile          # Container definition
└── docker-compose.yml  # Multi-container setup
```

### Key Directories

- **`website/`** - Docusaurus documentation site with comprehensive guides
- **`frontend/`** - Open Navigator for interactive data exploration
- **`api/`** - FastAPI backend serving both the application and public API
- **`discovery/`** - Data ingestion modules for Census, NCES, nonprofits, etc.
- **`agents/`** - AI agents for scraping, parsing, classification, and advocacy
- **`docs/`** - Legacy markdown documentation (being migrated to `website/docs/`)

---

## 🔌 Open-Source Integrations

This project leverages proven patterns from **11 civic tech projects** to build a production-grade system:

### Core Scraping & Data Projects

| Project | Integration | Status |
|---------|-------------|--------|
| [**Civic Scraper**](https://github.com/biglocalnews/civic-scraper) | Platform detection, document downloading | ✅ Patterns integrated (no URL list) |
| [**City Scrapers**](https://github.com/city-scrapers/city-scrapers) | Event schema, URL extraction | ✅ **URLs integrated** (100-500 agencies) |
| [**Council Data Project**](https://github.com/CouncilDataProject/cookiecutter-cdp-deployment) | Ingestion pipeline, transcript processing | ⏳ 20 cities identified, URLs pending |
| [**Engagic**](https://github.com/Engagic/engagic) | Matter tracking, LLM parsing | ✅ Model created (research project) |
| [**Councilmatic**](https://github.com/datamade/councilmatic-starter-template) | Person/vote tracking, search UX | 📋 6 deployments, could extract URLs |

### End-to-End Platforms & Scale Projects

| Project | Integration | Status |
|---------|-------------|--------|
| [**OpenTowns**](https://opentowns.org) | AI summarization, keyword alerts | ✅ **Implemented** |
| [**LocalView**](https://www.localview.net) | Scale patterns, quality metrics | ✅ **Implemented** |
| [**MeetingBank**](https://meetingbank.github.io) | Summarization benchmarks | ✅ **Implemented** |
| [**CivicBand**](https://civic.band) | Multi-jurisdiction search | 📋 Architecture designed |
| [**OpenCouncil**](https://github.com/schemalabz/opencouncil) | International adaptability | 📋 Patterns documented |

### What We've Built

#### 1. Platform Detection (`discovery/platform_detector.py`)
Automatically identifies which CMS/platform a municipality uses:
```python
from discovery.platform_detector import detect_platform

platform = detect_platform("https://chicago.legistar.com/Calendar.aspx")
# Returns: "legistar"
```

Detects public meeting platforms: Legistar, Granicus, CivicPlus, Municode (all FREE public data sources).

#### 2. Standardized Event Model (`models/meeting_event.py`)
City Scrapers-compatible meeting representation:
```python
from models.meeting_event import MeetingEvent, Classification

event = MeetingEvent(
    title="City Council Meeting",
    classification=Classification.COUNCIL,
    start=datetime(2026, 4, 21, 18, 0),
    jurisdiction_name="Birmingham",
    state_code="AL"
)

# Extended with oral health tracking
event.oral_health_relevant = True
event.keywords_found = ["fluoridation", "dental"]
event.confidence_score = 0.85
```

#### 3. Matter Tracking (`models/meeting_event.py`)
Track legislative items across multiple meetings:
```python
from models.meeting_event import Matter

matter = Matter(
    matter_id="BHM-2024-FL001",
    title="Community Water Fluoridation Ordinance",
    type="Ordinance",
    status="Committee Review",
    is_health_policy=True
)
```

#### 4. AI Summarization (`extraction/summarizer.py`) 🆕
OpenTowns-style human-readable summaries:
```python
from extraction.summarizer import MeetingSummarizer

summarizer = MeetingSummarizer()
summary = summarizer.summarize(event, full_transcript)

print(summary.executive_summary)
# "The council voted 7-2 to schedule a public hearing on community
#  water fluoridation for April 10th..."

print(summary.health_policy_items)
# ["Water fluoridation program approved for public hearing",
#  "Budget allocation of $120,000 annually discussed"]
```

#### 5. Keyword Alerts (`alerts/keyword_monitor.py`) 🆕
Real-time monitoring for oral health keywords:
```python
from alerts.keyword_monitor import KeywordAlertSystem

alert_system = KeywordAlertSystem()
alerts = alert_system.scan_meeting(event, full_text)

for alert in alerts:
    print(f"🔔 {alert.priority.value.upper()}: {alert.meeting_title}")
    print(f"   Keywords: {', '.join(alert.keywords_found)}")
    print(f"   Categories: {', '.join(alert.categories_matched)}")
```

Features:
- **6 keyword categories**: fluoridation, dental access, water systems, public health, health policy, children's health
- **Priority levels**: Critical, High, Medium, Low
- **Context extraction**: Relevant snippets around keywords
- **Email generation**: HTML alert emails ready to send

#### 6. Batch Processing & Quality Metrics (`discovery/batch_processor.py`) 🆕
LocalView-style scale handling for 1,000+ jurisdictions:
```python
from discovery.batch_processor import BatchProcessor

processor = BatchProcessor(batch_size=100)

# Process all jurisdictions in batches
for batch_result in processor.process_all_jurisdictions():
    print(f"Batch {batch_result.batch_number}: "
          f"{batch_result.success_rate:.1f}% success")
    print(f"  Meetings found: {batch_result.meetings_found}")
```

Quality tracking per jurisdiction:
- **Completeness score**: Meeting discovery rate, agenda/minutes coverage
- **Reliability score**: Success rate over time
- **Freshness score**: How recently scraped
- **Health status**: Healthy, degraded, failed
- **Automatic retry**: Exponential backoff for failed jurisdictions

### Documentation

- **Core Integration Guide**: [`docs/INTEGRATION_GUIDE.md`](docs/INTEGRATION_GUIDE.md) - First 5 projects (Civic Scraper, City Scrapers, CDP, Engagic, Councilmatic)
- **Scale & Search Patterns**: [`docs/SCALE_AND_SEARCH_PATTERNS.md`](docs/SCALE_AND_SEARCH_PATTERNS.md) 🆕 - Next 6 projects (OpenTowns, LocalView, MeetingBank, CivicBand, OpenCouncil)

### Attribution

We're grateful to these open-source projects and their communities:

**Core Projects**:
- **Civic Scraper** (Apache 2.0) - Big Local News / Stanford Journalism
- **City Scrapers** (MIT) - City Bureau / Pat Sier
- **Council Data Project** (MIT) - Eva Maxfield Brown, Isaac Na, et al.
- **Engagic** - Check repository for license
- **Councilmatic** (MIT) - DataMade

**Scale & End-to-End Projects**:
- **OpenTowns** - Open civic tech project
- **LocalView** - Harvard Mellon Urbanism Initiative
- **MeetingBank** - Open dataset for summarization research
- **CivicBand** - Raft Foundation
- **OpenCouncil** (MIT) - Schemalab

---

## Related Organizations & Projects

### Government Accountability & Transparency

**[GroundVue](https://www.groundvue.org/)** - Nonprofit organization dedicated to government accountability through data transparency and civic engagement. GroundVue provides tools and resources for citizens to monitor government activities, track spending, and hold elected officials accountable. Their work parallels this project's mission of using data to empower advocacy and community engagement.

**Shared Goals:**
- 📊 Making government data accessible and actionable
- 🔍 Tracking the gap between political rhetoric and actual policy outcomes
- 💡 Empowering citizens with tools for accountability
- 🏛️ Promoting transparency in government decision-making

This project complements GroundVue's work by focusing specifically on oral health policy opportunities while applying similar principles of data-driven accountability.

---

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Acknowledgments

- Built for advocacy groups working to improve community oral health
- Inspired by the need to identify legislative opportunities early
- Powered by modern AI/ML techniques and distributed data processing

## Contact

For questions or support:
- GitHub Issues: [github.com/getcommunityone/oral-health-policy-pulse/issues](https://github.com/getcommunityone/oral-health-policy-pulse/issues)
- Email: support@communityone.com

---

**Note**: This system is designed to support advocacy efforts and provide information. All generated content should be reviewed by humans before use. The accuracy of scraped data depends on source availability and format consistency.
