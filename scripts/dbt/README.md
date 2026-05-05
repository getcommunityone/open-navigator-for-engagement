# dbt Stats Pipeline

## Overview

This directory contains scripts for building and syncing statistics from dbt models.

## Pipeline Architecture

```
Bronze DB (dev)  →  Production DB (queries)  →  Neon Cloud (website)
open_navigator_bronze  →  open_navigator  →  Neon PostgreSQL
```

### Database Roles

- **`open_navigator_bronze`**: Development database for raw data and dbt transformations
  - Contains `bronze_*` tables from data loading scripts
  - dbt models run here (staging, intermediate, marts)
  - NOT deployed to production servers

- **`open_navigator`**: Production-ready local PostgreSQL database
  - Fast queries for API endpoints
  - Synced from bronze via export scripts
  - Source for Neon cloud deployment

- **Neon Cloud**: Production database for deployed website
  - Synced via `scripts/deployment/neon/migrate.py`
  - Optimized for HuggingFace Spaces deployment

## Workflow: Building Stats

### 1. Run dbt models

Build the stats in the bronze database:

```bash
cd dbt_project
source ../.venv/bin/activate
dbt run --target bronze --select stg_bronze_decisions+
```

**What this does:**
- `stg_bronze_decisions`: Cleans and filters recent decisions (last 90 days)
- `int_trending_causes_by_jurisdiction`: Aggregates decisions by NTEE cause category
- `stats_aggregates`: Final stats table with trending causes JSON

**Output:** `open_navigator_bronze.public_public.stats_aggregates`

### 2. Export to production database

Sync stats from bronze to production:

```bash
cd /home/developer/projects/open-navigator
source .venv/bin/activate
python scripts/dbt/export_stats_to_open_navigator.py
```

**What this does:**
- Reads from `open_navigator_bronze.public_public.stats_aggregates`
- Deletes old data from `open_navigator.stats_aggregates`
- Inserts updated stats (3 records: national, state, jurisdiction levels)
- Handles JSONB serialization for trending_causes column

**Output:** `open_navigator.stats_aggregates` (ready for API queries)

### 3. Deploy to Neon Cloud (optional)

For production deployment:

```bash
python scripts/deployment/neon/migrate.py
```

## Data Schema

### stats_aggregates Table

| Column | Type | Description |
|--------|------|-------------|
| `level` | VARCHAR(20) | Aggregation level: `national`, `state`, `county`, `city`, `jurisdiction` |
| `state_code` | VARCHAR(2) | Two-letter state code (e.g., 'AL', 'MA') |
| `state` | VARCHAR(50) | Full state name (e.g., 'Alabama', 'Massachusetts') |
| `county` | VARCHAR(100) | County name |
| `city` | VARCHAR(100) | City name |
| `jurisdictions_count` | INTEGER | Number of jurisdictions |
| `school_districts_count` | INTEGER | Number of school districts |
| `nonprofits_count` | INTEGER | Number of nonprofits |
| `events_count` | INTEGER | Number of events/meetings |
| `bills_count` | INTEGER | Number of bills |
| `contacts_count` | INTEGER | Number of contacts |
| `total_revenue` | BIGINT | Total nonprofit revenue |
| `total_assets` | BIGINT | Total nonprofit assets |
| `trending_causes` | JSONB | **Array of trending policy causes** |
| `last_updated` | TIMESTAMP | Last update timestamp |

### Trending Causes JSON Structure

```json
[
  {
    "causes": [
      {
        "code": "COFOG-01",
        "rank": 1,
        "cause": "Governance and Administrative Policy",
        "topics": 9,
        "most_recent": "2026-04-20",
        "decision_count": 9,
        "sample_headlines": [
          "Council approves appointment of new City Clerk",
          "Previous meeting minutes approved",
          "Meeting called to order"
        ]
      },
      {
        "code": "COFOG-04",
        "rank": 2,
        "cause": "Infrastructure and Capital Projects",
        "topics": 4,
        "most_recent": "2026-04-21",
        "decision_count": 4,
        "sample_headlines": [
          "Council discusses City Hall renovation project.",
          "Council Reviews City Hall Renovation Options"
        ]
      }
    ]
  }
]
```

## API Usage

Query trending causes from the production database:

```python
# In FastAPI endpoint
from api.database import get_db_connection

conn = get_db_connection()
cursor = conn.cursor()

# Get trending causes for a state
cursor.execute("""
    SELECT trending_causes 
    FROM stats_aggregates 
    WHERE level = 'state' AND state_code = %s
""", ('AL',))

causes = cursor.fetchone()[0]  # Returns JSONB as Python dict
```

## dbt Profile Configuration

The `~/.dbt/profiles.yml` file defines three targets:

- **`dev`**: Default target, uses `open_navigator` database
- **`bronze`**: Uses `open_navigator_bronze` for stats pipeline
- **`prod`**: Neon cloud database (requires env vars)

To switch targets:
```bash
dbt run --target bronze  # For stats pipeline
dbt run --target dev     # For other models
```

## Common Tasks

### Rebuild all stats from scratch

```bash
# 1. Run dbt models
cd dbt_project && dbt run --target bronze --select stg_bronze_decisions+

# 2. Export to production
cd .. && python scripts/dbt/export_stats_to_open_navigator.py

# 3. Verify
psql -h localhost -p 5433 -U postgres -d open_navigator -c \
  "SELECT level, jsonb_array_length(trending_causes) FROM stats_aggregates WHERE trending_causes IS NOT NULL;"
```

### Add new dbt models

1. Create model in `dbt_project/models/`
2. Update `_staging.yml`, `_intermediate.yml`, or `_marts.yml`
3. Run: `dbt run --target bronze --select your_model+`
4. Export if needed: `python scripts/dbt/export_stats_to_open_navigator.py`

## Troubleshooting

### "cross-database references are not implemented"

This error occurs when dbt tries to query across databases. Make sure you're using the correct target:

```bash
dbt run --target bronze  # NOT --target dev
```

### "relation does not exist"

The staging model needs to be built before intermediate/mart models:

```bash
dbt run --target bronze --select stg_bronze_decisions+  # The + builds downstream
```

### "can't adapt type 'dict'"

The export script handles JSONB serialization automatically. If you see this error, check that you're using `psycopg2.extras.Json()` wrapper.

## Files in this Directory

- `export_stats_to_open_navigator.py` - Sync script (bronze → production)
- `README.md` - This file

## Related Documentation

- [dbt Project README](../../dbt_project/README.md)
- [Trending Causes Guide](../../dbt_project/README_TRENDING_CAUSES.md)
- [Neon Deployment](../deployment/neon/README.md)
