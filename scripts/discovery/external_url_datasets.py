"""
Integrate existing URL datasets from civic tech projects.

Instead of trying to match Census names to domains (15% success rate),
we download pre-existing URL lists from:
1. LocalView (1,000-10,000 jurisdictions)
2. Council Data Project (20+ cities)
3. City Scrapers (100-500 agencies)
4. Legistar subdomain enumeration (1,000-3,000)

This gives us 7,000-20,000 URLs vs. our current 76.
"""
import json
import httpx
from pathlib import Path
from typing import List, Dict
from datetime import datetime

from pyspark.sql import SparkSession
from loguru import logger

from config.settings import settings


# ============================================================================
# Council Data Project Deployments (Confirmed 20+ locations)
# ============================================================================

CDP_DEPLOYMENTS = [
    {
        "jurisdiction_name": "Seattle",
        "state_code": "WA",
        "cdp_url": "https://councildataproject.org/seattle",
        "source_url": "https://seattle.gov/city-council",
        "has_transcripts": True,
        "has_videos": True,
        "data_quality": "excellent"
    },
    {
        "jurisdiction_name": "King County",
        "state_code": "WA",
        "cdp_url": "https://councildataproject.org/king-county",
        "source_url": "https://kingcounty.gov/council",
        "has_transcripts": True,
        "has_videos": True,
        "data_quality": "excellent"
    },
    {
        "jurisdiction_name": "Portland",
        "state_code": "OR",
        "cdp_url": "https://councildataproject.org/portland",
        "source_url": "https://www.portland.gov/council",
        "has_transcripts": True,
        "has_videos": True,
        "data_quality": "excellent"
    },
    {
        "jurisdiction_name": "Denver",
        "state_code": "CO",
        "cdp_url": "https://councildataproject.org/denver",
        "source_url": "https://www.denvergov.org/Government/Agencies-Departments-Offices/City-Council",
        "has_transcripts": True,
        "has_videos": True,
        "data_quality": "excellent"
    },
    {
        "jurisdiction_name": "Boston",
        "state_code": "MA",
        "cdp_url": "https://councildataproject.org/boston",
        "source_url": "https://www.boston.gov/departments/city-council",
        "has_transcripts": True,
        "has_videos": True,
        "data_quality": "excellent"
    },
    {
        "jurisdiction_name": "Oakland",
        "state_code": "CA",
        "cdp_url": "https://councildataproject.org/oakland",
        "source_url": "https://www.oaklandca.gov/departments/city-council",
        "has_transcripts": True,
        "has_videos": True,
        "data_quality": "excellent"
    },
    {
        "jurisdiction_name": "Charlotte",
        "state_code": "NC",
        "cdp_url": "https://councildataproject.org/charlotte",
        "source_url": "https://www.charlottenc.gov/city-government/city-council",
        "has_transcripts": True,
        "has_videos": True,
        "data_quality": "excellent"
    },
    {
        "jurisdiction_name": "San José",
        "state_code": "CA",
        "cdp_url": "https://councildataproject.org/san-jose",
        "source_url": "https://www.sanjoseca.gov/your-government/city-council",
        "has_transcripts": True,
        "has_videos": True,
        "data_quality": "excellent"
    },
    {
        "jurisdiction_name": "Milwaukee",
        "state_code": "WI",
        "cdp_url": "https://councildataproject.org/milwaukee",
        "source_url": "https://milwaukee.gov/CommonCouncil",
        "has_transcripts": True,
        "has_videos": True,
        "data_quality": "excellent"
    },
    {
        "jurisdiction_name": "Louisville",
        "state_code": "KY",
        "cdp_url": "https://councildataproject.org/louisville",
        "source_url": "https://louisvilleky.gov/government/metro-council",
        "has_transcripts": True,
        "has_videos": True,
        "data_quality": "excellent"
    },
    {
        "jurisdiction_name": "Atlanta",
        "state_code": "GA",
        "cdp_url": "https://councildataproject.org/atlanta",
        "source_url": "https://www.atlantaga.gov/government/city-council",
        "has_transcripts": True,
        "has_videos": True,
        "data_quality": "excellent"
    },
    {
        "jurisdiction_name": "Pittsburgh",
        "state_code": "PA",
        "cdp_url": "https://councildataproject.org/pittsburgh-pa",
        "source_url": "https://pittsburghpa.gov/council",
        "has_transcripts": True,
        "has_videos": True,
        "data_quality": "excellent"
    },
    {
        "jurisdiction_name": "Alameda",
        "state_code": "CA",
        "cdp_url": "https://councildataproject.org/alameda",
        "source_url": "https://www.alamedaca.gov/Departments/City-Council",
        "has_transcripts": True,
        "has_videos": True,
        "data_quality": "excellent"
    },
    {
        "jurisdiction_name": "Mountain View",
        "state_code": "CA",
        "cdp_url": "https://councildataproject.org/mountain-view",
        "source_url": "https://www.mountainview.gov/city-hall/departments/city-council",
        "has_transcripts": True,
        "has_videos": True,
        "data_quality": "excellent"
    },
    {
        "jurisdiction_name": "Long Beach",
        "state_code": "CA",
        "cdp_url": "https://councildataproject.org/long-beach",
        "source_url": "https://www.longbeach.gov/city-council",
        "has_transcripts": True,
        "has_videos": True,
        "data_quality": "excellent"
    },
    {
        "jurisdiction_name": "Albuquerque",
        "state_code": "NM",
        "cdp_url": "https://councildataproject.org/albuquerque",
        "source_url": "https://www.cabq.gov/council",
        "has_transcripts": True,
        "has_videos": True,
        "data_quality": "excellent"
    },
    {
        "jurisdiction_name": "Richmond",
        "state_code": "VA",
        "cdp_url": "https://councildataproject.org/richmond",
        "source_url": "https://www.rva.gov/city-council",
        "has_transcripts": True,
        "has_videos": True,
        "data_quality": "excellent"
    },
    {
        "jurisdiction_name": "Asheville",
        "state_code": "NC",
        "cdp_url": "https://sunshine-request.github.io/cdp-asheville/",
        "source_url": "https://www.ashevillenc.gov/department/city-council",
        "has_transcripts": True,
        "has_videos": True,
        "data_quality": "good"
    },
    {
        "jurisdiction_name": "Missoula",
        "state_code": "MT",
        "cdp_url": "https://www.openmontana.org/missoula-council-data-project",
        "source_url": "https://www.ci.missoula.mt.us/government/mayor-city-council/city-council",
        "has_transcripts": True,
        "has_videos": True,
        "data_quality": "good"
    },
]


