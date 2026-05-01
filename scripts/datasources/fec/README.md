# FEC Campaign Finance Scripts

Scripts for working with [Federal Election Commission](https://www.fec.gov/) campaign finance data.

## Data Source

- **Website**: https://www.fec.gov/
- **API**: https://api.open.fec.gov/developers/
- **Bulk Data**: https://www.fec.gov/data/browse-data/?tab=bulk-data
- **Coverage**: Federal candidates, committees, contributions
- **Data Types**: Candidates, committees, contributions, expenditures, filings

## Scripts

### `bulk_download_fec.py`
Download all FEC bulk data files and organize them by year and type.

**Features:**
- Downloads all bulk data from 1980-present
- Organizes files matching FEC website structure
- Resume interrupted downloads
- Progress tracking and logging
- Filter by year or file type

**Usage:**
```bash
# Download everything to D:/fec_data/
python bulk_download_fec.py

# Download to custom directory
python bulk_download_fec.py --base-dir /mnt/d/fec_data

# Download specific years only
python bulk_download_fec.py --years 2020,2022,2024

# Download specific file types only
python bulk_download_fec.py --types indiv,cn,cm

# Resume interrupted download
python bulk_download_fec.py --resume

# Dry run (show what would be downloaded)
python bulk_download_fec.py --dry-run
```

**File Types:**
- `cm` - Committee Master files
- `cn` - Candidate Master files
- `ccl` - Candidate-Committee Linkages
- `indiv` - Individual Contributions
- `pas2` - PAC Summary files
- `oth` - Other Transactions
- `oppexp` - Operating Expenditures
- `weball` - All Candidates
- `webk` / `webl` - Current House/Senate Campaigns

**Output Structure:**
```
/mnt/d/fec_data/
└── bulk-downloads/
    ├── candidate-master/          (Candidate master files)
    │   ├── 1980/cn80.zip
    │   ├── 2024/cn24.zip
    │   └── ...
    ├── all-candidates/            (All candidates files)
    │   ├── 1980/weball80.zip
    │   └── 2024/weball24.zip
    ├── house-senate-campaigns/    (Current campaigns)
    │   └── 2024/
    │       ├── webk24.zip
    │       └── webl24.zip
    ├── committee-master/          (Committee master files)
    │   └── 2024/cm24.zip
    ├── pac-summary/               (PAC summary files)
    │   └── 2024/pas224.zip
    ├── contributions-by-individuals/ (Individual contributions)
    │   └── 2024/indiv24.zip
    ├── candidate-committee-linkages/ (Linkages)
    │   └── 2024/ccl24.zip
    ├── committee-to-committee/    (Committee transactions)
    │   └── 2024/oth24.zip
    ├── operating-expenditures/    (Operating expenses)
    │   └── 2024/oppexp24.zip
    ├── summary-reports/           (Summary CSVs)
    │   └── 2024/
    │       ├── candidate_summary_2024.csv
    │       ├── independent_expenditure_2024.csv
    │       └── ...
    ├── headers/                   (Data dictionaries)
    │   ├── cm_header_file.csv
    │   └── ...
    └── special-files/             (Lobbyist data, etc.)
        ├── lobbyist.csv
        └── ...
```

### `fec_integration.py`
Integrate FEC API data for real-time queries.

## Key Datasets

### Candidates
- Federal candidates (President, Senate, House)
- Party affiliation
- Election years

### Committees
- Campaign committees
- PACs, Super PACs
- Party committees

### Financial Data
- Individual contributions
- Committee expenditures
- Independent expenditures
- Disbursements

## Usage Examples

```bash
# Download candidate data
python fec_integration.py --data-type candidates --state MA

# Download committee data
python fec_integration.py --data-type committees --cycle 2024
```

## API Key

Requires FEC API key. Set environment variable:
```bash
export FEC_API_KEY=your_key_here
```

Register at: https://api.data.gov/signup/

## Data License

FEC data is public domain.
