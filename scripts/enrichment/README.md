# Enrichment Scripts

Scripts for enriching nonprofit data with additional metadata from various sources.

## 990 Forms Processing

### batch_download_990s.py
Downloads IRS 990 forms in bulk for offline processing.

### extract_990_zips.sh
Extracts downloaded 990 ZIP files into organized directories.

### build_990_local_index.py
Builds a searchable index of downloaded 990 forms.

## Nonprofit Enrichment

### enrich_nonprofits_async.py
**Main enrichment script** - enriches nonprofits asynchronously from multiple sources.

**Usage:**
```bash
python scripts/enrichment/enrich_nonprofits_async.py
```

### Source-Specific Enrichment

- `enrich_nonprofits_propublica.py` - ProPublica Nonprofit Explorer
- `enrich_nonprofits_everyorg.py` - Every.org API
- `enrich_nonprofits_form990.py` - IRS Form 990 data
- `enrich_nonprofits_bigquery.py` - Google BigQuery IRS data
- `enrich_nonprofits_gt990.py` - GT990 API
- `enrich_nonprofits_logodev.py` - Logo enrichment

### Batch Processing

- `auto_enrich_nonprofits.sh` - Automated enrichment pipeline
- `enrich_all_states_local.sh` - State-by-state enrichment
- `enrich_nonprofits_no_auth.sh` - Enrichment without API authentication

## Utilities

- `cleanup_nonprofit_files.py` - Clean up temporary enrichment files
- `discover_tuscaloosa_nonprofits.py` - Example discovery pipeline
- `run_tuscaloosa_pipeline.sh` - Full pipeline for Tuscaloosa, AL
