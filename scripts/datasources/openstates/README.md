# OpenStates Data Scripts

Scripts for working with [OpenStates](https://openstates.org/) legislative data.

## Data Source

- **Website**: https://openstates.org/
- **API Docs**: https://docs.openstates.org/api-v3/
- **Bulk Data**: https://openstates.org/data/
- **Coverage**: 52 US states and territories
- **Data Types**: Bills, legislators, votes, committees

## Scripts

### Download & Import
- `bulk_legislative_download.py` - Download OpenStates bulk data dumps
- `load_openstates_csv.sh` - Load CSV exports into database
- `load_openstates_people.py` - Load legislator data from GitHub repo

### Schema & Export
- `create_openstates_schema.py` - Create PostgreSQL schema for OpenStates data
- `export_openstates_to_gold.py` - Export from PostgreSQL to Gold Parquet files

### Processing
- `aggregate_bills_from_postgres.py` - Aggregate bill statistics by state/topic
- `legislative_tracker.py` - Track legislative activity

## Usage Examples

```bash
# Download April 2026 bulk data
python bulk_legislative_download.py --postgres --month 2026-04

# Create database schema
python create_openstates_schema.py

# Load legislator data
python load_openstates_people.py

# Export to Gold format
python export_openstates_to_gold.py

# Aggregate bill statistics
python aggregate_bills_from_postgres.py
```

## Data License

OpenStates data is available under various open licenses. See https://openstates.org/data/ for details.
