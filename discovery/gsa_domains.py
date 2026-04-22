"""
GSA .gov Domain List Integration

Downloads and processes the GSA's public list of all registered .gov domains
to identify official government websites.

Data Source: https://github.com/cisagov/dotgov-data
"""
import asyncio
from typing import List, Dict, Any, Set
from datetime import datetime
from pathlib import Path
import httpx
import csv
from loguru import logger
from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.types import StructType, StructField, StringType, BooleanType
from config import settings


class GSADomainList:
    """Process GSA .gov domain registry."""
    
    # GSA maintains this on GitHub
    DOMAIN_LIST_URL = "https://raw.githubusercontent.com/cisagov/dotgov-data/main/current-full.csv"
    
    def __init__(self, spark: Optional[SparkSession] = None):
        """Initialize with Spark session."""
        self.spark = spark or SparkSession.builder.appName("GSADomains").getOrCreate()
        self.cache_dir = Path("data/cache/gsa")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    async def download_domain_list(self) -> Path:
        """
        Download latest .gov domain list from GSA.
        
        Returns:
            Path to downloaded CSV file
        """
        cache_file = self.cache_dir / f"dotgov_domains_{datetime.now().strftime('%Y%m%d')}.csv"
        
        # Use cached if recent (< 1 day old)
        if cache_file.exists() and (datetime.now().timestamp() - cache_file.stat().st_mtime) < 86400:
            logger.info(f"Using cached GSA domain list from {cache_file}")
            return cache_file
        
        logger.info("Downloading .gov domain list from GSA...")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(self.DOMAIN_LIST_URL)
            response.raise_for_status()
            
            cache_file.write_bytes(response.content)
            logger.success(f"Downloaded {len(response.content)} bytes")
            
            return cache_file
    
    def parse_domains(self, csv_path: Path) -> DataFrame:
        """
        Parse GSA domain CSV into Spark DataFrame.
        
        CSV columns:
        - Domain name
        - Domain type (Federal, State, County, City, etc.)
        - Agency
        - Organization
        - City
        - State
        - Security contact email
        
        Returns:
            Spark DataFrame with .gov domains
        """
        logger.info(f"Parsing GSA domain list from {csv_path}...")
        
        df = self.spark.read.csv(
            str(csv_path),
            header=True,
            inferSchema=True
        )
        
        # Filter for local government domains
        local_gov_types = ["City", "County", "Township", "Special District", "School District"]
        
        df_local = df.filter(df["Domain Type"].isin(local_gov_types))
        
        logger.success(f"Found {df_local.count():,} local government domains")
        return df_local
    
    def create_domain_index(self, df: DataFrame) -> Dict[str, List[str]]:
        """
        Create fast lookup index of domains by jurisdiction.
        
        Returns:
            Dictionary mapping (state, city/county) to list of domains
        """
        logger.info("Creating domain lookup index...")
        
        index = {}
        
        for row in df.collect():
            state = row["State"]
            org = row["Organization"] or row["City"]
            domain = row["Domain Name"]
            
            if state and org:
                key = f"{state}_{org}".lower().replace(" ", "_")
                if key not in index:
                    index[key] = []
                index[key].append(domain)
        
        logger.success(f"Indexed {len(index):,} jurisdiction-domain mappings")
        return index
    
    def write_to_bronze_layer(self, df: DataFrame):
        """
        Write .gov domain list to Delta Lake.
        
        Args:
            df: DataFrame with domain data
        """
        logger.info("Writing .gov domains to Bronze layer...")
        
        bronze_path = f"{settings.delta_lake_path}/bronze/gov_domains"
        
        df.write \
            .format("delta") \
            .mode("overwrite") \
            .partitionBy("Domain Type", "State") \
            .save(bronze_path)
        
        logger.success(f"Wrote domains to {bronze_path}")


async def main():
    """Run GSA domain ingestion."""
    gsa = GSADomainList()
    
    # Download
    csv_path = await gsa.download_domain_list()
    
    # Parse
    df = gsa.parse_domains(csv_path)
    
    # Create index
    index = gsa.create_domain_index(df)
    
    # Write to Delta Lake
    gsa.write_to_bronze_layer(df)
    
    # Print statistics
    print(f"\nGSA .gov Domain Statistics:")
    print(f"  Total local gov domains: {df.count():,}")
    print(f"  Unique states: {df.select('State').distinct().count()}")
    print(f"  Indexed jurisdictions: {len(index):,}")


if __name__ == "__main__":
    asyncio.run(main())
