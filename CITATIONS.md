# Citations and Acknowledgments

This project uses several open datasets and research contributions. Please cite the following works when using or referencing this project.

## 📚 **Datasets**

### **MeetingBank Dataset**

We use the MeetingBank benchmark dataset for meeting summarization and analysis.

**Citation:**
```
Yebowen Hu, Tim Ganter, Hanieh Deilamsalehy, Franck Dernoncourt, Hassan Foroosh, Fei Liu.
"MeetingBank: A Benchmark Dataset for Meeting Summarization"
In Proceedings of the 61st Annual Meeting of the Association for Computational Linguistics (ACL),
July 2023, Toronto, Canada.
```

**BibTeX:**
```bibtex
@inproceedings{hu-etal-2023-meetingbank,
    title = "MeetingBank: A Benchmark Dataset for Meeting Summarization",
    author = "Yebowen Hu and Tim Ganter and Hanieh Deilamsalehy and Franck Dernoncourt and Hassan Foroosh and Fei Liu",
    booktitle = "Proceedings of the 61st Annual Meeting of the Association for Computational Linguistics (ACL)",
    month = July,
    year = "2023",
    address = "Toronto, Canada",
    publisher = "Association for Computational Linguistics",
}
```

**Resources:**
- Paper: https://arxiv.org/abs/2305.17529
- Dataset: https://huggingface.co/datasets/huuuyeah/meetingbank
- Zenodo: https://zenodo.org/record/7989108

**What we use:**
- 1,366 city council meetings from 6 U.S. cities
- Meeting transcripts and summaries
- Used for: Meeting discovery, transcript analysis, summarization benchmarking

---

## 🗂️ **Other Data Sources**

### **U.S. Census Bureau**
- Geographic boundaries and demographic data
- Source: https://www.census.gov/
- License: Public Domain (U.S. Government)

### **Open States / Plural Policy** ⭐
- Comprehensive state and local legislative information
- Organization: Plural Policy (formerly Open States Foundation)
- Source: https://openstates.org/
- API: https://openstates.org/api/
- Data Downloads: https://open.pluralpolicy.com/data/
- License: Various (check per state)
- API Key: Required for access (free tier: 50,000 requests/month)

**Coverage:**
- All 50 states + DC + Puerto Rico
- 7,300+ state legislators
- Millions of bills, votes, and legislative sessions
- Monthly PostgreSQL database dumps (9.8GB+)

**What we use:**
- Bulk legislative session downloads (CSV/JSON/PostgreSQL)
- State legislator data with committee assignments
- Bill tracking and voting records
- Legislative video sources (YouTube channels, Granicus portals)

**Resources:**
- Open Data: https://open.pluralpolicy.com/data/
- Scrapers Repository: https://github.com/openstates/openstates-scrapers
- Local Database Setup: https://docs.openstates.org/contributing/local-database/
- Code of Conduct: https://docs.openstates.org/code-of-conduct/
- Schema Documentation: https://github.com/openstates/people/blob/master/schema.md

**BibTeX:**
```bibtex
@software{openstates,
    title = {Open States},
    author = {{Plural Policy}},
    year = {2024},
    url = {https://openstates.org/},
    note = {Comprehensive state legislative data for all 50 U.S. states}
}
```

**Potential Contributions:**
- Our scraper patterns could be contributed to openstates-scrapers
- Video source discovery could enhance their data
- We follow their Code of Conduct for all contributions

### **LegiScan** ⭐
- Comprehensive legislative tracking and bill text database
- Organization: LegiScan LLC
- Source: https://legiscan.com/
- API: https://legiscan.com/legiscan
- License: API access requires subscription (free tier available with limitations)
- Coverage: All 50 states + U.S. Congress + Washington D.C.
- API Key: Required for access (free tier: limited requests)

**Coverage:**
- Real-time legislative tracking for all U.S. states and Congress
- Full bill text, amendments, and legislative documents
- Roll call votes and voting records
- Committee assignments and hearings
- Bill status tracking and history
- Sponsor and co-sponsor information
- Bill text in PDF, HTML, and plain text formats

**What we use:**
- Bill text downloads and full-text search
- Legislative document archives
- Bill status and tracking data
- Voting records and roll calls
- Supplement to Open States data for missing jurisdictions
- Historical legislative data back to 2011

**API Features:**
- GetBillText: Retrieve full bill text in multiple formats
- GetBill: Detailed bill metadata and status
- GetRollCall: Voting records with legislator positions
- GetSponsor: Sponsor and co-sponsor information
- Search: Full-text search across all bills
- GetDatasetList: Bulk dataset downloads

**Resources:**
- API Documentation: https://legiscan.com/legiscan
- Dataset Downloads: https://legiscan.com/datasets
- Search Interface: https://legiscan.com/gaits/search
- State Coverage: https://legiscan.com/legiscan/states

**BibTeX:**
```bibtex
@software{legiscan,
    title = {LegiScan},
    author = {{LegiScan LLC}},
    year = {2024},
    url = {https://legiscan.com/},
    note = {Comprehensive legislative tracking and bill text database covering all 50 U.S. states and Congress}
}
```

**Complementary to Open States:**
- LegiScan provides bill text in multiple formats (PDF, HTML, plain text)
- Historical data back to 2011 for all states
- Real-time updates and notifications
- More comprehensive document archives
- Paid API provides higher rate limits and bulk downloads
- Use LegiScan for bill text analysis, Open States for structured legislative data

### **Harvard Dataverse**
- Meeting datasets and civic engagement research
- Source: https://dataverse.harvard.edu/
- License: Varies by dataset

### **City Scrapers** ⭐
- Open source civic tech project for scraping local government meetings
- Organization: Documenters.org / City Bureau
- Source: https://cityscrapers.org/
- GitHub: https://github.com/city-scrapers
- License: MIT License (open source)
- Coverage: Chicago, Pittsburgh, Detroit, Cleveland, Los Angeles (250+ government agencies)
- What we use: Validated meeting URLs, Legistar/Granicus platform endpoints, spider code for scraper patterns
- Used for: Meeting discovery, URL extraction, platform detection, scraper validation

**City Scrapers Repositories:**
- Chicago: https://github.com/city-scrapers/city-scrapers (~100 agencies)
- Pittsburgh: https://github.com/city-scrapers/city-scrapers-pitt (~30 agencies)
- Detroit: https://github.com/city-scrapers/city-scrapers-detroit (~40 agencies)
- Cleveland: https://github.com/city-scrapers/city-scrapers-cle (~30 agencies)
- Los Angeles: https://github.com/city-scrapers/city-scrapers-la (~50 agencies)

**BibTeX:**
```bibtex
@software{city_scrapers,
    title = {City Scrapers},
    author = {{Documenters.org}},
    year = {2024},
    url = {https://cityscrapers.org/},
    note = {Open source civic tech project providing validated scrapers for local government meetings across major U.S. cities}
}
```

### **Google Civic Information API** ⭐
- Government officials, polling locations, and election data
- Organization: Google LLC
- API Documentation: https://developers.google.com/civic-information
- License: Free (with quota limits)
- Rate Limit: 25,000 requests/day (free tier)
- Coverage: U.S. federal, state, and local government officials; polling locations; election data
- What we use: Elected officials by address, representative contact info, voting districts
- Used for: Contact discovery, official verification, civic engagement tools

**API Endpoints Used:**
- Representatives by Address: Get all elected officials for a given address
- Elections: Voter information, polling locations, ballot information
- Divisions: Geographic/political divisions (OCD-IDs)

**BibTeX:**
```bibtex
@misc{google_civic_api,
    title = {Google Civic Information API},
    author = {{Google LLC}},
    year = {2024},
    url = {https://developers.google.com/civic-information},
    note = {API providing government official contact information, election data, and polling locations}
}
```

**Terms of Service:**
- Attribution required when displaying official data
- Caching limited to 30 days
- Must comply with Google API Terms of Service

