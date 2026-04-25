# 🦷 Open Navigator for Engagement

> *AI-powered advocacy opportunity finder with React + FastAPI web interface*

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![React](https://img.shields.io/badge/React-18.2-61DAFB.svg)](https://reactjs.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-009688.svg)](https://fastapi.tiangolo.com)
[![Databricks](https://img.shields.io/badge/Databricks-Apps-FF3621.svg)](https://www.databricks.com)

## Overview

The **Open Navigator for Engagement** is a full-stack AI application that analyzes thousands of municipal meeting minutes across the country to identify policy opportunities for oral health advocacy. It features a **modern React web interface**, **FastAPI backend**, and **multi-agent AI system** powered by Databricks.

**✨ New in v2.0:**
- 🎨 **React Frontend** - Modern, responsive UI with interactive visualizations
- 🚀 **Databricks Apps** - One-click deployment to Databricks workspace
- 📊 **Live Dashboard** - Real-time analytics and opportunity tracking
- 🗺️ **Interactive Heatmap** - Geographic visualization of advocacy opportunities
- 📧 **Automated Generation** - AI-powered advocacy emails and materials

### Key Features

- 🤖 **Multi-Agent Architecture**: Coordinated agents for scraping, parsing, classification, sentiment analysis, and advocacy generation
- 🔍 **Jurisdiction Discovery**: Automatically identifies 90,000+ local government websites using Census Bureau data
- 🏛️ **Massive Scale**: Handles millions of meeting minutes using Delta Lake on Databricks
- 🗺️ **Advocacy Heatmap**: Visual representation of policy opportunities across the country
- 📧 **Automated Materials**: Generates personalized emails, talking points, and social media content
- 📊 **Real-Time Analytics**: Identifies windows of opportunity for policy change
- 🎯 **Topic-Focused**: Monitors water fluoridation, school dental programs, Medicaid dental, and more

## 💰 Free Nonprofit Data Sources

Access comprehensive nonprofit data without expensive subscriptions. The platform integrates with **100% free** open data APIs to discover and track organizations already providing services that governments claim are "impossible."

### Why This Matters

When officials reject policy proposals with technical objections ("We can't do dental screenings - legal liability"), you can instantly show citizens the nonprofits **already doing it successfully**. This:

- **Bypasses technocratic vetoes** - Shows working alternatives exist
- **Creates accountability pressure** - Exposes inefficiency ("$5K legal review vs $25 screening")  
- **Mobilizes citizens** - Provides direct volunteer/donation pathways

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

### Implementation

See [`discovery/nonprofit_discovery.py`](discovery/nonprofit_discovery.py) for full implementation and [`discovery/README_NONPROFIT_DISCOVERY.md`](discovery/README_NONPROFIT_DISCOVERY.md) for detailed documentation.

Access via API:
```bash
GET /api/nonprofits?location=Tuscaloosa,AL&keyword=dental
```

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
│  │  • Policy documents & classifications           │   │
│  │  • Advocacy opportunities                       │   │
│  │  • Analytics & reporting                        │   │
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
Meeting Minutes → Scraping → Parsing → Classification → 
Sentiment Analysis → Advocacy Generation → Delta Lake Storage →
Heatmap Visualization
```

## Installation

### Prerequisites

- Python 3.11+
- Docker (optional, for containerized deployment)
- Databricks workspace (for production lakehouse)
- OpenAI API key (for LLM capabilities)

Note: `./install.sh` now attempts to install `tesseract-ocr` automatically (Linux via `apt-get`, macOS via `brew`) so OCR parsing works out of the box.

### Quick Start

**Option 1: Automated Installation (Recommended)**

```bash
# Clone the repository
git clone https://github.com/getcommunityone/oral-health-policy-pulse.git
cd oral-health-policy-pulse

# Run installation script
chmod +x install.sh
./install.sh

# Activate virtual environment
source venv/bin/activate

# Edit .env with your API keys
nano .env  # or vim .env

# Run the API server
python main.py serve
```

**Option 2: Using Makefile**

```bash
# Clone and navigate
git clone https://github.com/getcommunityone/oral-health-policy-pulse.git
cd oral-health-policy-pulse

# Install everything
make install

# Activate virtual environment
source venv/bin/activate

# Configure .env with your API keys
cp .env.example .env
nano .env

# Start the server
make run
```

**Option 3: Manual Installation**

```bash
# Clone the repository
git clone https://github.com/getcommunityone/oral-health-policy-pulse.git
cd oral-health-policy-pulse

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Run the API server
python main.py serve
```

Visit `http://localhost:8000` to access the API and `http://localhost:8000/docs` for interactive documentation.

> **Note:** Always activate the virtual environment before running commands:
> ```bash
> source venv/bin/activate
> ```

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
│   └── main.py           # API endpoints
├── pipeline/             # Data pipeline components
│   └── delta_lake.py     # Delta Lake integration
├── visualization/        # Visualization components
│   └── heatmap.py        # Heatmap generation
├── config/               # Configuration
│   └── settings.py       # Application settings
├── tests/                # Test suite
├── examples/             # Example scripts
├── notebooks/            # Analysis notebooks
├── main.py              # CLI entry point
├── requirements.txt     # Python dependencies
├── Dockerfile          # Container definition
└── docker-compose.yml  # Multi-container setup
```

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
