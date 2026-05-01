# FEC Campaign Finance Scripts

Scripts for working with [Federal Election Commission](https://www.fec.gov/) campaign finance data.

## Data Source

- **Website**: https://www.fec.gov/
- **API**: https://api.open.fec.gov/developers/
- **Bulk Data**: https://www.fec.gov/data/browse-data/?tab=bulk-data
- **Coverage**: Federal candidates, committees, contributions
- **Data Types**: Candidates, committees, contributions, expenditures, filings

## Scripts

- `fec_integration.py` - Integrate FEC API data

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
