---
sidebar_position: 1
---

# Introduction

Welcome to **Open Navigator for Engagement** - an AI-powered platform that analyzes municipal meeting minutes and financial documents to identify policy opportunities for advocacy.

## What It Does

Open Navigator for Engagement combines data from multiple sources to:

- 📄 **Analyze Meeting Minutes** - Automatically scrapes and processes meetings from 90,000+ government jurisdictions
- 💰 **Track Financial Documents** - Correlates budget data with meeting rhetoric to reveal true priorities
- 🏛️ **Monitor Nonprofits** - Integrates IRS Form 990 data for 3M+ organizations
- 🗺️ **Visualize Opportunities** - Creates interactive heatmaps of policy opportunities
- 📧 **Generate Materials** - Auto-creates advocacy emails, talking points, and policy briefs

## Key Features

### Multi-Agent AI System

Coordinated agents handle the entire pipeline:
- **Scraper Agent** - Discovers and downloads meeting documents
- **Parser Agent** - Extracts structured data from PDFs and HTML
- **Classifier Agent** - Identifies relevant policy topics
- **Sentiment Analyzer** - Assesses stance and urgency
- **Advocacy Writer** - Generates actionable materials

### Budget-to-Minutes Analysis

The platform implements "political economy forensics" by comparing what organizations say in meetings with what they actually fund:

```
Meeting Rhetoric          Budget Reality          Analysis
────────────────────────────────────────────────────────
"Critical priority"   →   +5% increase      =   ✅ Aligned
"Essential program"   →   Flat funding       =   ⚠️ Lip Service  
Rarely discussed      →   +25% increase     =   🔍 Hidden Priority
Heavy debate          →   -15% cut          =   ❌ Performative Talk
```

### Comprehensive Data Sources

All data sources are **100% free and public**:

**Government Data:**
- **Census Bureau** - 90,000+ government jurisdictions
- **NCES** - 13,000+ school districts with contact info
- **CISA** - 15,000+ official .gov domains

**Nonprofit Data:**
- **ProPublica Nonprofit Explorer** - 3M+ IRS Form 990 filings
- **Reference Sites:** Charity Navigator, Candid/GuideStar, GiveWell (see [Nonprofit Data Sources](/docs/data-sources/nonprofit-sources))

**Research Collections:**
- **Harvard Dataverse** - Academic research datasets
- **MeetingBank, LocalView, City Scrapers** - Pre-built meeting collections

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+ (for React frontend)
- Databricks workspace (optional, for production)
- OpenAI API key (for AI capabilities)

### Installation

```bash
# Clone the repository
git clone https://github.com/getcommunityone/oral-health-policy-pulse.git
cd oral-health-policy-pulse

# Run installation script
chmod +x install.sh
./install.sh

# Activate virtual environment
source .venv/bin/activate

# Configure API keys
cp .env.example .env
# Edit .env with your API keys

# Start the API server
python main.py serve
```

Visit `http://localhost:8000` for the API and `http://localhost:8000/docs` for interactive API documentation.

### Using the Dashboard

```bash
# In a separate terminal
cd frontend
npm install
npm run dev

# Open http://localhost:3000
```

## Next Steps

<div class="alert alert--info">
  <strong>📚 Explore the Documentation</strong>
  <ul>
    <li><a href="/docs/data-sources">Data Sources</a> - Learn about all integrated datasets</li>
    <li><a href="/docs/guides/jurisdiction-discovery">Jurisdiction Discovery</a> - Discover government websites</li>
    <li><a href="/docs/guides/nonprofit-data">Nonprofit Data</a> - Work with nonprofit financials</li>
    <li><a href="/docs/api">API Reference</a> - Full API documentation</li>
  </ul>
</div>

## Architecture

The platform uses a medallion architecture on Delta Lake:

- **Bronze Layer** - Raw scraped data
- **Silver Layer** - Cleaned and standardized
- **Gold Layer** - Enriched with analysis and classifications

All processing is scalable via Databricks for production workloads.

## Use Cases

### Government Accountability

Track whether elected officials follow through on stated priorities:

```
City Council: "School dental programs are a top priority"
Budget Reality: Dental program funding decreased 20%

→ Advocacy Message: "City cut dental screenings by 20% 
   despite calling it a priority. 800 kids now without care."
```

### Nonprofit Accountability

Verify that nonprofits allocate resources according to their mission:

```
Board Minutes: "Expanding access to underserved communities"
Form 990: Only 12% of budget on direct services

→ Donor Alert: "Organization claims to prioritize underserved 
   but allocates \<15% to programs."
```

### Community Mobilization

Find existing solutions when government claims something is impossible:

```
Official: "We can't do dental screenings - legal risk"
Reality: 3 local nonprofits already providing screenings

→ Response: "Here are 3 organizations already doing it 
   successfully. Can we support their expansion?"
```

## Support

- **GitHub Issues**: [Report bugs or request features](https://github.com/getcommunityone/oral-health-policy-pulse/issues)
- **Documentation**: Browse the docs sidebar
- **Dashboard**: Access the interactive dashboard

---

**Ready to get started?** Check out the [Data Sources](/docs/data-sources) page to learn about available datasets, or jump into the [Jurisdiction Discovery Guide](/docs/guides/jurisdiction-discovery) to start finding government websites.
