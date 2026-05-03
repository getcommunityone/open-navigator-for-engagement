# Data Integration Examples

> **📁 Note**: Demo scripts and documentation have been reorganized:
> - **Data source demos**: Moved to `scripts/datasources/[source]/`
> - **General demos**: Moved to `scripts/examples/`
> - This README provides an overview and links to the new locations.

This directory contains working examples and documentation for all major data integrations in the Open Navigator platform.

## 🎯 Available Integrations

### 1. Federal Grant Opportunities (Grants.gov)

**What it does**: Track federal grant opportunities and match them to eligible nonprofits

**Files**:
- `scripts/datasources/grants_gov/demo_grants_gov.py` - Working demo
- `scripts/datasources/grants_gov/GRANTS_GOV_VALUE.md` - Data comparison and value proposition

**Quick start**:
```bash
python scripts/datasources/grants_gov/demo_grants_gov.py
```

**Documentation**: [website/docs/integrations/grants-gov-api.md](../website/docs/integrations/grants-gov-api.md)

**Key value**: Alert nonprofits BEFORE deadlines instead of just showing who got funded AFTER

---

### 2. Political Contributions (FEC)

**What it does**: Track political donations by nonprofit leadership and analyze influence on grant awards

**Files**:
- `scripts/datasources/fec/demo_political_influence.py` - Working demo
- `scripts/datasources/fec/POLITICAL_INFLUENCE_INTEGRATION.md` - Complete analysis guide
- `scripts/datasources/fec/POLITICAL_FINANCE_QUICK_START.md` - Quick start guide

**Quick start**:
```bash
# Get free API key at: https://api.data.gov/signup/
python scripts/datasources/fec/demo_political_influence.py --api-key YOUR_KEY
```

**Documentation**: [website/docs/integrations/fec-political-contributions.md](../website/docs/integrations/fec-political-contributions.md)

**Key value**: Reveal political-financial connections with full transparency

---

### 3. Complete Data Ecosystem

All integrations work together:

```
┌────────────────────────────────────────────────────────┐
│            OPEN NAVIGATOR DATA ECOSYSTEM               │
├────────────────────────────────────────────────────────┤
│                                                        │
│  EXISTING DATA           NEW INTEGRATIONS              │
│  ──────────────          ────────────────              │
│                                                        │
│  IRS Form 990            Grants.gov API                │
│  • 3M+ nonprofits   ───> • Grant opportunities         │
│  • Officers              • Deadlines                   │
│  • Financials            • Eligibility                 │
│  • Past grants                │                        │
│                               │                        │
│  Jurisdictions                │      FEC API           │
│  • 90k+ cities      ──────────┴───> • Political $$$    │
│  • Meetings                         • Donor networks   │
│  • Contacts                         • Influence        │
│                                                        │
│  UNIQUE VALUE: Complete political-financial picture    │
│  • Who donated → Which campaigns → Grant awards        │
│  • Timeline analysis: Donation → Policy → Funding      │
│  • Transparency through data                           │
│                                                        │
└────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start (5 Minutes)

### Step 1: Get API Keys

**FEC API** (Required for political data):
```
Visit: https://api.data.gov/signup/
Enter email → Receive key instantly
```

**Grants.gov** (No key needed!):
```
Public API - just run the demos
```

### Step 2: Run Demos

```bash
# 1. Federal grant opportunities (no key needed)
python scripts/datasources/grants_gov/demo_grants_gov.py

# 2. Political contributions (requires FEC key)
python scripts/datasources/fec/demo_political_influence.py --api-key YOUR_FEC_KEY
```

### Step 3: Review Output

```bash
# Check generated data
ls -lh data/gold/grants/
ls -lh data/gold/fec/
ls -lh data/gold/states/MA/

# View results
python -c "
import pandas as pd
grants = pd.read_parquet('data/gold/grants/oral_health_opportunities.parquet')
print(f'Found {len(grants):,} federal grant opportunities')
print(grants[['opportunityTitle', 'agencyName', 'openDate']].head())
"
```

## 📚 Documentation Guide

### For Quick Reference

Start here:
1. **[scripts/datasources/fec/POLITICAL_FINANCE_QUICK_START.md](../scripts/datasources/fec/POLITICAL_FINANCE_QUICK_START.md)** - Overview and quick start
2. **[scripts/datasources/grants_gov/GRANTS_GOV_VALUE.md](../scripts/datasources/grants_gov/GRANTS_GOV_VALUE.md)** - What Grants.gov adds to your data

### For Complete Analysis

Deep dives:
1. **[scripts/datasources/fec/POLITICAL_INFLUENCE_INTEGRATION.md](../scripts/datasources/fec/POLITICAL_INFLUENCE_INTEGRATION.md)** - Complete political analysis guide
2. **[../website/docs/integrations/grants-gov-api.md](../website/docs/integrations/grants-gov-api.md)** - Full Grants.gov docs
3. **[../website/docs/integrations/fec-political-contributions.md](../website/docs/integrations/fec-political-contributions.md)** - Full FEC docs

### For Implementation

Code references:
1. **[../discovery/grants_gov_integration.py](../discovery/grants_gov_integration.py)** - Grants.gov client
2. **[../discovery/fec_integration.py](../discovery/fec_integration.py)** - FEC client
3. **[../discovery/voter_data_integration.py](../discovery/voter_data_integration.py)** - Voter data client

## 🎯 Use Case Examples

### 1. Grant Opportunity Dashboard

**Goal**: Alert nonprofits about relevant funding

**Implementation**:
```python
from discovery.grants_gov_integration import GrantsGovAPI, GrantMatcher
import pandas as pd