### **YouTube Data API v3** ⭐
- Video metadata, channel information, and search for government meetings
- Organization: Google LLC
- API Documentation: https://developers.google.com/youtube/v3
- License: Free (with quota limits)
- Rate Limit: 10,000 units/day (free tier), search costs 100 units per request
- Coverage: Global video platform with millions of government channels
- What we use: Government channel discovery, meeting video metadata, transcript availability
- Used for: Video discovery, channel statistics, meeting video archival

**API Features Used:**
- Search: Find government channels by jurisdiction name
- Channels: Get channel metadata, subscriber counts, video counts
- Videos: Metadata including title, description, upload date, duration
- Captions: Check for closed caption/transcript availability

**BibTeX:**
```bibtex
@misc{youtube_data_api,
    title = {YouTube Data API v3},
    author = {{Google LLC}},
    year = {2024},
    url = {https://developers.google.com/youtube/v3},
    note = {API for accessing YouTube video metadata, channel information, and search functionality}
}
```

**Terms of Service:**
- YouTube API Services Terms: https://developers.google.com/youtube/terms/api-services-terms-of-service
- Attribution required with YouTube logo
- Quota limits enforced (10,000 units/day free)
- Video embeds must use official YouTube player

### **Ballotpedia** ⭐
- Ballot measures, referendums, and propositions
- Organization: Lucy Burns Institute
- Source: https://ballotpedia.org/
- API: https://ballotpedia.org/API-documentation
- License: API access is limited at scale (paid tier available)
- Coverage: All 50 states, historical measures back to 1990s
- Used for: Tracking fluoridation votes, school bond measures, health policy propositions

### **MIT Election Data + Science Lab**
- Presidential, Congressional, and gubernatorial election results
- Organization: Massachusetts Institute of Technology
- Source: https://electionlab.mit.edu/data
- Repository: https://github.com/MEDSL/official-returns
- License: Free for research and commercial use
- Coverage: 1976-present, county-level results
- Used for: Political composition analysis, jurisdiction context

### **OpenElections**
- State-by-state certified election results in standardized CSV format
- Source: https://openelections.net/
- GitHub: https://github.com/openelections
- License: Open source (various by state)
- Coverage: All 50 states (various completion levels), precinct-level data
- Used for: Detailed election results, local race outcomes, advocacy targeting

### **Open Civic Data (OCD) Standards**
- Division identifiers and civic data standards
- Specification: https://open-civic-data.readthedocs.io/en/latest/proposals/0002.html
- Repository: https://github.com/opencivicdata/ocd-division-ids
- License: Open source
- Used for: Standardized jurisdiction identifiers, cross-platform compatibility

### **Popolo Project**
- International open government data specification for people, organizations, and elected positions
- Specification: https://www.popoloproject.com/
- GitHub: https://github.com/popolo-project/popolo-spec
- Documentation: http://www.popoloproject.com/specs/
- License: Creative Commons Attribution 4.0 International

### **BillMap** ⭐
- Tracks bill text similarity across all 50 U.S. states to identify copy-paste legislation and model bill influence
- Organization: Sunlight Foundation / @unitedstates community
- Repository: https://github.com/unitedstates/BillMap
- Research: Anderson et al., "Detecting Policy Influence in Legislatures" (2019)
- Paper: https://arxiv.org/abs/1906.03699
- Live Demo: https://billmap.cs.princeton.edu/
- License: Open source
- Coverage: All 50 states, tracks legislative text diffusion across jurisdictions
- Used for: Identifying model legislation, tracking policy influence, finding similar bills across states
- Method: Text similarity analysis, n-gram matching, bill text alignment

**What we use:**
- Bill similarity detection algorithms
- Model legislation tracking methodology
- Cross-state policy diffusion analysis
- Legislative text comparison techniques

**BibTeX:**
```bibtex
@article{anderson2019billmap,
    title = {Detecting Policy Influence in Legislatures},
    author = {Anderson, Evan and Fowler, Anthony and Grossmann, Matt and Sahn, Alexander and Shiraito, Yuki},
    journal = {arXiv preprint arXiv:1906.03699},
    year = {2019},
    url = {https://arxiv.org/abs/1906.03699}
}
```

### **@unitedstates Images Repository** ⭐
- High-resolution photos of all U.S. Congress members (past and present)
- Organization: @unitedstates community (Sunlight Foundation legacy project)
- Repository: https://github.com/unitedstates/images
- CDN: https://theunitedstates.io/images/congress/
- License: Public domain (government photos)
- Coverage: All U.S. Senators and Representatives (1789-present), updated regularly
- Image Format: JPEG, multiple resolutions (original, 450x550, 225x275)
- Used for: Legislator profile photos, visual identification, representative directories

**Image URL Format:**
```
https://theunitedstates.io/images/congress/original/[bioguide_id].jpg
https://theunitedstates.io/images/congress/450x550/[bioguide_id].jpg
https://theunitedstates.io/images/congress/225x275/[bioguide_id].jpg
```

**Example:**
```
https://theunitedstates.io/images/congress/original/P000197.jpg
(Nancy Pelosi, bioguide_id: P000197)
```

**What we use:**
- Legislator profile photos for federal representatives
- Visual identification in advocacy tools
- Representative directories and contact pages
- Cross-referenced with Open States data using bioguide IDs

**Related Projects:**
- **congress-legislators**: https://github.com/unitedstates/congress-legislators (YAML data files)
- **congress**: https://github.com/unitedstates/congress (scraping tools)
- **districts**: https://github.com/unitedstates/districts (GeoJSON boundaries)

---

## 💰 **Nonprofit Financial Data**

### **GivingTuesday 990 Data Infrastructure** ⭐

We use the GivingTuesday 990 Data Lake for detailed nonprofit financial data from IRS Form 990 XML filings.

**Organization:** GivingTuesday  
**Website:** https://990data.givingtuesday.org/  
**Data Lake:** `s3://gt990datalake-rawdata` (AWS S3, us-east-1 Virginia, Public Access)  
**Console:** https://us-east-1.console.aws.amazon.com/s3/buckets/gt990datalake-rawdata  
**License:** Public domain (IRS data) + Open source tools  
**Access:** Free, no AWS credentials required (anonymous access via `--no-sign-request`)

**What we use:**
- **Raw 990 XMLs**: Individual e-filed Form 990 returns in XML format (1-2 MB each)
- **Indices**: CSV/Parquet files listing all available 990s with metadata
- **Coverage**: 5.4M+ e-filed Form 990s (2011-present, ~300K new filings/year)
- **Scale**: ~10 TB of raw XML data
- **Data extracted**: Revenue, expenses, assets, liabilities, grants, programs, officer compensation, mission statements, website URLs

**Data Lake Structure:**
```
s3://gt990datalake-rawdata/
├── EfileData/
│   ├── XmlFiles/              # Individual 990 XMLs (~5.4M files, ~10 TB)
│   │   └── [OBJECT_ID]_public.xml  (e.g., 202233259349300703_public.xml)
│   └── XmlZips/               # ZIP archives (97 files, ~38 GB → ~95 GB uncompressed)
│       └── YYYY_TEOS_XML_*.zip     (e.g., 2023_TEOS_XML_01A.zip ~400 MB)
└── Indices/
    └── 990xmls/               # CSV indices with metadata
        └── index_all_years_efiledata_xmls_created_on_2023-10-29.csv (~925 MB)
```

**Download Strategies:**

| Approach | Best For | Time | Bandwidth | Storage |
|----------|----------|------|-----------|---------|
| **Individual XMLs** | Single state or targeted download | ~2 hrs (22K orgs) | 32 GB | 32 GB |
| **ZIP Archives** | All states / nationwide | ~6 hrs total | 38 GB | 95 GB |

**Choose Individual XMLs when:**
- You need data for 1-5 states only
- You want to download only specific EINs
- Storage space is limited
- You want incremental caching (download as needed)

**Choose ZIP Archives when:**
- You need all 50 states
- You're building a comprehensive nonprofit database
- You have 100+ GB storage
- You want offline access to all filings

**S3 Access Examples:**