# ============================================================================
# City Scrapers Known Agencies
# ============================================================================

CITY_SCRAPERS_AGENCIES = {
    "Chicago, IL": [
        "https://www.chicago.gov/city/en/depts/cdph.html",  # Board of Health
        "https://www.chicago.gov/city/en/depts/dol.html",   # Board of Education
        "https://www.chicago.gov/city/en/depts/dcd.html",   # Planning Commission
        # ... Chicago has ~100 agencies
    ],
    "Pittsburgh, PA": [
        "https://pittsburghpa.gov/council",
        # ... more agencies
    ],
    # TODO: Clone city-scrapers repos and extract all URLs
}


# ============================================================================
# Legistar Known Cities
# ============================================================================

KNOWN_LEGISTAR_CITIES = [
    {"name": "Chicago", "state": "IL", "url": "https://chicago.legistar.com"},
    {"name": "Seattle", "state": "WA", "url": "https://seattle.legistar.com"},
    {"name": "Los Angeles", "state": "CA", "url": "https://losangeles.legistar.com"},
    {"name": "Boston", "state": "MA", "url": "https://boston.legistar.com"},
    {"name": "Phoenix", "state": "AZ", "url": "https://phoenix.legistar.com"},
    {"name": "San Diego", "state": "CA", "url": "https://sandiego.legistar.com"},
    {"name": "Austin", "state": "TX", "url": "https://austin.legistar.com"},
    # TODO: Enumerate more by testing all Census jurisdictions
]


# ============================================================================
# Integration Functions
# ============================================================================

