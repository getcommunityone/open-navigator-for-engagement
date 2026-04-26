---
sidebar_position: 1
displayed_sidebar: gettingStartedSidebar
---

# Introduction

Welcome to **Open Navigator for Engagement** - an AI-powered platform that analyzes municipal meeting minutes and financial documents to identify policy opportunities for advocacy.

## 👋 Choose Your Path

This documentation is organized by audience. Click the section that best describes you:

<div style={{display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '20px', margin: '30px 0'}}>

<div style={{border: '2px solid #4CAF50', borderRadius: '8px', padding: '20px', background: '#f1f8f4'}}>
  <h3>📊 Policy Makers & Advocates</h3>
  <p><strong>I want to:</strong></p>
  <ul>
    <li>Hold governments accountable</li>
    <li>Analyze meeting minutes and budgets</li>
    <li>Track nonprofit spending</li>
    <li>Find advocacy opportunities</li>
  </ul>
  <p><strong><a href="/docs/for-advocates">→ Go to Advocacy Documentation</a></strong></p>
</div>

<div style={{border: '2px solid #2196F3', borderRadius: '8px', padding: '20px', background: '#e3f2fd'}}>
  <h3>🛠️ Developers & Technical Users</h3>
  <p><strong>I want to:</strong></p>
  <ul>
    <li>Install and configure the platform</li>
    <li>Scrape meeting data</li>
    <li>Deploy to production</li>
    <li>Contribute to development</li>
  </ul>
  <p><strong><a href="/docs/for-developers">→ Go to Developer Documentation</a></strong></p>
</div>

</div>

---

## Platform Scale

Open Navigator provides access to comprehensive data across the United States:

<div style={{display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '20px', margin: '30px 0', textAlign: 'center'}}>

<div style={{padding: '20px', background: '#f5f5f5', borderRadius: '8px'}}>
  <div style={{fontSize: '2.5em', fontWeight: 'bold', color: '#2196F3'}}>90,000+</div>
  <div style={{marginTop: '10px', color: '#666'}}>Government Jurisdictions</div>
</div>

<div style={{padding: '20px', background: '#f5f5f5', borderRadius: '8px'}}>
  <div style={{fontSize: '2.5em', fontWeight: 'bold', color: '#4CAF50'}}>3,000,000+</div>
  <div style={{marginTop: '10px', color: '#666'}}>Nonprofit Organizations</div>
</div>

<div style={{padding: '20px', background: '#f5f5f5', borderRadius: '8px'}}>
  <div style={{fontSize: '2.5em', fontWeight: 'bold', color: '#FF9800'}}>3,144</div>
  <div style={{marginTop: '10px', color: '#666'}}>U.S. Counties</div>
</div>

<div style={{padding: '20px', background: '#f5f5f5', borderRadius: '8px'}}>
  <div style={{fontSize: '2.5em', fontWeight: 'bold', color: '#9C27B0'}}>19,500+</div>
  <div style={{marginTop: '10px', color: '#666'}}>Cities & Municipalities</div>
</div>

<div style={{padding: '20px', background: '#f5f5f5', borderRadius: '8px'}}>
  <div style={{fontSize: '2.5em', fontWeight: 'bold', color: '#F44336'}}>13,000+</div>
  <div style={{marginTop: '10px', color: '#666'}}>School Districts</div>
</div>

<div style={{padding: '20px', background: '#f5f5f5', borderRadius: '8px'}}>
  <div style={{fontSize: '2.5em', fontWeight: 'bold', color: '#00BCD4'}}>50</div>
  <div style={{marginTop: '10px', color: '#666'}}>States (All U.S. States)</div>
</div>

</div>

### Data Sources At Scale

- **📄 Meeting Minutes**: 1,000+ municipalities with full transcripts and videos
- **📺 Video Channels**: 50+ state legislature YouTube channels
- **💰 Financial Data**: Complete budget and Form 990 coverage
- **🗺️ Geographic Coverage**: All 50 states, 3,000+ counties and cities

All data is **100% free and public** - no subscriptions or API fees required.

---

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

### Automated Scraping & Discovery

The platform automatically discovers and scrapes government websites at scale:

**Discovery Methods:**
- **Pattern Matching** - Tests common government URL patterns (city-name.gov, cityof*.org)
- **Census Integration** - Uses official government registries to find jurisdictions
- **CISA .gov Domains** - Validates against 15,000+ official government domains
- **Pre-Built Datasets** - Leverages MeetingBank, LocalView, City Scrapers URLs

**Scraping Platforms:**
- **Legistar** - 1,000-3,000 cities use this platform (confidence: high)
- **Granicus** - Government meeting management with video hosting
- **CivicPlus** - Municipal website platform
- **Municode** - Code and meeting platform
- **Custom .gov Sites** - Adaptable scrapers for any municipal website

