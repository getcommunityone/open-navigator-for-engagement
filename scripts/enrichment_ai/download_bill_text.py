#!/usr/bin/env python3
"""
Download and Extract Bill Text to Parquet

Creates bills_bill_text.parquet with normalized bill text storage:
- Separates large text content from bill metadata
- Uses state APIs when available (GA SOAP API)
- Falls back to OpenStates bulk downloads
- Stores in compressed parquet for space efficiency

Schema:
- bill_id: Link to bills_bills.parquet
- version_note: "Introduced", "Enrolled", etc.
- text: Full bill text (plain text)
- source_url: Where text was fetched from
- source_type: 'state_api', 'openstates_bulk', 'pdf_download'
- extracted_date: When text was extracted
- text_format: 'txt', 'html', 'pdf'
- character_count: Length of text
- word_count: Number of words
- state: Two-letter state code

Usage:
    # Download text for specific states
    python scripts/enrichment_ai/download_bill_text.py --states GA,AL --year 2024
    
    # Download for all states with available data
    python scripts/enrichment_ai/download_bill_text.py --year 2024 --limit 100
"""

import argparse
import sys
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
import re

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from loguru import logger
import polars as pl
import httpx
from bs4 import BeautifulSoup
from pypdf import PdfReader
import io
import xml.etree.ElementTree as ET

# Import our bill text source configuration
from scripts.enrichment_ai.bill_text_sources import (
    get_bill_text_source,
    BillTextSource,
    can_fetch_bill_text
)


