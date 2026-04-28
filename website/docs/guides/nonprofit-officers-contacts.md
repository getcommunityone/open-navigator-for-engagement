---
sidebar_position: 12
---

# Nonprofit Officers & Board Members Contact Data

Extract and track nonprofit leadership (officers, directors, trustees) from IRS Form 990 filings as searchable contacts.

## 🎯 Overview

The system now enriches nonprofit data with **officer and board member information** from IRS Form 990 Schedule J, creating versioned contact records with:

- **Officer names** (CEO, CFO, Executive Director, etc.)
- **Board members** and trustees
- **Titles/positions**
- **Compensation** amounts
- **Hours per week**
- **Annual snapshots** for historical tracking

## 📊 Data Sources

### IRS Form 990 Schedule J (Executive Compensation)

**Available via Google BigQuery:**
- `bigquery-public-data.irs_990.irs_990_schedule_j_YYYY`
- Updated annually
- Includes all nonprofits filing Form 990

**Fields Extracted:**
| Field | Description | Example |
|-------|-------------|---------|
| `person_name` | Officer/director name | "Sarah Johnson" |
| `title_txt` | Position/title | "CEO", "Board Chair" |
| `compensation_amount` | Annual compensation | 150000 |
| `average_hours_per_week` | Hours worked | 40 |

## 🚀 Quick Start

### Step 1: Enrich Nonprofits with Officer Data

```bash
# Activate environment
source .venv/bin/activate

# Enrich with BigQuery (includes officers)
python scripts/enrich_nonprofits_bigquery.py \
  --input data/gold/nonprofits_organizations.parquet \
  --output data/gold/nonprofits_organizations.parquet \
  --update-in-place \
  --project YOUR_GCP_PROJECT
```

This adds a `bigquery_officers` JSON field to each nonprofit record:

```json
{
  "ein": "123456789",
  "organization_name": "Alabama Oral Health Foundation",
  "bigquery_officers": [
    {
      "name": "Sarah Johnson",
      "title": "CEO",
      "compensation": 150000,
      "hours_per_week": 40
    },
    {
      "name": "John Smith",
      "title": "Board Chair",
      "compensation": 0,
      "hours_per_week": 5
    }
  ]
}
```

### Step 2: Create Contact Tables with Versioning

```bash
# Create nonprofit officer contacts
python -c "
from pipeline.create_contacts_gold_tables import ContactsGoldTableCreator

creator = ContactsGoldTableCreator()

# Create current year + 2 historical years
creator.create_all_contacts_tables(
    include_nonprofit_officers=True,
    snapshot_years=[2023, 2022, 2021]
)
"
```

**Creates:**
- `contacts_nonprofit_officers.parquet` - Current year
- `contacts_nonprofit_officers_2023.parquet` - 2023 snapshot
- `contacts_nonprofit_officers_2022.parquet` - 2022 snapshot  
- `contacts_nonprofit_officers_2021.parquet` - 2021 snapshot
- `contacts_nonprofit_officers_history.parquet` - Combined history

### Step 3: Search Officers

Officers are now searchable alongside elected officials:

```bash
curl "http://localhost:8000/api/search/?q=Sarah&types=contacts&state=AL"
```

**Returns:**

```json
{
  "query": "Sarah",
  "total_results": 5,
  "results": {
    "contacts": [
      {
        "type": "contact",
        "title": "Sarah Johnson",
        "subtitle": "CEO - Alabama Oral Health Foundation ($150,000)",
        "description": "Nonprofit officer in Birmingham, AL",
        "url": "/nonprofits?name=Alabama-Oral-Health-Foundation",
        "score": 1.5,
        "metadata": {
          "title": "CEO",
          "organization": "Alabama Oral Health Foundation",
          "compensation": 150000,
          "contact_type": "nonprofit_officer"
        }
      }
    ]
  }
}
```

## 📋 Data Schema

### Nonprofit Officers Contact Table

```python
{
    # Officer Info
    'name': 'Sarah Johnson',
    'title': 'CEO',
    'compensation': 150000,
    'hours_per_week': 40,
    
    # Organization
    'organization_ein': '123456789',
    'organization_name': 'Alabama Oral Health Foundation',
    'organization_ntee_code': 'E',
    'organization_type': 'nonprofit',
    
    # Location
    'state': 'AL',
    'city': 'Birmingham',
    'zip_code': '35203',
    
    # Versioning (for annual snapshots)
    'snapshot_year': 2023,
    
    # Metadata
    'source': 'irs_990_schedule_j',
    'contact_type': 'nonprofit_officer',
    'extracted_date': '2024-01-15'
}
```

## 📅 Annual Snapshots & Historical Tracking

### Why Versioning?

**Track changes over time:**
- Officer turnover
- Compensation changes
- Board composition
- Leadership transitions

### Creating Snapshots

