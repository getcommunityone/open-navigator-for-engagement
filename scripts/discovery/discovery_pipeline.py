"""
Complete Jurisdiction Discovery Pipeline

Orchestrates the full discovery workflow:
1. Ingest Census Bureau data (Bronze layer)
2. Download GSA .gov domain list
3. Run URL discovery for all jurisdictions
4. Validate and score results (Silver layer)
5. Create actionable scraping targets (Gold layer)

This implements the Medallion Architecture for jurisdiction discovery.
"""
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
from loguru import logger

try:
    from pyspark.sql import SparkSession
    from pyspark.sql.functions import col, lit, when
    PYSPARK_AVAILABLE = True
except ImportError:
    PYSPARK_AVAILABLE = False
    SparkSession = None

from config import settings

from census_ingestion import CensusGovernmentIngestion
from gsa_domains import GSADomainList
from url_discovery_agent import URLDiscoveryAgent, JurisdictionURL


class DiscoveryPipeline:
    """Orchestrate full jurisdiction discovery pipeline."""
    
    def __init__(self):
        """Initialize pipeline components."""
        # Configure Spark with Delta Lake support
        # For local mode, we need to explicitly add delta-spark JARs
        import delta
        
        builder = SparkSession.builder \
            .appName("JurisdictionDiscovery") \
            .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
            .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")
        
        # Use delta-spark's configure_spark_with_delta_pip to add JARs
        self.spark = delta.configure_spark_with_delta_pip(builder).getOrCreate()
        
        self.census = CensusGovernmentIngestion(self.spark)
        self.gsa = GSADomainList(self.spark)
    
    async def run_bronze_ingestion(self):
        """
        BRONZE LAYER: Ingest raw data from Census and GSA.
        
        Tables created:
        - bronze/jurisdictions/counties
        - bronze/jurisdictions/municipalities
        - bronze/jurisdictions/school_districts
        - bronze/jurisdictions/special_districts
        - bronze/jurisdictions/unified
        - bronze/gov_domains
        """
        logger.info("=" * 60)
        logger.info("BRONZE LAYER: Ingesting raw jurisdiction data")
        logger.info("=" * 60)
        
        # Step 1: Census data
        logger.info("\n[1/2] Downloading Census Bureau data...")
        census_dfs = await self.census.ingest_all_jurisdictions()
        census_result = self.census.write_to_bronze_layer(census_dfs)
        
        # Step 2: GSA domains
        logger.info("\n[2/2] Downloading GSA .gov domain list...")
        gsa_csv = await self.gsa.download_domain_list()
        gsa_df = self.gsa.parse_domains(gsa_csv)
        gsa_result = self.gsa.write_to_bronze_layer(gsa_df)
        
        logger.success("✓ Bronze layer ingestion complete")
        
        return {
            "status": "complete",
            "total_records": census_result.get("total_records", 0) + gsa_result.get("total_records", 0),
            "census_records": census_result.get("total_records", 0),
            "gsa_domains": gsa_result.get("total_records", 0)
        }
    
    async def run_url_discovery(self, limit: Optional[int] = None):
        """
        SILVER LAYER: Discover URLs for jurisdictions.
        
        Args:
            limit: Optional limit for testing (e.g., 100 jurisdictions)
        
        Table created:
        - silver/discovered_urls
        """
        logger.info("=" * 60)
        logger.info("SILVER LAYER: URL Discovery")
        logger.info("=" * 60)
        
        # Load municipalities table (has most complete data)
        # Note: Census 2022 data is aggregated counts, not individual listings
        # For production, we'd need a different data source for individual jurisdictions
        bronze_path = f"{settings.delta_lake_path}/bronze/jurisdictions/municipalities"
        
        try:
            jurisdictions_df = self.spark.read.format("delta").load(bronze_path)
            logger.info(f"Loaded {jurisdictions_df.count()} jurisdiction records from Census data")
        except Exception as e:
            logger.error(f"Failed to load jurisdiction data: {e}")
            logger.warning("Skipping URL discovery - no jurisdiction data available")
            return {"urls_discovered": 0, "validated_domains": 0}
        
        # Apply limit if specified
        if limit:
            jurisdictions_df = jurisdictions_df.limit(limit)
        
        total_count = jurisdictions_df.count()
        logger.info(f"Processing {total_count:,} jurisdiction records...")
        
        # Load GSA domains for validation
        gsa_path = f"{settings.delta_lake_path}/bronze/gov_domains"
        gsa_df = self.spark.read.format("delta").load(gsa_path)
        gsa_rows = gsa_df.collect()
        
        # Extract domain set and full data (column names have underscores after cleaning)
        gsa_domains = set(row["Domain_name"] if "Domain_name" in row.asDict() else row.asDict().get(list(row.asDict().keys())[0], "") for row in gsa_rows)
        gsa_domain_data = [row.asDict() for row in gsa_rows]
        
        logger.info(f"Loaded {len(gsa_domains):,} .gov domains for validation")
        
        # Construct search patterns from jurisdiction names
        # GSA domains typically follow patterns like:
        # - "citystatecode.gov" (e.g., "aberdeenmd.gov" for Aberdeen, MD)
        # - "city-state.gov" (e.g., "abingdon-va.gov")
        # - "countystate.gov" (e.g., "alamedacountyca.gov")
        # - "cityname.gov" (e.g., "abilenetx.gov")
        
        discovered_urls = []
        
        for row in jurisdictions_df.take(limit if limit else total_count):
            row_dict = row.asDict()
            name = row_dict.get("name", "")
            state_code = row_dict.get("state_code", "")
            fips = row_dict.get("fips_code", "")
            
            if not name:
                continue
            
            # Strip common jurisdiction type suffixes
            clean_name = name
            for suffix in [" city", " town", " village", " borough", " CDP", " County", " municipality",
                          " City", " Town", " Village", " Borough", " COUNTY"]:
                clean_name = clean_name.replace(suffix, "")
            
            # Normalize to lowercase and remove special characters
            base_name = clean_name.lower().strip()
            # Remove all spaces, periods, commas, apostrophes for compact form
            compact_name = base_name.replace(" ", "").replace(".", "").replace(",", "").replace("'", "")
            # Version with hyphens instead of spaces
            hyphenated_name = base_name.replace(" ", "-").replace(".", "").replace(",", "").replace("'", "")
            
            state_lower = state_code.lower()
            
            # Try multiple domain patterns (most common first)
            candidate_domains = [
                f"{compact_name}{state_lower}.gov",           # aberdeenmd.gov
                f"{compact_name}-{state_lower}.gov",          # abingdon-va.gov
                f"{state_lower}{compact_name}.gov",           # mdaberdeen.gov
                f"{hyphenated_name}{state_lower}.gov",        # multi-word-cityal.gov
                f"{hyphenated_name}-{state_lower}.gov",       # multi-word-city-al.gov
                f"{compact_name}.gov",                        # abilene.gov
                f"{hyphenated_name}.gov",                     # multi-word.gov
                f"cityof{compact_name}.gov",                  # cityofabilene.gov
                f"{compact_name}city.gov",                    # aberdeencity.gov
                f"{compact_name}county.gov",                  # alamedacounty.gov
                f"{compact_name}county{state_lower}.gov",     # alamedacountyca.gov
            ]
            
            # Check if any candidate matches GSA domains
            for domain in candidate_domains:
                if domain in gsa_domains:
                    discovered_urls.append({
                        "jurisdiction_name": name,
                        "state_code": state_code,
                        "fips_code": fips,
                        "url": f"https://{domain}",
                        "domain": domain,
                        "source": "gsa_match",
                        "confidence": "high"
                    })
                    break
        
        logger.info(f"Discovered {len(discovered_urls):,} URLs from GSA domain matching")
        
        # Write discovered URLs to Silver layer
        if discovered_urls:
            from pyspark.sql import Row
            urls_df = self.spark.createDataFrame([Row(**url) for url in discovered_urls])
            silver_path = f"{settings.delta_lake_path}/silver/discovered_urls"
            urls_df.write.format("delta").mode("overwrite").save(silver_path)
            logger.success(f"Wrote {len(discovered_urls):,} discovered URLs to Silver layer")
        
        return {
            "census_records": total_count,
            "gov_domains": len(gsa_domains),
            "discovered_urls": len(discovered_urls)
        }
    
    def create_scraping_targets(self):
        """
        GOLD LAYER: Create actionable scraping targets.
        
        Filters for high-quality targets:
        - Has minutes URL
        - High confidence score (>0.6)
        - Preferably .gov domain
        
        Table created:
        - gold/scraping_targets
        """
        logger.info("=" * 60)
        logger.info("GOLD LAYER: Creating scraping targets")
        logger.info("=" * 60)
        
        # Check if Silver layer exists
        from pathlib import Path
        silver_path = f"{settings.delta_lake_path}/silver/discovered_urls"
        if not Path(silver_path).exists():
            logger.warning("Silver layer (discovered URLs) does not exist")
            logger.info("Skipping Gold layer - requires Silver layer URL data")
            return {"status": "skipped", "reason": "no_silver_layer"}
        
        # Load discovered URLs - these already have jurisdiction details
        urls_df = self.spark.read.format("delta").load(silver_path)
        
        # Create scraping targets from discovered URLs
        # Silver layer already has: jurisdiction_name, state_code, fips_code, url, domain, source, confidence
        targets_df = urls_df \
            .withColumn("scraping_status", lit("pending")) \
            .withColumn("last_scraped", lit(None).cast("timestamp")) \
            .withColumn("documents_found", lit(0)) \
            .withColumn("created_at", lit(datetime.now().isoformat()))
        
        # Prioritization score based on confidence and source
        targets_df = targets_df.withColumn(
            "priority_score",
            when(col("source") == "gsa_match", 100).otherwise(50) +
            when(col("confidence") == "high", 50).otherwise(25)
        )
        
        # Write to Gold layer
        gold_path = f"{settings.delta_lake_path}/gold/scraping_targets"
        targets_df.write \
            .format("delta") \
            .mode("overwrite") \
            .partitionBy("state_code") \
            .save(gold_path)
        
        # Statistics
        logger.success("✓ Scraping targets created:")
        
        total = targets_df.count()
        high_priority = targets_df.filter(col("priority_score") >= 150).count()
        medium_priority = targets_df.filter((col("priority_score") >= 100) & (col("priority_score") < 150)).count()
        low_priority = targets_df.filter(col("priority_score") < 100).count()
        
        logger.info(f"\n  TOTAL: {total:,} ready for scraping")
        logger.info(f"  High priority (≥150): {high_priority:,}")
        logger.info(f"  Medium priority (100-149): {medium_priority:,}")
        logger.info(f"  Low priority (<100): {low_priority:,}")
        
        return {
            "targets_created": total,
            "high_priority": high_priority,
            "medium_priority": medium_priority,
            "low_priority": low_priority
        }
    
    async def run_full_pipeline(self, discovery_limit: Optional[int] = None,
                               state_filter: Optional[str] = None,
                               type_filter: Optional[str] = None):
        """
        Execute complete discovery pipeline.
        
        Args:
            discovery_limit: Limit URL discovery for testing
            state_filter: Filter to single state (e.g., "CA")
            type_filter: Filter to jurisdiction type (e.g., "county")
        
        Returns:
            Dictionary with complete pipeline statistics
        """
        start_time = datetime.now()
        
        logger.info("\n" + "=" * 60)
        logger.info("JURISDICTION DISCOVERY PIPELINE")
        logger.info("=" * 60 + "\n")
        
        try:
            # Bronze Layer
            bronze_stats = await self.run_bronze_ingestion()
            
            # Silver Layer (with optional filters)
            # Note: Filters would need to be added to run_url_discovery method
            discovery_stats = await self.run_url_discovery(limit=discovery_limit)
            
            # Gold Layer
            gold_stats = self.create_scraping_targets()
            
            elapsed = (datetime.now() - start_time).total_seconds()
            logger.success(f"\n{'=' * 60}")
            logger.success(f"PIPELINE COMPLETE in {elapsed:.1f}s")
            logger.success(f"{'=' * 60}\n")
            
            return {
                "bronze_records": bronze_stats.get("total_records", 0),
                "urls_discovered": discovery_stats.get("successful", 0) if discovery_stats else 0,
                "scraping_targets": gold_stats.get("targets_created", 0) if gold_stats else 0,
                "elapsed_seconds": elapsed,
                "bronze_status": bronze_stats.get("status", "complete"),
                "silver_status": discovery_stats.get("status", "skipped") if discovery_stats else "skipped",
                "gold_status": gold_stats.get("status", "skipped") if gold_stats else "skipped"
            }
            
        except Exception as e:
            logger.error(f"Pipeline failed: {e}")
            raise


async def main():
    """Run discovery pipeline."""
    pipeline = DiscoveryPipeline()
    
    # Run with limit for testing (remove limit for production)
    await pipeline.run_full_pipeline(discovery_limit=100)


if __name__ == "__main__":
    asyncio.run(main())
