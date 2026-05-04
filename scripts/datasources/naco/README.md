# National Association of Counties (NACo) Data Source

Source organization for county-level data from the **National Association of Counties**.

## 📊 Data Source

- **Website:** https://www.naco.org/
- **County Explorer:** https://ce.naco.org/
- **Coverage:** 3,069 counties across all U.S. states and territories

## 🎯 Purpose

Enrich county jurisdiction records with:
- County official directories (commissioners, managers, clerks)
- Contact information (emails, phone numbers)
- County government websites
- County services and departments
- Demographic and economic data

## 📁 Scripts

- `scrape_naco_counties.py` - Scrape county data from NACo County Explorer

## 🚀 Usage

```bash
# Scrape all dev states
python scrape_naco_counties.py --states AL,GA,IN,MA,WA,WI

# Dry run (preview without updating)
python scrape_naco_counties.py --states MA --dry-run

# Scrape specific state
python scrape_naco_counties.py --states WA
```

## 📋 Data Fields

- **County officials:** Names, titles, contact info
- **Contact information:** Official emails, phone numbers
- **Websites:** County government portals
- **Services:** List of county services and departments
- **Demographics:** Population, area, economic indicators

## 🔄 Type of Load

**ENRICHMENT/UPDATE LOAD** - Updates existing county records in `jurisdictions_details_search`

## ⚠️ Notes

- Respects robots.txt and rate limits
- Caches results to avoid duplicate requests
- May require authentication or membership for full access to some data
- Check NACo terms of service before large-scale scraping
