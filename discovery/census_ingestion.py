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

try:
    from pyspark.sql import SparkSession, DataFrame
    from pyspark.sql.types import StructType, StructField, StringType, IntegerType
    from pyspark.sql.functions import lit
    PYSPARK_AVAILABLE = True
except ImportError:
    PYSPARK_AVAILABLE = False
    SparkSession = None
    DataFrame = None

from config import settings


class CensusGovernmentIngestion:
    """Ingest Census Bureau government entity data."""
    
    # Census Bureau API endpoint
    CENSUS_API_BASE = "https://api.census.gov/data"
    
    # Government Integrated Directory URLs - Updated for 2022 Census of Governments
    # These are the actual available tables from the Census Bureau
    GID_URLS = {
        # Table 2: Local Governments by Type and State: 2022
        "all_governments": "https://www2.census.gov/programs-surveys/gus/tables/2022/cog2022_cg2200org02.zip",
        # Table 5: County Governments by Population-Size Group and State: 2022
        "counties": "https://www2.census.gov/programs-surveys/gus/tables/2022/cog2022_cg2200org05.zip",
        # Table 6: Subcounty General-Purpose Governments (municipalities & townships)
        "municipalities": "https://www2.census.gov/programs-surveys/gus/tables/2022/cog2022_cg2200org06.zip",
        "townships": "https://www2.census.gov/programs-surveys/gus/tables/2022/cog2022_cg2200org06.zip",
        # Table 9: Public School Systems by Type of Organization and State: 2022
        "school_districts": "https://www2.census.gov/programs-surveys/gus/tables/2022/cog2022_cg2200org09.zip",
        # Table 8: Special District Governments by Function and State: 2022
        "special_districts": "https://www2.census.gov/programs-surveys/gus/tables/2022/cog2022_cg2200org08.zip"
    }
    
    # Set to False to use real Census data
    USE_MOCK_DATA = False
    
    def __init__(self, spark: Optional[SparkSession] = None):
        """Initialize ingestion with Spark session."""
        if not PYSPARK_AVAILABLE:
            logger.warning("PySpark not available - using mock data mode")
            self.spark = None
        else:
            self.spark = spark or SparkSession.builder.appName("CensusIngestion").getOrCreate()
        self.cache_dir = Path("data/cache/census")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def _create_mock_data(self, jurisdiction_type: str) -> List[Dict[str, Any]]:
        """
        Create mock jurisdiction data for local testing.
        
        This allows the system to run without downloading Census data.
        """
        logger.info(f"Using mock data for {jurisdiction_type}")
        
        mock_data = {
            "counties": [
                {"name": "Los Angeles County", "state": "CA", "state_code": "06", "fips": "06037", "population": "10014009"},
                {"name": "Cook County", "state": "IL", "state_code": "17", "fips": "17031", "population": "5275541"},
                {"name": "Harris County", "state": "TX", "state_code": "48", "fips": "48201", "population": "4731145"},
                {"name": "Maricopa County", "state": "AZ", "state_code": "04", "fips": "04013", "population": "4485414"},
                {"name": "San Diego County", "state": "CA", "state_code": "06", "fips": "06073", "population": "3286069"},
                {"name": "Orange County", "state": "CA", "state_code": "06", "fips": "06059", "population": "3167809"},
                {"name": "Miami-Dade County", "state": "FL", "state_code": "12", "fips": "12086", "population": "2716940"},
                {"name": "Dallas County", "state": "TX", "state_code": "48", "fips": "48113", "population": "2647787"},
                {"name": "Kings County", "state": "NY", "state_code": "36", "fips": "36047", "population": "2559903"},
                {"name": "Riverside County", "state": "CA", "state_code": "06", "fips": "06065", "population": "2470546"},
            ],
            "municipalities": [
                {"name": "New York City", "state": "NY", "state_code": "36", "fips": "3651000", "population": "8336817"},
                {"name": "Los Angeles", "state": "CA", "state_code": "06", "fips": "0644000", "population": "3979576"},
                {"name": "Chicago", "state": "IL", "state_code": "17", "fips": "1714000", "population": "2746388"},
                {"name": "Houston", "state": "TX", "state_code": "48", "fips": "4835000", "population": "2314157"},
                {"name": "Phoenix", "state": "AZ", "state_code": "04", "fips": "0455000", "population": "1680992"},
                {"name": "Philadelphia", "state": "PA", "state_code": "42", "fips": "4260000", "population": "1584064"},
                {"name": "San Antonio", "state": "TX", "state_code": "48", "fips": "4865000", "population": "1547253"},
                {"name": "San Diego", "state": "CA", "state_code": "06", "fips": "0666000", "population": "1423851"},
                {"name": "Dallas", "state": "TX", "state_code": "48", "fips": "4819000", "population": "1343573"},
                {"name": "San Jose", "state": "CA", "state_code": "06", "fips": "0668000", "population": "1013240"},
            ],
            "townships": [
                {"name": "Bloomfield Township", "state": "MI", "state_code": "26", "fips": "2609320", "population": "44253"},
                {"name": "Canton Township", "state": "MI", "state_code": "26", "fips": "2613960", "population": "98659"},
                {"name": "Wayne Township", "state": "IN", "state_code": "18", "fips": "1883718", "population": "97878"},
            ],
            "school_districts": [
                {"name": "Los Angeles Unified School District", "state": "CA", "state_code": "06", "fips": "0600001", "population": "600000"},
                {"name": "Chicago Public Schools", "state": "IL", "state_code": "17", "fips": "1700002", "population": "340000"},
                {"name": "Miami-Dade County Public Schools", "state": "FL", "state_code": "12", "fips": "1200003", "population": "330000"},
            ],
            "special_districts": [
                {"name": "Metropolitan Water District", "state": "CA", "state_code": "06", "fips": "06SD001", "population": "19000000"},
                {"name": "Port Authority of NY & NJ", "state": "NY", "state_code": "36", "fips": "36SD002", "population": "21000000"},
            ]
        }
        
        return mock_data.get(jurisdiction_type, [])
    
    async def download_census_data(self, jurisdiction_type: str) -> Path:
        """
        Download Census government data for a jurisdiction type.
        
        The Census Bureau provides data as ZIP files containing Excel files.
        This method downloads, extracts, and converts to CSV.
        
        Args:
            jurisdiction_type: One of 'counties', 'municipalities', 'townships', 
                             'school_districts', 'special_districts'
        
        Returns:
            Path to extracted CSV file
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
        logger.info(f"URL: {url}")
        
        async with httpx.AsyncClient(timeout=60.0, follow_redirects=True) as client:
            try:
                response = await client.get(url)
                response.raise_for_status()
                
                # Save ZIP file
                zip_file = self.cache_dir / f"{jurisdiction_type}_temp.zip"
                zip_file.write_bytes(response.content)
                logger.success(f"Downloaded {len(response.content)} bytes")
                
                # Extract ZIP file
                import zipfile
                with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                    # Extract all files
                    extract_dir = self.cache_dir / f"{jurisdiction_type}_extracted"
                    extract_dir.mkdir(exist_ok=True)
                    zip_ref.extractall(extract_dir)
                    
                    # Find Excel file - prioritize *_Data.xlsx files (actual data)
                    # Census ZIPs contain multiple Excel files: Data, Column Descriptions, Aggregate Descriptions
                    excel_files = list(extract_dir.glob("*_Data.xlsx")) + list(extract_dir.glob("*_Data.xls"))
                    if not excel_files:
                        # Fallback to any Excel file
                        excel_files = list(extract_dir.glob("*.xlsx")) + list(extract_dir.glob("*.xls"))
                    if excel_files:
                        excel_file = excel_files[0]
                        logger.info(f"Found Excel file: {excel_file.name}")
                        
                        # Convert Excel to CSV using pandas
                        import pandas as pd
                        df = pd.read_excel(excel_file, engine='openpyxl')
                        df.to_csv(cache_file, index=False)
                        logger.success(f"Converted to CSV: {cache_file}")
                        
                        # Clean up
                        zip_file.unlink()
                        import shutil
                        shutil.rmtree(extract_dir)
                        
                        return cache_file
                    else:
                        raise FileNotFoundError(f"No Excel file found in ZIP for {jurisdiction_type}")
                
            except httpx.HTTPError as e:
                logger.error(f"Failed to download {jurisdiction_type} data: {e}")
                logger.error(f"URL that failed: {url}")
                raise
            except Exception as e:
                logge
                return await self.download_census_data(jurisdiction_type)
    
    def parse_csv_to_dataframe(self, csv_path: Path, jurisdiction_type: str) -> DataFrame:
        """
        Parse Census CSV into Spark DataFrame.
        
        Note: Census 2022 data is aggregated counts, not individual jurisdiction listings.
        This method preserves the original Census schema and adds metadata.
        
        Args:
            csv_path: Path to CSV file
            jurisdiction_type: Type of jurisdiction
        
        Returns:
            Spark DataFrame with Census data + metadata
        """
        logger.info(f"Parsing {csv_path} into DataFrame...")
        
        # Read CSV with Spark (preserve original Census schema)
        df = self.spark.read.csv(
            str(csv_path),
            header=True,
            inferSchema=True
        )
        
        # Clean column names (Delta Lake doesn't allow spaces or special chars)
        for col_name in df.columns:
            clean_name = col_name.replace(" ", "_").replace("(", "").replace(")", "").replace(",", "_")
            if clean_name != col_name:
                df = df.withColumnRenamed(col_name, clean_name)
        
        # Add metadata columns
        df = df.withColumn("jurisdiction_type", lit(jurisdiction_type))
        df = df.withColumn("ingestion_date", lit(datetime.now().isoformat()))
        
        # Census data has columns like: GEO_ID, GEO_TTL, YEAR, AMOUNT, AGG_DESC_TTL, ST (state), etc.
        # We preserve this as-is for Bronze layer (raw data)
        
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
        
        Bronze layer stores raw Census data as-is with minimal transformation.
        
        Args:
            dataframes: Dictionary of jurisdiction DataFrames
        """
        logger.info("Writing jurisdiction data to Bronze layer...")
        
        bronze_path = f"{settings.delta_lake_path}/bronze/jurisdictions"
        
        # Write individual tables
        for jurisdiction_type, df in dataframes.items():
            table_path = f"{bronze_path}/{jurisdiction_type}"
            
            # Write without partitioning for Bronze (raw data)
            df.write \
                .format("delta") \
                .mode("overwrite") \
                .save(table_path)
            
            logger.success(f"Wrote {jurisdiction_type} to {table_path}")
        
        # Note: Skip unified view creation because Census tables have different schemas
        # (Some tables are summaries with 4 columns, others are detailed with 14 columns)
        # Silver layer will standardize these into a common schema
        
        total_records = sum(df.count() for df in dataframes.values())
        logger.success(f"Bronze layer complete: {len(dataframes)} tables with {total_records} total records")
        
        return {
            "total_records": total_records,
            "tables": len(dataframes)
        }


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