```python
from pipeline.create_contacts_gold_tables import ContactsGoldTableCreator

creator = ContactsGoldTableCreator()

# Create snapshot for specific year
creator.create_contacts_nonprofit_officers(snapshot_year=2022)

# Create multi-year history
creator.create_nonprofit_officers_history(years=[2023, 2022, 2021])
```

### Querying Historical Data

```python
import pandas as pd

# Load history
history = pd.read_parquet('data/gold/contacts_nonprofit_officers_history.parquet')

# Find all positions held by a person
sarah_history = history[history['name'] == 'Sarah Johnson']

# Track compensation changes
comp_changes = history.groupby(['organization_ein', 'snapshot_year'])['compensation'].mean()

# Identify board turnover
turnover = history.groupby('organization_ein')['name'].nunique()
```

## 🔍 Use Cases

### 1. Nonprofit Leadership Research

**Find health nonprofit CEOs in Alabama:**

```python
import pandas as pd

officers = pd.read_parquet('data/gold/contacts_nonprofit_officers.parquet')

health_ceos = officers[
    (officers['state'] == 'AL') &
    (officers['organization_ntee_code'].str.startswith('E')) &
    (officers['title'].str.contains('CEO|Executive Director', case=False, na=False))
]

print(f"Found {len(health_ceos)} health nonprofit CEOs in Alabama")
print(health_ceos[['name', 'organization_name', 'compensation']].head())
```

### 2. Compensation Analysis

**Identify highest-paid nonprofit executives:**

```python
top_paid = officers.nlargest(20, 'compensation')[
    ['name', 'title', 'organization_name', 'compensation', 'state']
]
```

### 3. Board Composition

**Find board members (zero/low compensation):**

```python
board_members = officers[
    (officers['title'].str.contains('Board|Director|Trustee', case=False, na=False)) &
    (officers['compensation'] < 10000)
]
```

### 4. Network Analysis

**Map leadership connections across organizations:**

```python
# Find people who serve on multiple boards
multi_board = officers.groupby('name')['organization_ein'].nunique()
cross_board = multi_board[multi_board > 1].sort_values(ascending=False)

print(f"{len(cross_board)} people serve on multiple boards")
```

## 🎯 Integration Points

### Search API

Officers appear in unified search results:

```bash
GET /api/search/?q=dental&types=contacts
GET /api/search/?q=CEO&state=AL
GET /api/search/?q=Board+Chair&ntee_code=E
```

### Frontend Display

**Contact cards show:**
- Officer name and title
- Organization affiliation
- Compensation (if public)
- Link to organization profile

### Data Pipeline

**Automatic updates:**
1. BigQuery enrichment runs annually (when new 990s filed)
2. Contact tables regenerated with new snapshot_year
3. Historical tables updated automatically
4. Search index refreshed

## 📈 Statistics

**Example coverage (Alabama health nonprofits):**
- **Organizations**: 2,500 health nonprofits
- **Officer records**: ~15,000 (avg 6 officers per org)
- **With compensation data**: ~8,000 (53%)
- **Board members**: ~10,000
- **Executive staff**: ~5,000

## 🔧 Technical Notes

### BigQuery Query Performance

The enrichment query joins:
- `irs_990.irs_990_YYYY` (financial data)
- `irs_990.irs_990_schedule_j_YYYY` (officer compensation)

**Optimization tips:**
- Query by state first to reduce data
- Use ARRAY_AGG to consolidate officers
- Cache results (990s don't change after filing)

### Parquet Storage

Officers stored as JSON string in nonprofit table:
```python
'bigquery_officers': '[{"name":"Sarah Johnson","title":"CEO",...}]'
```

Expanded to individual rows in contacts table for searchability.

### Annual Snapshots

**File naming convention:**
- Current: `contacts_nonprofit_officers.parquet`
- Historical: `contacts_nonprofit_officers_2023.parquet`
- Combined: `contacts_nonprofit_officers_history.parquet`

## 🚨 Limitations

### Data Availability

1. **Only e-filed returns**: Schedule J not always available
2. **Varies by form type**: 990-EZ may not include all officers
3. **990-PF different**: Foundation filings use different schema
4. **Lag time**: 990s filed ~18 months after tax year end

### Privacy Considerations

**Public data but sensitive:**
- Compensation is public information (legally required disclosure)
- Names and titles are part of public record
- Consider context when displaying (advocacy vs. general search)

## 📚 Related Documentation

- [IRS Form 990 XML Data](/docs/data-sources/form-990-xml)
- [BigQuery IRS Dataset](/docs/data-sources/irs-bulk-data)
- [Contacts Gold Tables](/docs/guides/contacts-officials)
- [Search API Reference](/docs/api-reference)

## 🎉 Next Steps

1. **Enrich your nonprofit data** with officer information
2. **Create versioned snapshots** for historical tracking
3. **Search officers** via API or frontend
4. **Analyze leadership** patterns and compensation
5. **Track changes** over time with history tables

**Questions?** See [BigQuery enrichment script](https://github.com/getcommunityone/open-navigator-for-engagement/blob/main/scripts/enrich_nonprofits_bigquery.py) for implementation details.
