# HIFLD Data Scripts

Scripts for downloading and processing Homeland Infrastructure Foundation-Level Data (HIFLD) from the U.S. Department of Homeland Security.

## Overview

HIFLD provides geospatial data on critical infrastructure and community resources including:
- **Places of worship** - 350,000+ churches, mosques, synagogues, temples
- **Schools and educational facilities** - K-12 schools, universities, vocational centers
- **Hospitals and healthcare facilities** - Hospitals, urgent care centers, clinics
- **Emergency services** - Law enforcement (23,486 locations), fire stations, EMS
- **Government buildings** - City halls, courthouses, federal facilities
- **And more** - Libraries, post offices, airports, prisons, etc.

**Data is public domain** (U.S. Government work) with no usage restrictions.

## Scripts

### `download_arcgis_dataset.py`

Download any HIFLD dataset from ArcGIS using the REST API.

**Usage:**

```bash
# Download Law Enforcement dataset (verified Item ID)
python scripts/datasources/hifld/download_arcgis_dataset.py \
  --item-id 333a74c8e9c64cb6870689d31e8836af

# Get metadata first to verify the dataset
python scripts/datasources/hifld/download_arcgis_dataset.py \
  --item-id 333a74c8e9c64cb6870689d31e8836af \
  --metadata-only

# Download as GeoJSON (includes geometry for mapping)
python scripts/datasources/hifld/download_arcgis_dataset.py \
  --item-id 333a74c8e9c64cb6870689d31e8836af \
  --format GeoJSON

# Download as CSV (no geometry, lighter file)
python scripts/datasources/hifld/download_arcgis_dataset.py \
  --item-id 333a74c8e9c64cb6870689d31e8836af \
  --format CSV

# Convert to Parquet (best for data analysis)
python scripts/datasources/hifld/download_arcgis_dataset.py \
  --item-id 333a74c8e9c64cb6870689d31e8836af \
  --to-parquet

# Use a different dataset (replace with your Item ID)
python scripts/datasources/hifld/download_arcgis_dataset.py \
  --item-id YOUR_ITEM_ID_HERE \
  --to-parquet \
  --output data/gold/infrastructure/hospitals.parquet
```

**Arguments:**

- `--item-id`: ArcGIS Item ID (required - find in the dataset URL)
- `--format`: Output format (`CSV`, `GeoJSON`, `Shapefile`, `KML`) - default: `CSV`
- `--output`: Custom output path (optional, defaults to cache directory)
- `--to-parquet`: Convert to Parquet format after download
- `--metadata-only`: Only display dataset information without downloading
- `--portal`: ArcGIS portal URL (default: https://www.arcgis.com)

## Finding Dataset IDs

1. Go to https://hifld-geoplatform.opendata.arcgis.com/
2. Search for your dataset (e.g., "hospitals", "schools", "places of worship")
3. Click on the dataset you want
4. Look at the URL - the Item ID is at the end:
   ```
   https://www.arcgis.com/home/item.html?id=YOUR_ITEM_ID_HERE
   ```
5. Copy that Item ID and use it with the download script

**Available Datasets:**

| Dataset | Item ID | Count | Status |
|---------|---------|-------|--------|
| Law Enforcement Locations | `333a74c8e9c64cb6870689d31e8836af` | 23,486 | ✅ Verified |
| Places of Worship | [Find Item ID](https://hifld-geoplatform.opendata.arcgis.com/) | 350,000+ | 🔍 Search for ID |
| Schools | [Find Item ID](https://hifld-geoplatform.opendata.arcgis.com/) | Varies | 🔍 Search for ID |
| Hospitals | [Find Item ID](https://hifld-geoplatform.opendata.arcgis.com/) | Varies | 🔍 Search for ID |
| Fire Stations | [Find Item ID](https://hifld-geoplatform.opendata.arcgis.com/) | Varies | 🔍 Search for ID |
| Government Buildings | [Find Item ID](https://hifld-geoplatform.opendata.arcgis.com/) | Varies | 🔍 Search for ID |

## Data Output

Downloaded data is cached in `data/cache/hifld/` with filenames like:

```
data/cache/hifld/
├── Places_of_Worship_333a74c8e9c64cb6870689d31e8836af.geojson
├── Places_of_Worship_333a74c8e9c64cb6870689d31e8836af.csv
└── Places_of_Worship_333a74c8e9c64cb6870689d31e8836af.parquet
```

Cache is valid for 7 days to avoid redundant downloads.

## Dependencies

Install required Python packages:

```bash
pip install arcgis geopandas loguru
```

Or install all project dependencies from the project root:
```bash
pip install -r requirements.txt
```

**Note:** The `arcgis` library is the official ArcGIS Python API for accessing ArcGIS Online datasets.

## Data Structure

### GeoJSON Format

```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "geometry": {
        "type": "Point",
        "coordinates": [-71.0589, 42.3601]
      },
      "properties": {
        "NAME": "Old North Church",
        "ADDRESS": "193 Salem Street",
        "CITY": "Boston",
        "STATE": "MA",
        "ZIP": "02113",
        "DENOMINATION": "Episcopal",
        ...
      }
    }
  ],
  "metadata": {
    "title": "Places of Worship",
    "source": "https://www.arcgis.com/home/item.html?id=333a74c8e9c64cb6870689d31e8836af",
    "downloaded": "2026-05-04T11:30:00",
    "feature_count": 350000
  }
}
```

### CSV Format

Includes all attribute fields but no geometry column. Suitable for analysis without GIS software.

### Parquet Format

Optimized for data analysis with pandas/polars. Can include geometry if using GeoPandas.

## Citations

When using HIFLD data, cite as:

> "Homeland Infrastructure Foundation-Level Data (HIFLD). U.S. Department of Homeland Security. https://hifld-geoplatform.opendata.arcgis.com/"

See [Citations](/docs/data-sources/citations#homeland-infrastructure-foundation-level-data-hifld-places-of-worship) for complete citation information.

## License

HIFLD data is **Public Domain** (U.S. Government work). No restrictions on use.

## API Rate Limits

The ArcGIS REST API has rate limits:
- Max 1,000 features per request (handled by batch_size)
- Recommended: Add delays between batches for very large datasets
- The script automatically handles pagination

## Troubleshooting

**"Connection timeout"**
- Increase timeout with larger datasets
- The script will retry failed batches

**"Invalid item ID"**
- Verify the ID is correct by visiting the ArcGIS item page
- Some datasets may require authentication (not currently supported)

**"No features returned"**
- Dataset may be empty or unavailable
- Check if the dataset has been updated/moved

## Related Data Sources

- **ARDA (Association of Religion Data Archives):** Congregation statistics and surveys
- **National Congregations Study:** Representative sample of U.S. congregations
- **IRS Tax-Exempt Organizations:** Churches and religious nonprofits

See complete data source list in [Citations](/docs/data-sources/citations).
