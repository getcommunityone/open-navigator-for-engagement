---
sidebar_position: 1
---

# Introduction

Welcome to **Open Navigator for Engagement** - an AI-powered platform that analyzes municipal meeting minutes and financial documents to identify policy opportunities for advocacy.

## What It Does

Open Navigator for Engagement combines data from multiple sources to provide comprehensive advocacy intelligence:

- 📄 **Scrape Meeting Minutes** - Automatically discovers and scrapes meetings from 90,000+ government websites
  - Supports Legistar, Granicus, CivicPlus, Municode platforms
  - Downloads PDFs and extracts text from public .gov sites
  - Processes 1,000+ municipalities from pre-built datasets (MeetingBank, LocalView, City Scrapers)
  
- 📺 **Analyze Video Content** - Extracts and processes meeting videos
  - YouTube channels (50+ state legislatures, expanding to local)
  - Granicus video pages with embedded streams
  - Vimeo and Archive.org historical recordings
  - Direct video URLs from research datasets

- 💰 **Track Financial Documents** - Correlates budget data with meeting rhetoric to reveal true priorities
  - Municipal budgets, school district financials, health department spending
  - IRS Form 990s for 3M+ nonprofits (ProPublica API)
  - Budget-to-Minutes analysis reveals gaps between talk and funding

- 🏛️ **Monitor Nonprofits** - Integrates nonprofit financial and operational data
  - Form 990 analysis (revenue, expenses, executive compensation)
  - Board meeting minutes when publicly available
  - Service verification and mission alignment checks

- 🗺️ **Visualize Opportunities** - Creates interactive heatmaps of policy opportunities
  - Geographic distribution of advocacy targets
  - Urgency levels (critical, high, medium, low)
  - Timeline views for action windows

- 📧 **Generate Materials** - Auto-creates advocacy content
  - Personalized emails with local context
  - Talking points backed by evidence
  - Social media content and policy briefs

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

All data sources are **100% free and public**. The platform combines **reference datasets**, **pre-built collections**, and **automated scraping** to analyze meetings and financials across the country.

#### 📄 Meeting Minutes & Transcript Sources

**Pre-Built Datasets (Download & Use):**
- 📚 **[MeetingBank](https://huggingface.co/datasets/huuuyeah/meetingbank)** - 1,366 meetings from 6 major cities
  - Full transcripts with human-written summaries
  - YouTube/Vimeo video URLs extracted
  - Academic-quality benchmark dataset
- 🎓 **[LocalView (Harvard)](https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/NJTBEM)** - 1,000+ municipalities
  - Meeting videos and automated transcripts
  - Continuous data collection
- 🏛️ **[Council Data Project](https://councildataproject.org)** - 20+ cities
  - Complete pipelines: transcripts, videos, voting records
  - Legislation tracking
- 📹 **[City Scrapers](https://cityscrapers.org)** - 100-500 validated agency URLs
  - Curated from 5 cities (Chicago, Pittsburgh, Detroit, Cleveland, LA)
  - Includes Granicus video pages with YouTube embeds
- 🏛️ **[Open States](https://openstates.org)** - 50+ state legislature channels
  - YouTube/Vimeo sources via API
  - Expanding to local jurisdictions

**Public Website Scrapers (Automated Collection):**
- **Legistar** - Meeting management platform used by 1,000-3,000 cities (e.g., chicago.legistar.com)
- **Granicus** - Government meeting platform (ViewPublisher, MetaViewer)
- **CivicPlus** - Municipal website platform with public meeting sections
- **Municode** - Municipal code and meeting platform
- **Generic .gov Sites** - Custom scrapers for municipal websites
- **PDF Documents** - Extract text from publicly posted meeting minutes

> **⚠️ Important:** All meeting data is **free public data**. Municipalities pay for these platforms, but the data is publicly accessible by law. We don't pay for data access.

#### 📺 Video Sources (YouTube & Meeting Videos)

- **YouTube Channels** - 50+ state legislature channels, expanding to local governments
- **Granicus Video Pages** - Meeting videos embedded in government websites
- **Vimeo** - Alternative video hosting for government meetings
- **Archive.org** - Historical meeting recordings
- **Direct Video URLs** - Extracted from MeetingBank and LocalView datasets

See [Video Sources Documentation](/docs/data-sources/video-sources) for complete details.

#### 💰 Financial Documents & Budget Sources

**Government Finances:**
- **Municipal Budgets** - Annual budgets, amendments, departmental allocations
- **School District Financials** - K-12 budgets, per-pupil spending ([NCES Data](https://nces.ed.gov/ccd/))
- **Health Department Budgets** - Public health spending, program allocations
- **Census Annual Survey** - State & local government finances ([Census Finance Data](https://www.census.gov/programs-surveys/gov-finances.html))
- **CAFRs** - Comprehensive Annual Financial Reports from .gov sites
- **OpenGov Platforms** - City transparency portals

**Nonprofit Finances:**
- **[ProPublica Nonprofit Explorer](https://projects.propublica.org/nonprofits/)** - 3M+ IRS Form 990 filings
  - Revenue, expenses, assets, executive compensation
  - 10+ years of historical data
  - Free unlimited API access
- **IRS TEOS** - Official source for all nonprofit financial data
- **Annual Reports** - Mission statements, program descriptions
- **Audited Financial Statements** - When publicly available

See [Budget-to-Minutes Analysis](/docs/guides/political-economy) for how we correlate spending with rhetoric.

#### 📊 Reference Data & Jurisdiction Discovery

**Census Bureau:**
- **90,000+ government jurisdictions** - Counties, municipalities, townships
- **FIPS codes** - Standardized geographic identifiers
- **Population data** - Demographics and geographic coordinates
- **[Census Gazetteer 2024](https://www.census.gov/geographies/reference-files/time-series/geo/gazetteer-files.html)**

**NCES School Districts:**
- **13,000+ school districts** - Complete U.S. coverage
- **Contact information** - Addresses, phone numbers, websites
- **Enrollment data** - Student counts and demographics
- **[NCES Common Core of Data](https://nces.ed.gov/ccd/)**

**CISA .gov Domains:**
- **15,000+ validated .gov domains** - Official government websites
- **[cisagov/dotgov-data](https://github.com/cisagov/dotgov-data)** - Free GitHub dataset

See [Jurisdiction Discovery](/docs/data-sources/jurisdiction-discovery) for complete reference data documentation.

#### 🏛️ Nonprofit Data Sources

- **[ProPublica Nonprofit Explorer](https://projects.propublica.org/nonprofits/)** - Primary source (3M+ organizations)
- **IRS Tax Exempt Organization Search** - Official IRS database
- **Every.org Charity API** - Mission statements and visual assets
- **Findhelp.org** - 400,000+ community programs (services directory)
- **211 Directory** - Regional social services referrals

See [Nonprofit Data Sources](/docs/data-sources/nonprofit-sources) for detailed integration guides.

#### 🌐 Open Source & Civic Tech

- **GitHub** - Civic tech repositories and community tools
- **Code for America** - Civic technology projects
- **U.S. Digital Response** - Emergency response tools
- **Civic Tech Field Guide** - Curated project directory

See [Open Source Repositories](/docs/data-sources/open-source-repositories) for tracking civic tech projects.

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
