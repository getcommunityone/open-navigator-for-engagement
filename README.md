# 🦷 Oral Health Policy Pulse

> *A multi-agent system for analyzing local government oral health policy discussions and empowering advocacy*

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-009688.svg)](https://fastapi.tiangolo.com)

## Overview

The **Oral Health Policy Pulse** is a sophisticated multi-agent system designed to scrape and analyze thousands of municipal meeting minutes from across the country. It identifies where fluoridation, school dental screenings, or funding for low-income dental care is being debated or ignored, providing advocacy groups with a real-time "Advocacy Heatmap" and automated policy outreach drafts.

### Key Features

- 🤖 **Multi-Agent Architecture**: Coordinated agents for scraping, parsing, classification, sentiment analysis, and advocacy generation
- 🏛️ **Massive Scale**: Handles millions of meeting minutes using Delta Lake on Databricks
- 🗺️ **Advocacy Heatmap**: Visual representation of policy opportunities across the country
- 📧 **Automated Materials**: Generates personalized emails, talking points, and social media content
- 📊 **Real-Time Analytics**: Identifies windows of opportunity for policy change
- 🎯 **Topic-Focused**: Monitors water fluoridation, school dental programs, Medicaid dental, and more

## Architecture

### Deployment Options

**🏠 Standalone Mode**: Run agents locally with custom Python implementation

**☁️ Databricks Agent Bricks Mode**: Production-ready deployment with:
- MLflow-based agents with automatic tracing
- Unity Catalog governance and lineage
- Model Serving endpoints with auto-scaling
- Built-in evaluation framework
- Enterprise monitoring and observability

See [`databricks/README.md`](databricks/README.md) for Agent Bricks setup.

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
   └─────────┘  └─────────┘  └──────────┘  └──────────┘
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

# Scrape a single source
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

The system supports scraping from:

- **Legistar**: Widely used city council meeting management platform
- **Granicus**: Government meeting and agenda management
- **Generic Municipal Websites**: Custom scrapers for various formats
- **PDF Documents**: Extracts text from meeting minute PDFs

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
- Email: support@communityone.org

---

**Note**: This system is designed to support advocacy efforts and provide information. All generated content should be reviewed by humans before use. The accuracy of scraped data depends on source availability and format consistency.