# Find oral health grants
api = GrantsGovAPI()
matcher = GrantMatcher(api)
grants = matcher.find_oral_health_grants(opp_statuses="posted")

# Match to MA nonprofits
nonprofits = pd.read_parquet("data/gold/states/MA/nonprofits_organizations.parquet")
matches = matcher.match_grants_to_state("MA", grants, nonprofits)

# Email alerts
for _, match in matches.iterrows():
    send_email(
        to=nonprofits[nonprofits['EIN'] == match['ein']]['EMAIL'],
        subject=f"NEW Grant: {match['opportunity_title']}",
        body=f"Deadline: {match['close_date']}\nAward: {match['award_amount']}"
    )
```

### 2. Political Transparency Widget

**Goal**: Show political connections on nonprofit profiles

**Implementation**:
```python
from discovery.fec_integration import OpenFECAPI, PoliticalContributionMatcher

# Load nonprofit officers
officers = pd.read_parquet("data/gold/states/MA/nonprofits_officers.parquet")

# Find their political contributions
api = OpenFECAPI(api_key="your_key")
matcher = PoliticalContributionMatcher(api)
contributions = matcher.find_nonprofit_leadership_contributions(
    officers_df=officers,
    state_code="MA",
    min_amount=200
)

# Display on profile
for ein in nonprofits['EIN'].unique():
    org_contributions = contributions[contributions['nonprofit_ein'] == ein]
    if len(org_contributions) > 0:
        display_political_connections_widget(ein, org_contributions)
```

### 3. Influence Analysis

**Goal**: Research political influence on grant awards

**Implementation**:
```python
# Load all data
grants = pd.read_parquet("data/gold/states/MA/grants_revenue_sources.parquet")
contributions = pd.read_parquet("data/gold/fec/political_contributions.parquet")

# Analyze
influence = matcher.analyze_political_influence(contributions, grants)

# Report
print(f"Politically active orgs: {len(influence):,}")
print(f"Avg grant (politically active): ${influence['total_grants_received'].mean():,.0f}")
print(f"Avg grant (not active): ${nonprofits_without_donations['grants'].mean():,.0f}")
```

## 📊 Data Schema Reference

### Federal Grant Opportunities (Grants.gov)

```python
{
    'id': 289999,
    'opportunityNumber': 'HRSA-24-123',
    'opportunityTitle': 'Oral Health Workforce Development',
    'agencyCode': 'HHS-HRSA',
    'agencyName': 'Health Resources & Services Administration',
    'openDate': '2024-10-15',
    'closeDate': '2024-12-31',
    'opportunityStatus': 'posted',
    'cfdaList': [{'cfdaNumber': '93.224'}],
    'fundingCategories': 'HL'
}
```

### Political Contributions (FEC)

```python
{
    'contributor_name': 'John Smith',
    'contributor_city': 'Boston',
    'contributor_state': 'MA',
    'contributor_employer': 'MA Dental Health Clinic',
    'contributor_occupation': 'Executive Director',
    'contribution_receipt_amount': 2500.00,
    'contribution_receipt_date': '2024-06-15',
    'committee_name': 'Smith for Senate',
    'candidate_name': 'Jane Doe'
}
```

### IRS Form 990 (Your Existing Data)

```python
{
    'EIN': '12-3456789',
    'NAME': 'MA Dental Health Clinic',
    'STATE': 'MA',
    'NTEE_CD': 'E32',  # Dental Clinic
    'INCOME_AMT': 2000000,
    'ASSET_AMT': 5000000,
    'REVENUE_AMT': 2000000
}
```

## 🔍 Analysis Examples

### Question 1: Political Influence on Grant Awards?

```python
# Compare nonprofits with/without politically active leadership
politically_active = contributions['nonprofit_ein'].unique()

active_orgs = nonprofits[nonprofits['EIN'].isin(politically_active)]
inactive_orgs = nonprofits[~nonprofits['EIN'].isin(politically_active)]

print(f"With political activity: Avg grant = ${active_orgs['government_grants'].mean():,.0f}")
print(f"Without: Avg grant = ${inactive_orgs['government_grants'].mean():,.0f}")

# Statistical test
from scipy import stats
t_stat, p_value = stats.ttest_ind(
    active_orgs['government_grants'].dropna(),
    inactive_orgs['government_grants'].dropna()
)
print(f"Statistical significance: p={p_value:.4f}")
```

### Question 2: Which Candidates Get Health Sector Donations?

```python
# Filter to health sector
health_contributions = contributions[
    contributions['contributor_employer'].str.contains(
        'health|dental|clinic|hospital',
        case=False,
        na=False
    )
]

