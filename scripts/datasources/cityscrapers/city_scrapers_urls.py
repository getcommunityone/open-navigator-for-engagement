"""
City Scrapers URL Extraction

City Scrapers is the most comprehensive civic tech project for scraping local
government meeting data across the United States.

They maintain validated scrapers for:
- Chicago: ~100 agencies
- Pittsburgh: ~30 agencies
- Detroit: ~40 agencies
- Cleveland: ~30 agencies
- Los Angeles: ~50 agencies

Each spider file contains:
- start_urls: Validated meeting pages
- Scraping logic for Granicus, Legistar, custom platforms
- Video link extraction (often YouTube embeds from Granicus)

Website: https://cityscrapers.org
GitHub: https://github.com/city-scrapers
"""
import sys
import re
import subprocess
import tempfile
from pathlib import Path
from typing import List, Dict
from datetime import datetime
from loguru import logger
from pyspark.sql import SparkSession
from pyspark.sql.functions import lit

# Add project root to Python path for standalone execution
project_root = Path(__file__).parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from config.settings import settings


CITY_SCRAPERS_REPOS = [
    {
        "city": "Chicago",
        "state": "IL",
        "repo": "https://github.com/city-scrapers/city-scrapers",
        "spiders_path": "city_scrapers/spiders",
        "expected_agencies": 100
    },
    {
        "city": "Pittsburgh",
        "state": "PA",
        "repo": "https://github.com/city-scrapers/city-scrapers-pitt",
        "spiders_path": "city_scrapers_pitt/spiders",
        "expected_agencies": 30
    },
    {
        "city": "Detroit",
        "state": "MI",
        "repo": "https://github.com/city-scrapers/city-scrapers-detroit",
        "spiders_path": "city_scrapers_det/spiders",
        "expected_agencies": 40
    },
    {
        "city": "Cleveland",
        "state": "OH",
        "repo": "https://github.com/city-scrapers/city-scrapers-cle",
        "spiders_path": "city_scrapers_cle/spiders",
        "expected_agencies": 30
    },
    {
        "city": "Los Angeles",
        "state": "CA",
        "repo": "https://github.com/city-scrapers/city-scrapers-la",
        "spiders_path": "city_scrapers_la/spiders",
        "expected_agencies": 50
    }
]


def extract_start_urls_from_spider_file(spider_file_content: str) -> List[str]:
    """
    Extract start_urls from a City Scrapers spider file.
    
    Pattern matches:
    - start_urls = ["https://..."]
    - start_urls = ['https://...']
    - start_urls = [
          "https://...",
          "https://..."
      ]
    """
    urls = []
    
    # Match start_urls = [...]
    pattern = r'start_urls\s*=\s*\[(.*?)\]'
    matches = re.findall(pattern, spider_file_content, re.DOTALL)
    
    for match in matches:
        # Extract quoted strings
        url_pattern = r'["\']([^"\']+)["\']'
        found_urls = re.findall(url_pattern, match)
        urls.extend(found_urls)
    
    return urls


def extract_agency_name_from_spider(spider_file_content: str, spider_filename: str) -> str:
    """
    Extract agency name from spider class.
    
    Priority:
    1. agency = "..." attribute
    2. name = "..." attribute
    3. Spider filename (fallback)
    """
    # Try agency attribute
    agency_pattern = r'agency\s*=\s*["\']([^"\']+)["\']'
    agency_match = re.search(agency_pattern, spider_file_content)
    if agency_match:
        return agency_match.group(1)
    
    # Try name attribute
    name_pattern = r'name\s*=\s*["\']([^"\']+)["\']'
    name_match = re.search(name_pattern, spider_file_content)
    if name_match:
        return name_match.group(1).replace('_', ' ').title()
    
    # Fallback to filename
    return spider_filename.replace('_', ' ').replace('.py', '').title()


