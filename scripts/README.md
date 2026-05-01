# Scripts Directory

All scripts are organized into logical subdirectories by function.

## 📂 Directory Structure

```
scripts/
├── data/                    # Data processing and migration
├── datasources/             # Data source integrations and connectors
├── deployment/              # Deployment and setup
├── development/             # Development and debugging tools
├── enrichment/              # Data enrichment (990s, nonprofits)
├── huggingface/             # HuggingFace dataset management
└── maintenance/             # Cleanup and maintenance
```

## 📖 Folder Descriptions

### [data/](data/)
Data processing pipelines, migrations, and aggregations.
- Bill aggregations from PostgreSQL
- Gold table creation
- Contact extraction
- Data splits and partitioning

### [datasources/](datasources/)
Data source integrations and API connectors organized by external data source.

**Available Sources:**
- `openstates/` - OpenStates legislative data (bills, legislators, votes) - 7 scripts
- `census/` - US Census Bureau geographic and demographic data - 3 scripts
- `irs/` - IRS nonprofit data (Form 990, Business Master File) - 3 scripts
- `fec/` - Federal Election Commission campaign finance data - 2 scripts
- `ballotpedia/` - Ballotpedia election and official data - 1 script
- `google_civic/` - Google Civic Information API - 1 script
- `grants_gov/` - Grants.gov federal grant data - 1 script
- `localview/` - LocalView meeting transcripts - 1 script
- `meetingbank/` - MeetingBank research dataset - 1 script
- `nces/` - National Center for Education Statistics - 1 script
- `wikidata/` - Wikidata structured knowledge - 1 script
- `dbpedia/` - DBpedia structured Wikipedia data - 1 script
- `voter_data/` - Voter registration and turnout data - 1 script

See [datasources/README.md](datasources/README.md) for detailed documentation.

### [deployment/](deployment/)
Setup scripts for local development and production deployment.
- Local environment setup
- Database initialization
- Databricks deployment

### [development/](development/)
Development and debugging tools.
- Debug scripts for scrapers
- Testing utilities
- Development helpers

### [enrichment/](enrichment/)
Scripts to enrich nonprofit data with additional metadata.
- 990 form downloads and processing
- Nonprofit profile enrichment
- Multiple data source integrations

### [huggingface/](huggingface/)
HuggingFace dataset preparation and upload.
- Dataset restructuring
- Multi-dataset uploads
- Finalization scripts

### [maintenance/](maintenance/)
System maintenance and cleanup utilities.
- Disk space cleanup
- File management
- Development utilities

## 🔍 Finding Scripts

Use these commands to find scripts:

```bash
# List all scripts in a category
ls scripts/data/

# Search for a specific script
find scripts/ -name "*aggregate*"

# See what a script does
head -20 scripts/data/aggregate_bills_from_postgres.py
```

## ⚠️ Important Note

All scripts should be run from the project root directory:

```bash
# ✅ Correct
cd /home/developer/projects/open-navigator
python scripts/data/aggregate_bills_from_postgres.py

# ❌ Wrong
cd scripts/data
python aggregate_bills_from_postgres.py
```