# Top recipients
top_recipients = health_contributions.groupby('committee_name').agg({
    'contribution_amount': 'sum',
    'contributor_name': 'count'
}).sort_values('contribution_amount', ascending=False)

print("Top 10 Recipients of Health Sector Donations:")
print(top_recipients.head(10))
```

### Question 3: Grant Opportunity Matching

```python
# Which MA oral health orgs are eligible for current grants?
health_orgs = nonprofits[nonprofits['NTEE_CD'].str.startswith('E', na=False)]
grants = pd.read_parquet("data/gold/grants/oral_health_opportunities.parquet")

matches = matcher.match_grants_to_state("MA", grants, health_orgs)

print(f"{len(matches):,} grant opportunities for {len(health_orgs):,} MA health orgs")
print(f"Total potential funding: ${matches['award_ceiling'].sum():,.0f}")
```

## 🛠️ Troubleshooting

### "No API key" Error

**Problem**: FEC API requires authentication

**Solution**:
```bash
# Get free key at: https://api.data.gov/signup/
python scripts/datasources/fec/demo_political_influence.py --api-key YOUR_KEY

# Or use DEMO_KEY for testing (limited to 30 requests/hour)
python scripts/datasources/fec/demo_political_influence.py --api-key DEMO_KEY
```

### "File not found" Error

**Problem**: Data files haven't been generated yet

**Solution**:
```bash
# Run demos to generate data first
python scripts/datasources/grants_gov/demo_grants_gov.py
python scripts/datasources/fec/demo_political_influence.py --api-key YOUR_KEY

# Or generate specific state data
python -c "
from discovery.irs_bmf_ingestion import IRSBMFIngestion
bmf = IRSBMFIngestion()
ma_df = bmf.download_state_file('MA')
ma_df.to_parquet('data/gold/states/MA/nonprofits_organizations.parquet')
"
```

### "No results found" Error

**Problem**: Search parameters too restrictive

**Solution**:
```python
# Try broader search
results = api.search_individual_contributions(
    contributor_state="MA",  # Remove employer filter
    min_amount=100,  # Lower minimum
    per_page=100  # More results
)

# Or try different keywords
grants = api.search_to_dataframe(
    keyword="health",  # Broader than "oral health"
    funding_categories="HL"
)
```

## 📈 Performance Tips

### Rate Limiting

**FEC API**:
- With API key: 1,000 requests/hour
- DEMO_KEY: 30 requests/hour
- Built-in delays: 0.2s between requests

**Grants.gov**:
- No authentication required
- No published rate limits
- Recommended: 0.5s between requests

### Large Data Sets

**Bulk downloads**:
```python
# FEC bulk files are 1-5 GB
# Use filters to reduce memory:
from discovery.fec_integration import FECBulkDataLoader

loader = FECBulkDataLoader()
zip_file = loader.download_individual_contributions(cycle="2024")

# Parse with filters
contributions_df = loader.parse_individual_contributions(
    zip_path=zip_file,
    state_filter="MA",  # Reduce by 98%
    employer_filter="health",  # Further reduction
    min_amount=200  # Only significant donations
)
```

### Caching

```python
# Cache grant opportunities (update daily)
from pathlib import Path
import pandas as pd
from datetime import datetime, timedelta

cache_file = Path("data/cache/grants_cache.parquet")

if cache_file.exists():
    cache_age = datetime.now() - datetime.fromtimestamp(cache_file.stat().st_mtime)
    if cache_age < timedelta(days=1):
        # Use cache
        grants = pd.read_parquet(cache_file)
    else:
        # Refresh
        grants = fetch_fresh_grants()
        grants.to_parquet(cache_file)
else:
    grants = fetch_fresh_grants()
    grants.to_parquet(cache_file)
```

## 🎓 Learning Resources

### API Documentation

- **Grants.gov API**: https://www.grants.gov/api
- **OpenFEC API**: https://api.open.fec.gov/developers/
- **FEC Bulk Data**: https://www.fec.gov/data/browse-data/?tab=bulk-data

### Research & Analysis

- **OpenSecrets.org**: Campaign finance research
- **FollowTheMoney.org**: State-level money tracking
- **USAspending.gov**: Federal spending database
- **ProPublica Nonprofit Explorer**: IRS 990 data

### Related Projects

- **OpenStates**: State legislator data
- **Google Civic API**: Local elected officials
- **MIT Election Lab**: Election results
- **Ballotpedia**: Comprehensive political data

## 🎯 Next Steps

1. **Run the demos** (see Quick Start above)
2. **Review output files** in `data/gold/`
3. **Try analysis examples** (see Analysis Examples above)
4. **Read documentation** (see Documentation Guide above)
5. **Build features** (see Use Case Examples above)

## 📞 Support

- Check documentation in `website/docs/integrations/`
- Review examples in this directory
- Read API documentation linked above
- Check error messages and logs

**You now have everything you need to integrate political finance data into your civic engagement platform!** 🚀
