---
sidebar_position: 12
---

# Form 990 XML Data (GivingTuesday Data Lake)

Extract detailed financial data from IRS Form 990 XML filings using [GivingTuesday's 990 Data Infrastructure](https://990data.givingtuesday.org/).

## 🎯 Overview

**Current data:** IRS EO-BMF CSV files (basic info - name, EIN, address, NTEE code)  
**Enhancement:** Form 990 XML filings from GivingTuesday Data Lake (detailed financials - revenue, expenses, programs, grants)

### What is the GivingTuesday 990 Data Lake?

The [990 Data Infrastructure](https://990data.givingtuesday.org/) is a collaborative data lake of clean, standardized 990 data in XML format maintained by GivingTuesday. This is the rawest form of 990 data in GivingTuesday's infrastructure.

**Data Lake Structure:**
- **Bucket**: `gt990datalake-rawdata` (AWS S3, us-east-1 Virginia)
- **Access**: Public, no AWS credentials required (`--no-sign-request`)
- **E-filed 990s**: `EfileData/XmlFiles/` (individual XML returns)
- **Indices**: `Indices/990xmls/` (CSV files listing all available 990s)

**Console Access**: [https://us-east-1.console.aws.amazon.com/s3/buckets/gt990datalake-rawdata](https://us-east-1.console.aws.amazon.com/s3/buckets/gt990datalake-rawdata)

### What's the Difference?

| Data Source | Type | Records | Data Richness | What You Get |
|-------------|------|---------|---------------|--------------|
| **EO-BMF CSV** ✅ Currently using | Basic registry | 1.9M+ | ⭐ Low | Name, EIN, address, NTEE code, subsection |
| **Form 990 XML** 🚀 Enhancement | Tax returns | ~300K/year | ⭐⭐⭐⭐⭐ High | Revenue, expenses, assets, grants, programs, officer compensation, mission statements |

## 📊 What Additional Data You Can Get

### From Form 990 XML:
- **Financials**: Total revenue, program revenue, contributions, grants, investment income
- **Expenses**: Total expenses, program expenses, administrative, fundraising
- **Assets**: Total assets, liabilities, net assets
- **Programs**: Program service descriptions, accomplishments, expenses per program
- **Governance**: Board members, officer compensation, key employees
- **Grants**: Grants awarded, grant recipients
- **Mission**: Detailed mission statement and program descriptions
- **Activities**: Legislative activities, political expenditures, lobbying

**Example:** Instead of just knowing "Alabama Oral Health Foundation exists," you get:
- Revenue: $2.5M
- Program expenses: $1.8M
- Grants awarded: $500K to 10 community health centers
- Mission: "Improve oral health access in underserved communities"
- Officers: CEO Sarah Johnson ($150K salary)

## 🚀 Accessing the GivingTuesday Data Lake

### Option 1: Via AWS Console (Free Account)

1. Visit [aws.amazon.com](https://aws.amazon.com) and create a free AWS account (requires CC for validation, but no charges for accessing this data)
2. Log in to AWS Console
3. Open the data lake: [https://s3.console.aws.amazon.com/s3/buckets/gt990datalake-rawdata/?region=us-east-1&tab=objects](https://s3.console.aws.amazon.com/s3/buckets/gt990datalake-rawdata/?region=us-east-1&tab=objects)

### Option 2: Via Command Line (Recommended for Automation)

**Prerequisites**: Install [AWS CLI](https://aws.amazon.com/cli/)

```bash
# List main bucket contents
aws s3 ls gt990datalake-rawdata --no-sign-request

# List indices (CSV files listing all 990s)
aws s3 ls gt990datalake-rawdata/Indices/990xmls/ --no-sign-request

# Download the latest index
aws s3 cp \
  s3://gt990datalake-rawdata/Indices/990xmls/index_all_years_efiledata_xmls_created_on_2023-10-29.csv \
  data/cache/form990_index.csv \
  --no-sign-request

# Download a specific 990 XML
aws s3 cp \
  s3://gt990datalake-rawdata/EfileData/XmlFiles/[OBJECT_ID]_public.xml \
  data/cache/form_990_xml/ \
  --no-sign-request
```

### Option 3: Automated Python Integration

Use our enrichment script that automates downloading and parsing:

```python
import boto3
from botocore import UNSIGNED
from botocore.config import Config
import pandas as pd

# Configure S3 client for GivingTuesday Data Lake (no credentials needed)
s3 = boto3.client(
    's3',
    region_name='us-east-1',
    config=Config(signature_version=UNSIGNED)
)

# Download index to find available 990s
index_response = s3.get_object(
    Bucket='gt990datalake-rawdata',
    Key='Indices/990xmls/index_all_years_efiledata_xmls_created_on_2023-10-29.csv'
)
index_df = pd.read_csv(index_response['Body'])

print(f"Available 990s: {len(index_df):,}")
print(f"Columns: {index_df.columns.tolist()}")

# Find 990s for a specific EIN
ein = "123456789"
org_filings = index_df[index_df['EIN'] == ein]

# Download latest filing
if len(org_filings) > 0:
    latest = org_filings.iloc[0]
    xml_key = f"EfileData/XmlFiles/{latest['OBJECT_ID']}_public.xml"
    
    xml_obj = s3.get_object(Bucket='gt990datalake-rawdata', Key=xml_key)
    xml_content = xml_obj['Body'].read()
    
    # Parse with xmltodict (simplified approach)
    import xmltodict
    doc = xmltodict.parse(xml_content)
    # Extract fields from doc['Return']['ReturnData']['IRS990']
```

## 🤖 Automated Enrichment Script

We provide **[scripts/enrich_nonprofits_gt990.py](../../scripts/enrich_nonprofits_gt990.py)** - a complete automated solution.

### Quick Start

**Step 1: Download Index (One-Time Setup)**
```bash
# Install dependencies
pip install boto3 xmltodict pandas pyarrow tqdm loguru

# Download GivingTuesday Data Lake index (~200MB CSV, 1M+ records)
python scripts/enrich_nonprofits_gt990.py --download-index
```

This creates `data/cache/form990_gt_index.parquet` for fast EIN→OBJECT_ID lookups.

**Step 2: Enrich Your Data**
```bash
# Enrich all Tuscaloosa nonprofits
python scripts/enrich_nonprofits_gt990.py \
    --input data/gold/nonprofits_tuscaloosa.parquet \
    --output data/gold/nonprofits_tuscaloosa_form990.parquet \
    --concurrent 20

# Enrich Alabama + Michigan health orgs
python scripts/enrich_nonprofits_gt990.py \
    --input data/gold/nonprofits_organizations.parquet \
    --output data/gold/nonprofits_990_enriched.parquet \
    --states AL MI \
    --ntee E \
    --concurrent 50

# Test with sample
python scripts/enrich_nonprofits_gt990.py \
    --input data/gold/nonprofits_organizations.parquet \
    --output /tmp/test_990.parquet \
    --sample 100
```

### Features

✅ **Index-based lookup**: Uses OBJECT_ID from GivingTuesday index (no filename guessing)  
✅ **Async/parallel**: Process 20-50 organizations concurrently  
✅ **Smart caching**: JSON cache prevents re-downloading same 990s  
✅ **Automatic retries**: Handles S3 errors gracefully  
✅ **Progress tracking**: tqdm progress bar with ETA  
✅ **Comprehensive logging**: Detailed logs with statistics

### Performance

- **Speed**: ~2-3 sec/org (download + parse)
- **Concurrent=20**: ~450 orgs/hour
- **Concurrent=50**: ~1,100 orgs/hour
- **1,000 orgs @ 50% success**: ~15-20 minutes

### Enriched Fields

The script adds these columns to your DataFrame:

```python
form_990_status             # 'found', 'not_found', or 'parse_error'
form_990_tax_year          # e.g., 202312
form_990_filing_type       # 990, 990EZ, or 990PF
form_990_total_revenue     # Total revenue
form_990_total_expenses    # Total expenses
form_990_net_income        # Revenue - Expenses
form_990_contributions     # Donations and grants received
form_990_program_revenue   # Revenue from programs/services
form_990_investment_income # Investment income
form_990_program_expenses  # Program service expenses
form_990_admin_expenses    # Administrative expenses
form_990_fundraising_expenses  # Fundraising expenses
form_990_total_assets      # Total assets
form_990_total_liabilities # Total liabilities
form_990_net_assets        # Assets - Liabilities
form_990_grants_paid       # Grants awarded to others
form_990_mission           # Mission statement
form_990_last_updated      # Timestamp of enrichment

# Filter to your state
alabama_filings = filings_index[filings_index['State'] == 'AL']
print(f"Alabama filings: {len(alabama_filings):,}")

# Sample columns
# EIN, OrganizationName, State, URL, SubmittedOn, TaxPeriod
```

## 🔗 Integration with Current Data

### Enrich Existing Nonprofits

```python
import pandas as pd
from form990_parser import Form990Parser
import boto3

# Load your current nonprofit data
orgs = pd.read_parquet('data/gold/nonprofits_organizations.parquet')

# Filter to Alabama health organizations (NTEE code E)
health_orgs = orgs[
    (orgs['state'] == 'AL') & 
    (orgs['ntee_code'].str.startswith('E', na=False))
]

print(f"Alabama health nonprofits: {len(health_orgs):,}")

# Enrich with Form 990 data
s3 = boto3.client('s3', region_name='us-east-1')
parser = Form990Parser()

enriched = []
for idx, org in health_orgs.iterrows():
    ein = org['ein']
    
    # Try to find most recent 990
    try:
        # Construct likely S3 key (simplified - actual naming varies)
        key = f"{ein}_202312_990.xml"
        
        xml_obj = s3.get_object(Bucket='irs-form-990', Key=key)
        xml_content = xml_obj['Body'].read()
        
        filing_data = parser.parse_xml(xml_content)
        
        # Merge with org data
        org_enriched = org.to_dict()
        org_enriched.update(filing_data)
        enriched.append(org_enriched)
        
    except Exception as e:
        # No 990 found for this org
        continue

enriched_df = pd.DataFrame(enriched)
enriched_df.to_parquet('data/gold/nonprofits_alabama_health_990.parquet')

print(f"Enriched {len(enriched_df):,} organizations with Form 990 data")
```

## 💾 Data Schema

### Form 990 Parser Output

```python
{
    # Basic Info
    'ein': '123456789',
    'organization_name': 'Alabama Oral Health Foundation',
    'tax_year': 2023,
    'tax_period': '202312',
    
    # Financials
    'total_revenue': 2500000,
    'total_expenses': 2100000,
    'net_income': 400000,
    'total_assets': 5000000,
    'total_liabilities': 500000,
    
    # Revenue Breakdown
    'contributions_grants': 1200000,
    'program_service_revenue': 800000,
    'investment_income': 300000,
    'other_revenue': 200000,
    
    # Expense Breakdown
    'program_expenses': 1800000,
    'administrative_expenses': 200000,
    'fundraising_expenses': 100000,
    
    # Programs
    'program_service_descriptions': [
        {
            'description': 'Community dental clinics',
            'expenses': 1000000,
            'grants': 200000
        },
        {
            'description': 'School fluoride programs',
            'expenses': 500000,
            'grants': 100000
        }
    ],
    
    # Governance
    'officers': [
        {
            'name': 'Sarah Johnson',
            'title': 'CEO',
            'compensation': 150000
        },
        {
            'name': 'John Smith',
            'title': 'CFO',
            'compensation': 120000
        }
    ],
    
    # Mission
    'mission_statement': 'Improve oral health access in underserved communities...',
    'program_accomplishments': 'Served 10,000 patients in 2023...'
}
```

## 📈 Performance Considerations

### Data Volume

- **Form 990 XMLs**: ~300,000 new filings per year
- **Average XML size**: 500KB - 5MB
- **Total storage**: ~500GB for all historical 990s (2011-present)

### Processing Speed

**Sequential (current approach):**
- Download + parse: ~2-5 seconds per 990
- 300,000 filings × 3 sec = **250 hours** 😱

**Async parallel (recommended):**
- 50 concurrent workers
- 300,000 filings × 3 sec / 50 = **5 hours** ⚡

### Smart Strategies

1. **Filter first**: Only download 990s for organizations you care about
   ```python
   # Only health orgs in your states
   health_eins = orgs[
       (orgs['state'].isin(['AL', 'MI'])) &
       (orgs['ntee_code'].str.startswith('E'))
   ]['ein'].tolist()
   
   # Result: ~50,000 instead of 300,000 = 1 hour
   ```

2. **Use index files**: Download the index first, filter, then fetch XMLs
   ```python
   # Get index
   index = pd.read_json('https://s3.amazonaws.com/irs-form-990/index_2023.json')
   
   # Filter to your EINs
   relevant = index[index['EIN'].isin(health_eins)]
   
   # Only download these
   for url in relevant['URL']:
       # download and parse
   ```

3. **Cache aggressively**: 990s don't change after filing
   ```python
   cache_dir = Path('data/cache/form_990_xml')
   cache_file = cache_dir / f"{ein}_{tax_year}.parquet"
   
   if cache_file.exists():
       return pd.read_parquet(cache_file)
   else:
       # download, parse, cache
   ```

## 🎯 Use Cases

### 1. Financial Health Analysis

```python
# Which nonprofits are most financially stable?
df['efficiency_ratio'] = df['program_expenses'] / df['total_expenses']
df['reserve_months'] = df['net_assets'] / (df['total_expenses'] / 12)

efficient = df[df['efficiency_ratio'] > 0.75]  # >75% on programs
print(f"Efficient organizations: {len(efficient):,}")
```

### 2. Grant Research

```python
# Who's giving grants in oral health?
grantmakers = df[
    (df['grants_paid'] > 0) &
    (df['ntee_code'].str.startswith('E'))
]

print(f"Oral health grantmakers: {len(grantmakers):,}")
print(f"Total grants: ${grantmakers['grants_paid'].sum():,.0f}")
```

### 3. Program Discovery

```python
# Find organizations running specific programs
fluoride_programs = df[
    df['program_service_descriptions'].str.contains('fluoride', case=False, na=False)
]

print(f"Orgs with fluoride programs: {len(fluoride_programs):,}")
```

## 🚀 Next Steps

### Quick Test

```bash
# Install dependencies
pip install form-990-xml-parser boto3

# Test with single organization
python -c "
from form990_parser import Form990Parser
import boto3

s3 = boto3.client('s3', region_name='us-east-1')
ein = '631307851'  # Delta Dental of Alabama (example)

try:
    # Try to fetch 2023 filing
    key = f'{ein}_202312_990.xml'
    obj = s3.get_object(Bucket='irs-form-990', Key=key)
    
    parser = Form990Parser()
    data = parser.parse_xml(obj['Body'].read())
    
    print(f'Organization: {data.get(\"organization_name\")}')
    print(f'Revenue: \${data.get(\"total_revenue\", 0):,.0f}')
    print(f'Assets: \${data.get(\"total_assets\", 0):,.0f}')
except Exception as e:
    print(f'Error: {e}')
"
```

### Full Integration

Create a new enrichment pipeline:

```bash
# Create new script
python scripts/enrich_nonprofits_form990.py \
    --input data/gold/nonprofits_organizations.parquet \
    --output data/gold/nonprofits_organizations_990.parquet \
    --states AL MI \
    --ntee E \
    --concurrent 50
```

## 📚 Resources

- **Giving Tuesday GitHub**: https://github.com/Giving-Tuesday
- **Form 990 XML Parser**: https://github.com/Giving-Tuesday/form-990-xml-parser
- **Form 990 XML Mapper**: https://github.com/Giving-Tuesday/form-990-xml-mapper
- **IRS 990 AWS Bucket**: https://registry.opendata.aws/irs990/
- **IRS Index Files**: https://s3.amazonaws.com/irs-form-990/index_YYYY.json
- **990 Schema Documentation**: https://www.irs.gov/e-file-providers/current-valid-xml-schemas-and-business-rules

## ❓ FAQ

### Q: Are we currently downloading XML?

**A: No.** Currently using EO-BMF CSV files (basic data). Form 990 XML would be an enhancement for detailed financials.

### Q: Can we use Giving Tuesday libraries?

**A: Yes!** They're open source and designed exactly for this purpose. Would provide much richer data.

### Q: How much data is it?

**A:** 
- All 990s (2011-present): ~500GB
- Alabama only: ~5GB
- Alabama health orgs: ~500MB
- Very manageable!

### Q: What's the license?

**A:** Public domain (U.S. Government data) + Giving Tuesday tools are open source

### Q: Integration effort?

**A:** Low - can reuse existing async enrichment patterns. Estimated: 1-2 days for initial integration.