**Individual XMLs (for single state or targeted download):**
```bash
# List index files (no credentials needed)
aws s3 ls s3://gt990datalake-rawdata/Indices/990xmls/ --no-sign-request

# Download index (~925 MB)
aws s3 cp s3://gt990datalake-rawdata/Indices/990xmls/index_all_years_efiledata_xmls_created_on_2023-10-29.csv . --no-sign-request

# Download specific XML
aws s3 cp s3://gt990datalake-rawdata/EfileData/XmlFiles/202233259349300703_public.xml . --no-sign-request

# Batch download for single state (using our script)
python scripts/batch_download_990s.py --state MA --health-only --concurrent 1000
```

**ZIP Archives (for all states / nationwide):**
```bash
# Download all 97 ZIPs (~38 GB) to local directory
./scripts/download_990_zips.sh

# Extract all ZIPs to get ~384K XMLs (~95 GB)
./scripts/extract_990_zips.sh

# Build local index for fast lookup
python scripts/build_990_local_index.py

# Now enrich from local files (no network needed!)
python scripts/enrich_all_states_990.py
```

**Index Schema:**
The CSV index contains columns: `EIN`, `TaxPeriod`, `ObjectId`, `URL`, `FormType`, `OrganizationName`, `DLN`, `SubmittedOn`

**Python Access:**
```python
import boto3
from botocore import UNSIGNED
from botocore.config import Config

# Configure anonymous S3 client
s3 = boto3.client('s3', config=Config(signature_version=UNSIGNED))

# Download XML
xml_obj = s3.get_object(
    Bucket='gt990datalake-rawdata',
    Key='EfileData/XmlFiles/202233259349300703_public.xml'
)
xml_content = xml_obj['Body'].read()
```

**BibTeX:**
```bibtex
@misc{givingtuesday990data,
    title = {GivingTuesday 990 Data Infrastructure},
    author = {{GivingTuesday}},
    year = {2023},
    url = {https://990data.givingtuesday.org/},
    note = {Collaborative data lake of standardized IRS Form 990 XML filings}
}
```

**Attribution:** When publishing analyses using this data, please cite both:
1. GivingTuesday 990 Data Infrastructure: https://990data.givingtuesday.org/
2. Our enrichment tools: https://github.com/getcommunityone/open-navigator-for-engagement

---

### **Google Cloud Public Datasets: IRS 990** ⭐

Google hosts the complete IRS Form 990 dataset in BigQuery for fast SQL-based querying.

**Platform:** Google Cloud BigQuery  
**Dataset:** `bigquery-public-data.irs_990`  
**Table:** `bigquery-public-data.irs_990.irs_990_xml`  
**Documentation:** https://console.cloud.google.com/marketplace/product/internal-revenue-service/irs-990  
**Cost:** First 1 TB of queries per month is **FREE**  
**Coverage:** All e-filed Form 990s (2011-present, 5M+ records)

**What we use:**
- **Mission statements**: Extracted from `return_header` or `part_i_mission_desc` fields
- **Website URLs**: Found in `website_address_txt` field
- **Financial data**: All Form 990 fields accessible via SQL
- **Fast bulk queries**: Extract data for 1M+ orgs in seconds (vs hours downloading XMLs)

**Advantages:**
- ✅ No local XML downloads needed
- ✅ Single SQL query to bulk-extract fields
- ✅ Serverless (no infrastructure to manage)
- ✅ Fast (queries complete in seconds)
- ✅ Free tier covers most research use cases

**Example Query:**
```sql
SELECT 
  ein,
  org_name,
  website_address_txt,
  part_i_mission_desc,
  total_revenue_current_year,
  total_expenses_current_year
FROM `bigquery-public-data.irs_990.irs_990_2023`
WHERE state = 'AL'
  AND ntee_code LIKE 'E%'
LIMIT 1000;
```

**BibTeX:**
```bibtex
@misc{googlecloud_irs990,
    title = {IRS 990 Public Dataset},
    author = {{Google Cloud Public Datasets}},
    year = {2024},
    publisher = {Google Cloud Platform},
    url = {https://console.cloud.google.com/marketplace/product/internal-revenue-service/irs-990},
    note = {BigQuery public dataset of IRS Form 990 e-file data}
}
```

**Attribution:** When using BigQuery 990 data, cite:
1. IRS 990 Public Dataset (Google Cloud)
2. Internal Revenue Service (original data source)

---

### **National Center for Charitable Statistics (NCCS) Unified BMF** ⭐

The NCCS Unified BMF is a longitudinal nonprofit dataset specifically designed for AI and "Lakehouse" projects with pre-geocoded locations and Census integration.

**Organization:** National Center for Charitable Statistics (NCCS), Urban Institute  
**Website:** https://nccs.urban.org/  
**Dataset:** Unified BMF (Business Master File)  
**Documentation:** https://nccs.urban.org/project/irs-exempt-organizations-business-master-file  
**License:** Public domain (IRS data) + Urban Institute terms  
**Released:** Late 2025/Early 2026  
**Coverage:** 1989 through mid-2025 (update pending)

**What we use:**
- **Longitudinal tracking**: Single file with one row per organization that has ever held tax-exempt status
- **Pre-geocoded addresses**: Most recent address geocoded to Census block level
- **Geographic codes**: FIPS codes at block, tract, county, and state levels
- **Metropolitan area codes**: Current CBSA (Core Based Statistical Area) definitions
- **Temporal tracking**: `ORG_YEAR_FIRST` and `ORG_YEAR_LAST` variables for organization lifecycle
- **Census integration**: Ready for merging with Census demographic and economic data

**Key Features:**
- ✅ **Eliminates annual file merging**: Consolidates all historical BMF releases into single file
- ✅ **AI/Lakehouse optimized**: Designed for modern data infrastructure
- ✅ **Census-ready**: FIPS codes enable direct joins with Census data
- ✅ **Metropolitan vs Rural**: CBSA codes identify urban/rural areas
- ✅ **Historical analysis**: Track organizations over time without complex ETL
- ✅ **Geographic analysis**: Pre-geocoded to Census block granularity

**Use Cases:**
- Longitudinal analysis of nonprofit sector
- Building historical sampling frames
- Linking nonprofit data to Census demographics
- Metropolitan vs rural nonprofit analysis
- Policy research requiring geographic precision
- Time-series analysis of organizational entry/exit

**Geographic Levels Available:**
- Census Block (finest granularity)
- Census Tract
- County (FIPS codes)
- State (FIPS codes)
- CBSA (Core Based Statistical Area)

**Related Resources:**
- NCCS Census Crosswalk: For aggregating to additional geographic levels
- BMF Overview: https://nccs.urban.org/project/irs-exempt-organizations-business-master-file
- NCCS Data Archive: https://nccs.urban.org/nccs-data-archive

**BibTeX:**
```bibtex
@dataset{nccs_unified_bmf,
    title = {Unified Business Master File (BMF)},
    author = {{National Center for Charitable Statistics}},
    year = {2026},
    publisher = {Urban Institute},
    url = {https://nccs.urban.org/},
    note = {Longitudinal nonprofit dataset with pre-geocoded Census integration, 1989-2025}
}
```

**Attribution:** When using NCCS Unified BMF data, cite:
1. National Center for Charitable Statistics, Urban Institute
2. IRS Business Master File (original data source)
3. Specify the data vintage/update date used

---

### **Charity Navigator** ⭐

**Powered by Charity Navigator**

We use the Charity Navigator GraphQL API to enrich nonprofit profiles with star ratings, mission statements, and organizational metrics.

**Organization:** Charity Navigator, Inc.  
**Website:** https://www.charitynavigator.org  
**API Documentation:** https://www.charitynavigator.org/partner/api  
**Principal Office:** 299 Market Street, Suite 250, Saddle Brook, NJ 07663  
**License:** API Terms of Use (Last updated March 2025)  
**Rate Limit:** 1,000 API calls per day  

**What we use:**
- **Charity Ratings**: Encompass Star Rating (0-4 stars)
- **Mission Statements**: Organization mission and purpose
- **Website URLs**: Official organization websites
- **Organizational Data**: EIN, name, address, category, cause
- **Active Advisories**: Alerts about organization status
- **Encompass Score**: Overall rating score
- **Rating Publication Date**: When the rating was last updated