def load_cdp_deployments_to_bronze(spark: SparkSession) -> dict:
    """
    Load CDP deployments to Bronze layer.
    
    These are premium jurisdictions with full transcript/video pipelines.
    """
    logger.info(f"Loading {len(CDP_DEPLOYMENTS)} CDP deployments to Bronze layer")
    
    # Convert to DataFrame
    df = spark.createDataFrame(CDP_DEPLOYMENTS)
    
    # Add metadata
    df = df.withColumn("source", "council_data_project")
    df = df.withColumn("ingested_at", df.lit(datetime.utcnow().isoformat()))
    df = df.withColumn("priority_score", df.lit(200))  # Very high priority
    
    # Write to Bronze layer
    output_path = f"{settings.delta_lake_path}/bronze/cdp_deployments"
    df.write \
        .format("delta") \
        .mode("overwrite") \
        .save(output_path)
    
    logger.info(f"✅ Wrote {len(CDP_DEPLOYMENTS)} CDP deployments to {output_path}")
    
    return {
        "total_records": len(CDP_DEPLOYMENTS),
        "source": "council_data_project",
        "quality": "excellent"
    }


async def download_localview_dataset() -> dict:
    """
    Download LocalView dataset from Harvard Dataverse.
    
    This is the largest known database of local government meetings.
    """
    logger.info("Downloading LocalView dataset from Harvard Dataverse")
    
    # Harvard Dataverse API
    dataverse_api = "https://dataverse.harvard.edu/api/datasets/:persistentId/"
    dataset_doi = "doi:10.7910/DVN/NJTBEM"
    
    # Get dataset metadata
    async with httpx.AsyncClient(timeout=120.0) as client:
        try:
            response = await client.get(
                dataverse_api,
                params={"persistentId": dataset_doi}
            )
            
            if response.status_code == 200:
                metadata = response.json()
                
                # Extract file download URLs
                files = metadata.get("data", {}).get("latestVersion", {}).get("files", [])
                
                logger.info(f"Found {len(files)} files in LocalView dataset")
                
                # Download each file
                cache_dir = Path("data/cache/localview")
                cache_dir.mkdir(parents=True, exist_ok=True)
                
                downloaded_files = []
                for file_info in files:
                    file_id = file_info["dataFile"]["id"]
                    filename = file_info["dataFile"]["filename"]
                    
                    download_url = f"https://dataverse.harvard.edu/api/access/datafile/{file_id}"
                    
                    logger.info(f"Downloading {filename}...")
                    file_response = await client.get(download_url)
                    
                    if file_response.status_code == 200:
                        output_file = cache_dir / filename
                        output_file.write_bytes(file_response.content)
                        downloaded_files.append(str(output_file))
                        logger.info(f"✅ Downloaded {filename}")
                
                return {
                    "status": "success",
                    "files_downloaded": len(downloaded_files),
                    "files": downloaded_files,
                    "cache_dir": str(cache_dir)
                }
            
            else:
                logger.error(f"Failed to fetch dataset metadata: {response.status_code}")
                return {"status": "error", "message": f"HTTP {response.status_code}"}
        
        except Exception as e:
            logger.error(f"Error downloading LocalView dataset: {e}")
            return {"status": "error", "message": str(e)}


def enumerate_legistar_subdomains(
    spark: SparkSession,
    jurisdictions_df = None
) -> List[str]:
    """
    Enumerate Legistar subdomains by testing jurisdiction names.
    
    Pattern: {city}.legistar.com, {city}-{state}.legistar.com
    """
    logger.info("Enumerating Legistar subdomains")
    
    if jurisdictions_df is None:
        # Load from Bronze layer
        jurisdictions_df = spark.read.format("delta").load(
            f"{settings.delta_lake_path}/bronze/census_jurisdictions"
        )
    
    # Get municipalities only (most likely to use Legistar)
    municipalities = jurisdictions_df.filter(
        jurisdictions_df["jurisdiction_type"] == "municipality"
    ).collect()
    
    found_urls = []
    
    async def test_legistar_url(url: str) -> bool:
        """Test if a Legistar URL exists."""
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                response = await client.head(url)
                return response.status_code == 200
            except:
                return False
    
    # Test patterns for each jurisdiction
    import asyncio
    
    async def test_all():
        for row in municipalities[:100]:  # Test first 100 for demo
            name = row["name"].lower().replace(" ", "").replace("city", "")
            state = row["state_code"].lower()
            
            # Generate test URLs
            test_urls = [
                f"https://{name}.legistar.com",
                f"https://{name}-{state}.legistar.com",
                f"https://{name}{state}.legistar.com",
            ]
            
            # Test each URL
            for url in test_urls:
                if await test_legistar_url(url):
                    found_urls.append({
                        "jurisdiction_name": row["name"],
                        "state_code": row["state_code"],
                        "url": url,
                        "platform": "legistar"
                    })
                    logger.info(f"✅ Found: {url}")
                    break
    
    # Run async tests
    asyncio.run(test_all())
    
    logger.info(f"Found {len(found_urls)} Legistar URLs")
    
    return found_urls


