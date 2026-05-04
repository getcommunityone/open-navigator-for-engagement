"""
NCES School District Data Ingestion to PostgreSQL

Downloads and processes National Center for Education Statistics (NCES)
Common Core of Data (CCD) to get comprehensive school district information.

Data Source: https://nces.ed.gov/ccd/
Primary Dataset: Local Education Agency (School District) Universe Survey

Loads into PostgreSQL tables:
- jurisdictions_details_schools: District directory info (addresses, websites, phones)
- organizations_school_members: Student enrollment by district
- organizations_school_staff: Staff counts by district and category
"""
import asyncio
import csv
import zipfile
from typing import Dict, Optional
from datetime import datetime
from pathlib import Path

import httpx
import psycopg2
from psycopg2.extras import execute_batch
from loguru import logger


class NCESPostgreSQLIngestion:
    """Ingest NCES Common Core of Data for school districts to PostgreSQL."""
    
    # PostgreSQL connection
    DB_HOST = "localhost"
    DB_PORT = 5433
    DB_NAME = "open_navigator"
    DB_USER = "postgres"
    DB_PASSWORD = "password"
    
    def __init__(self):
        """Initialize ingestion."""
        self.cache_dir = Path("data/cache/nces")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.conn = None
    
    def get_connection(self):
        """Get PostgreSQL connection."""
        if not self.conn or self.conn.closed:
            self.conn = psycopg2.connect(
                host=self.DB_HOST,
                port=self.DB_PORT,
                database=self.DB_NAME,
                user=self.DB_USER,
                password=self.DB_PASSWORD
            )
        return self.conn
    
    def get_nces_files(self) -> dict:
        """Get NCES file URLs for Directory, Membership, and Staff data."""
        logger.info("Using known NCES file URLs for SY 2024-25 version 1a...")
        
        return {
            'directory': {
                'url': 'https://nces.ed.gov/ccd/Data/zip/ccd_lea_029_2425_w_1a_073025.zip',
                'size': '2.76 MB',
                'cache_file': 'nces_directory.csv',
                'table': 'jurisdictions_details_schools'
            },
            'membership': {
                'url': 'https://nces.ed.gov/ccd/Data/zip/ccd_lea_052_2425_l_1a_073025.zip',
                'size': '62 MB',
                'cache_file': 'nces_membership.csv',
                'table': 'organizations_school_members'
            },
            'staff': {
                'url': 'https://nces.ed.gov/ccd/Data/zip/ccd_lea_059_2425_l_1a_073025.zip',
                'size': '5.8 MB',
                'cache_file': 'nces_staff.csv',
                'table': 'organizations_school_staff'
            },
            'school_year': "2024-25"
        }
    
    async def download_file(self, url: str, cache_file: Path, file_type: str, school_year: str) -> Path:
        """Download NCES file from URL and extract if ZIP."""
        # Check cache first
        if cache_file.exists():
            age_days = (datetime.now() - datetime.fromtimestamp(cache_file.stat().st_mtime)).days
            if age_days < 30:
                logger.info(f"✅ Using cached {file_type} data (age: {age_days} days)")
                return cache_file
        
        async with httpx.AsyncClient(timeout=300.0, follow_redirects=True) as client:
            logger.info(f"📥 Downloading {file_type} from: {url}")
            response = await client.get(url)
            response.raise_for_status()
            
            if url.endswith('.zip'):
                zip_path = self.cache_dir / f"nces_{file_type}_{school_year.replace('-', '')}.zip"
                zip_path.write_bytes(response.content)
                logger.info(f"✅ Downloaded {len(response.content) / 1024 / 1024:.2f} MB ZIP")
                
                # Extract CSV
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    csv_files = [f for f in zip_ref.namelist() 
                                if f.endswith(('.csv', '.txt')) and not f.startswith('__MACOSX')]
                    
                    if not csv_files:
                        raise ValueError(f"No CSV found in ZIP")
                    
                    preferred = [f for f in csv_files if 'lea' in f.lower()]
                    csv_filename = preferred[0] if preferred else csv_files[0]
                    
                    logger.info(f"Extracting {csv_filename}...")
                    zip_ref.extract(csv_filename, self.cache_dir)
                    extracted = self.cache_dir / csv_filename
                    extracted.rename(cache_file)
                    logger.info(f"✅ Extracted to {cache_file}")
            else:
                cache_file.write_bytes(response.content)
                logger.info(f"✅ Downloaded {len(response.content) / 1024 / 1024:.2f} MB")
            
            return cache_file
    
    def create_tables(self):
        """Create PostgreSQL tables for NCES data."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Drop existing tables
        cursor.execute("DROP TABLE IF EXISTS jurisdictions_details_schools CASCADE")
        cursor.execute("DROP TABLE IF EXISTS organizations_school_members CASCADE")
        cursor.execute("DROP TABLE IF EXISTS organizations_school_staff CASCADE")
        
        # Create jurisdictions_details_schools table
        cursor.execute("""
            CREATE TABLE jurisdictions_details_schools (
                nces_id VARCHAR(20) PRIMARY KEY,
                district_name VARCHAR(500),
                state_code VARCHAR(2),
                state_fips VARCHAR(2),
                street_address VARCHAR(500),
                city VARCHAR(200),
                zip VARCHAR(10),
                phone VARCHAR(50),
                website VARCHAR(500),
                district_type VARCHAR(200),
                num_schools INTEGER,
                school_year VARCHAR(20),
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW()
            )
        """)
        
        # Create organizations_school_members table
        cursor.execute("""
            CREATE TABLE organizations_school_members (
                id SERIAL PRIMARY KEY,
                nces_id VARCHAR(20),
                state_code VARCHAR(2),
                state_fips VARCHAR(2),
                total_students INTEGER,
                school_year VARCHAR(20),
                created_at TIMESTAMP DEFAULT NOW(),
                FOREIGN KEY (nces_id) REFERENCES jurisdictions_details_schools(nces_id)
            )
        """)
        
        # Create organizations_school_staff table
        cursor.execute("""
            CREATE TABLE organizations_school_staff (
                id SERIAL PRIMARY KEY,
                nces_id VARCHAR(20),
                state_code VARCHAR(2),
                state_fips VARCHAR(2),
                staff_category VARCHAR(200),
                staff_count NUMERIC(10, 2),
                school_year VARCHAR(20),
                created_at TIMESTAMP DEFAULT NOW(),
                FOREIGN KEY (nces_id) REFERENCES jurisdictions_details_schools(nces_id)
            )
        """)
        
        # Create indexes
        cursor.execute("CREATE INDEX idx_schools_state ON jurisdictions_details_schools(state_code)")
        cursor.execute("CREATE INDEX idx_schools_nces ON jurisdictions_details_schools(nces_id)")
        cursor.execute("CREATE INDEX idx_orgs_school_members_nces ON organizations_school_members(nces_id)")
        cursor.execute("CREATE INDEX idx_orgs_school_staff_nces ON organizations_school_staff(nces_id)")
        cursor.execute("CREATE INDEX idx_orgs_school_staff_category ON organizations_school_staff(staff_category)")
        
        conn.commit()
        logger.info("✅ Created PostgreSQL tables")
    
    def load_directory_data(self, csv_path: Path, school_year: str):
        """Load directory data into jurisdictions_details_schools table."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        records = []
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                records.append((
                    row.get('LEAID'),
                    row.get('LEA_NAME'),
                    row.get('ST'),
                    row.get('FIPST'),
                    row.get('LSTREET1'),
                    row.get('LCITY'),
                    row.get('LZIP'),
                    row.get('PHONE'),
                    row.get('WEBSITE'),
                    row.get('LEA_TYPE_TEXT'),
                    int(row.get('OPERATIONAL_SCHOOLS', 0)) if row.get('OPERATIONAL_SCHOOLS') else None,
                    school_year
                ))
        
        execute_batch(cursor, """
            INSERT INTO jurisdictions_details_schools 
            (nces_id, district_name, state_code, state_fips, street_address, city, zip, 
             phone, website, district_type, num_schools, school_year)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (nces_id) DO UPDATE SET
                district_name = EXCLUDED.district_name,
                state_code = EXCLUDED.state_code,
                state_fips = EXCLUDED.state_fips,
                street_address = EXCLUDED.street_address,
                city = EXCLUDED.city,
                zip = EXCLUDED.zip,
                phone = EXCLUDED.phone,
                website = EXCLUDED.website,
                district_type = EXCLUDED.district_type,
                num_schools = EXCLUDED.num_schools,
                school_year = EXCLUDED.school_year,
                updated_at = NOW()
        """, records, page_size=1000)
        
        conn.commit()
        logger.info(f"✅ Loaded {len(records):,} directory records")
    
    def load_membership_data(self, csv_path: Path, school_year: str):
        """Load membership data into organizations_school_members table."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Aggregate student counts by district
        enrollment = {}
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                leaid = row.get('LEAID')
                student_count = row.get('STUDENT_COUNT')
                
                if leaid and student_count and student_count.strip():
                    try:
                        count = int(student_count)
                        if leaid not in enrollment:
                            enrollment[leaid] = {
                                'state': row.get('ST'),
                                'state_fips': row.get('FIPST'),
                                'total': 0
                            }
                        enrollment[leaid]['total'] += count
                    except ValueError:
                        continue
        
        records = [
            (leaid, data['state'], data['state_fips'], data['total'], school_year)
            for leaid, data in enrollment.items()
        ]
        
        execute_batch(cursor, """
            INSERT INTO organizations_school_members 
            (nces_id, state_code, state_fips, total_students, school_year)
            VALUES (%s, %s, %s, %s, %s)
        """, records, page_size=1000)
        
        conn.commit()
        logger.info(f"✅ Loaded {len(records):,} membership records")
    
    def load_staff_data(self, csv_path: Path, school_year: str):
        """Load staff data into organizations_school_staff table."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        records = []
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                staff_count = row.get('STAFF_COUNT')
                if staff_count and staff_count.strip():
                    try:
                        count = float(staff_count)
                        records.append((
                            row.get('LEAID'),
                            row.get('ST'),
                            row.get('FIPST'),
                            row.get('STAFF'),
                            count,
                            school_year
                        ))
                    except ValueError:
                        continue
        
        execute_batch(cursor, """
            INSERT INTO organizations_school_staff 
            (nces_id, state_code, state_fips, staff_category, staff_count, school_year)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, records, page_size=1000)
        
        conn.commit()
        logger.info(f"✅ Loaded {len(records):,} staff records")
    
    async def ingest_all(self):
        """Complete ingestion pipeline."""
        files_info = self.get_nces_files()
        school_year = files_info['school_year']
        
        # Download all files
        logger.info("\n" + "=" * 80)
        logger.info("📥 DOWNLOADING NCES FILES")
        logger.info("=" * 80)
        
        downloaded_files = {}
        for file_type in ['directory', 'membership', 'staff']:
            info = files_info[file_type]
            cache_file = self.cache_dir / info['cache_file']
            downloaded_files[file_type] = await self.download_file(
                info['url'], cache_file, file_type, school_year
            )
        
        # Create tables
        logger.info("\n" + "=" * 80)
        logger.info("📊 CREATING POSTGRESQL TABLES")
        logger.info("=" * 80)
        self.create_tables()
        
        # Load directory data first (it has the primary key)
        logger.info("\n" + "=" * 80)
        logger.info("📁 LOADING DIRECTORY DATA")
        logger.info("=" * 80)
        self.load_directory_data(downloaded_files['directory'], school_year)
        
        # Load membership data
        logger.info("\n" + "=" * 80)
        logger.info("👥 LOADING MEMBERSHIP DATA")
        logger.info("=" * 80)
        self.load_membership_data(downloaded_files['membership'], school_year)
        
        # Load staff data
        logger.info("\n" + "=" * 80)
        logger.info("👨‍🏫 LOADING STAFF DATA")
        logger.info("=" * 80)
        self.load_staff_data(downloaded_files['staff'], school_year)
        
        # Show stats
        logger.info("\n" + "=" * 80)
        logger.info("📈 SUMMARY STATISTICS")
        logger.info("=" * 80)
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM jurisdictions_details_schools")
        logger.info(f"Total districts: {cursor.fetchone()[0]:,}")
        
        cursor.execute("SELECT COUNT(*) FROM organizations_school_members")
        logger.info(f"Total enrollment records: {cursor.fetchone()[0]:,}")
        
        cursor.execute("SELECT SUM(total_students) FROM organizations_school_members")
        total_students = cursor.fetchone()[0]
        if total_students:
            logger.info(f"Total students nationwide: {int(total_students):,}")
        
        cursor.execute("SELECT COUNT(*) FROM organizations_school_staff")
        logger.info(f"Total staff records: {cursor.fetchone()[0]:,}")
        
        cursor.execute("""
            SELECT state_code, COUNT(*) as count 
            FROM jurisdictions_details_schools 
            GROUP BY state_code 
            ORDER BY count DESC 
            LIMIT 10
        """)
        logger.info("\nTop 10 states by district count:")
        for row in cursor.fetchall():
            logger.info(f"  {row[0]}: {row[1]:,} districts")
        
        logger.info("\n✅ NCES ingestion complete!")


async def main():
    """Run NCES ingestion."""
    ingestion = NCESPostgreSQLIngestion()
    await ingestion.ingest_all()


if __name__ == "__main__":
    asyncio.run(main())