**Data Fields Accessed:**
```
- Employer Identification Number (EIN)
- Charity Name
- Mission
- Organization Website URL
- Charity Navigator URL
- Category & Cause
- Street Address, City, State, Zip, Country
- Active Advisories
- Encompass Score & Star Rating
- Encompass Rating Publication Date & ID
```

**Attribution Requirements:**
- **Text Credit:** "Powered by Charity Navigator" (displayed on pages using their data)
- **Source Citation:** Charity Navigator cited as source on all pages displaying their data
- **Linkbacks:** All charity data links back to corresponding Charity Navigator profile pages
- **Trademark Notice:** CHARITY NAVIGATOR and the CHARITY NAVIGATOR logo are registered trademarks of Charity Navigator. All rights reserved. Used with permission.

**BibTeX:**
```bibtex
@misc{charitynavigator_api,
    title = {Charity Navigator API},
    author = {{Charity Navigator, Inc.}},
    year = {2025},
    url = {https://www.charitynavigator.org},
    note = {GraphQL API providing nonprofit ratings, mission statements, and organizational data}
}
```

**Compliance:**
This project complies with Charity Navigator's API Terms of Use, including:
- Rate limit compliance (max 1,000 calls/day)
- Proper attribution and branding
- Linkbacks to Charity Navigator profile pages
- Trademark acknowledgment
- Data caching for performance only (not for redistribution)

**Example Profile Link Format:**
```html
<a href="https://www.charitynavigator.org/ein/134141945">
  Michael J. Fox Foundation for Parkinson's Research
</a>
```

**Related Tools:**
- [Nonprofit enrichment script](scripts/enrich_nonprofits_charitynavigator.py) (if created)
- [API integration documentation](website/docs/data-sources/charity-navigator.md) (if created)

---

### **OpenSecrets.org (Center for Responsive Politics)** ⭐

**Organization:** OpenSecrets, a nonpartisan research organization tracking money in U.S. politics  
**Website:** https://www.opensecrets.org  
**Bulk Data:** https://www.opensecrets.org/open-data/bulk-data  
**API Documentation:** https://www.opensecrets.org/open-data/api  
**Status:** Bulk data access pending approval

**What they offer:**
- **Campaign Finance Data**: Federal campaign contributions, expenditures, and fundraising
- **Lobbying Data**: Federal lobbying spending by organizations and industries
- **Political Action Committees (PACs)**: PAC contributions and expenditures
- **Personal Finance Disclosures**: Wealth and financial interests of federal lawmakers
- **501(c) Organizations**: Political spending by nonprofits and dark money groups
- **Foreign Lobby Influence**: Foreign agents registered under FARA

**Data Access:**
- **Bulk Data Downloads**: Available to nonprofits upon approval (application pending)
- **Public API**: Available with rate limits for smaller queries
- **Data Format**: CSV files with detailed transaction-level records
- **Update Frequency**: Regular updates as new filings are processed
- **Coverage**: Federal-level political finance data (1990-present)

**What we plan to use:**
- Nonprofit political spending and advocacy activity
- Lobbying expenditures by healthcare and oral health organizations
- Campaign contributions from dental associations and health policy groups
- 501(c)(4) "dark money" spending on ballot measures
- Cross-reference EINs with IRS nonprofit data for comprehensive profiles

**BibTeX:**
```bibtex
@misc{opensecrets,
    title = {OpenSecrets.org: Money in Politics Database},
    author = {{Center for Responsive Politics}},
    year = {2024},
    url = {https://www.opensecrets.org},
    note = {Comprehensive database of campaign finance, lobbying, and political spending in U.S. politics}
}
```

**License & Attribution:**
- Data collected from Federal Election Commission (FEC) and other public sources
- Attribution required: "Data from OpenSecrets.org, a project of the Center for Responsive Politics"
- Nonprofit bulk data access subject to approval and terms of use

**Application Status:**
- ⏳ Bulk data access application pending approval
- Will enable comprehensive analysis of nonprofit political activity
- Integration planned upon approval

---

### **IRS Exempt Organizations Business Master File (EO-BMF)**

Basic nonprofit registration data (name, EIN, address, NTEE code).

### **IRS Exempt Organizations Business Master File (EO-BMF)**
- Complete database of 1.9M+ U.S. tax-exempt organizations
- Organization: Internal Revenue Service (IRS)
- Source: https://www.irs.gov/charities-non-profits/exempt-organizations-business-master-file-extract-eo-bmf
- Download: https://www.irs.gov/pub/irs-soi/ (4 regional CSV files)
- Format: CSV (basic organizational data: name, EIN, address, NTEE code, etc.)
- Update frequency: Monthly
- License: Public Domain (U.S. Government data)
- Coverage: All registered tax-exempt organizations under sections 501(c)(3), 501(c)(4), etc.
- Used for: Nonprofit discovery, organization matching, NTEE categorization

**Note:** This is the **Business Master File** (basic info). For detailed financial data, see IRS Form 990 XML below.

### **IRS Form 990 XML Filings** ⭐
- Detailed financial filings from nonprofit tax returns
- Organization: Internal Revenue Service (IRS)
- Source: https://www.irs.gov/charities-non-profits/form-990-series-downloads
- Format: XML (highly detailed financial and operational data)
- Parser Tools: **Giving Tuesday** open source libraries
  - XML Parser: https://github.com/Giving-Tuesday/form-990-xml-parser
  - XML Mapper: https://github.com/Giving-Tuesday/form-990-xml-mapper
- AWS S3 Index: https://registry.opendata.aws/irs990/
- License: Public Domain (U.S. Government data)
- Coverage: Annual filings from organizations with >$50K revenue
- Data includes: Detailed revenue, expenses, program services, officer compensation, grants, donors
- Used for: Financial analysis, transparency, grant research, program evaluation

**Giving Tuesday Attribution:**
The Giving Tuesday Data Commons provides essential tools for parsing IRS Form 990 XML data:
```bibtex
@software{giving_tuesday_form990_parser,
  title = {Form 990 XML Parser},
  author = {{Giving Tuesday}},
  year = {2024},
  url = {https://github.com/Giving-Tuesday/form-990-xml-parser},
  note = {Open source Python library for parsing IRS Form 990 XML filings}
}

@software{giving_tuesday_form990_mapper,
  title = {Form 990 XML Mapper},
  author = {{Giving Tuesday}},
  year = {2024},
  url = {https://github.com/Giving-Tuesday/form-990-xml-mapper},
  note = {Maps Form 990 XML to standardized data structures}
}
```

**More Giving Tuesday Resources:**
- GitHub Organization: https://github.com/Giving-Tuesday
- Data Commons: https://www.givingtuesday.org/data-commons
- Research & Insights: https://www.givingtuesday.org/research
- Coverage: Standardized schemas for Person, Organization, Membership, Post, Area, Motion, VoteEvent, Count
- Used for: Leader/official data modeling, organization structure, membership tracking, voting records
- Adoption: Used by Civic Commons, OpenNorth, mySociety, Sunlight Foundation, and 30+ civic tech organizations worldwide
- Citation: "Popolo Project. Open government data specifications. https://www.popoloproject.com/"
- **Key Features:**
  - **Person**: Names, contact details, identifiers, links to images/sources
  - **Organization**: Names, classification, founding/dissolution dates, contact information
  - **Membership**: Relationship between persons and organizations (with roles and time periods)
  - **Post**: Positions within organizations (e.g., "Mayor", "City Council Member District 3")
  - **VoteEvent**: Votes on motions/bills with individual voter positions
- **Our Implementation**: LEADER and ORGANIZATION entities follow Popolo schema for maximum interoperability with civic tech platforms

**Popolo Dependencies & Standards:**
The Popolo specification builds upon and references the following W3C, IETF, and open data standards:

