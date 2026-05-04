# US Census Bureau Data Scripts

Scripts for working with [US Census Bureau](https://www.census.gov/) geographic and demographic data.

## Data Source

- **Website**: https://www.census.gov/
- **API**: https://www.census.gov/data/developers.html
- **Geography**: https://www.census.gov/geographies.html
- **Coverage**: All US jurisdictions
- **Data Types**: Geographic boundaries, demographics, housing, economic data

## Scripts

### Core Scripts

- **`census_ingestion.py`** - Download Census Gazetteer files (government jurisdictions)
- **`acs_ingestion.py`** ⭐ - Download American Community Survey demographic data
- **`download_shapefiles.py`** ⭐ **NEW** - Download TIGER/Line shapefiles (states, counties, ZIP codes)
- `download_county_mappings.py` - Download Census Geographic Relationship Files
- `create_zip_county_mapping.py` - Create ZIP-to-county mapping table

### New: American Community Survey (ACS) Integration

The **`acs_ingestion.py`** script provides comprehensive demographic data download capabilities:

**Key Features:**
- Download demographic, economic, housing, and health data
- Support for multiple geography levels (county, place, tract)
- Automatic caching to D drive or custom directory
- Census API integration with rate limiting
- 20+ pre-configured key tables

**Quick Start:**
```python
from acs_ingestion import ACSDataIngestion
from pathlib import Path

# Use D drive for storage
acs = ACSDataIngestion(data_dir=Path("D:/open-navigator-data/acs"))

# Download median household income
income_df = await acs.download_acs_data_api("B19013", "county", "*")

# Download child health insurance (oral health focus!)
insurance_df = await acs.download_acs_data_api("B27010", "county", "*")
```

**See Also:**
- Full documentation: `website/docs/data-sources/census-acs.md`
- D drive setup: `website/docs/deployment/d-drive-configuration.md`
- Example script: `examples/download_acs_to_d_drive.py`

## Key Datasets

### Census of Governments (census_ingestion.py)
- Counties (3,200+)
- Municipalities/Cities (19,500+)
- Townships (36,000+)
- School Districts (13,000+)

### American Community Survey (acs_ingestion.py) ⭐
- **Demographics**: Age, race, ethnicity, language
- **Economics**: Income, poverty, employment
- **Health Insurance**: Coverage by age (critical for oral health!)
- **Education**: School enrollment, attainment
- **Housing**: Occupancy, value, rent

### TIGER/Line Shapefiles (download_shapefiles.py) ⭐ NEW
- **States**: 50 states + DC + territories (56 total boundaries)
- **Counties**: 3,143 county boundaries
- **ZIP Codes**: 33,000+ ZIP Code Tabulation Areas (ZCTAs)
- **Format**: Cartographic boundary files (optimized for mapping)
- **Use Cases**: Choropleth maps, spatial joins, jurisdiction boundaries

### Geographic Relationship Files
- ZIP Code Tabulation Area (ZCTA) to County mappings
- County to State mappings
- Place to County mappings

## Usage Examples

### Download TIGER/Line Shapefiles ⭐ NEW

```bash
# Download all shapefiles (states, counties, ZIP codes) for 2023
python scripts/datasources/census/download_shapefiles.py --year 2023

# Download only states and counties
python scripts/datasources/census/download_shapefiles.py --year 2023 --types states counties

# Download and auto-extract ZIP files
python scripts/datasources/census/download_shapefiles.py --year 2023 --extract

# Download only ZIP codes (postal codes)
python scripts/datasources/census/download_shapefiles.py --year 2023 --types zcta
```

**Output Location:** `data/cache/census/shapefiles/{year}/`

**Next Steps:**
```python
import geopandas as gpd

# Load shapefile (from ZIP, no extraction needed!)
states = gpd.read_file("data/cache/census/shapefiles/2023/cb_2023_us_state_500k.zip")

# Convert to GeoJSON for web mapping
states.to_file("data/gold/boundaries/states.geojson", driver="GeoJSON")

# Or save as GeoParquet (more efficient)
states.to_parquet("data/gold/boundaries/states.parquet")
```

**See Full Guide:** `website/docs/data-sources/census-shapefiles.md`

### Download ACS Data to D Drive

```bash
# Download all key demographic tables for all counties
python examples/download_acs_to_d_drive.py --geography county --state "*"

# Download California counties only
python examples/download_acs_to_d_drive.py --geography county --state 06

# Download health insurance data only
python examples/download_acs_to_d_drive.py --health-insurance-only

# List all available tables
python examples/download_acs_to_d_drive.py --list-tables
```

### Download County Mappings

```bash
# Download county relationship files
python download_county_mappings.py

# Create ZIP-county mapping
python create_zip_county_mapping.py
```

### Download Jurisdiction Lists

```bash
# Ingest Census API data
python census_ingestion.py --state MA --dataset acs5
```

## Data License

US Census Bureau data is public domain.
