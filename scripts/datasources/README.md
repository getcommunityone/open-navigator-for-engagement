# Data Source Scripts

This directory contains scripts organized by external data source.

## Structure

Each subdirectory contains scripts for a specific data source:

- **openstates/** - OpenStates legislative data (bills, legislators, votes)
- **census/** - US Census Bureau geographic and demographic data
- **irs/** - IRS nonprofit data (Form 990, Business Master File)
- **nccs/** - National Center for Charitable Statistics unified nonprofit data
- **fec/** - Federal Election Commission campaign finance data
- **ballotpedia/** - Ballotpedia election and official data
- **google_civic/** - Google Civic Information API
- **grants_gov/** - Grants.gov federal grant data
- **localview/** - LocalView meeting transcripts and agendas
- **meetingbank/** - MeetingBank research dataset
- **nces/** - National Center for Education Statistics
- **wikidata/** - Wikidata structured knowledge base
- **dbpedia/** - DBpedia structured Wikipedia data
- **voter_data/** - Voter registration and turnout data

## Usage

Each subdirectory may contain:
- Ingestion/download scripts
- Schema creation scripts
- Export/transformation scripts
- README with data source details