class BillTextDownloader:
    """Download and extract bill text from various sources"""
    
    def __init__(
        self,
        output_dir: Path = Path("data/gold"),
        cache_dir: Path = Path("data/cache/bill_text")
    ):
        self.output_dir = output_dir
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Output parquet file
        self.output_file = output_dir / "bills_bill_text.parquet"
        
        # Load existing bills data to get bill IDs and version URLs
        self.bills_file = output_dir / "bills_bills.parquet"
        self.versions_file = output_dir / "bills_versions.parquet"
        
    def load_bills_for_processing(
        self,
        states: Optional[List[str]] = None,
        year: Optional[int] = None,
        limit: Optional[int] = None
    ) -> pl.DataFrame:
        """
        Load bills that need text extraction
        
        Returns DataFrame with bill_id, state, session, and version URLs
        """
        if not self.bills_file.exists():
            logger.error(f"Bills file not found: {self.bills_file}")
            logger.info("Run: python scripts/datasources/openstates/export_openstates_to_gold.py")
            return pl.DataFrame()
        
        # Load bills
        logger.info(f"📖 Loading bills from {self.bills_file}")
        # Handle timezone issues in parquet file (offset-based tzinfo like '-05:00')
        try:
            bills_df = pl.read_parquet(self.bills_file)
        except pl.exceptions.ComputeError as e:
            if "time zone" in str(e):
                logger.warning("Timezone parsing issue, converting offset-based timestamps...")
                import pyarrow.parquet as pq
                import pyarrow.compute as pc
                
                table = pq.read_table(self.bills_file)
                # Convert timestamp columns to remove timezone offset
                for col_name in table.schema.names:
                    col = table.schema.field(col_name)
                    if str(col.type).startswith('timestamp'):
                        # Cast to timestamp without timezone
                        table = table.set_column(
                            table.schema.get_field_index(col_name),
                            col_name,
                            pc.cast(table[col_name], 'timestamp[us]')
                        )
                bills_df = pl.from_arrow(table)
            else:
                raise
        
        # Filter by state
        if states:
            bills_df = bills_df.filter(pl.col("state").is_in(states))
        
        # Filter by year if specified
        if year:
            bills_df = bills_df.filter(
                pl.col("session").str.contains(str(year))
            )
        
        # Load versions (contains URLs to bill text)
        if self.versions_file.exists():
            logger.info(f"📖 Loading bill versions from {self.versions_file}")
            versions_df = pl.read_parquet(self.versions_file)
            
            # Join bills with their versions
            bills_df = bills_df.join(
                versions_df,
                on="bill_id",
                how="left"
            )
        
        # Apply limit
        if limit:
            bills_df = bills_df.head(limit)
        
        logger.info(f"✅ Found {len(bills_df)} bills to process")
        return bills_df
    
    def extract_text_from_html(self, html_content: str) -> str:
        """Extract plain text from HTML"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.extract()
        
        # Get text
        text = soup.get_text()
        
        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return text
    
    def extract_text_from_pdf(self, pdf_content: bytes) -> str:
        """Extract plain text from PDF bytes"""
        try:
            pdf_reader = PdfReader(io.BytesIO(pdf_content))
            text_parts = []
            
            for page in pdf_reader.pages:
                text = page.extract_text()
                if text:
                    text_parts.append(text)
            
            full_text = '\n'.join(text_parts)
            # Clean up excessive whitespace
            full_text = re.sub(r'\n\s*\n', '\n\n', full_text)
            return full_text.strip()
            
        except Exception as e:
            logger.error(f"Error extracting PDF text: {e}")
            return ""
    
    def download_from_url(
        self,
        url: str,
        bill_id: str
    ) -> Optional[Dict]:
        """
        Download bill text from URL
        
        Returns dict with text and metadata or None
        """
        # Skip old Alabama URLs that are broken (2017-2022)
        if 'alisondb.legislature.state.al.us' in url:
            logger.debug(f"Skipping broken old Alabama URL: {url}")
            logger.debug(f"Use scripts/enrichment_ai/download_alabama_bills_scraper.py for AL 2017-2022")
            return None
        
        try:
            with httpx.Client(timeout=30.0, follow_redirects=True) as client:
                response = client.get(url)
                response.raise_for_status()
                
                # Determine content type
                content_type = response.headers.get('content-type', '').lower()
                
                if 'pdf' in content_type or url.endswith('.pdf'):
                    # PDF - extract text
                    text = self.extract_text_from_pdf(response.content)
                    if not text:
                        logger.warning(f"Failed to extract text from PDF for {bill_id}")
                        return None
                    text_format = 'pdf'
                
                elif 'html' in content_type or url.endswith('.html'):
                    # HTML - extract text
                    text = self.extract_text_from_html(response.text)
                    text_format = 'html'
                
                else:
                    # Assume plain text
                    text = response.text
                    text_format = 'txt'
                
                return {
                    'text': text,
                    'text_format': text_format,
                    'source_url': url,
                    'character_count': len(text),
                    'word_count': len(text.split())
                }
                
        except Exception as e:
            logger.error(f"Error downloading {url}: {e}")
            return None
    
    def fetch_georgia_bill_text(
        self,
        bill_id: str,
        session: str,
        bill_number: str = None
    ) -> Optional[Dict]:
        """
        Fetch bill text from Georgia SOAP API
        
        Returns dict with text and metadata or None
        """
        if not bill_number:
            logger.debug(f"No bill number provided for Georgia API")
            return None
        
        try:
            # Georgia SOAP API endpoint
            api_url = "http://webservices.legis.ga.gov/GGAServices/Service/Service.asmx/GetLegislationDetail"
            
            # Extract session year from session string (e.g., '2023_24' -> '2023')
            session_year = session.split('_')[0] if '_' in session else session
            
            # Make SOAP request
            params = {
                'sessionId': session_year,
                'legislationId': bill_number.replace(' ', '')
            }
            
            with httpx.Client(timeout=30.0) as client:
                response = client.get(api_url, params=params)
                response.raise_for_status()
                
                # Parse XML response
                root = ET.fromstring(response.content)
                
                # Find LegislationText element (namespace handling)
                text_elem = root.find('.//{http://www.legis.ga.gov/}LegislationText')
                if text_elem is None:
                    text_elem = root.find('.//LegislationText')
                
                if text_elem is not None and text_elem.text:
                    text = text_elem.text.strip()
                    return {
                        'text': text,
                        'text_format': 'txt',
                        'source_url': f"{api_url}?sessionId={session_year}&legislationId={bill_number}",
                        'character_count': len(text),
                        'word_count': len(text.split())
                    }
                else:
                    logger.debug(f"No text found in Georgia API response for {bill_number}")
                    return None
                    
        except Exception as e:
            logger.debug(f"Georgia API error for {bill_number}: {e}")
            return None
    
    def process_bills(
        self,
        bills_df: pl.DataFrame
    ) -> pl.DataFrame:
        """
        Process bills and extract text
        
        Returns DataFrame with bill text records
        """
        text_records = []
        
        for row in bills_df.iter_rows(named=True):
            bill_id = row.get('bill_id')
            state = row.get('state')
            version_note = row.get('version_note', 'Unknown')
            document_url = row.get('document_url')
            bill_number = row.get('bill_number')
            
            if not bill_id:
                continue
            
            logger.info(f"Processing {bill_id} ({state}) - {version_note}")
            
            # Determine source
            source = get_bill_text_source(state)
            result = None
            source_type = 'unknown'
            
            # Try state-specific API first
            if source == BillTextSource.GEORGIA_SOAP:
                result = self.fetch_georgia_bill_text(
                    bill_id,
                    row.get('session', ''),
                    bill_number
                )
                if result:
                    source_type = 'state_api'
            
            # Fall back to URL download if state API didn't work and we have a URL
            if not result and document_url:
                result = self.download_from_url(document_url, bill_id)
                source_type = 'url_download'
            
            # If still no result, skip
            if not result:
                logger.warning(f"No source available for {bill_id}")
                continue
            
            # Save result if we got text
            if result and result.get('text'):
                text_records.append({
                    'bill_id': bill_id,
                    'state': state,
                    'version_note': version_note,
                    'text': result['text'],
                    'source_url': result.get('source_url', ''),
                    'source_type': source_type,
                    'extracted_date': datetime.now().isoformat(),
                    'text_format': result.get('text_format', 'unknown'),
                    'character_count': result.get('character_count', 0),
                    'word_count': result.get('word_count', 0)
                })
                
                logger.success(f"✅ Extracted {result.get('word_count', 0)} words from {bill_id}")
        
        if not text_records:
            logger.warning("No bill text extracted")
            return pl.DataFrame()
        
        # Convert to Polars DataFrame
        return pl.DataFrame(text_records)
    
    def save_to_parquet(self, text_df: pl.DataFrame):
        """
        Save bill text to parquet file
        
        Appends to existing file or creates new one
        """
        if len(text_df) == 0:
            logger.warning("No data to save")
            return
        
        # Check if file exists
        if self.output_file.exists():
            logger.info(f"📝 Appending to existing {self.output_file}")
            existing_df = pl.read_parquet(self.output_file)
            
            # Combine and deduplicate
            combined_df = pl.concat([existing_df, text_df])
            combined_df = combined_df.unique(subset=['bill_id', 'version_note'])
            
            # Save
            combined_df.write_parquet(
                self.output_file,
                compression='zstd',  # Better compression for text
                compression_level=3
            )
            
            logger.success(f"✅ Updated {self.output_file}")
            logger.info(f"   Total records: {len(combined_df)}")
            logger.info(f"   New records: {len(text_df)}")
        
        else:
            # Create new file
            text_df.write_parquet(
                self.output_file,
                compression='zstd',
                compression_level=3
            )
            
            logger.success(f"✅ Created {self.output_file}")
            logger.info(f"   Records: {len(text_df)}")
        
        # Show file size
        file_size_mb = self.output_file.stat().st_size / (1024 * 1024)
        logger.info(f"   File size: {file_size_mb:.1f} MB")


def main():
    parser = argparse.ArgumentParser(
        description="Download and extract bill text to parquet"
    )
    parser.add_argument(
        '--states',
        type=str,
        help='Comma-separated state codes (e.g., GA,AL,TX)'
    )
    parser.add_argument(
        '--year',
        type=int,
        help='Legislative session year (e.g., 2024)'
    )
    parser.add_argument(
        '--limit',
        type=int,
        help='Limit number of bills to process (for testing)'
    )
    
    args = parser.parse_args()
    
    # Parse states
    states = None
    if args.states:
        states = [s.strip().upper() for s in args.states.split(',')]
    
    # Initialize downloader
    downloader = BillTextDownloader()
    
    # Load bills to process
    logger.info("=" * 80)
    logger.info("BILL TEXT EXTRACTION PIPELINE")
    logger.info("=" * 80)
    
    bills_df = downloader.load_bills_for_processing(
        states=states,
        year=args.year,
        limit=args.limit
    )
    
    if len(bills_df) == 0:
        logger.error("No bills to process")
        return
    
    # Process bills
    logger.info("\n" + "=" * 80)
    logger.info("EXTRACTING BILL TEXT")
    logger.info("=" * 80)
    
    text_df = downloader.process_bills(bills_df)
    
    # Save results
    if len(text_df) > 0:
        logger.info("\n" + "=" * 80)
        logger.info("SAVING RESULTS")
        logger.info("=" * 80)
        
        downloader.save_to_parquet(text_df)
        
        # Print summary
        logger.info("\n" + "=" * 80)
        logger.info("SUMMARY")
        logger.info("=" * 80)
        logger.info(f"✅ Successfully extracted text for {len(text_df)} bill versions")
        
        # Show stats
        avg_words = text_df.get_column('word_count').mean()
        total_words = text_df.get_column('word_count').sum()
        logger.info(f"📊 Average: {avg_words:.0f} words per bill")
        logger.info(f"📊 Total: {total_words:,} words extracted")
    
    else:
        logger.warning("No bill text extracted")


if __name__ == "__main__":
    main()
