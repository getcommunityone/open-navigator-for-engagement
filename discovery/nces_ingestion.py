"""
NCES School District Data Ingestion

Downloads and processes National Center for Education Statistics (NCES)
Common Core of Data (CCD) to get comprehensive school district information.

Data Source: https://nces.ed.gov/ccd/
Primary Dataset: Local Education Agency (School District) Universe Survey

This provides:
- School district names and locations
- Physical addresses and phone numbers
- NCES IDs for standardized identification
- Enrollment and demographic data
"""
import asyncio
import csv
import zipfile
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path

try:
    import httpx
except ImportError:
    httpx = None

from loguru import logger
from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.types import StructType, StructField, StringType, IntegerType
from pyspark.sql.functions import col, trim, lower, regexp_replace
from config import settings


class NCESSchoolDistrictIngestion:
    """Ingest NCES Common Core of Data for school districts."""
    
    # NCES provides CSV/Text files for the Local Education Agency Universe Survey
    # Updated annually - using 2023-24 school year data
    NCES_CCD_URL = "https://nces.ed.gov/ccd/data/zip/ccd_lea_052_2324_l_1a_083023.csv"
    
    # Alternative: Directory of school districts with contact info
    NCES_DIRECTORY_URL = "https://nces.ed.gov/ccd/data/zip/ccd_lea_directory_2324.csv"
    
    def __init__(self, spark: Optional[SparkSession] = None):
        """Initialize ingestion with Spark session."""
        self.spark = spark or SparkSession.builder.appName("NCESIngestion").getOrCreate()
        self.cache_dir = Path("data/cache/nces")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    async def download_nces_data(self) -> Path:
        """
        Download NCES school district data.
        
        Returns:
            Path to downloaded CSV file
        """
        cache_file = self.cache_dir / "nces_school_districts.csv"
        
        # Cache for 30 days (NCES data updates annually)
        if cache_file.exists():
            age_days = (datetime.now() - datetime.fromtimestamp(cache_file.stat().st_mtime)).days
            if age_days < 30:
                logger.info(f"Using cached NCES data (age: {age_days} days)")
                return cache_file
        
        logger.info("Downloading NCES school district data...")
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                # Try primary directory file first (has website URLs)
                response = await client.get(self.NCES_DIRECTORY_URL)
                response.raise_for_status()
                
                cache_file.write_bytes(response.content)
                logger.info(f"Downloaded NCES data to {cache_file}")
                return cache_file
                
            except Exception as e:
                logger.error(f"Failed to download NCES directory: {e}")
                # Fall back to universe survey file
                try:
                    response = await client.get(self.NCES_CCD_URL)
                    response.raise_for_status()
                    cache_file.write_bytes(response.content)
                    logger.info(f"Downloaded NCES universe data to {cache_file}")
                    return cache_file
                except Exception as e2:
                    logger.error(f"Failed to download NCES universe data: {e2}")
                    raise
    
    def parse_csv_to_dataframe(self, csv_path: Path) -> DataFrame:
        """
        Parse NCES CSV into standardized DataFrame.
        
        Args:
            csv_path: Path to NCES CSV file
            
        Returns:
            Spark DataFrame with standardized schema
        """
        # Define schema for NCES data
        schema = StructType([
            StructField("nces_id", StringType(), False),
            StructField("district_name", StringType(), False),
            StructField("state", StringType(), False),
            StructField("state_fips", StringType(), True),
            StructField("county_name", StringType(), True),
            StructField("street_address", StringType(), True),
            StructField("city", StringType(), True),
            StructField("zip", StringType(), True),
            StructField("phone", StringType(), True),
            StructField("website", StringType(), True),  # Some NCES files include this!
            StructField("enrollment", IntegerType(), True),
            StructField("district_type", StringType(), True),  # Regular, Charter, etc.
        ])
        
        # Read raw CSV
        raw_df = self.spark.read.csv(
            str(csv_path),
            header=True,
            inferSchema=False
        )
        
        # Map NCES column names to our schema
        # NCES uses: LEAID, LEA_NAME, STATE_ABBR, LSTREET1, LCITY, LZIP, PHONE, WEBSITE
        mapped_df = raw_df.select(
            col("LEAID").alias("nces_id"),
            col("LEA_NAME").alias("district_name"),
            col("STATE_ABBR").alias("state"),
            col("ST_FIPS").alias("state_fips"),
            col("COUNTY_NAME").alias("county_name"),
            col("LSTREET1").alias("street_address"),
            col("LCITY").alias("city"),
            col("LZIP").alias("zip"),
            col("PHONE").alias("phone"),
            col("WEBSITE").alias("website") if "WEBSITE" in raw_df.columns else col("LEAID").cast("string").alias("website"),  # Placeholder if no website column
            col("ENROLLMENT").cast("int").alias("enrollment") if "ENROLLMENT" in raw_df.columns else col("LEAID").cast("int").alias("enrollment"),
            col("TYPE").alias("district_type") if "TYPE" in raw_df.columns else col("LEAID").cast("string").alias("district_type"),
        )
        
        # Clean and standardize
        cleaned_df = mapped_df \
            .withColumn("district_name", trim(col("district_name"))) \
            .withColumn("state", trim(col("state"))) \
            .withColumn("website", trim(lower(col("website")))) \
            .withColumn("website", regexp_replace(col("website"), r"^https?://", "")) \
            .withColumn("website", regexp_replace(col("website"), r"/$", "")) \
            .filter(col("district_name").isNotNull())
        
        logger.info(f"Parsed {cleaned_df.count()} school districts from NCES data")
        
        return cleaned_df
    
    def write_to_bronze_layer(self, df: DataFrame) -> None:
        """
        Write NCES data to Bronze layer in Delta Lake.
        
        Args:
            df: NCES school district DataFrame
        """
        output_path = f"{settings.delta_lake_path}/bronze/nces_school_districts"
        
        df.write \
            .format("delta") \
            .mode("overwrite") \
            .partitionBy("state") \
            .option("overwriteSchema", "true") \
            .save(output_path)
        
        logger.info(f"Wrote NCES data to {output_path}")
    
    async def ingest_school_districts(self) -> DataFrame:
        """
        Complete ingestion pipeline for NCES school district data.
        
        Returns:
            DataFrame with school district information
        """
        # Download data
        csv_path = await self.download_nces_data()
        
        # Parse to DataFrame
        df = self.parse_csv_to_dataframe(csv_path)
        
        # Write to Bronze layer
        self.write_to_bronze_layer(df)
        
        return df


async def main():
    """Test NCES ingestion."""
    ingestion = NCESSchoolDistrictIngestion()
    df = await ingestion.ingest_school_districts()
    
    print("\n📊 NCES School District Sample:")
    df.show(20, truncate=False)
    
    print("\n📈 Statistics by State:")
    df.groupBy("state").count().orderBy(col("count").desc()).show(10)


if __name__ == "__main__":
    asyncio.run(main())