def clone_and_extract_city_scrapers_urls() -> List[Dict]:
    """
    Clone all City Scrapers repos and extract URLs from spider files.
    
    Returns list of dicts with:
    - url: Meeting page URL
    - city: City name
    - state: State code
    - agency: Agency name (from spider file)
    - source: "city_scrapers"
    - repo: GitHub repo URL
    """
    logger.info("Cloning City Scrapers repositories and extracting URLs")
    
    all_urls = []
    
    with tempfile.TemporaryDirectory() as tmpdir:
        for repo_info in CITY_SCRAPERS_REPOS:
            logger.info(f"\n📦 Processing {repo_info['city']}, {repo_info['state']}...")
            
            # Clone repo
            repo_path = Path(tmpdir) / repo_info['city'].replace(' ', '_')
            
            try:
                subprocess.run([
                    "git", "clone", "--depth", "1", "--quiet",
                    repo_info['repo'], str(repo_path)
                ], check=True, capture_output=True)
                
                logger.info(f"✅ Cloned {repo_info['city']} repo")
            
            except subprocess.CalledProcessError as e:
                logger.error(f"❌ Failed to clone {repo_info['city']} repo: {e}")
                continue
            
            # Find spider files
            spiders_path = repo_path / repo_info['spiders_path']
            
            if not spiders_path.exists():
                logger.warning(f"⚠️  Spider path not found: {spiders_path}")
                continue
            
            spider_files = list(spiders_path.glob("*.py"))
            logger.info(f"Found {len(spider_files)} spider files")
            
            city_urls = []
            
            for spider_file in spider_files:
                # Skip internal files
                if spider_file.name.startswith("_") or spider_file.name == "__init__.py":
                    continue
                
                try:
                    # Read spider file
                    content = spider_file.read_text(encoding='utf-8')
                    
                    # Extract start_urls
                    urls = extract_start_urls_from_spider_file(content)
                    
                    if not urls:
                        continue
                    
                    # Extract agency name
                    agency = extract_agency_name_from_spider(content, spider_file.stem)
                    
                    for url in urls:
                        city_urls.append({
                            "url": url,
                            "city": repo_info['city'],
                            "state": repo_info['state'],
                            "agency": agency,
                            "source": "city_scrapers",
                            "repo": repo_info['repo']
                        })
                
                except Exception as e:
                    logger.warning(f"Failed to parse {spider_file.name}: {e}")
                    continue
            
            logger.info(f"✅ Extracted {len(city_urls)} URLs from {repo_info['city']}")
            all_urls.extend(city_urls)
    
    logger.info(f"\n🎯 TOTAL: Extracted {len(all_urls)} URLs from {len(CITY_SCRAPERS_REPOS)} cities")
    
    return all_urls


def write_to_bronze_layer(
    urls: List[Dict],
    spark: SparkSession
) -> Dict[str, int]:
    """
    Write City Scrapers URLs to Bronze layer.
    
    Creates table: bronze/city_scrapers_urls
    """
    if not urls:
        logger.warning("No URLs to write")
        return {"total_urls": 0}
    
    # Add ingestion timestamp
    for url in urls:
        url['ingested_at'] = datetime.utcnow().isoformat()
    
    # Convert to DataFrame
    df = spark.createDataFrame(urls)
    
    # Write to Delta Lake
    output_path = f"{settings.delta_lake_path}/bronze/city_scrapers_urls"
    
    logger.info(f"Writing City Scrapers URLs to Bronze layer: {output_path}")
    
    df.write \
        .format("delta") \
        .mode("overwrite") \
        .save(output_path)
    
    # Get stats by city
    city_counts = df.groupBy("city").count().collect()
    
    logger.info("\n✅ City Scrapers URLs written to Bronze layer")
    logger.info("\nURLs by city:")
    for row in sorted(city_counts, key=lambda r: r['count'], reverse=True):
        logger.info(f"  • {row['city']}: {row['count']} URLs")
    
    return {
        "total_urls": df.count(),
        "cities": df.select("city").distinct().count(),
        "table": "bronze/city_scrapers_urls"
    }


def ingest_city_scrapers_urls(spark: SparkSession) -> Dict[str, int]:
    """
    Main function: Clone City Scrapers repos and extract URLs.
    
    Returns:
    - total_urls: Number of URLs extracted
    - cities: Number of cities covered
    - table: Bronze layer table name
    """
    logger.info("=" * 60)
    logger.info("CITY SCRAPERS URL EXTRACTION")
    logger.info("=" * 60)
    
    # Extract URLs from GitHub repos
    urls = clone_and_extract_city_scrapers_urls()
    
    if not urls:
        logger.error("❌ No URLs extracted from City Scrapers")
        return {"total_urls": 0, "cities": 0}
    
    # Write to Bronze layer
    stats = write_to_bronze_layer(urls, spark)
    
    logger.info("\n" + "=" * 60)
    logger.info(f"✅ CITY SCRAPERS INGESTION COMPLETE")
    logger.info(f"   • URLs extracted: {stats['total_urls']}")
    logger.info(f"   • Cities covered: {stats['cities']}")
    logger.info(f"   • Table: {stats['table']}")
    logger.info("=" * 60)
    
    return stats


if __name__ == "__main__":
    # Test extraction
    from delta import configure_spark_with_delta_pip
    from pyspark.sql import SparkSession
    
    # Configure Spark with Delta Lake
    builder = SparkSession.builder \
        .appName("CityScrapersURLExtraction") \
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
        .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")
    
    spark = configure_spark_with_delta_pip(builder).getOrCreate()
    
    # Run ingestion
    stats = ingest_city_scrapers_urls(spark)
    
    print(f"\n✅ Extracted {stats['total_urls']} URLs from City Scrapers")