**What Gets Scraped:**
- Meeting agendas and minutes (PDF, HTML, Word docs)
- Budget documents and financial reports
- Video recordings and transcripts
- Voting records and legislation text
- Board member information and contact details

See [Jurisdiction Discovery Guide](/docs/guides/jurisdiction-setup) to run discovery for your target area.

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

### Three Services

Open Navigator runs three separate services:

| Service | Port | Description |
|---------|------|-------------|
| **⚛️ Open Navigator** | 5173 | **MAIN APPLICATION** - Search, filters, heatmap, data exploration |
| **📚 Documentation** | 3000 | This Docusaurus site with guides and tutorials |
| **🔥 API Backend** | 8000 | FastAPI server with AI agents |

### Prerequisites

- Python 3.11+
- Node.js 18+ (for React frontend and documentation)
- Databricks workspace (optional, for production)
- OpenAI API key (for AI capabilities)

### Installation

**Automated Setup (Recommended):**

```bash
# Clone the repository
git clone https://github.com/getcommunityone/open-navigator-for-engagement.git
cd oral-health-policy-pulse

# Install all dependencies
./install.sh                          # Python backend
cd frontend && npm install && cd ..   # React app
cd website && npm install && cd ..    # Documentation

# Start all services
./start-all.sh

# Visit:
# 🚀 Main App: http://localhost:5173 (Open Navigator)
# 📚 Docs:     http://localhost:3000 (this site)
# 🔥 API:      http://localhost:8000/docs (FastAPI)
```

**Manual Setup:**

```bash
# Python backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Configure API keys
cp .env.example .env
# Edit .env with your OpenAI API key

# Start services (separate terminals)
python main.py serve                    # Terminal 1: API
cd frontend && npm run dev              # Terminal 2: Main App
cd website && npm start                 # Terminal 3: Docs
```

## Next Steps

### 🚀 Using Open Navigator

Once services are running, visit **http://localhost:5173** for the main application interface with:
- Search and filter meetings by location, topic, date
- Interactive heatmap of advocacy opportunities
- Data exploration and analysis tools
- Nonprofit organization lookup

### 📚 Learn More

Explore the documentation to understand the platform's capabilities:

- **[Architecture](/docs/architecture)** - System design and components
- **[Data Sources Overview](/docs/data-sources/overview)** - All integrated datasets
- **[Meeting Minutes Sources](/docs/data-sources/confirmed-datasets)** - MeetingBank, LocalView, City Scrapers
- **[Video Sources](/docs/data-sources/video-sources)** - YouTube channels and video platforms
- **[Jurisdiction Discovery](/docs/data-sources/jurisdiction-discovery)** - How we find 90,000+ government websites
- **[Nonprofit Data](/docs/data-sources/nonprofit-sources)** - Working with Form 990 data
- **[Budget-to-Minutes Analysis](/docs/guides/political-economy)** - Correlating rhetoric with spending
- **[Deployment Guide](/docs/deployment/databricks-apps)** - Production deployment options

### 🛠️ Common Tasks

**Run Jurisdiction Discovery:**
```bash
source .venv/bin/activate
python main.py discover-jurisdictions --state CA --limit 100
```

**Scrape Meeting Minutes:**
```bash
python main.py scrape-batch --source discovered --limit 50
```

**Ingest Reference Data:**
```bash
python -m discovery.census_ingestion
python -m discovery.nces_ingestion
python discovery/meetingbank_ingestion.py
```

See the **[Quick Reference](/docs/quick-reference)** for all available commands.

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

## Support & Community

- **GitHub Issues**: [Report bugs or request features](https://github.com/getcommunityone/open-navigator-for-engagement/issues)
- **Documentation**: Use the sidebar to explore all guides and references
- **Main Application**: Launch Open Navigator at http://localhost:5173
- **API Documentation**: Interactive API docs at http://localhost:8000/docs

## What You Can Build

Open Navigator provides the foundation for:
- **Advocacy Campaigns** - Target specific jurisdictions with data-backed arguments
- **Accountability Dashboards** - Track government and nonprofit spending vs. rhetoric
- **Policy Research** - Analyze meeting patterns across hundreds of jurisdictions
- **Community Mobilization** - Find existing solutions to share with decision-makers
- **Budget Analysis** - Reveal hidden priorities through spending patterns

---

**Ready to get started?** 

- 🚀 **Quick Start:** [Install and run](/docs/quickstart) the platform
- 📊 **Explore Data:** Learn about [all data sources](/docs/data-sources/overview)
- 🎓 **Case Study:** See a [real-world example](/docs/case-studies/tuscaloosa-complete) (Tuscaloosa, AL)
- 🏗️ **Architecture:** Understand the [system design](/docs/architecture)
