# City Scrapers Integration

City Scrapers is a civic tech network that maintains validated scrapers for local government meeting data across major U.S. cities.

## Overview

City Scrapers provides:
- **Validated scrapers** for ~250 government agencies across 5+ major cities
- **Start URLs** for meeting pages (Granicus, Legistar, custom platforms)
- **Video link extraction** (often YouTube embeds from Granicus)
- **Community-maintained** with active contributors

### Covered Cities

| City | State | Agencies | Repository |
|------|-------|----------|------------|
| Chicago | IL | ~100 | [city-scrapers/city-scrapers](https://github.com/city-scrapers/city-scrapers) |
| Pittsburgh | PA | ~30 | [city-scrapers/city-scrapers-pitt](https://github.com/city-scrapers/city-scrapers-pitt) |
| Detroit | MI | ~40 | [city-scrapers/city-scrapers-detroit](https://github.com/city-scrapers/city-scrapers-detroit) |
| Cleveland | OH | ~30 | [city-scrapers/city-scrapers-cle](https://github.com/city-scrapers/city-scrapers-cle) |
| Los Angeles | CA | ~50 | [city-scrapers/city-scrapers-la](https://github.com/city-scrapers/city-scrapers-la) |

**Total**: ~250 validated government agency URLs

## Scripts

### city_scrapers_urls.py

**Purpose**: Extract meeting page URLs from all City Scrapers repositories

**What it does**:
1. Clones all City Scrapers GitHub repositories
2. Parses Python spider files to extract `start_urls`
3. Extracts agency names from spider metadata
4. Writes validated URLs to Bronze layer

**Usage**:
```bash
python scripts/datasources/cityscrapers/city_scrapers_urls.py
```

**Output**: 
- Bronze layer table: `bronze/city_scrapers_urls`
- Fields: `url`, `city`, `state`, `agency`, `source`, `repo`, `ingested_at`

**Example output**:
```
Chicago: 98 URLs
Los Angeles: 52 URLs  
Detroit: 43 URLs
Pittsburgh: 31 URLs
Cleveland: 28 URLs

TOTAL: 252 URLs extracted
```

## Data Schema

### Bronze Layer: city_scrapers_urls

```python
{
    "url": "https://chicago.legistar.com/Calendar.aspx",
    "city": "Chicago",
    "state": "IL", 
    "agency": "Board of Education",
    "source": "city_scrapers",
    "repo": "https://github.com/city-scrapers/city-scrapers",
    "ingested_at": "2024-05-03T10:30:00"
}
```

## Value Proposition

### Why Use City Scrapers URLs?

**✅ Advantages:**
- **Validated**: Each URL has been verified by community contributors
- **Maintained**: Active community updates when sites change
- **Agency metadata**: Know which department each URL represents
- **Platform intelligence**: Scrapers show how to parse Granicus, Legistar, etc.
- **Free & Open**: MIT licensed, no API keys needed

**⚠️ Limitations:**
- Only covers 5 cities (vs. 90,000+ jurisdictions we track)
- Requires git clone (not a REST API)
- Spider code in Python (may need translation)

### Integration Strategy

**Use City Scrapers as:**
1. **Validation dataset** - Cross-check our discovered URLs
2. **Seed URLs** - Bootstrap scraping for covered cities  
3. **Platform detection** - Learn which agencies use which platforms
4. **Quality benchmark** - Compare our extraction accuracy

**Combine with:**
- Our URL discovery pipeline (90,000+ jurisdictions)
- Google Civic API (elected officials)
- OpenStates (state legislatures)
- Ballotpedia (comprehensive coverage)

## Use Cases

### 1. Bootstrap Chicago Meeting Scraping

```python
from pyspark.sql import SparkSession

spark = SparkSession.builder.getOrCreate()

# Get Chicago URLs
chicago_urls = spark.read.format("delta") \
    .load("bronze/city_scrapers_urls") \
    .filter("city = 'Chicago'")

# Filter to specific platforms
legistar_urls = chicago_urls.filter(
    chicago_urls.url.contains("legistar.com")
)

print(f"Found {legistar_urls.count()} Chicago Legistar URLs")
legistar_urls.select("agency", "url").show(truncate=False)
```

### 2. Cross-Validate Our Discovered URLs

```python
# Load our discovered URLs
our_urls = spark.read.format("delta").load("bronze/discovered_urls")

# Load City Scrapers URLs  
cs_urls = spark.read.format("delta").load("bronze/city_scrapers_urls")

# Find URLs in City Scrapers but missing from our discovery
missing = cs_urls.join(
    our_urls, 
    cs_urls.url == our_urls.url, 
    "left_anti"
)

print(f"Found {missing.count()} URLs in City Scrapers that we missed")
missing.select("city", "agency", "url").show()
```

### 3. Platform Detection Analysis

```python
from pyspark.sql.functions import when, col

cs_urls = spark.read.format("delta").load("bronze/city_scrapers_urls")

# Detect platforms
with_platform = cs_urls.withColumn(
    "platform",
    when(col("url").contains("legistar"), "Legistar")
    .when(col("url").contains("granicus"), "Granicus")
    .when(col("url").contains("civicplus"), "CivicPlus")
    .otherwise("Custom")
)

# Count by platform
with_platform.groupBy("platform").count() \
    .orderBy("count", ascending=False) \
    .show()
```

## Technical Details

### Spider File Format

City Scrapers uses Scrapy. Each spider file looks like:

```python
class ChiBoardOfEducationSpider(CityScrapersSpider):
    name = "chi_board_of_education"
    agency = "Chicago Board of Education"
    start_urls = [
        "https://www.chicagopsa.org/meetings/"
    ]
    
    def parse(self, response):
        # Scraping logic
        ...
```

**Our extraction targets:**
- `start_urls`: Meeting page URLs (what we want)
- `agency`: Department name (for metadata)
- `name`: Spider identifier (fallback for agency name)

### Why Clone Repos?

City Scrapers doesn't provide a REST API or data dump. The URLs are embedded in Python code, so we must:

1. Clone repos from GitHub
2. Parse Python files with regex
3. Extract `start_urls` arrays
4. Clean and validate URLs

**Performance**: Cloning is fast (~30 seconds for all 5 repos with `--depth 1`)

### Requirements

```bash
# Git (for cloning repos)
sudo apt-get install git

# Python dependencies
pip install pyspark delta-spark loguru
```

## Related Resources

- **Website**: https://cityscrapers.org
- **GitHub**: https://github.com/city-scrapers
- **Documentation**: https://cityscrapers.org/docs/
- **Contribute**: https://cityscrapers.org/docs/contribute/

## Contributing

City Scrapers is community-driven. To add a new city or update scrapers, see their [contribution guide](https://cityscrapers.org/docs/contribute/).

## Next Steps

1. **Run extraction**: `python scripts/datasources/cityscrapers/city_scrapers_urls.py`
2. **Validate URLs**: Compare with our discovered URLs
3. **Enhance discovery**: Use City Scrapers URLs to improve our pipeline
4. **Monitor changes**: Re-run periodically to catch URL updates
