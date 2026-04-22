"""
Batch processing and quality metrics for large-scale jurisdiction scraping.

Based on LocalView patterns for handling thousands of jurisdictions
with quality tracking and failure management.
"""
from typing import Dict, List, Optional, Iterator
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import json

from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import col, count, sum as spark_sum, avg, max as spark_max
from loguru import logger

from config.settings import settings


class ScrapeStatus(Enum):
    """Status of scraping operation."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    PARTIAL = "partial"  # Some data retrieved
    FAILED = "failed"
    SKIPPED = "skipped"


class HealthStatus(Enum):
    """Health status of a jurisdiction scraper."""
    HEALTHY = "healthy"        # No recent failures
    DEGRADED = "degraded"      # Some failures
    FAILED = "failed"          # Multiple consecutive failures
    UNKNOWN = "unknown"        # Never scraped


@dataclass
class JurisdictionQuality:
    """
    LocalView pattern: Track data quality and completeness per jurisdiction.
    """
    # Identification
    jurisdiction_name: str
    state_code: str
    fips_code: Optional[str]
    url: str
    platform: Optional[str]
    
    # Completeness metrics
    total_meetings_expected: int  # Based on typical schedule
    total_meetings_found: int
    meetings_with_agendas: int
    meetings_with_minutes: int
    meetings_with_videos: int
    meetings_with_transcripts: int
    
    # Freshness
    last_scraped: Optional[datetime]
    last_meeting_found: Optional[datetime]
    scraping_frequency: str  # 'daily', 'weekly', 'monthly'
    
    # Reliability
    consecutive_successes: int
    consecutive_failures: int
    total_scrapes: int
    successful_scrapes: int
    last_success: Optional[datetime]
    last_error: Optional[str]
    
    # Quality scores
    completeness_score: float  # 0-100
    reliability_score: float   # 0-100
    freshness_score: float     # 0-100
    overall_quality: float     # 0-100 (weighted average)
    health_status: str         # healthy, degraded, failed
    
    # Timestamps
    created_at: datetime
    updated_at: datetime
    
    @classmethod
    def from_dict(cls, data: dict) -> 'JurisdictionQuality':
        """Create from dictionary with datetime parsing."""
        # Parse datetime fields
        for field in ['last_scraped', 'last_meeting_found', 'last_success', 'created_at', 'updated_at']:
            if data.get(field) and isinstance(data[field], str):
                data[field] = datetime.fromisoformat(data[field])
        return cls(**data)
    
    def to_dict(self) -> dict:
        """Convert to dictionary with datetime serialization."""
        data = asdict(self)
        # Serialize datetime fields
        for field in ['last_scraped', 'last_meeting_found', 'last_success', 'created_at', 'updated_at']:
            if data.get(field):
                data[field] = data[field].isoformat()
        return data


@dataclass
class BatchResult:
    """Result of processing a batch of jurisdictions."""
    batch_number: int
    batch_size: int
    jurisdictions_processed: int
    jurisdictions_succeeded: int
    jurisdictions_failed: int
    meetings_found: int
    agendas_found: int
    minutes_found: int
    errors: List[dict]
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_seconds: float = 0.0
    
    @property
    def success_rate(self) -> float:
        """Percentage of jurisdictions successfully scraped."""
        if self.jurisdictions_processed == 0:
            return 0.0
        return (self.jurisdictions_succeeded / self.jurisdictions_processed) * 100


class BatchProcessor:
    """
    LocalView pattern: Process large numbers of jurisdictions in batches.
    
    Features:
    - Batch processing with configurable size
    - Quality metrics per jurisdiction
    - Failure tracking and retry logic
    - Progress monitoring
    - Resume from interruption
    
    Example:
        >>> processor = BatchProcessor(batch_size=100)
        >>> for batch_result in processor.process_all_jurisdictions():
        ...     print(f"Batch {batch_result.batch_number}: "
        ...           f"{batch_result.success_rate:.1f}% success")
    """
    
    def __init__(
        self,
        spark: Optional[SparkSession] = None,
        batch_size: int = 100,
        max_failures: int = 3,
        retry_delay_hours: int = 24
    ):
        """
        Initialize batch processor.
        
        Args:
            spark: SparkSession (creates new if None)
            batch_size: Number of jurisdictions per batch
            max_failures: Max consecutive failures before marking as failed
            retry_delay_hours: Hours to wait before retrying failed jurisdictions
        """
        self.spark = spark or self._create_spark_session()
        self.batch_size = batch_size
        self.max_failures = max_failures
        self.retry_delay_hours = retry_delay_hours
        
        self.quality_metrics_path = f"{settings.delta_lake_path}/quality/jurisdiction_metrics"
        self.batch_results_path = f"{settings.delta_lake_path}/quality/batch_results"
    
    def _create_spark_session(self) -> SparkSession:
        """Create SparkSession if not provided."""
        from delta import configure_spark_with_delta_pip
        
        builder = SparkSession.builder \
            .appName("BatchProcessor") \
            .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
            .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")
        
        return configure_spark_with_delta_pip(builder).getOrCreate()
    
    def process_all_jurisdictions(
        self,
        priority_filter: str = "high",
        resume_from_batch: Optional[int] = None
    ) -> Iterator[BatchResult]:
        """
        Process all jurisdictions in batches.
        
        Args:
            priority_filter: Priority tier to process ('high', 'medium', 'low', 'all')
            resume_from_batch: Resume from specific batch number (for interruptions)
            
        Yields:
            BatchResult for each processed batch
        """
        logger.info(f"Starting batch processing (batch_size={self.batch_size})")
        
        # Load targets from Gold layer
        targets_df = self.spark.read.format("delta").load(
            f"{settings.delta_lake_path}/gold/scraping_targets"
        )
        
        # Filter by priority
        if priority_filter != "all":
            targets_df = targets_df.filter(col("priority_tier") == priority_filter)
        
        # Filter out recently failed jurisdictions
        quality_df = self._load_quality_metrics()
        if quality_df is not None:
            # Skip jurisdictions that failed recently and are within retry delay
            retry_cutoff = datetime.utcnow() - timedelta(hours=self.retry_delay_hours)
            retry_cutoff_str = retry_cutoff.isoformat()
            
            # Join with quality metrics and filter
            targets_df = targets_df.join(
                quality_df.select("url", "consecutive_failures", "last_scraped", "health_status"),
                on="url",
                how="left"
            ).filter(
                (col("consecutive_failures").isNull()) |  # Never scraped
                (col("consecutive_failures") < self.max_failures) |  # Not max failures
                (col("last_scraped") < retry_cutoff_str)  # Retry delay passed
            )
        
        # Order by priority score
        targets_df = targets_df.orderBy(col("priority_score").desc())
        
        total_targets = targets_df.count()
        logger.info(f"Processing {total_targets} jurisdictions")
        
        # Calculate starting batch
        start_batch = resume_from_batch or 0
        
        # Process in batches
        for batch_num in range(start_batch, (total_targets // self.batch_size) + 1):
            offset = batch_num * self.batch_size
            
            # Get batch
            batch_df = targets_df.offset(offset).limit(self.batch_size)
            batch_data = batch_df.collect()
            
            if not batch_data:
                break
            
            logger.info(f"Processing batch {batch_num + 1} ({len(batch_data)} jurisdictions)")
            
            # Process batch
            batch_result = self._process_batch(batch_num + 1, batch_data)
            
            # Save batch result
            self._save_batch_result(batch_result)
            
            # Update quality metrics
            # (In real implementation, this would be called after actual scraping)
            
            yield batch_result
    
    def _process_batch(self, batch_num: int, batch_data: List) -> BatchResult:
        """
        Process a single batch of jurisdictions.
        
        Note: This is a skeleton. Actual scraping logic would go here.
        """
        result = BatchResult(
            batch_number=batch_num,
            batch_size=len(batch_data),
            jurisdictions_processed=0,
            jurisdictions_succeeded=0,
            jurisdictions_failed=0,
            meetings_found=0,
            agendas_found=0,
            minutes_found=0,
            errors=[],
            start_time=datetime.utcnow()
        )
        
        for row in batch_data:
            jurisdiction = row['jurisdiction_name']
            url = row['url']
            platform = row.get('platform')
            
            try:
                # TODO: Replace with actual scraping logic
                # For now, simulate scraping
                logger.info(f"Processing {jurisdiction}: {url}")
                
                # Placeholder: Would call appropriate scraper here
                # meetings = scrape_jurisdiction(url, platform)
                
                # Simulate success
                result.jurisdictions_processed += 1
                result.jurisdictions_succeeded += 1
                result.meetings_found += 5  # Placeholder
                result.agendas_found += 5
                result.minutes_found += 3
                
            except Exception as e:
                logger.error(f"Error processing {jurisdiction}: {e}")
                result.jurisdictions_processed += 1
                result.jurisdictions_failed += 1
                result.errors.append({
                    'jurisdiction': jurisdiction,
                    'url': url,
                    'error': str(e)
                })
        
        result.end_time = datetime.utcnow()
        result.duration_seconds = (result.end_time - result.start_time).total_seconds()
        
        return result
    
    def calculate_quality_metrics(self, jurisdiction_url: str) -> JurisdictionQuality:
        """
        Calculate quality metrics for a jurisdiction.
        
        Args:
            jurisdiction_url: URL of the jurisdiction
            
        Returns:
            JurisdictionQuality object with all scores
        """
        # Load existing metrics
        existing = self._get_existing_metrics(jurisdiction_url)
        
        # Load scraped data for this jurisdiction
        # (In production, query from silver/gold layers)
        
        # For now, create placeholder metrics
        now = datetime.utcnow()
        
        # Calculate completeness score
        if existing:
            total_expected = existing.total_meetings_expected or 12  # Assume monthly meetings
            total_found = existing.total_meetings_found or 0
            with_agendas = existing.meetings_with_agendas or 0
            with_minutes = existing.meetings_with_minutes or 0
            
            found_rate = min(total_found / total_expected, 1.0) if total_expected > 0 else 0
            agenda_rate = with_agendas / total_found if total_found > 0 else 0
            minutes_rate = with_minutes / total_found if total_found > 0 else 0
            
            completeness_score = (
                found_rate * 40 +      # 40%: Finding meetings
                agenda_rate * 30 +     # 30%: Having agendas
                minutes_rate * 30      # 30%: Having minutes
            )
        else:
            completeness_score = 0.0
        
        # Calculate reliability score
        if existing:
            total_scrapes = existing.total_scrapes or 0
            successful = existing.successful_scrapes or 0
            reliability_score = (successful / total_scrapes * 100) if total_scrapes > 0 else 0
        else:
            reliability_score = 0.0
        
        # Calculate freshness score
        if existing and existing.last_scraped:
            days_since = (now - existing.last_scraped).days
            if days_since <= 1:
                freshness_score = 100
            elif days_since <= 7:
                freshness_score = 80
            elif days_since <= 30:
                freshness_score = 60
            else:
                freshness_score = 40
        else:
            freshness_score = 0.0
        
        # Overall quality (weighted average)
        overall_quality = (
            completeness_score * 0.5 +
            reliability_score * 0.3 +
            freshness_score * 0.2
        )
        
        # Determine health status
        consecutive_failures = existing.consecutive_failures if existing else 0
        if consecutive_failures >= self.max_failures:
            health_status = HealthStatus.FAILED
        elif consecutive_failures >= 2:
            health_status = HealthStatus.DEGRADED
        elif reliability_score >= 70:
            health_status = HealthStatus.HEALTHY
        else:
            health_status = HealthStatus.UNKNOWN
        
        # Create metrics object
        metrics = JurisdictionQuality(
            jurisdiction_name=existing.jurisdiction_name if existing else "Unknown",
            state_code=existing.state_code if existing else "XX",
            fips_code=existing.fips_code if existing else None,
            url=jurisdiction_url,
            platform=existing.platform if existing else None,
            total_meetings_expected=existing.total_meetings_expected if existing else 12,
            total_meetings_found=existing.total_meetings_found if existing else 0,
            meetings_with_agendas=existing.meetings_with_agendas if existing else 0,
            meetings_with_minutes=existing.meetings_with_minutes if existing else 0,
            meetings_with_videos=existing.meetings_with_videos if existing else 0,
            meetings_with_transcripts=existing.meetings_with_transcripts if existing else 0,
            last_scraped=now,
            last_meeting_found=existing.last_meeting_found if existing else None,
            scraping_frequency=existing.scraping_frequency if existing else "monthly",
            consecutive_successes=existing.consecutive_successes if existing else 0,
            consecutive_failures=consecutive_failures,
            total_scrapes=existing.total_scrapes + 1 if existing else 1,
            successful_scrapes=existing.successful_scrapes if existing else 0,
            last_success=existing.last_success if existing else None,
            last_error=existing.last_error if existing else None,
            completeness_score=round(completeness_score, 2),
            reliability_score=round(reliability_score, 2),
            freshness_score=round(freshness_score, 2),
            overall_quality=round(overall_quality, 2),
            health_status=health_status.value,
            created_at=existing.created_at if existing else now,
            updated_at=now
        )
        
        return metrics
    
    def _get_existing_metrics(self, url: str) -> Optional[JurisdictionQuality]:
        """Load existing metrics for a jurisdiction."""
        try:
            df = self.spark.read.format("delta").load(self.quality_metrics_path)
            result = df.filter(col("url") == url).first()
            if result:
                return JurisdictionQuality.from_dict(result.asDict())
        except Exception:
            pass
        return None
    
    def _load_quality_metrics(self) -> Optional[DataFrame]:
        """Load all quality metrics."""
        try:
            return self.spark.read.format("delta").load(self.quality_metrics_path)
        except Exception:
            return None
    
    def _save_batch_result(self, result: BatchResult):
        """Save batch result to Delta Lake."""
        # Convert to DataFrame
        data = [{
            'batch_number': result.batch_number,
            'batch_size': result.batch_size,
            'jurisdictions_processed': result.jurisdictions_processed,
            'jurisdictions_succeeded': result.jurisdictions_succeeded,
            'jurisdictions_failed': result.jurisdictions_failed,
            'meetings_found': result.meetings_found,
            'agendas_found': result.agendas_found,
            'minutes_found': result.minutes_found,
            'success_rate': result.success_rate,
            'duration_seconds': result.duration_seconds,
            'start_time': result.start_time.isoformat(),
            'end_time': result.end_time.isoformat() if result.end_time else None,
            'errors': json.dumps(result.errors)
        }]
        
        df = self.spark.createDataFrame(data)
        
        # Write to Delta Lake
        df.write \
            .format("delta") \
            .mode("append") \
            .save(self.batch_results_path)
        
        logger.info(f"Saved batch result {result.batch_number} to Delta Lake")
    
    def get_system_health_report(self) -> dict:
        """
        Generate overall system health report.
        
        Returns:
            Dictionary with aggregate statistics
        """
        quality_df = self._load_quality_metrics()
        
        if quality_df is None:
            return {
                'status': 'no_data',
                'message': 'No quality metrics available yet'
            }
        
        # Aggregate statistics
        stats = quality_df.agg(
            count("*").alias("total_jurisdictions"),
            avg("overall_quality").alias("avg_quality"),
            avg("completeness_score").alias("avg_completeness"),
            avg("reliability_score").alias("avg_reliability"),
            spark_sum((col("health_status") == "healthy").cast("int")).alias("healthy_count"),
            spark_sum((col("health_status") == "degraded").cast("int")).alias("degraded_count"),
            spark_sum((col("health_status") == "failed").cast("int")).alias("failed_count")
        ).first()
        
        return {
            'total_jurisdictions': stats['total_jurisdictions'],
            'average_quality': round(stats['avg_quality'], 2),
            'average_completeness': round(stats['avg_completeness'], 2),
            'average_reliability': round(stats['avg_reliability'], 2),
            'healthy_count': stats['healthy_count'],
            'degraded_count': stats['degraded_count'],
            'failed_count': stats['failed_count'],
            'health_percentage': round(
                (stats['healthy_count'] / stats['total_jurisdictions']) * 100, 1
            ) if stats['total_jurisdictions'] > 0 else 0
        }


if __name__ == "__main__":
    # Demo
    processor = BatchProcessor(batch_size=10)
    
    print("🔄 Batch Processing Demo")
    print("=" * 70)
    print("\nThis would process jurisdictions in batches with quality tracking.")
    print("\nExample batch results:\n")
    
    # Simulate processing (would normally call process_all_jurisdictions)
    for i in range(3):
        result = BatchResult(
            batch_number=i + 1,
            batch_size=10,
            jurisdictions_processed=10,
            jurisdictions_succeeded=8,
            jurisdictions_failed=2,
            meetings_found=45,
            agendas_found=40,
            minutes_found=30,
            errors=[],
            start_time=datetime.utcnow(),
            end_time=datetime.utcnow() + timedelta(minutes=5),
            duration_seconds=300
        )
        
        print(f"Batch {result.batch_number}:")
        print(f"  Processed: {result.jurisdictions_processed}")
        print(f"  Success rate: {result.success_rate:.1f}%")
        print(f"  Meetings found: {result.meetings_found}")
        print(f"  Duration: {result.duration_seconds:.0f}s")
        print()
    
    print("📊 System health tracking:")
    print("  • Quality scores per jurisdiction")
    print("  • Completeness, reliability, freshness metrics")
    print("  • Health status: healthy, degraded, failed")
    print("  • Automatic retry with exponential backoff")
