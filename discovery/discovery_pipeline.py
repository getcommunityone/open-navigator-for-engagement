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

from discovery.census_ingestion import CensusGovernmentIngestion
from discovery.gsa_domains import GSADomainList
from discovery.url_discovery_agent import URLDiscoveryAgent, JurisdictionURL


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
        self.census.write_to_bronze_layer(census_dfs)
        
        # Step 2: GSA domains
        logger.info("\n[2/2] Downloading GSA .gov domain list...")
        gsa_csv = await self.gsa.download_domain_list()
        gsa_df = self.gsa.parse_domains(gsa_csv)
        self.gsa.write_to_bronze_layer(gsa_df)
        
        logger.success("✓ Bronze layer ingestion complete")
    
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
        
        # Load unified jurisdiction list
        bronze_path = f"{settings.delta_lake_path}/bronze/jurisdictions/unified"
        jurisdictions_df = self.spark.read.format("delta").load(bronze_path)
        
        # Priority: Focus on larger jurisdictions first
        # (Cities > 10k population, all counties, all school districts)
        jurisdictions_df = jurisdictions_df.filter(
            (col("jurisdiction_type") == "counties") |
            (col("jurisdiction_type") == "school_districts") |
            ((col("jurisdiction_type") == "municipalities") & (col("population") > 10000))
        )
        
        if limit:
            jurisdictions_df = jurisdictions_df.limit(limit)
        
        total_count = jurisdictions_df.count()
        logger.info(f"Discovering URLs for {total_count:,} jurisdictions...")
        
        # Load GSA domains for validation
        gsa_path = f"{settings.delta_lake_path}/bronze/gov_domains"
        gsa_df = self.spark.read.format("delta").load(gsa_path)
        gsa_rows = gsa_df.collect()
        
        # Extract domain set and full data
        gsa_domains = set(row["Domain Name"] for row in gsa_rows)
        gsa_domain_data = [row.asDict() for row in gsa_rows]
        
        logger.info(f"Loaded {len(gsa_domains):,} .gov domains for validation")
        
        # Initialize discovery agent with full domain data for matching
        agent = URLDiscoveryAgent(gsa_domains, gsa_domain_data)
        
        # Process in batches for efficiency
        batch_size = 10
        discovered_urls = []
        
        jurisdictions = jurisdictions_df.collect()
        
        for i in range(0, len(jurisdictions), batch_size):
            batch = jurisdictions[i:i + batch_size]
            
            # Discover in parallel
            tasks = [
                agent.discover_jurisdiction(
                    row["jurisdiction_id"],
                    row["jurisdiction_name"],
                    row["state_name"],
                    row["jurisdiction_type"]
                )
                for row in batch
            ]
            
            results = await asyncio.gather(*tasks)
            discovered_urls.extend(results)
            
            logger.info(f"Progress: {min(i + batch_size, len(jurisdictions))}/{len(jurisdictions)}")
        
        await agent.close()
        
        # Convert to DataFrame
        from pyspark.sql import Row
        
        rows = [
            Row(
                jurisdiction_id=url.jurisdiction_id,
                jurisdiction_name=url.jurisdiction_name,
                state=url.state,
                homepage_url=url.homepage_url,
                minutes_url=url.minutes_url,
                cms_platform=url.cms_platform,
                is_gov_domain=url.is_gov_domain,
                discovery_method=url.discovery_method,
                confidence_score=url.confidence_score,
                last_verified=url.last_verified.isoformat() if url.last_verified else None
            )
            for url in discovered_urls
        ]
        
        discovered_df = self.spark.createDataFrame(rows)
        
        # Write to Silver layer
        silver_path = f"{settings.delta_lake_path}/silver/discovered_urls"
        discovered_df.write \
            .format("delta") \
            .mode("overwrite") \
            .partitionBy("state") \
            .save(silver_path)
        
        # Statistics
        total = discovered_df.count()
        with_homepage = discovered_df.filter(col("homepage_url").isNotNull()).count()
        with_minutes = discovered_df.filter(col("minutes_url").isNotNull()).count()
        gov_domains = discovered_df.filter(col("is_gov_domain") == True).count()
        avg_confidence = discovered_df.select("confidence_score").rdd.map(lambda r: r[0]).mean()
        
        logger.success(f"✓ URL Discovery complete:")
        logger.info(f"  Total jurisdictions: {total:,}")
        logger.info(f"  Homepages found: {with_homepage:,} ({with_homepage/total*100:.1f}%)")
        logger.info(f"  Minutes URLs found: {with_minutes:,} ({with_minutes/total*100:.1f}%)")
        logger.info(f"  Validated .gov domains: {gov_domains:,} ({gov_domains/total*100:.1f}%)")
        
        return {
            "attempted": total,
            "successful": with_homepage,
            "homepages": with_homepage,
            "minutes_urls": with_minutes,
            "gov_domains": gov_domains,
            "avg_confidence": avg_confidence
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
        
        # Load discovered URLs
        silver_path = f"{settings.delta_lake_path}/silver/discovered_urls"
        urls_df = self.spark.read.format("delta").load(silver_path)
        
        # Join with jurisdiction details
        bronze_path = f"{settings.delta_lake_path}/bronze/jurisdictions/unified"
        jurisdictions_df = self.spark.read.format("delta").load(bronze_path)
        
        # Create scraping targets
        targets_df = urls_df \
            .join(jurisdictions_df, "jurisdiction_id", "left") \
            .filter(col("minutes_url").isNotNull()) \
            .filter(col("confidence_score") > 0.6) \
            .select(
                col("jurisdiction_id"),
                col("jurisdiction_name"),
                col("jurisdiction_type"),
                col("state"),
                col("county_name"),
                col("population"),
                col("homepage_url"),
                col("minutes_url"),
                col("cms_platform"),
                col("is_gov_domain"),
                col("confidence_score"),
                lit("pending").alias("scraping_status"),
                lit(None).alias("last_scraped"),
                lit(0).alias("documents_found"),
                lit(datetime.now().isoformat()).alias("created_at")
            )
        
        # Prioritization score
        targets_df = targets_df.withColumn(
            "priority_score",
            when(col("is_gov_domain"), 100).otherwise(50) +
            when(col("cms_platform").isNotNull(), 50).otherwise(0) +
            (col("confidence_score") * 100).cast("int")
        )
        
        # Write to Gold layer
        gold_path = f"{settings.delta_lake_path}/gold/scraping_targets"
        targets_df.write \
            .format("delta") \
            .mode("overwrite") \
            .partitionBy("jurisdiction_type", "state") \
            .save(gold_path)
        
        # Statistics by type
        logger.success("✓ Scraping targets created:")
        
        high_priority = targets_df.filter(col("priority_score") > 150).count()
        medium_priority = targets_df.filter((col("priority_score") >= 100) & (col("priority_score") <= 150)).count()
        low_priority = targets_df.filter(col("priority_score") < 100).count()
        
        for jtype in ["counties", "municipalities", "school_districts", "special_districts"]:
            count = targets_df.filter(col("jurisdiction_type") == jtype).count()
            if count > 0:
                logger.info(f"  {jtype}: {count:,} targets")
        
        total = targets_df.count()
        logger.info(f"\n  TOTAL: {total:,} ready for scraping")
        logger.info(f"  High priority (>150): {high_priority:,}")
        logger.info(f"  Medium priority (100-150): {medium_priority:,}")
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
                "bronze_records": bronze_stats["total_records"],
                "urls_discovered": discovery_stats["successful"],
                "scraping_targets": gold_stats["targets_created"],
                "elapsed_seconds": elapsed
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
