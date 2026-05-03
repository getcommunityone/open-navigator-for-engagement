# Discovery Scripts

Scripts for discovering government data sources across U.S. jurisdictions.

## Comprehensive Discovery Pipeline

**Script:** `comprehensive_discovery_pipeline.py`

Automates discovery of data sources for all U.S. cities and counties (22,000+ jurisdictions):

- Government websites
- YouTube channels (with statistics)
- Vimeo channels
- Meeting platforms (Legistar, SuiteOne, Granicus, etc.)
- Agenda portals and document systems
- Social media accounts
- Meeting schedules and archives

### Usage

**Run for all jurisdictions (incremental mode):**
```bash
python scripts/discovery/comprehensive_discovery_pipeline.py --all
```

**Run for specific state:**
```bash
python scripts/discovery/comprehensive_discovery_pipeline.py --state AL
```

**Run for top N cities by population:**
```bash
python scripts/discovery/comprehensive_discovery_pipeline.py --top 100
```

**Disable incremental mode (rediscover all):**
```bash
python scripts/discovery/comprehensive_discovery_pipeline.py --all --no-incremental
```

**Change refresh threshold (default 90 days):**
```bash
python scripts/discovery/comprehensive_discovery_pipeline.py --all --refresh-days 30
```

### Incremental Mode

By default, the script runs in **incremental mode**:
- Skips jurisdictions already discovered
- Only re-processes jurisdictions with stale data (older than 90 days by default)
- Significantly reduces API costs and processing time
- Use `--no-incremental` to force rediscovery of all jurisdictions

### Options

- `--state` - Filter to specific state (e.g., AL, CA, TX)
- `--top N` - Limit to top N jurisdictions by population
- `--all` - Process all jurisdictions (warning: 20,000+)
- `--youtube-api-key` - YouTube Data API v3 key for accurate statistics
- `--max-concurrent` - Maximum concurrent requests (default: 10)
- `--no-incremental` - Disable incremental mode (rediscover all)
- `--refresh-days` - Days before discovery is considered stale (default: 90)

### Output

Discovery results are saved to:
- `data/gold/discovered_urls.parquet` - All discovered URLs
- `data/gold/youtube_channels.parquet` - YouTube channel data
- `data/gold/social_media.parquet` - Social media accounts

## Other Discovery Tools

### URL Discovery Agent
**Script:** `url_discovery_agent.py`

Agent-based URL discovery using web search and scraping.

### Platform Detector
**Script:** `platform_detector.py`

Detects meeting platforms (Legistar, Granicus, etc.) from URLs.

### Batch Processor
**Script:** `batch_processor.py`

Batch processing for large-scale jurisdiction discovery operations.

### External URL Datasets
**Script:** `external_url_datasets.py`

Imports URLs from external curated datasets (City Scrapers, LocalView, etc.).

### Curated Sources
**Script:** `curated_sources.py`

Manages manually curated high-quality data sources.