| Publisher | Specification | Prefix | Use in Popolo | URL |
|-----------|---------------|--------|---------------|-----|
| Bibliographic Framework Initiative | BIBFRAME Vocabulary | `bf` | Bibliographic references | https://www.loc.gov/bibframe/ |
| Ian Davis | BIO: Biographical Information | `bio` | Life events, relationships | http://purl.org/vocab/bio/0.1/ |
| W3C | Contact: Utility concepts | `con` | Contact information | http://www.w3.org/2000/10/swap/pim/contact# |
| DCMI | DCMI Metadata Terms | `dcterms` | Metadata, provenance | https://www.dublincore.org/specifications/dublin-core/dcmi-terms/ |
| FOAF Project | FOAF Vocabulary | `foaf` | People, social networks | http://xmlns.com/foaf/0.1/ |
| GeoNames | GeoNames Ontology | `gn` | Geographic names | http://www.geonames.org/ontology/ |
| ISA Programme | Location Core Vocabulary | `locn` | Addresses, locations | https://www.w3.org/ns/locn |
| OSCA Foundation | NEPOMUK Calendar Ontology | `ncal` | Events, meetings | http://www.semanticdesktop.org/ontologies/ncal/ |
| Open Data Institute | Open Data Rights Statement | `odrs` | Data licensing | http://schema.theodi.org/odrs |
| W3C | The Organization Ontology | `org` | Organizational structures | https://www.w3.org/TR/vocab-org/ |
| ISA Programme | Person Core Vocabulary | `person` | Person attributes | http://www.w3.org/ns/person |
| W3C | RDF Schema | `rdfs` | Semantic web foundation | https://www.w3.org/TR/rdf-schema/ |
| W3C | Schema.org | `schema` | Structured data | https://schema.org/ |
| W3C | SKOS | `skos` | Taxonomies, classification | https://www.w3.org/2004/02/skos/ |
| IETF | vCard Format | `vcard` | Contact information | https://www.rfc-editor.org/rfc/rfc6350.html |

**Popolo Classes Implemented:**
- ✅ **Person** → LEADER entity (elected officials, appointees)
- ✅ **Organization** → ORGANIZATION entity (nonprofits, government agencies)
- ✅ **Membership** → Implicit through leader_id/organization relationships
- ✅ **Post** → position_type, office fields in LEADER
- ✅ **Contact Detail** → email, phone, website fields
- ✅ **Motion** → AGENDA items, LEGISLATION entities
- ✅ **Vote Event** → VOTE entity
- ✅ **Count** → vote_yes, vote_no in VOTE and LEGISLATION
- ✅ **Area** → JURISDICTION entity (geographic/political boundaries)
- ✅ **Event** → MEETING entity
- ✅ **Speech** → Extracted from MINUTES, VIDEO transcripts

### **Roper Center for Public Opinion Research**
- Scientifically validated survey questions and public opinion data
- Organization: Cornell University
- Source: https://ropercenter.cornell.edu/
- iPoll Database: https://ropercenter.cornell.edu/ipoll/
- License: Free public search (metadata and question wording), full data requires institutional membership
- Coverage: 500,000+ survey questions from 1930s-present, all major polling organizations
- Used for: Topic definitions, validated question wording, national opinion baselines, messaging optimization
- Citation: "Roper Center for Public Opinion Research, Cornell University. iPoll Databank. https://ropercenter.cornell.edu/ipoll/"

### **Google Fact Check Tools API**
- Aggregated fact-checking data with ClaimReview structured data
- Organization: Google LLC
- Source: https://toolbox.google.com/factcheck/explorer
- API: https://developers.google.com/fact-check/tools/api
- Schema: https://developers.google.com/search/docs/appearance/structured-data/factcheck
- License: Free API with quota (10,000 queries/day)
- Coverage: 100+ fact-checking organizations worldwide, all claim types
- Used for: Verifying claims from meetings/legislation, tracking misinformation, accountability scoring
- Citation: "Google Fact Check Tools API. Google LLC. https://developers.google.com/fact-check/tools/api"

### **FactCheck.org**
- Nonpartisan fact-checking of political claims and viral misinformation
- Organization: Annenberg Public Policy Center, University of Pennsylvania
- Source: https://www.factcheck.org/
- License: Free (web scraping allowed with rate limiting)
- Coverage: National politics, health claims, science, viral content (2003-present)
- Used for: Verifying political claims, health policy fact-checking, scientific claim verification
- Citation: "FactCheck.org. Annenberg Public Policy Center, University of Pennsylvania. https://www.factcheck.org/"

### **PolitiFact**
- Pulitzer Prize-winning fact-checking with Truth-O-Meter ratings
- Organization: Poynter Institute
- Source: https://www.politifact.com/
- License: Free (web scraping allowed with rate limiting)
- Coverage: All 50 states, federal politics, ballot measures (2007-present)
- Rating Scale: 6-point (True, Mostly True, Half True, Mostly False, False, Pants on Fire)
- Used for: State-level fact-checking, tracking politician claims, ballot measure verification
- Citation: "PolitiFact. Poynter Institute. https://www.politifact.com/"

### **Schema.org**
- Structured data vocabulary for semantic web markup
- Organization: W3C Community Group (sponsors: Google, Microsoft, Yahoo, Yandex)
- Source: https://schema.org/
- Documentation: https://schema.org/docs/schemas.html
- License: Creative Commons Attribution-ShareAlike License (CC BY-SA 3.0)
- Coverage: 800+ types, 1,400+ properties for describing web content
- Used for: SEO-optimized structured data, JSON-LD exports, API documentation, search engine compatibility
- Citation: "Schema.org. W3C Community Group. https://schema.org/"

**Our Schema.org Type Mappings:**

