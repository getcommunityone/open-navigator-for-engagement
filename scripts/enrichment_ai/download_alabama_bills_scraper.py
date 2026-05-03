#!/usr/bin/env python3
"""
Alabama Bill Text Scraper (Backup Method)

For Alabama bills where direct URLs are broken (2017-2022), this script
uses Playwright to navigate the ALISON website interface, filter by
year/session, and download bill PDFs.

This is slower than direct URL downloads but works when URLs are unavailable.

Usage:
    # Scrape specific session
    python scripts/enrichment_ai/download_alabama_bills_scraper.py --session 2017rs --limit 10
    
    # Scrape multiple sessions
    python scripts/enrichment_ai/download_alabama_bills_scraper.py --sessions 2017rs,2018rs,2019rs
"""

import argparse
import sys
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
import time
import re

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from loguru import logger
import polars as pl
from playwright.sync_api import sync_playwright, Page, Browser
from pypdf import PdfReader
import io

# Configure logger
logger.add(sys.stderr, format="{time} {level} {message}", level="INFO")


class AlabamaBillScraper:
    """Scrape Alabama bills using Playwright browser automation"""
    
    def __init__(self, headless: bool = True):
        self.headless = headless
        self.base_url = "https://alison.legislature.state.al.us"
        self.output_file = Path("data/gold/bills_bill_text.parquet")
        
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
    
    def navigate_to_session(self, page: Page, session: str):
        """Navigate to specific legislative session"""
        logger.info(f"Navigating to session: {session}")
        
        # Go to bills search page
        page.goto(f"{self.base_url}/bills")
        page.wait_for_load_state("networkidle")
        
        # Look for "Bills - Search All Sessions" link or similar
        try:
            # Try to find the filter icon or session selector
            page.click("button:has-text('Filter'), button[aria-label='Filter']", timeout=5000)
        except:
            logger.debug("No filter button found, trying alternative navigation")
        
        # Wait for page to stabilize
        time.sleep(2)
        
    def construct_bill_url(self, bill_number: str, session: str, version: str = "int") -> str:
        """Construct the bill URL from components"""
        # Convert session to uppercase (e.g., 2017rs -> 2017RS)
        session_upper = session.upper()
        
        # Construct URL: https://alison.legislature.state.al.us/SearchableInstruments/2017RS/PrintFiles/HB1-int.pdf
        bill_clean = bill_number.replace(" ", "")
        url = f"{self.base_url}/SearchableInstruments/{session_upper}/PrintFiles/{bill_clean}-{version}.pdf"
        return url
    
    def scrape_bill(self, page: Page, bill_number: str, session: str, version_note: str = None) -> Optional[Dict]:
        """
        Scrape a single bill's text from ALISON
        
        Strategy:
        1. Try to construct direct PDF URL (common patterns: -int, -eng, -enr)
        2. If that fails, navigate to bill page and find PDF link
        
        Returns dict with bill text and metadata
        """
        try:
            logger.info(f"Scraping {bill_number} from {session}")
            
            # Try common version suffixes
            version_suffixes = ['int', 'eng', 'enr', 'sub']
            
            for version in version_suffixes:
                try:
                    pdf_url = self.construct_bill_url(bill_number, session, version)
                    logger.debug(f"Trying: {pdf_url}")
                    
                    # Try to download directly
                    response = page.request.get(pdf_url)
                    
                    if response.status == 200 and response.headers.get('content-type', '').startswith('application/pdf'):
                        logger.info(f"✅ Found PDF at: {pdf_url}")
                        pdf_content = response.body()
                        text = self.extract_text_from_pdf(pdf_content)
                        
                        if text:
                            return {
                                'text': text,
                                'text_format': 'pdf',
                                'source_url': pdf_url,
                                'character_count': len(text),
                                'word_count': len(text.split())
                            }
                except Exception as e:
                    logger.debug(f"Version '{version}' not found: {e}")
                    continue
            
            # If direct URL failed, try navigating to bill page
            logger.debug(f"Direct URL failed, trying web navigation for {bill_number}")
            return self.scrape_bill_via_navigation(page, bill_number, session)
                
        except Exception as e:
            logger.error(f"Error scraping {bill_number}: {e}")
            return None
    
    def scrape_bill_via_navigation(self, page: Page, bill_number: str, session: str) -> Optional[Dict]:
        """Fallback: Navigate to bill page and find PDF link"""
        try:
            # Navigate to bills page with longer timeout
            page.goto(f"{self.base_url}/bills", timeout=60000)
            page.wait_for_load_state("domcontentloaded")
            time.sleep(2)
            
            # Try to find and use search input
            try:
                # Wait for search input to be available
                search_input = page.wait_for_selector(
                    "input[type='search'], input[placeholder*='search' i], input[name*='search' i]",
                    timeout=10000
                )
                if search_input:
                    search_input.fill(bill_number)
                    search_input.press("Enter")
                    page.wait_for_load_state("domcontentloaded")
                    time.sleep(2)
            except Exception as e:
                logger.warning(f"Could not use search for {bill_number}: {e}")
                return None
            
            # Look for PDF link
            try:
                pdf_link = page.wait_for_selector(
                    "a[href$='.pdf'], a:has-text('PDF'), a:has-text('Download')",
                    timeout=10000
                )
                if pdf_link:
                    pdf_url = pdf_link.get_attribute("href")
                    
                    if not pdf_url.startswith("http"):
                        pdf_url = self.base_url + pdf_url
                    
                    logger.info(f"Found PDF URL via navigation: {pdf_url}")
                    
                    # Download PDF
                    response = page.request.get(pdf_url)
                    if response.status == 200:
                        pdf_content = response.body()
                        text = self.extract_text_from_pdf(pdf_content)
                        
                        if text:
                            return {
                                'text': text,
                                'text_format': 'pdf',
                                'source_url': pdf_url,
                                'character_count': len(text),
                                'word_count': len(text.split())
                            }
            except Exception as e:
                logger.warning(f"Could not find PDF link for {bill_number}: {e}")
                return None
                
        except Exception as e:
            logger.warning(f"Navigation method failed for {bill_number}: {e}")
            return None
    
    def scrape_session(
        self,
        session: str,
        bill_numbers: Optional[List[str]] = None,
        limit: Optional[int] = None
    ) -> pl.DataFrame:
        """
        Scrape bills from a legislative session
        
        Args:
            session: Session code (e.g., '2017rs', '2019fs')
            bill_numbers: Specific bills to scrape (if None, scrapes all from DB)
            limit: Maximum number of bills to scrape
        
        Returns:
            DataFrame with bill text records
        """
        text_records = []
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=self.headless)
            page = browser.new_page()
            
            try:
                # If no bill numbers provided, try to get list from database
                if not bill_numbers:
                    logger.info(f"Loading bills for {session} from database")
                    bills_info = self.get_bills_for_session(session)
                else:
                    # Convert bill numbers to info dicts
                    bills_info = [{'bill_id': f'al-{session}-{bn.lower().replace(" ", "")}', 'bill_number': bn} 
                                  for bn in bill_numbers]
                
                if limit:
                    bills_info = bills_info[:limit]
                
                logger.info(f"Scraping {len(bills_info)} bills from {session}")
                
                for i, bill_info in enumerate(bills_info, 1):
                    bill_number = bill_info['bill_number']
                    bill_id = bill_info['bill_id']
                    
                    logger.info(f"[{i}/{len(bills_info)}] Processing {bill_number}")
                    
                    # Try scraping with retry logic
                    max_retries = 2
                    result = None
                    
                    for attempt in range(max_retries):
                        try:
                            result = self.scrape_bill(page, bill_number, session)
                            if result and result.get('text'):
                                break
                            elif attempt < max_retries - 1:
                                logger.debug(f"Retry {attempt + 1}/{max_retries} for {bill_number}")
                                time.sleep(2)
                        except Exception as e:
                            logger.warning(f"Attempt {attempt + 1} failed for {bill_number}: {e}")
                            if attempt < max_retries - 1:
                                time.sleep(2)
                    
                    if result and result.get('text'):
                        text_records.append({
                            'bill_id': bill_id,  # Use actual bill_id from database
                            'state': 'AL',
                            'session': session,
                            'bill_number': bill_number,
                            'version_note': 'Scraped from ALISON',
                            'text': result['text'],
                            'source_url': result['source_url'],
                            'source_type': 'alison_scraper',
                            'extracted_date': datetime.now().isoformat(),
                            'text_format': result['text_format'],
                            'character_count': result['character_count'],
                            'word_count': result['word_count']
                        })
                        logger.success(f"✅ Extracted {result['word_count']} words from {bill_number}")
                    else:
                        logger.warning(f"❌ No text extracted for {bill_number}")
                    
                    # Be nice to the server
                    time.sleep(1)
                    
            finally:
                browser.close()
        
        if not text_records:
            logger.warning("No bill text extracted")
            return pl.DataFrame()
        
        return pl.DataFrame(text_records)
    
    def get_bills_for_session(self, session: str) -> List[Dict[str, str]]:
        """Get bill information for a session from our database"""
        try:
            import pyarrow.parquet as pq
            import pyarrow.compute as pc
            
            # Read bills with timezone fix
            table = pq.read_table('data/gold/bills_bills.parquet')
            for col_name in table.schema.names:
                col = table.schema.field(col_name)
                if str(col.type).startswith('timestamp'):
                    table = table.set_column(
                        table.schema.get_field_index(col_name),
                        col_name,
                        pc.cast(table[col_name], 'timestamp[us]')
                    )
            bills_df = pl.from_arrow(table)
            
            # Filter for Alabama bills in this session
            session_bills = bills_df.filter(
                (pl.col('state') == 'AL') & 
                (pl.col('session') == session)
            ).select(['bill_id', 'bill_number']).unique()
            
            # Convert to list of dicts
            bills_list = []
            for row in session_bills.iter_rows(named=True):
                bills_list.append({
                    'bill_id': row['bill_id'],
                    'bill_number': row['bill_number']
                })
            
            logger.info(f"Found {len(bills_list)} bills for session {session}")
            return bills_list
            
        except Exception as e:
            logger.error(f"Error loading bills from database: {e}")
            return []
    
    def save_to_parquet(self, text_df: pl.DataFrame):
        """Save or append to bills_bill_text.parquet"""
        if self.output_file.exists():
            logger.info(f"📝 Appending to existing {self.output_file}")
            existing_df = pl.read_parquet(self.output_file)
            
            # Combine and deduplicate
            combined_df = pl.concat([existing_df, text_df])
            combined_df = combined_df.unique(subset=['bill_id', 'version_note'])
            
            # Save
            combined_df.write_parquet(
                self.output_file,
                compression='zstd',
                compression_level=3
            )
            
            logger.success(f"✅ Updated {self.output_file}")
            logger.info(f"   Total records: {len(combined_df)}")
            logger.info(f"   New records: {len(text_df)}")
        else:
            logger.info(f"📝 Creating new {self.output_file}")
            text_df.write_parquet(
                self.output_file,
                compression='zstd',
                compression_level=3
            )
            logger.success(f"✅ Created {self.output_file}")
            logger.info(f"   Records: {len(text_df)}")
        
        # Show file size
        size_mb = self.output_file.stat().st_size / (1024 * 1024)
        logger.info(f"   File size: {size_mb:.1f} MB")


