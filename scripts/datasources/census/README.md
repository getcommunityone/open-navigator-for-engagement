# US Census Bureau Data Scripts

Scripts for working with [US Census Bureau](https://www.census.gov/) geographic and demographic data.

## Data Source

- **Website**: https://www.census.gov/
- **API**: https://www.census.gov/data/developers.html
- **Geography**: https://www.census.gov/geographies.html
- **Coverage**: All US jurisdictions
- **Data Types**: Geographic boundaries, demographics, housing, economic data

## Scripts

- `census_ingestion.py` - Ingest Census API data
- `download_county_mappings.py` - Download Census Geographic Relationship Files
- `create_zip_county_mapping.py` - Create ZIP-to-county mapping table

## Key Datasets

### Geographic Relationship Files
- ZIP Code Tabulation Area (ZCTA) to County mappings
- County to State mappings
- Place to County mappings

### Demographics
- Population by jurisdiction
- Age, race, income distributions
- Housing units and occupancy

## Usage Examples

```bash
# Download county relationship files
python download_county_mappings.py

# Create ZIP-county mapping
python create_zip_county_mapping.py

# Ingest Census API data
python census_ingestion.py --state MA --dataset acs5
```

## Data License

US Census Bureau data is public domain.
