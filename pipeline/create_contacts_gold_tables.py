"""
Create Contacts Gold Tables from Meeting Data

Extract structured contact information from meeting transcripts:
- Local officials (mayors, council members, commissioners)
- State legislators (from Open States API)
- School board members

Gold Tables Created:
1. contacts_local_officials - Extracted from meeting roll calls
2. contacts_state_legislators - From Open States API  
3. contacts_school_board - School board members

Input: data/gold/meetings_transcripts.parquet
Output: data/gold/contacts_*.parquet
"""

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from pathlib import Path
from typing import List, Dict, Optional, Set
from datetime import datetime
import re
from loguru import logger
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import settings


class ContactsGoldTableCreator:
    """Extract contact information from meeting data"""
    
    def __init__(
        self,
        meetings_gold_dir: str = "data/gold",
        output_dir: str = "data/gold"
    ):
        self.meetings_gold_dir = Path(meetings_gold_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Meetings Gold Dir: {self.meetings_gold_dir}")
        logger.info(f"Output Dir: {self.output_dir}")
    
    def extract_officials_from_transcript(self, text: str, jurisdiction: str) -> List[Dict]:
        """
        Extract official names and titles from meeting transcripts.
        
        Patterns we look for:
        - Roll call: "Jerry Schultz here, Ted Nelson here"
        - Title mentions: "Mayor Smith", "Councilmember Jones"
        - Speaker patterns: "John Doe: Thank you Mr. Mayor"
        """
        if not text or pd.isna(text):
            return []
        
        text_str = str(text)
        officials = []
        seen_names = set()
        
        # Pattern 1: Titles with names
        title_patterns = [
            r'(?:Mayor|Councilmember|Council Member|Commissioner|Supervisor)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,2})',
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,2})(?:,\s*Mayor)',
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,2})(?:,\s*(?:Council|Commission)\s+(?:Member|Chair))',
        ]
        
        for pattern in title_patterns:
            matches = re.finditer(pattern, text_str, re.IGNORECASE)
            for match in matches:
                name = match.group(1).strip()
                
                # Skip common false positives
                if self._is_valid_name(name) and name not in seen_names:
                    seen_names.add(name)
                    
                    # Try to extract title from context
                    title = self._extract_title_from_context(text_str, match.start(), match.end())
                    
                    officials.append({
                        'name': name,
                        'title': title,
                        'jurisdiction': jurisdiction,
                        'source': 'meeting_transcript'
                    })
        
        # Pattern 2: Roll call format (very common in transcripts)
        # "call roll Jerry Schultz here Ted Nelson Mike Barbour"
        roll_call_pattern = r'(?:call\s+roll|roll\s+call)[:\s]+((?:[A-Z][a-z]+\s+[A-Z][a-z]+\s+(?:here|present|aye|yes)[\s,]*)+)'
        
        roll_matches = re.finditer(roll_call_pattern, text_str, re.IGNORECASE)
        for roll_match in roll_matches:
            roll_text = roll_match.group(1)
            
            # Extract individual names
            name_pattern = r'([A-Z][a-z]+\s+[A-Z][a-z]+)(?:\s+(?:here|present|aye|yes))'
            name_matches = re.finditer(name_pattern, roll_text)
            
            for name_match in name_matches:
                name = name_match.group(1).strip()
                
                if self._is_valid_name(name) and name not in seen_names:
                    seen_names.add(name)
                    
                    officials.append({
                        'name': name,
                        'title': 'Council Member',  # Default for roll call
                        'jurisdiction': jurisdiction,
                        'source': 'roll_call'
                    })
        
        return officials
    
    def _is_valid_name(self, name: str) -> bool:
        """Check if a name looks valid (not a false positive)"""
        if not name:
            return False
        
        # Must be 2-4 words
        parts = name.split()
        if len(parts) < 2 or len(parts) > 4:
            return False
        
        # Skip common false positives
        skip_words = {
            'City Council', 'Council Meeting', 'Public Comment', 'Mr Mayor',
            'Thank You', 'Good Evening', 'All Right', 'Item Number',
            'United States', 'Texas Flag', 'God Bless', 'Let Us'
        }
        
        if name in skip_words:
            return False
        
        # Each part should start with capital letter
        for part in parts:
            if not part[0].isupper():
                return False
        
        return True
    
    def _extract_title_from_context(self, text: str, start: int, end: int) -> str:
        """Extract title from surrounding context"""
        # Get 50 chars before and after
        context_start = max(0, start - 50)
        context_end = min(len(text), end + 50)
        context = text[context_start:context_end].lower()
        
        # Check for titles in context
        if 'mayor' in context:
            return 'Mayor'
        elif 'council' in context or 'councilmember' in context:
            return 'Council Member'
        elif 'commissioner' in context:
            return 'Commissioner'
        elif 'supervisor' in context:
            return 'Supervisor'
        elif 'chair' in context:
            return 'Chair'
        else:
            return 'Official'
    
    def create_contacts_local_officials(self) -> pd.DataFrame:
        """
        Create contacts_local_officials gold table
        
        Extract official names from meeting transcripts
        """
        logger.info("Creating contacts_local_officials gold table...")
        
        # Load meetings transcripts
        transcripts_path = self.meetings_gold_dir / "meetings_transcripts.parquet"
        
        if not transcripts_path.exists():
            logger.error(f"Meetings transcripts not found: {transcripts_path}")
            logger.error("Run: python scripts/create_all_gold_tables.py --meetings-only")
            return pd.DataFrame()
        
        logger.info(f"Loading {transcripts_path}")
        df = pd.read_parquet(transcripts_path)
        logger.info(f"  Loaded {len(df):,} meeting transcripts")
        
        # Extract officials from each meeting
        all_officials = []
        
        for idx, row in df.iterrows():
            if idx % 10000 == 0:
                logger.info(f"  Processed {idx:,}/{len(df):,} meetings...")
            
            officials = self.extract_officials_from_transcript(
                row['transcript_text'],
                row['jurisdiction']
            )
            
            for official in officials:
                official['meeting_id'] = row['meeting_id']
                all_officials.append(official)
        
        officials_df = pd.DataFrame(all_officials)
        
        if officials_df.empty:
            logger.warning("No officials extracted from transcripts")
            return pd.DataFrame()
        
        # Save FULL attendance data (meeting-level) FIRST
        logger.info(f"  Extracted {len(officials_df):,} official mentions")
        
        # Create meeting attendance table (many-to-many junction table)
        attendance_df = officials_df[[
            'meeting_id', 'name', 'title', 'jurisdiction', 'source'
        ]].copy()
        attendance_df['last_updated'] = datetime.now().isoformat()
        
        attendance_output = self.output_dir / "contacts_meeting_attendance.parquet"
        attendance_df.to_parquet(attendance_output, index=False)
        logger.success(f"Created {attendance_output} with {len(attendance_df):,} attendance records")
        
        # Now aggregate by name + jurisdiction for summary table
        grouped = officials_df.groupby(['name', 'jurisdiction']).agg({
            'title': lambda x: x.mode()[0] if len(x.mode()) > 0 else x.iloc[0],  # Most common title
            'meeting_id': 'count',  # Number of meetings attended
            'source': 'first'
        }).reset_index()
        
        grouped.rename(columns={'meeting_id': 'meetings_count'}, inplace=True)
        
        # Add metadata
        grouped['last_updated'] = datetime.now().isoformat()
        grouped['data_source'] = 'LocalView meeting transcripts'
        
        # Reorder columns
        officials_df = grouped[[
            'name', 'title', 'jurisdiction', 
            'meetings_count', 'source', 'data_source', 'last_updated'
        ]]
        
        # Save to parquet
        output_path = self.output_dir / "contacts_local_officials.parquet"
        officials_df.to_parquet(output_path, index=False)
        logger.success(f"Created {output_path} with {len(officials_df):,} unique officials")
        
        # Show sample
        logger.info("\n📊 Sample Officials:")
        sample = officials_df.sort_values('meetings_count', ascending=False).head(10)
        for _, row in sample.iterrows():
            logger.info(f"  {row['name']} ({row['title']}) - {row['jurisdiction']} - {row['meetings_count']} meetings")
        
        return officials_df
    
    def create_contacts_state_legislators(self) -> pd.DataFrame:
        """
        Create contacts_state_legislators gold table
        
        Fetch from Open States API
        """
        logger.info("Creating contacts_state_legislators gold table...")
        
        try:
            from discovery.openstates_sources import get_api_key, OPENSTATES_API_BASE
            import requests
        except ImportError:
            logger.error("requests library not installed. Install with: pip install requests")
            return pd.DataFrame()
        
        api_key = get_api_key()
        
        if not api_key:
            logger.warning("⚠️  OPENSTATES_API_KEY not set - skipping state legislators")
            logger.warning("   Sign up at: https://openstates.org/accounts/signup/")
            logger.warning("   Add to .env: OPENSTATES_API_KEY=your-key")
            return pd.DataFrame()
        
        logger.info("Fetching state legislators from Open States API...")
        
        # For now, create placeholder structure
        # Full implementation would fetch from Open States API
        legislators_df = pd.DataFrame(columns=[
            'name', 'title', 'jurisdiction', 'party', 'district',
            'chamber', 'email', 'phone', 'data_source', 'last_updated'
        ])
        
        output_path = self.output_dir / "contacts_state_legislators.parquet"
        legislators_df.to_parquet(output_path, index=False)
        logger.info(f"Created {output_path} (placeholder - add Open States API implementation)")
        
        return legislators_df
    
    def create_contacts_school_board(self) -> pd.DataFrame:
        """
        Create contacts_school_board gold table
        
        Extract from school district data sources
        """
        logger.info("Creating contacts_school_board gold table...")
        
        # Placeholder for now
        school_board_df = pd.DataFrame(columns=[
            'name', 'title', 'school_district', 'jurisdiction',
            'email', 'phone', 'data_source', 'last_updated'
        ])
        
        output_path = self.output_dir / "contacts_school_board.parquet"
        school_board_df.to_parquet(output_path, index=False)
        logger.info(f"Created {output_path} (placeholder)")
        
        return school_board_df
    
    def create_all_contacts_tables(self):
        """Create all contacts gold tables"""
        logger.info("=" * 60)
        logger.info("CREATING CONTACTS GOLD TABLES")
        logger.info("=" * 60)
        
        # Create each table
        self.create_contacts_local_officials()
        self.create_contacts_state_legislators()
        self.create_contacts_school_board()
        
        logger.success("=" * 60)
        logger.success("ALL CONTACTS GOLD TABLES CREATED!")
        logger.success("=" * 60)
        
        # Show summary
        contacts_files = list(self.output_dir.glob("contacts_*.parquet"))
        if contacts_files:
            logger.info(f"\nCreated {len(contacts_files)} contacts tables:")
            for file in sorted(contacts_files):
                df_check = pd.read_parquet(file)
                size_mb = file.stat().st_size / (1024 * 1024)
                logger.info(f"  - {file.name}: {len(df_check):,} records ({size_mb:.2f} MB)")


def main():
    """Main execution function"""
    creator = ContactsGoldTableCreator()
    creator.create_all_contacts_tables()


if __name__ == "__main__":
    main()