def main():
    parser = argparse.ArgumentParser(
        description="Scrape Alabama bill text from ALISON website (backup method)"
    )
    parser.add_argument(
        '--session',
        type=str,
        help='Single session to scrape (e.g., 2017rs)'
    )
    parser.add_argument(
        '--sessions',
        type=str,
        help='Comma-separated sessions (e.g., 2017rs,2018rs,2019rs)'
    )
    parser.add_argument(
        '--bills',
        type=str,
        help='Comma-separated bill numbers (e.g., HB1,HB10,SB5)'
    )
    parser.add_argument(
        '--limit',
        type=int,
        help='Limit number of bills to scrape per session'
    )
    parser.add_argument(
        '--headless',
        action='store_true',
        default=True,
        help='Run browser in headless mode (default: True)'
    )
    parser.add_argument(
        '--show-browser',
        action='store_true',
        help='Show browser window (disables headless mode)'
    )
    
    args = parser.parse_args()
    
    # Determine sessions to scrape
    sessions = []
    if args.session:
        sessions = [args.session]
    elif args.sessions:
        sessions = args.sessions.split(',')
    else:
        # Default: scrape old sessions with broken URLs
        sessions = ['2017rs', '2018rs', '2019rs', '2019fs', '2020rs', '2021rs', '2022rs']
    
    # Parse bill numbers if provided
    bill_numbers = None
    if args.bills:
        bill_numbers = [b.strip().upper() for b in args.bills.split(',')]
    
    # Create scraper
    headless = args.headless and not args.show_browser
    scraper = AlabamaBillScraper(headless=headless)
    
    logger.info("=" * 80)
    logger.info("ALABAMA BILL TEXT SCRAPER (BACKUP METHOD)")
    logger.info("=" * 80)
    logger.info(f"Sessions: {', '.join(sessions)}")
    if bill_numbers:
        logger.info(f"Bills: {', '.join(bill_numbers)}")
    if args.limit:
        logger.info(f"Limit: {args.limit} bills per session")
    logger.info("=" * 80)
    
    # Scrape each session
    all_records = []
    for session in sessions:
        logger.info(f"\n📋 Scraping session: {session}")
        logger.info("=" * 80)
        
        text_df = scraper.scrape_session(
            session=session,
            bill_numbers=bill_numbers,
            limit=args.limit
        )
        
        if len(text_df) > 0:
            all_records.append(text_df)
            logger.success(f"✅ Scraped {len(text_df)} bills from {session}")
    
    # Combine and save
    if all_records:
        logger.info("\n" + "=" * 80)
        logger.info("SAVING RESULTS")
        logger.info("=" * 80)
        
        combined_df = pl.concat(all_records)
        scraper.save_to_parquet(combined_df)
        
        logger.info("\n" + "=" * 80)
        logger.info("SUMMARY")
        logger.info("=" * 80)
        logger.info(f"✅ Successfully scraped {len(combined_df)} bill versions")
        
        total_words = combined_df['word_count'].sum()
        avg_words = combined_df['word_count'].mean()
        logger.info(f"📊 Average: {avg_words:.0f} words per bill")
        logger.info(f"📊 Total: {total_words:,} words extracted")
    else:
        logger.warning("No bills were scraped")


if __name__ == "__main__":
    main()
