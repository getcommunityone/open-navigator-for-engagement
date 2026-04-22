"""
Census Bureau Data Ingestion

Downloads and processes Census of Governments data to create master list
of all U.S. local government jurisdictions.

Data Sources:
- Census Bureau Government Integrated Directory (GID)
- Individual State Descriptions
- FIPS codes for standardized identification
"""
import asyncio
import csv
import io
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path
import httpx
from loguru import logger
from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.types import StructType, StructField, StringType, IntegerType
from config import settings


class CensusGovernmentIngestion:
    """Ingest Census Bureau government entity data."""
    
    # Census Bureau API endpoint
    CENSUS_API_BASE = "https://api.census.gov/data"
    
    # Government Integrated Directory URLs
    GID_URLS = {
        "counties": "https://www2.census.gov/programs-surveys/gus/datasets/2022/county_governments.csv",
        "municipalities": "https://www2.census.gov/programs-surveys/gus/datasets/2022/municipal_governments.csv",
        "townships": "https://www2.census.gov/programs-surveys/gus/datasets/2022/township_governments.csv",
        "school_districts": "https://www2.census.gov/programs-surveys/gus/datasets/2022/school_district_governments.csv",
        "special_districts": "https://www2.census.gov/programs-surveys/gus/datasets/2022/special_district_governments.csv"
    }
    
    def __init__(self, spark: Optional[SparkSession] = None):
        """Initialize ingestion with Spark session."""
        self.spark = spark or SparkSession.builder.appName("CensusIngestion").getOrCreate()
        self.cache_dir = Path("data/cache/census")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    async def download_census_data(self, jurisdiction_type: str) -> Path:
        """
        Download Census government data for a jurisdiction type.
        
        Args:
            jurisdiction_type: One of 'counties', 'municipalities', 'townships', 
                             'school_districts', 'special_districts'
        
        Returns:
            Path to downloaded CSV file
        """
        if jurisdiction_type not in self.GID_URLS:
            raise ValueError(f"Invalid jurisdiction type: {jurisdiction_type}")
        
        url = self.GID_URLS[jurisdiction_type]
        cache_file = self.cache_dir / f"{jurisdiction_type}_{datetime.now().strftime('%Y%m%d')}.csv"
        
        # Use cached file if exists and is recent (< 7 days old)
        if cache_file.exists() and (datetime.now().timestamp() - cache_file.stat().st_mtime) < 604800:
            logger.info(f"Using cached {jurisdiction_type} data from {cache_file}")
            return cache_file
        
        logger.info(f"Downloading {jurisdiction_type} data from Census Bureau...")
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                response = await client.get(url)
                response.raise_for_status()
                
                # Save to cache
                cache_file.write_bytes(response.content)
                logger.success(f"Downloaded {len(response.content)} bytes to {cache_file}")
                
                return cache_file
            
            except httpx.HTTPError as e:
                logger.error(f"Failed to download {jurisdiction_type} data: {e}")
                raise
    
    def parse_csv_to_dataframe(self, csv_path: Path, jurisdiction_type: str) -> DataFrame:
        """
        Parse Census CSV into Spark DataFrame.
        
        Args:
            csv_path: Path to CSV file
            jurisdiction_type: Type of jurisdiction
        
        Returns:
            Spark DataFrame with standardized schema
        """
        logger.info(f"Parsing {csv_path} into DataFrame...")
        
        # Define standardized schema
        schema = StructType([
            StructField("jurisdiction_id", StringType(), False),  # FIPS code
            StructField("jurisdiction_type", StringType(), False),
            StructField("jurisdiction_name", StringType(), False),
            StructField("state_fips", StringType(), False),
            StructField("state_name", StringType(), True),
            StructField("county_fips", StringType(), True),
            StructField("county_name", StringType(), True),
            StructField("population", IntegerType(), True),
            StructField("functional_status", StringType(), True),
            StructField("ingestion_date", StringType(), False)
        ])
        
        # Read CSV with Spark
        df = self.spark.read.csv(
            str(csv_path),
            header=True,
            inferSchema=True
        )
        
        # Add metadata columns
        df = df.withColumn("jurisdiction_type", lit(jurisdiction_type))
        df = df.withColumn("ingestion_date", lit(datetime.now().isoformat()))
        
        # Standardize column names (Census CSVs vary by type)
        # This is a simplified version - real implementation would need mapping logic
        
        logger.success(f"Parsed {df.count()} records from {csv_path}")
        return df
    
    async def ingest_all_jurisdictions(self) -> Dict[str, DataFrame]:
        """
        Download and parse all jurisdiction types.
        
        Returns:
            Dictionary mapping jurisdiction type to DataFrame
        """
        logger.info("Starting full Census data ingestion...")
        
        dataframes = {}
        
        for jurisdiction_type in self.GID_URLS.keys():
            try:
                # Download
                csv_path = await self.download_census_data(jurisdiction_type)
                
                # Parse
                df = self.parse_csv_to_dataframe(csv_path, jurisdiction_type)
                dataframes[jurisdiction_type] = df
                
            except Exception as e:
                logger.error(f"Failed to ingest {jurisdiction_type}: {e}")
                continue
        
        logger.success(f"Ingested {len(dataframes)} jurisdiction types")
        return dataframes
    
    def write_to_bronze_layer(self, dataframes: Dict[str, DataFrame]):
        """
        Write jurisdiction data to Delta Lake Bronze layer.
        
        Args:
            dataframes: Dictionary of jurisdiction DataFrames
        """
        logger.info("Writing jurisdiction data to Bronze layer...")
        
        bronze_path = f"{settings.delta_lake_path}/bronze/jurisdictions"
        
        for jurisdiction_type, df in dataframes.items():
            table_path = f"{bronze_path}/{jurisdiction_type}"
            
            df.write \
                .format("delta") \
                .mode("overwrite") \
                .partitionBy("state_fips") \
                .save(table_path)
            
            logger.success(f"Wrote {jurisdiction_type} to {table_path}")
        
        # Create unified view
        from functools import reduce
        unified_df = reduce(DataFrame.union, dataframes.values())
        
        unified_df.write \
            .format("delta") \
            .mode("overwrite") \
            .partitionBy("jurisdiction_type", "state_fips") \
            .save(f"{bronze_path}/unified")
        
        logger.success(f"Created unified jurisdiction table with {unified_df.count()} total records")


async def main():
    """Run Census ingestion pipeline."""
    ingestion = CensusGovernmentIngestion()
    
    # Download and parse all data
    dataframes = await ingestion.ingest_all_jurisdictions()
    
    # Write to Delta Lake
    ingestion.write_to_bronze_layer(dataframes)
    
    # Print summary statistics
    for jtype, df in dataframes.items():
        count = df.count()
        states = df.select("state_fips").distinct().count()
        print(f"{jtype}: {count:,} jurisdictions across {states} states")


if __name__ == "__main__":
    asyncio.run(main())