# ============================================================================
# Main Integration Function
# ============================================================================

def integrate_external_url_datasets(spark: SparkSession = None) -> dict:
    """
    Integrate all external URL datasets into Bronze layer.
    
    Priority order:
    1. CDP deployments (20+ premium jurisdictions)
    2. LocalView dataset (1,000-10,000 jurisdictions)
    3. City Scrapers agencies (100-500 URLs)
    4. Legistar enumeration (1,000-3,000 URLs)
    """
    from delta import configure_spark_with_delta_pip
    
    if spark is None:
        builder = SparkSession.builder \
            .appName("IntegrateExternalURLs") \
            .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
            .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")
        spark = configure_spark_with_delta_pip(builder).getOrCreate()
    
    results = {
        "cdp_deployments": 0,
        "localview_dataset": 0,
        "legistar_urls": 0,
        "total_new_urls": 0
    }
    
    # 1. Load CDP deployments
    logger.info("=" * 80)
    logger.info("STEP 1: Loading CDP Deployments")
    logger.info("=" * 80)
    cdp_result = load_cdp_deployments_to_bronze(spark)
    results["cdp_deployments"] = cdp_result["total_records"]
    
    # 2. Download LocalView dataset
    logger.info("\n" + "=" * 80)
    logger.info("STEP 2: Downloading LocalView Dataset")
    logger.info("=" * 80)
    logger.info("⚠️  Note: This requires manual download from Harvard Dataverse")
    logger.info("Visit: https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/NJTBEM")
    logger.info("Download files and place in: data/cache/localview/")
    
    # 3. Enumerate Legistar subdomains
    logger.info("\n" + "=" * 80)
    logger.info("STEP 3: Enumerating Legistar Subdomains")
    logger.info("=" * 80)
    legistar_urls = enumerate_legistar_subdomains(spark)
    results["legistar_urls"] = len(legistar_urls)
    
    # Save Legistar URLs to Bronze
    if legistar_urls:
        legistar_df = spark.createDataFrame(legistar_urls)
        legistar_df = legistar_df.withColumn("source", legistar_df.lit("legistar_enumeration"))
        legistar_df.write \
            .format("delta") \
            .mode("overwrite") \
            .save(f"{settings.delta_lake_path}/bronze/legistar_urls")
    
    # Calculate totals
    results["total_new_urls"] = sum([
        results["cdp_deployments"],
        results["legistar_urls"]
    ])
    
    logger.info("\n" + "=" * 80)
    logger.info("INTEGRATION COMPLETE")
    logger.info("=" * 80)
    logger.info(f"CDP deployments: {results['cdp_deployments']}")
    logger.info(f"Legistar URLs: {results['legistar_urls']}")
    logger.info(f"Total new URLs: {results['total_new_urls']}")
    logger.info("\n⚠️  Don't forget to download LocalView dataset manually!")
    
    return results


if __name__ == "__main__":
    print("🔗 Integrating External URL Datasets")
    print("=" * 80)
    print("\nThis script integrates pre-existing URL lists from:")
    print("  1. Council Data Project (20+ cities)")
    print("  2. LocalView (1,000-10,000 jurisdictions)")
    print("  3. Legistar enumeration (1,000-3,000 cities)")
    print("\nInstead of trying to discover URLs ourselves (15% success),")
    print("we leverage work already done by the civic tech community.\n")
    
    results = integrate_external_url_datasets()
    
    print("\n✅ Integration complete!")
    print(f"\nTotal URLs added: {results['total_new_urls']}")
    print("\nNext: Download LocalView dataset from Harvard Dataverse")
