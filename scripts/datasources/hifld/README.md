# HIFLD Data Scripts

> **⚠️ IMPORTANT (2026 Update):** The HIFLD Open portal (hifld-geoplatform.opendata.arcgis.com) has been officially sunsetted. Data has been migrated to:
> - **Data Rescue Project**: portal.datarescueproject.org (for Public/Private Schools and other rescued datasets)
> - **ArcGIS Online**: Specialized mirrors and re-indexed datasets
> - **USGS Mirrors**: Some infrastructure datasets maintained by USGS

## Overview

HIFLD (Homeland Infrastructure Foundation-Level Data) provided geospatial data on critical infrastructure and community resources. Following the portal sunset, data is now distributed across multiple sources:

### ✅ Currently Accessible (via these scripts)
- **Places of worship** - 254,742+ churches, mosques, synagogues, temples
- **Hospitals and healthcare facilities** - 7,496+ hospitals, urgent care centers, clinics
- **Law enforcement** - 46,972+ locations (police, sheriff, special jurisdiction)

### ⚠️ Requires Alternative Download Methods
- **Schools** - Now on Data Rescue Project (requires different API)
- **Fire Stations** - Available but dataset structure incompatible with current scripts
- **Government buildings** - May be available as "Courthouses" dataset

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

### 2026 Updated Sources

Due to the HIFLD portal sunset, datasets are now scattered across multiple portals:

**1. ArcGIS Online** (arcgis.com)
- Search at https://www.arcgis.com/home/search.html
- Look for datasets tagged with "HIFLD"
- Copy Item ID from URL

**2. Data Rescue Project** (portal.datarescueproject.org)
- Rescued datasets from old HIFLD portal
- Uses different identifier format (slugs, not Item IDs)
- **Not compatible with current download scripts**

**3. USGS and State Mirrors**
- Some datasets re-hosted by USGS or state agencies
- May have updated Item IDs

### Available Datasets (2026)

| Dataset | Item ID | Portal | Count | Status |
|---------|---------|--------|-------|--------|
| **Places of Worship** | `495cc33ef490462ab2d8933247a66a87` | ArcGIS Online | 254,742 | ✅ Working |
| **Hospitals** | `f36521f6e07f4a859e838f0ad7536898` | ArcGIS Online | 7,496 | ✅ Working |
| **Law Enforcement** | `333a74c8e9c64cb6870689d31e8836af` | ArcGIS Online | 46,972 | ✅ Working |
| **Fire Stations** | `d33b8b5d03a84170847b48d7d4c1bdf6` | ArcGIS Online | Unknown | ⚠️ API incompatible |
| **Public Schools** | `hifld-open-public-schools` | Data Rescue | Unknown | ⚠️ Requires different API |
| **Private Schools** | `hifld-open-private-schools` | Data Rescue | Unknown | ⚠️ Requires different API |
| **Courthouses** | `f4007823f38c4b12b508f7b76400c0a9` | ArcGIS Online | Unknown | 🔍 Not verified |

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