| Our Entity | Schema.org Type | Properties Used | Use Case |
|------------|----------------|-----------------|----------|
| JURISDICTION | [AdministrativeArea](https://schema.org/AdministrativeArea) | name, address, geo, telephone, url | City/county geographic data |
| MEETING | [Event](https://schema.org/Event) + [GovernmentService](https://schema.org/GovernmentService) | name, startDate, location, organizer, description | Public meetings, hearings |
| LEADER | [Person](https://schema.org/Person) + [GovernmentOfficial](https://schema.org/GovernmentOfficial) | name, email, telephone, jobTitle, worksFor | Elected officials |
| ORGANIZATION | [Organization](https://schema.org/Organization) + [NGO](https://schema.org/NGO) | name, address, telephone, url, foundingDate | Nonprofits, agencies |
| LEGISLATION | [Legislation](https://schema.org/Legislation) | name, legislationDate, legislationPassedBy, legislationType | Bills, ordinances |
| BALLOT_MEASURE | [Legislation](https://schema.org/Legislation) + referendumProposal | name, datePosted, legislationChanges | Referendums, propositions |
| VOTE | [VoteAction](https://schema.org/VoteAction) | agent (Person), candidate (Legislation), actionOption | Roll call votes |
| FACT_CHECK | [ClaimReview](https://schema.org/ClaimReview) | claimReviewed, reviewRating, author, datePublished | Verified fact-checks |
| SCHOOL_DISTRICT | [EducationalOrganization](https://schema.org/EducationalOrganization) | name, address, telephone, numberOfStudents | K-12 school districts |
| NONPROFIT_FINANCES | [MonetaryGrant](https://schema.org/MonetaryGrant) | funder, amount, fundedItem | IRS Form 990 data |
| VIDEO | [VideoObject](https://schema.org/VideoObject) | name, description, uploadDate, duration, thumbnailUrl | Meeting recordings |
| DOCUMENT | [DigitalDocument](https://schema.org/DigitalDocument) | name, fileFormat, datePublished, url | PDFs, agendas, minutes |

**Benefits:**
- ✅ **SEO Enhancement**: Google Search rich results for meetings, officials, organizations
- ✅ **Voice Assistant Ready**: Alexa, Google Assistant can parse our structured data
- ✅ **Knowledge Graph**: Data appears in Google Knowledge Panels
- ✅ **API Discoverability**: Standards-compliant REST/GraphQL responses
- ✅ **Cross-platform**: Compatible with Apple Podcasts, Microsoft Bing, Yandex

### **Common Education Data Standards (CEDS)**
- Comprehensive education data standards for K-12, postsecondary, and workforce
- Organization: U.S. Department of Education, National Center for Education Statistics (NCES)
- Source: https://ceds.ed.gov/
- GitHub: https://github.com/CEDStandards
- Specification Repository: https://github.com/CEDStandards/CEDS-Elements
- License: Public Domain (U.S. Government)
- Coverage: 2,300+ data elements, 500+ option sets, alignment with NCES surveys
- Used for: School district data modeling, NCES interoperability, education finance tracking
- Citation: "Common Education Data Standards (CEDS). National Center for Education Statistics. https://ceds.ed.gov/"

**CEDS Alignment for School Districts:**

| Our Field | CEDS Element ID | CEDS Element Name | Description |
|-----------|----------------|-------------------|-------------|
| `nces_id` | 000827 | LEA Identifier (NCES) | National Center for Education Statistics LEA ID |
| `district_name` | 000168 | Name of Institution | Legal name of the school district |
| `district_type` | 000108 | LEA Type | Local, State, Federal, or Other |
| `total_students` | 001475 | Student Count | Total number of students enrolled |
| `total_schools` | 000856 | Number of Schools | Count of schools in district |
| `total_revenue` | 000612 | Total Revenue | Sum of all revenue sources |
| `total_expenditures` | 000611 | Total Expenditures | Sum of all spending categories |
| `per_pupil_spending` | 000613 | Expenditure per Student | Total expenditures / student count |
| `federal_revenue` | 000614 | Federal Revenue | Revenue from federal government |
| `state_revenue` | 000615 | State Revenue | Revenue from state sources |
| `local_revenue` | 000616 | Local Revenue | Revenue from property taxes, bonds |
| `superintendent` | 000240 | Chief Administrator Name | District superintendent name |
| `school_year` | 000243 | School Year | Academic year (e.g., 2023-2024) |

**CEDS Option Sets Used:**
- **LEA Type** (CEDS 000108): Regular, Specialized, Supervisory Union, Service Agency, State Agency, Federal Agency
- **Grade Level** (CEDS 000100): PK, KG, 01-12, UG (ungraded)
- **Operational Status** (CEDS 000533): Open, Closed, New, Added, Changed Agency, Temporarily Closed
- **Locale Type** (CEDS 001315): City, Suburb, Town, Rural (NCES Urban-centric locale codes)

**Benefits of CEDS Compliance:**
- ✅ **NCES Compatibility**: Direct mapping to Common Core of Data (CCD) and F-33 Finance Survey
- ✅ **State Reporting**: Aligns with state education department data systems
- ✅ **Federal Grants**: Standardized reporting for ESSA, Title I, IDEA compliance
- ✅ **Longitudinal Tracking**: Consistent identifiers for multi-year analysis
- ✅ **Interoperability**: Works with Ed-Fi Alliance, IMS Global, SIF Association standards

### **Microsoft Common Data Model for Nonprofits**
- Industry-standard data model for nonprofit organizations built on Microsoft Dataverse
- Organization: Microsoft Corporation
- Repository: https://github.com/microsoft/Nonprofits/tree/master/CommonDataModelforNonprofits
- ERD Documentation: https://github.com/microsoft/Nonprofits/blob/master/CommonDataModelforNonprofits/Documents/common-data-model-for-nonprofits-erds.pdf
- License: MIT License
- Coverage: Donor management, fundraising, program delivery, volunteer management, impact measurement, award/grant tracking
- Used for: Nonprofit data standardization, Dynamics 365 integration, constituent relationship management, outcome tracking
- Citation: "Microsoft Common Data Model for Nonprofits. Microsoft Corporation. https://github.com/microsoft/Nonprofits/"

**Microsoft CDM Nonprofit Core Entities:**

| Entity | Description | Our Implementation |
|--------|-------------|--------------------|
| **Constituent** | Individuals who interact with nonprofit (donors, volunteers, members, beneficiaries) | CONSTITUENT entity |
| **Donation** | Financial contributions and in-kind gifts | DONATION entity |
| **Designation** | How donations are allocated (programs, funds, campaigns) | designation_id in DONATION |
| **Campaign** | Fundraising campaigns and appeals | CAMPAIGN entity |
| **Membership** | Member enrollment and renewal tracking | MEMBERSHIP entity |
| **Volunteer** | Volunteer activities, hours, and preferences | VOLUNTEER_ACTIVITY entity |
| **Award** | Grants received by the nonprofit | Awards captured in NONPROFIT_FINANCES |
| **Disbursement** | Spending of grant/award funds | Expenditures in GOVERNMENT_BUDGET |
| **Objective** | Measurable program outcomes and impact | PROGRAM_OUTCOME entity |
| **DeliveryFramework** | Programs and services delivered | PROGRAM_DELIVERY entity |
| **Budget** | Organizational budgets and allocations | GOVERNMENT_BUDGET, SCHOOL_DISTRICT budgets |
| **Indicator** | Key performance indicators for impact | Metrics in PROGRAM_OUTCOME |

**Key Entity Relationships (Microsoft CDM Pattern):**
- Constituent → Donation (one-to-many): A constituent makes many donations
- Donation → Designation (many-to-one): Multiple donations to one fund/program
- Campaign → Donation (one-to-many): A campaign receives many donations
- Constituent → Membership (one-to-many): A constituent can have multiple memberships over time
- Constituent → Volunteer (one-to-many): A constituent volunteers for multiple activities
- Organization → DeliveryFramework (one-to-many): An organization delivers multiple programs
- DeliveryFramework → Objective (one-to-many): A program has multiple outcome objectives

**Benefits of Microsoft CDM Alignment:**
- ✅ **Dynamics 365 Integration**: Native compatibility with Microsoft Cloud for Nonprofits
- ✅ **Power Platform**: Direct use in Power BI, Power Apps, Power Automate
- ✅ **Azure Synapse**: Seamless analytics with Azure data services
- ✅ **Industry Standard**: Adopted by large nonprofits using Microsoft ecosystem
- ✅ **Grant Compliance**: Built-in support for grant reporting and outcome measurement
- ✅ **Constituent 360**: Unified view of donor, volunteer, member activities

---

## 🎯 **Grant Research and Fundraising Platforms**

These platforms are built on open-source principles or community-funded models to keep grant and fundraising data accessible.

### **Grantmakers.io** ⭐

**"Free as in Freedom" Grant Research**

Grantmakers.io is the gold standard for open, community-supported foundation research. It provides lightning-fast search through IRS 990-PF data with no login required.

**Organization:** Community-supported open-source project  
**Website:** https://www.grantmakers.io/  
**Data Source:** IRS Form 990-PF (Private Foundation tax returns)  
**License:** Open source, community-funded  
**Access:** 100% free, no account or API key required  
**Coverage:** All U.S. private foundations filing Form 990-PF (75,000+ grantmaking foundations)

**What we use:**
- **Foundation Giving Histories**: Search foundations by who they've funded in the past
- **Grantee Databases**: Find all grants made to specific organizations
- **Geographic Targeting**: Search by state, city, or region
- **Funding Amounts**: Filter by grant size ranges
- **NTEE Categories**: Search by nonprofit sector (health, education, environment, etc.)
- **Year-over-Year Trends**: Track foundation giving patterns over time

**Key Features:**
- ⚡ **Lightning-Fast Search**: Instant results across millions of grant records
- 🔓 **No Login Required**: Completely open access, no barriers
- 📊 **Detailed 990-PF Data**: Full foundation financials, officers, assets
- 🎯 **Relationship Mapping**: Discover foundation-grantee connections
- 📈 **Trend Analysis**: Multi-year giving patterns and focus areas
- 🆓 **Always Free**: Community-funded to remain accessible

**Use Cases:**
- **Grant Prospecting**: Find foundations that fund similar organizations in your area
- **Relationship Research**: Identify foundations that have supported oral health, public health, or civic engagement
- **Competitive Analysis**: See which organizations are receiving grants in your field
- **Foundation Vetting**: Review foundation assets, giving patterns, and leadership before applying

**Example Searches:**
- Foundations that funded "fluoridation" or "oral health" projects
- Grantmakers in Massachusetts supporting health policy advocacy
- Foundations with >$10M assets funding civic engagement
- All grants made by Robert Wood Johnson Foundation to nonprofits in Alabama

**BibTeX:**
```bibtex
@misc{grantmakersio,
    title = {Grantmakers.io: Open Foundation Research Platform},
    year = {2026},
    url = {https://www.grantmakers.io/},
    note = {Community-supported open-source platform for searching IRS 990-PF private foundation data}
}
```

**Citation:** "Grantmakers.io. Community-supported open foundation research. https://www.grantmakers.io/"

---

### **Zeffy** ⭐

**100% Free Fundraising with AI-Powered Grant Matching**

Zeffy is unique for being a completely free fundraising platform that also offers an AI-powered grant search tool to help match nonprofit missions with potential grant opportunities.

**Organization:** Zeffy, Inc.  
**Website:** https://www.zeffy.com/  
**Platform:** Fundraising + Grant Discovery  
**Cost:** 100% free for nonprofits (donor-covered fees model)  
**Grant Tool:** AI-powered grant opportunity matching  
**Coverage:** U.S. and Canadian grant opportunities

**What we use:**
- **AI Grant Matching**: Automated matching of nonprofit missions to relevant grant opportunities
- **Fundraising Infrastructure**: Donation processing, event ticketing, membership management
- **Donor Management**: CRM for tracking constituent relationships
- **Grant Alerts**: Notifications when new matching opportunities are posted

**Key Features:**
- 💰 **100% Free**: No platform fees, monthly charges, or hidden costs
- 🤖 **AI-Powered Matching**: Machine learning matches your mission to grant opportunities
- 📧 **Grant Alerts**: Email notifications for new matching grants
- 🎟️ **All-in-One Platform**: Donations, events, memberships, grants in one system
- 🇺🇸 🇨🇦 **North America Coverage**: U.S. and Canadian grant databases
- 📊 **Impact Reporting**: Built-in analytics for grant reporting requirements

**Grant Discovery Capabilities:**
- **Mission-Based Matching**: Upload your mission statement, get matched grants
- **Federal Grants**: Monitors Grants.gov for federal opportunities
- **Foundation Grants**: Tracks private foundation RFPs and announcements
- **Corporate Giving**: Alerts for corporate philanthropy programs
- **Local Grants**: Community foundation and regional funder opportunities

**Use Cases for This Project:**
- **Nonprofit Fundraising**: Organizations can use Zeffy for zero-cost donation processing
- **Grant Prospecting**: AI helps match oral health nonprofits to relevant grant opportunities
- **Event Fundraising**: Free ticketing for fundraising galas, community events
- **Membership Management**: Track supporters, volunteers, members at no cost
- **Sustainability**: Recommend to small nonprofits to reduce overhead costs

**Why It's Important:**
Traditional fundraising platforms charge 3-5% fees on donations, which drains resources from small nonprofits. Zeffy's donor-covered model means 100% of donations go to the organization, making it especially valuable for grassroots oral health advocacy groups.

**BibTeX:**
```bibtex
@misc{zeffy_platform,
    title = {Zeffy: 100% Free Fundraising Platform with AI Grant Matching},
    author = {{Zeffy, Inc.}},
    year = {2026},
    url = {https://www.zeffy.com/},
    note = {Free fundraising platform with AI-powered grant discovery for U.S. and Canadian nonprofits}
}
```

**Citation:** "Zeffy. 100% Free Fundraising Platform with AI Grant Matching. https://www.zeffy.com/"

---

### **Community Foundations** ⭐

**Local Grant Opportunities Often Overlooked**

Community foundations are often the most accessible grant sources for local nonprofits, yet they're frequently overlooked because they don't appear in major federal databases. Most maintain their own open listings for regional grants.

**What Community Foundations Are:**
Community foundations are public charities that pool donations from individuals, families, and businesses to support local nonprofits through competitive grants, scholarship programs, and donor-advised funds.

**Why They Matter:**
- 🏘️ **Local Focus**: Prioritize organizations serving their specific geographic region
- 💵 **Smaller, Accessible Grants**: $500-$50,000 range, ideal for grassroots groups
- 🤝 **Relationship-Based**: Local foundations know local issues and local leaders
- 📋 **Simpler Applications**: Less bureaucratic than federal or national foundations
- ⚡ **Faster Decisions**: Many have quarterly or rolling deadlines
- 🎯 **Mission Alignment**: Support for community health, civic engagement, education

**Examples of Community Foundations:**

| Foundation | Region | Website | Grant Focus Areas |
|------------|--------|---------|-------------------|
| **Central Alabama Community Foundation** | Birmingham, AL metro | https://www.cacfbirmingham.org/ | Health, education, civic engagement, arts |
| **Community Foundation for Greater Atlanta** | Atlanta, GA metro | https://cfgreateratlanta.org/ | Health equity, education, economic mobility |
| **Boston Foundation** | Boston, MA metro | https://www.tbf.org/ | Health, housing, education, civic participation |
| **Community Foundation of Greater Memphis** | Memphis, TN metro | https://cfgm.org/ | Health, youth development, community engagement |
| **Silicon Valley Community Foundation** | San Francisco Bay Area | https://www.siliconvalleycf.org/ | Health, education, immigration, environment |
| **Greater Kansas City Community Foundation** | Kansas City, MO/KS | https://www.growyourgiving.org/ | Health, education, civic infrastructure |
| **Seattle Foundation** | Seattle, WA metro | https://www.seattlefoundation.org/ | Racial equity, community health, economic opportunity |

**How to Find Your Local Community Foundation:**
1. **Council on Foundations Directory**: https://www.cof.org/community-foundation-locator
2. **Candid (formerly Foundation Center)**: https://candid.org/find-us/foundation-finder
3. **State Associations**: Most states have a community foundation association
4. **Google Search**: "[Your City] Community Foundation" or "[Your County] Community Foundation"

**Grant Opportunities:**
- **Competitive Grants**: Open RFPs for nonprofits in specific focus areas
- **Capacity Building Grants**: Support for operations, staffing, strategic planning
- **Donor-Advised Funds**: Individuals/families make grants through the foundation
- **Fiscal Sponsorship**: Some foundations sponsor projects for groups without 501(c)(3) status
- **Scholarship Programs**: Education grants for students (often administered by community foundations)

**For Oral Health Advocacy:**
Many community foundations have health equity or preventive health focus areas that align perfectly with fluoridation advocacy, dental access programs, and oral health education. They're often the best first step for local grassroots campaigns.

**How We Use Community Foundation Data:**
- **Local Grant Mapping**: Identify which community foundations serve each jurisdiction
- **Nonprofit Funding Sources**: Link organizations to local foundation grants received
- **Geographic Targeting**: Recommend local funders when users search by city/county
- **Grant Prospecting**: Alert nonprofits to community foundation RFPs in their area

**BibTeX:**
```bibtex
@misc{community_foundations,
    title = {Community Foundations: Local Grant Opportunities},
    author = {{Council on Foundations}},
    year = {2026},
    url = {https://www.cof.org/community-foundation-locator},
    note = {Network of 700+ community foundations providing local grants across the United States}
}
```

**Citation:** "Community Foundations. Council on Foundations. https://www.cof.org/community-foundation-locator"

---

## 🏛️ **Civic Tech Organizations & Resources**

### **Code for America** ⭐

The flagship U.S. civic technology nonprofit organization, convening government leaders and technologists to transform public services.

**Organization:** Code for America  
**Website:** https://codeforamerica.org/  
**About:** National nonprofit working with government to build digital services that are simple, effective, and accessible to all  
**Founded:** 2009  
**Coverage:** National (50 states), with focus on state-level government transformation  

**What we use:**
- **Summit Insights**: Annual Summit (most recently Summit 2026) where state-level AI leads and municipal CIOs set the civic tech agenda for the year
- **Brigade Network**: Community chapters across the U.S. working on local civic tech projects
- **Best Practices**: Government service design patterns, digital service standards
- **Technology Landscape**: Trends in state and local government digital transformation

**Key Programs:**
- **Code for America Summit**: Annual conference bringing together 1,500+ government leaders, technologists, and advocates
- **Brigade Network**: 80+ volunteer chapters in cities across America building civic tech solutions
- **Get CalFresh**: Flagship product helping millions access food benefits through simplified digital applications
- **Clear My Record**: Automated criminal record clearance to help people move forward
- **Government Services Portfolio**: Digital tools for social safety net programs

**Resources:**
- Summit: https://codeforamerica.org/summit/
- Brigade Network: https://brigade.codeforamerica.org/
- Blog: https://codeforamerica.org/news/
- GitHub: https://github.com/codeforamerica
- Annual Reports: https://codeforamerica.org/news/category/annual-reports/

**Why Code for America:**
- **Agenda Setting**: The Summit is where state-level AI leads and municipal CIOs define priorities for the year
- **Network Effect**: Connects civic technologists across the country
- **Proven Impact**: Products serving millions of Americans annually
- **Open Source**: Many tools available as open source for other governments to adopt

**BibTeX:**
```bibtex
@misc{code_for_america,
    title = {Code for America},
    author = {{Code for America}},
    year = {2026},
    url = {https://codeforamerica.org/},
    note = {National nonprofit transforming government digital services and convening state and local government technology leaders}
}
```

**Citation:** "Code for America. https://codeforamerica.org/"

---

### **GovTech.com (Government Technology)** ⭐

The primary news and ranking source for the government technology industry, providing market intelligence and trend analysis.

**Organization:** Government Technology (e.Republic)  
**Website:** https://www.govtech.com/  
**About:** Leading publication covering technology trends, policy, and innovation in state and local government  
**Founded:** 1987  
**Coverage:** State and local government across all 50 states  

**What we use:**
- **GovTech 100**: Annual definitive directory of the top 100 trending companies in the U.S. public sector technology market
- **Industry Trends**: Analysis of emerging technologies, procurement trends, and digital transformation initiatives
- **Vendor Landscape**: Tracking government technology companies, products, and solutions
- **Policy Coverage**: Legislative and regulatory developments affecting civic technology

**Key Resources:**
- **GovTech 100 List**: https://www.govtech.com/100/ - The definitive annual ranking of companies shaping the future of state and local government
- **Navigator Awards**: https://www.govtech.com/navigator - Recognition of state and local government IT leaders
- **Digital Cities Survey**: Annual ranking of America's most digitally advanced cities and counties
- **Research Center**: https://www.govtech.com/research/ - White papers, surveys, and industry reports
- **Webinars & Events**: https://www.govtech.com/events/

**GovTech 100 Categories:**
- Cloud & Infrastructure
- Cybersecurity
- Data & Analytics
- Digital Government Services
- Education Technology
- Emergency Management
- Financial Management
- GIS & Mapping
- Health & Human Services
- Public Safety
- Transportation

**Why GovTech.com:**
- **Market Intelligence**: The GovTech 100 is the authoritative list of trending companies in government technology
- **Vendor Discovery**: Comprehensive directory of solutions available to state and local government
- **Industry Standards**: Defines what's considered "trending" and "emerging" in the civic tech marketplace
- **Procurement Insights**: Helps identify which technologies governments are actively adopting

**Resources:**
- Main Site: https://www.govtech.com/
- GovTech 100: https://www.govtech.com/100/
- Newsletter: https://www.govtech.com/newsletters/
- Podcasts: https://www.govtech.com/podcasts/
- Magazine Archive: https://www.govtech.com/magazines/

**BibTeX:**
```bibtex
@misc{govtech_magazine,
    title = {Government Technology Magazine},
    author = {{e.Republic Inc.}},
    year = {2026},
    url = {https://www.govtech.com/},
    note = {Leading publication and market intelligence source for state and local government technology, publisher of the annual GovTech 100 list}
}
```

**GovTech 100 BibTeX:**
```bibtex
@misc{govtech_100,
    title = {GovTech 100: Companies Trending in State and Local Government},
    author = {{Government Technology}},
    year = {2026},
    url = {https://www.govtech.com/100/},
    note = {Annual directory of the top 100 trending companies serving the U.S. public sector}
}
```

**Citation:** "Government Technology. e.Republic Inc. https://www.govtech.com/"

---

### **Civic Tech Guide** ⭐

Comprehensive, curated directory of civic technology projects, organizations, and tools worldwide, maintained by the civic tech community.

**Organization:** Civic Tech Field Guide (Community-maintained)  
**Website:** https://app.civictech.guide/  
**About:** Open directory and knowledge base of civic tech projects, tools, and organizations with detailed project profiles and categorization  
**Founded:** 2018  
**Coverage:** Global civic technology ecosystem (1,000+ projects)  

**What we use:**
- **Project Directory**: Discovery of related civic tech tools and platforms
- **Categorization**: Understanding how civic tech projects are classified and tagged
- **Community Connections**: Network of civic technologists and organizations
- **Best Practices**: Learning from similar projects and their approaches

**CommunityOne Profile:**
- **Listed as**: https://app.civictech.guide/p/communityone/r/recN0BG4gvjXT7WLf
- **Categories**: Open Government, Civic Engagement, AI/Machine Learning
- **Description**: AI-powered civic engagement platform tracking local government meetings, legislation, and advocacy opportunities

**Key Features:**
- **Search & Filter**: Discover projects by topic, geography, technology, and impact area
- **Project Profiles**: Detailed information about civic tech initiatives including status, team, and technology
- **Tagging System**: Categorization by civic tech domains (transparency, participation, accountability, etc.)
- **API Access**: Programmatic access to the project database
- **Community Contributions**: Open for civic tech projects to self-list and update profiles

**Categories in Civic Tech Guide:**
- Open Government & Transparency
- Civic Participation & Engagement
- Community Organizing
- Democracy & Voting
- Public Service Delivery
- Data & Research
- Advocacy & Policy
- Urban Planning & Development

**Resources:**
- Main Site: https://app.civictech.guide/
- About: https://civictech.guide/
- Submit Project: https://app.civictech.guide/submit
- GitHub: https://github.com/compilerla/civic-tech-taxonomy

**Why Civic Tech Guide:**
- **Discovery**: Find related projects and potential collaborators
- **Context**: Understand where your project fits in the broader civic tech ecosystem
- **Community**: Connect with civic technologists working on similar problems
- **Legitimacy**: Being listed establishes credibility in the civic tech community

**BibTeX:**
```bibtex
@misc{civic_tech_guide,
    title = {Civic Tech Field Guide},
    author = {{Civic Tech Field Guide Community}},
    year = {2026},
    url = {https://civictech.guide/},
    note = {Community-maintained directory of civic technology projects and organizations worldwide}
}
```

**Citation:** "Civic Tech Field Guide. https://civictech.guide/"

---

## 🙏 **Acknowledgments**

We are grateful to the authors of MeetingBank for making their dataset publicly available for research purposes. Their work on meeting summarization has been instrumental in developing civic engagement tools.

Special thanks to:
- The Association for Computational Linguistics (ACL)
- HuggingFace for hosting datasets
- Open States for legislative data
- All municipal governments providing open access to meeting records

---

## 📖 **How to Cite This Project**

If you use Open Navigator in your research, please cite:

```
Open Navigator
GitHub: https://github.com/getcommunityone/open-navigator-for-engagement
License: MIT
```

**BibTeX:**
```bibtex
@software{open-navigator-2026,
    title = {Open Navigator},
    author = {Community One},
    year = {2026},
    url = {https://github.com/getcommunityone/open-navigator-for-engagement},
    license = {MIT}
}
```

---

## 📝 **License Compliance**

This project respects all dataset licenses and terms of use. See [LICENSE](LICENSE) for this project's MIT license.

For dataset-specific licenses, please refer to the original sources listed above.
