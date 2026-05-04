# Data Sources

This directory contains scrapers and loaders for various civic data sources.

## 📚 Available Data Sources

### Federal/National Sources

- **[gsa/](gsa/)** - GSA .gov Domain Registry (2,272+ official government websites)
- **[census/](census/)** - U.S. Census Bureau (demographics, geographic boundaries)
- **[openstates/](openstates/)** - Plural Policy / Open States (state legislatures)
- **[fec/](fec/)** - Federal Election Commission (campaign finance)
- **[grants_gov/](grants_gov/)** - Grants.gov (federal grants)
- **[irs/](irs/)** - IRS (990 forms for nonprofits)
- **[nccs/](nccs/)** - National Center for Charitable Statistics
- **[nces/](nces/)** - National Center for Education Statistics

### Local Government Sources

- **[govwebsites/](govwebsites/)** ⭐ NEW - Official .gov website scraper
- **[usmayors/](usmayors/)** ⭐ NEW - U.S. Conference of Mayors (election results)
- **[naco/](naco/)** ⭐ NEW - National Association of Counties
- **[nlc/](nlc/)** 🚧 TODO - National League of Cities
- **[icma/](icma/)** 🚧 TODO - Intl City/County Management Assoc.

### Platform-Specific Scrapers

- **[civicplus/](civicplus/)** 🚧 TODO - CivicPlus municipal websites
- **[legistar/](legistar/)** 🚧 TODO - Granicus Legistar legislative portals
- **[youtube/](youtube/)** - YouTube (meeting videos, government channels)
- **[localview/](localview/)** - LocalView (meeting video platform)

### Civic Data APIs

- **[ballotpedia/](ballotpedia/)** - Ballotpedia (election data)
- **[google_civic/](google_civic/)** - Google Civic Information API
- **[voter_data/](voter_data/)** - Voter registration data

### Knowledge Bases

- **[wikidata/](wikidata/)** - Wikidata (structured jurisdiction metadata)
- **[dbpedia/](dbpedia/)** - DBpedia (Wikipedia structured data)
- **[social_media/](social_media/)** - Social media account discovery

### Meeting Data

- **[meetingbank/](meetingbank/)** - MeetingBank dataset (city council meetings)
- **[cityscrapers/](cityscrapers/)** - City Scrapers (meeting agendas)

## 🚀 Quick Start

### 1. Load GSA .gov Domains (Recommended First)

```bash
# Load all official government domains
cd gsa/
python load_gsa_domains_to_postgres.py --states AL,GA,IN,MA,WA,WI

# This creates 2,272+ jurisdiction records with official websites
```

### 2. Scrape Official Government Websites

```bash
# Extract YouTube channels, meetings, contacts from .gov sites
cd govwebsites/
python scrape_gov_websites.py --states AL,GA,IN,MA,WA,WI --limit 100
```

### 3. Load Census Data

```bash
# Geographic boundaries and demographics
cd census/
python load_census_places.py --states AL,GA,IN,MA,WA,WI
```

### 4. Load WikiData Enrichment

```bash
# Government officials, websites, metadata
cd wikidata/
python load_jurisdictions_wikidata.py --states AL,GA,IN,MA,WA,WI --types city,county,state
```

### 5. Load YouTube Meeting Videos

```bash
# Meeting videos from government YouTube channels
cd youtube/
python load_youtube_events_to_postgres.py --states AL,GA,IN,MA,WA,WI --max-videos 50
```

## 📋 Load Types

Each data source performs one of these load types:

- **CREATE LOAD** - Creates new records (e.g., Census places, GSA domains)
- **ENRICHMENT LOAD** - Updates existing records (e.g., WikiData, NACo)
- **EVENT LOAD** - Adds time-series events (e.g., YouTube videos, meetings)

## 🔄 Recommended Load Order

1. **GSA Domains** - Establishes official government web presence
2. **Census Data** - Base jurisdiction demographic data  
3. **WikiData** - Enriches with metadata and official sources
4. **Government Websites** - Discovers YouTube channels and meeting portals
5. **YouTube Videos** - Loads meeting videos from discovered channels
6. **NACo/NLC** - Enriches with county/city official directories
7. **OpenStates** - State legislative data (if applicable)

## 🎯 Coverage Goals

| Data Source | Target Coverage | Current Status |
|-------------|----------------|----------------|
| GSA Domains | 100% of .gov domains | ✅ 100% (2,272 loaded) |
| Census | 100% of cities/counties | ✅ 100% (4,385 loaded) |
| WikiData | 50%+ enrichment | ✅ 88.5% counties, <1% cities |
| Gov Websites | 25%+ scraped | 🚧 In progress |
| YouTube | 15%+ channels | ✅ 19% (834 jurisdictions) |
| NACo | 50%+ counties | 🚧 TODO |
| NLC | 25%+ cities | 🚧 TODO |

## ⚠️ Before Scraping

1. **Check robots.txt** - Respect crawl rules
2. **Set User-Agent** - Identify your scraper
3. **Rate limit** - Add delays between requests (2-5 seconds)
4. **Cache results** - Avoid duplicate requests
5. **Check terms of service** - Verify you have permission

## 📝 Adding a New Data Source

1. Create directory: `mkdir scripts/datasources/newsource/`
2. Add scraper script: `scripts/datasources/newsource/scrape_data.py`
3. Add README: `scripts/datasources/newsource/README.md`
4. Update CITATIONS.md with data source info
5. Document in this README
6. Test with `--dry-run` first

## 🆘 Support

- See individual source READMEs for specific documentation
- Check CITATIONS.md for source attribution and licenses
- Report issues with specific scrapers in their directories
