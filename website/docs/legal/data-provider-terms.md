---
sidebar_position: 2
sidebar_label: Data Provider Terms
---

# Data Provider Terms of Service

**Last Updated:** April 28, 2026

:::info[Purpose]
This document provides the complete terms of service, usage policies, and attribution requirements for all third-party data providers used by Open Navigator for Engagement. **Users of our Service must comply with all applicable provider terms.**
:::

## Overview

Open Navigator for Engagement aggregates data from multiple sources. Each source has its own terms of service, usage policies, and attribution requirements. This document consolidates all provider terms to help you stay compliant.

## 🏛️ U.S. Government Data Sources (Public Domain)

### IRS (Exempt Organizations Business Master File & Form 990)

**Data Type:** Tax-exempt organization records, Form 990 filings  
**License:** Public Domain (U.S. Government Work)  
**Terms of Use:** [IRS.gov Copyright and Reuse Policy](https://www.irs.gov/about-irs/irsgov-privacy-policy)

**Usage Rights:**
- ✅ Free to download and redistribute
- ✅ No restrictions on commercial or non-commercial use
- ✅ No API key required
- ✅ Attribution recommended but not required

**Restrictions:**
- ❌ Must not claim IRS endorsement
- ❌ Must not use for unauthorized commercial solicitation

**Attribution (Recommended):**
```
Data source: Internal Revenue Service (IRS)
Exempt Organizations Business Master File (EO-BMF)
https://www.irs.gov/charities-non-profits/exempt-organizations-business-master-file-extract-eo-bmf
```

---

### U.S. Census Bureau

**Data Type:** Geographic boundaries, demographics, government entities  
**License:** Public Domain (U.S. Government Work)  
**Terms of Use:** [Census Bureau Data Policy](https://www.census.gov/about/policies.html)  
**API Documentation:** [Census Bureau API](https://www.census.gov/data/developers.html)

**Usage Rights:**
- ✅ Public domain data
- ✅ Free API access (API key recommended but not required)
- ✅ No restrictions on use or redistribution
- ✅ Attribution appreciated

**Restrictions:**
- ❌ Must not claim U.S. Census Bureau endorsement

**Rate Limits:**
- Without API key: 500 requests/IP per day
- With API key: Higher limits available

**Attribution (Recommended):**
```
Data source: U.S. Census Bureau
https://www.census.gov/
```

---

### National Center for Education Statistics (NCES)

**Data Type:** School district boundaries, demographics, enrollment  
**License:** Public Domain (U.S. Government Work)  
**Terms of Use:** [NCES Privacy Policy](https://nces.ed.gov/privacysecurity/)  
**Data Source:** [NCES Common Core of Data](https://nces.ed.gov/ccd/)

**Usage Rights:**
- ✅ Public domain educational data
- ✅ No API key required
- ✅ Free download and redistribution
- ✅ No personal student information

**Restrictions:**
- ❌ Must not claim NCES endorsement

**Attribution (Recommended):**
```
Data source: National Center for Education Statistics (NCES)
U.S. Department of Education
https://nces.ed.gov/
```

---

### FEC / OpenFEC API

**Data Type:** Campaign finance, political contributions  
**License:** Public Domain (U.S. Government Work)  
**Terms of Use:** [FEC.gov Terms of Use](https://www.fec.gov/updates/sale-or-use-contributor-information/)  
**API Documentation:** [OpenFEC API](https://api.open.fec.gov/developers/)

**Usage Rights:**
- ✅ FEC data is public domain
- ✅ Free API access with API key

**Rate Limits:**
- With API key: 1,000 requests/hour
- Demo key: 30 requests/hour

**CRITICAL RESTRICTIONS:**
- ❌ **CANNOT use contributor information for commercial solicitation or fundraising**
- ❌ **CANNOT sell contributor lists**
- ❌ Must not violate federal campaign finance laws

**Attribution (Required):**
```
Data source: Federal Election Commission (FEC)
https://www.fec.gov/
```

**API Key:** Free at [api.data.gov](https://api.data.gov/signup/)

---

### Grants.gov API

**Data Type:** Federal grant opportunities  
**License:** Public Domain (U.S. Government Work)  
**Terms of Use:** [Grants.gov Terms of Use](https://www.grants.gov/web/grants/support/terms-of-use.html)  
**API Documentation:** [Grants.gov API](https://www.grants.gov/web/grants/support/technical-support/grantor-technical-support/grants-gov-api.html)

**Usage Rights:**
- ✅ Public government data
- ✅ No API key required
- ✅ Free unlimited access

**Restrictions:**
- ❌ Must not misrepresent grant opportunities
- ❌ Must not alter grant information

**Attribution (Recommended):**
```
Data source: Grants.gov
https://www.grants.gov/
```

---

## 💼 Google Services

### Google BigQuery IRS 990 Public Dataset

**Data Type:** IRS Form 990 filings  
**License:** IRS data is Public Domain; BigQuery access subject to Google Cloud Terms  
**Terms of Use:** [Google Cloud Terms of Service](https://cloud.google.com/terms)  
**Dataset:** `bigquery-public-data.irs_990`  
**Documentation:** [Google Cloud Marketplace](https://console.cloud.google.com/marketplace/product/internal-revenue-service/irs-990)

**Usage Rights:**
- ✅ IRS data is public domain
- ✅ BigQuery provides fast SQL-based access
- ✅ First 1 TB of queries per month is FREE

**Requirements:**
- ✅ **MUST comply with Google Cloud Terms of Service**
- ✅ Google Cloud account required
- ✅ Must provide attribution to IRS and Google Cloud

**Restrictions:**
- ❌ Subject to BigQuery quotas and pricing (beyond free tier)
- ❌ Must not use for unauthorized commercial solicitation

**Attribution (Required):**
```
Data source: IRS Form 990 Data
Provided by: Google Cloud Public Datasets
https://console.cloud.google.com/marketplace/product/internal-revenue-service/irs-990
```

---

### Google Civic Information API

**Data Type:** Elected officials, polling locations, election information  
**License:** [Google APIs Terms of Service](https://developers.google.com/terms)  
**API Documentation:** [Google Civic Information API](https://developers.google.com/civic-information)  
**Usage Limits:** [Google Civic API Policies](https://developers.google.com/civic-information/docs/usage_limits)

**Free Tier:**
- ✅ 25,000 requests per day
- ✅ API key required (free from Google Cloud Console)

**Requirements:**
- ✅ **MUST comply with Google APIs Terms of Service**
- ✅ **MUST display attribution:** "Data provided by Google"
- ✅ **MUST NOT cache data beyond 30 days**

**Restrictions:**
- ❌ Subject to Google API quotas
- ❌ Cannot cache data longer than 30 days
- ❌ Must respect rate limits

**Attribution (Required):**
```
Data provided by Google Civic Information API
https://developers.google.com/civic-information
```

**API Key:** Free from [Google Cloud Console](https://console.cloud.google.com/)

---

### Google Data Commons

**Data Type:** Demographics, economics, health statistics  
**License:** [Data Commons Terms](https://datacommons.org/about)  
**API Documentation:** [Data Commons API](https://docs.datacommons.org/api/)

**Usage Rights:**
- ✅ Free access to aggregated statistical data
- ✅ No API key required for most endpoints

**Requirements:**
- ✅ **MUST provide attribution to Google and original data sources**
- ✅ **MUST comply with Google Terms of Service**

**Attribution (Required):**
```
Data source: Google Data Commons
https://datacommons.org/
[Also cite original data sources as specified]
```

---

## 🏢 Nonprofit Data Providers

### Charity Navigator

**Organization:** Charity Navigator, Inc.  
**Principal Office:** 299 Market Street, Suite 250, Saddle Brook, NJ 07663  
**API Terms:** [Charity Navigator API Terms of Use](https://www.charitynavigator.org/partner/api-terms)  
**Last Updated:** March 2025

**Rate Limit:**
- ❌ **MAXIMUM: 1,000 API calls per day** (strictly enforced)

**MANDATORY Attribution Requirements:**

1. **Text Credit (on ALL pages using CN data):**
   ```
   Powered by Charity Navigator
   ```

2. **Source Citation:**
   ```
   Data provided by Charity Navigator
   ```

3. **Linkback (REQUIRED for all charity names):**
   ```html
   <a href="https://www.charitynavigator.org/ein/[EIN]">
     [Organization Name]
   </a>
   ```

4. **Trademark Notice (once per page or in footer/credits):**
   ```
   CHARITY NAVIGATOR and the CHARITY NAVIGATOR logo are registered trademarks 
   of Charity Navigator. All rights reserved. Used with permission.
   ```

**CRITICAL Restrictions:**
- ❌ **CANNOT redistribute Charity Navigator data**
- ❌ **CANNOT create competing rating systems using CN data**
- ❌ **CANNOT exceed 1,000 API calls per day**
- ❌ Caching permitted for performance ONLY (not for redistribution)
- ❌ No ownership rights to cached data
- ❌ CN can terminate access for violations

**Intellectual Property:**
- All Charity Navigator data and ratings are proprietary
- API and database owned by Charity Navigator, Inc.
- Users have NO ownership rights to CN data
- Feedback/suggestions become CN property

**Termination:**
- Charity Navigator may terminate API access at any time for violations
- Upon termination, must cease all use of CN data

**Full Terms:** https://www.charitynavigator.org/partner/api-terms

---

### ProPublica Nonprofit Explorer API

**Organization:** ProPublica, Inc.  
**API Documentation:** [Nonprofit Explorer API](https://projects.propublica.org/nonprofits/api)  
**Data Store Terms:** [ProPublica Data Store Terms](https://www.propublica.org/datastore/terms)

**Usage Rights:**
- ✅ Free unlimited API access
- ✅ IRS data is public domain
- ✅ Commercial and non-commercial use allowed

**Requirements:**
- ✅ **MUST provide attribution to ProPublica**
- ✅ Respectful rate limiting recommended (~1 request/second)

**Restrictions:**
- ❌ ProPublica's analysis may have separate copyright (distinct from IRS data)

**Attribution (Required):**
```
Data source: ProPublica Nonprofit Explorer
https://projects.propublica.org/nonprofits/
```

**Note:** API returns maximum 25 results per request with no pagination. For bulk data, use IRS EO-BMF downloads.

---

### ProPublica Congress API

**Organization:** ProPublica, Inc.  
**API Documentation:** [Congress API](https://projects.propublica.org/api-docs/congress-api/)  
**Coverage:** 102nd Congress (1991) to present

**Rate Limit:**
- 5,000 requests per day

**Requirements:**
- ✅ **API key required** (free at https://www.propublica.org/datastore/api/propublica-congress-api)
- ✅ **MUST provide attribution to ProPublica**
- ✅ Include as HTTP header: `X-API-Key: YOUR_API_KEY`

**Attribution (Required):**
```
Data source: ProPublica Congress API
https://projects.propublica.org/api-docs/congress-api/
```

---

### ProPublica Campaign Finance API

**Organization:** ProPublica, Inc.  
**API Documentation:** [Campaign Finance API](https://projects.propublica.org/api-docs/campaign-finance/)  
**Coverage:** FEC data from 2000 to present

**Rate Limit:**
- 5,000 requests per day

**Requirements:**
- ✅ **API key required** (free at https://www.propublica.org/datastore/api/campaign-finance-api)
- ✅ **MUST provide attribution to ProPublica**
- ✅ Include as HTTP header: `X-API-Key: YOUR_API_KEY`

**CRITICAL RESTRICTIONS:**
- ❌ **CANNOT use contributor information for commercial solicitation**
- ❌ **CANNOT use for fundraising purposes**
- ❌ Must comply with FEC regulations

**Attribution (Required):**
```
Data source: ProPublica Campaign Finance API
Federal Election Commission (FEC) data
https://projects.propublica.org/api-docs/campaign-finance/
```

---

### ProPublica Vital Signs API

**Organization:** ProPublica, Inc.  
**API Documentation:** [Vital Signs API](https://projects.propublica.org/api-docs/vital-signs/)  
**Coverage:** 1,000,000+ healthcare providers

**Rate Limit:**
- 5,000 requests per day

**Requirements:**
- ✅ **API key required** (free at https://www.propublica.org/datastore/api/vital-signs-api)
- ✅ **MUST provide attribution to ProPublica**
- ✅ Include as HTTP header: `X-API-Key: YOUR_API_KEY`

**Attribution (Required):**
```
Data source: ProPublica Vital Signs
https://projects.propublica.org/vital-signs/
```

---

### Every.org Charity API

**Organization:** Every.org (Public Benefit Corporation)  
**API Documentation:** [Every.org Nonprofit API](https://www.every.org/nonprofit-api)  
**Coverage:** 1,000,000+ verified nonprofits

**Requirements:**
- ✅ API key required (free tier available)
- ✅ Must comply with Every.org API Terms of Service

**Attribution (Required):**
```
Data source: Every.org
https://www.every.org/
```

**Note:** API authentication required. Contact Every.org for API access.

---

### GivingTuesday 990 Data Lake

**Organization:** GivingTuesday  
**Source:** [GivingTuesday 990 Data Infrastructure](https://990data.givingtuesday.org/)  
**Storage:** AWS S3 Public Bucket  
**License:** Public Domain (IRS data)  
**AWS Registry:** [OpenData on AWS](https://registry.opendata.aws/gt990datalake/)

**Usage Rights:**
- ✅ Free access via AWS S3
- ✅ No AWS credentials required (`--no-sign-request`)
- ✅ IRS data is public domain

**Requirements:**
- ✅ **MUST attribute to GivingTuesday and IRS**

**Costs:**
- Standard AWS data egress charges may apply

**Attribution (Required):**
```
Data source: GivingTuesday 990 Data Infrastructure
Internal Revenue Service (IRS) Form 990 XML Filings
https://990data.givingtuesday.org/
```

---

## 🗳️ Civic & Government APIs

### Open States API

**Organization:** Open States Foundation (part of Plural)  
**API Documentation:** [Open States API v3](https://docs.openstates.org/api-v3/)  
**Terms of Service:** [Open States ToS](https://openstates.org/tos/)

**Free Tier:**
- 50,000 requests per month

**Requirements:**
- ✅ **API key required** (free at https://openstates.org/accounts/signup/)
- ✅ **MUST display attribution:** "Powered by Open States"
- ✅ Must comply with API rate limits

**Restrictions:**
- ❌ Data licenses vary by state jurisdiction
- ❌ Must respect 50,000 requests/month limit on free tier

**Attribution (Required):**
```
Powered by Open States
https://openstates.org/
```

**Data Licensing:**
- Legislative data licenses vary by state
- Check specific state terms for redistribution rights

---

## 🌐 Linked Open Data Sources

### Wikidata

**Organization:** Wikimedia Foundation  
**SPARQL Endpoint:** [Wikidata Query Service](https://query.wikidata.org/)  
**License:** [CC0 1.0 Public Domain Dedication](https://creativecommons.org/publicdomain/zero/1.0/)  
**Terms of Use:** [Wikimedia Terms of Use](https://foundation.wikimedia.org/wiki/Terms_of_Use)

**Usage Rights:**
- ✅ CC0 Public Domain - no restrictions
- ✅ No API key required
- ✅ Free unlimited access
- ✅ Attribution appreciated but not required

**Requirements:**
- ✅ **MUST respect rate limits** (1 request/second recommended)
- ✅ **MUST set descriptive User-Agent header**

**User-Agent Format:**
```
User-Agent: YourApp/1.0 (https://yoursite.com/; contact@example.com)
```

**Attribution (Appreciated):**
```
Data source: Wikidata
https://www.wikidata.org/
License: CC0 Public Domain
```

---

### DBpedia

**Organization:** DBpedia Association  
**Lookup API:** [DBpedia Lookup Service](https://lookup.dbpedia.org/)  
**License:** [CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0/) and [GFDL](https://www.gnu.org/licenses/fdl-1.3.html)  
**Terms of Use:** [DBpedia Usage Policies](https://www.dbpedia.org/about/)

**Usage Rights:**
- ✅ Free to use with attribution
- ✅ No API key required

**Requirements:**
- ✅ **MUST provide attribution to DBpedia and Wikipedia**
- ✅ **MUST respect rate limits** (1-2 requests/second recommended)
- ✅ **MUST set descriptive User-Agent header**
- ✅ **Share-alike license applies** (CC BY-SA 3.0)

**Attribution (Required):**
```
Data source: DBpedia and Wikipedia
https://www.dbpedia.org/
License: CC BY-SA 3.0 and GFDL
```

**Share-Alike Requirement:**
- If you create derivative works, you must license them under CC BY-SA 3.0 or compatible license

---

## 🎓 Academic & Research Datasets

### MeetingBank Dataset

**Organization:** Association for Computational Linguistics (ACL)  
**Dataset:** [MeetingBank on HuggingFace](https://huggingface.co/datasets/huuuyeah/meetingbank)  
**Paper:** [ACL 2023 Proceedings](https://arxiv.org/abs/2305.17529)

**Citation Required:**
```bibtex
@inproceedings{hu-etal-2023-meetingbank,
    title = "MeetingBank: A Benchmark Dataset for Meeting Summarization",
    author = "Yebowen Hu and Tim Ganter and Hanieh Deilamsalehy and 
              Franck Dernoncourt and Hassan Foroosh and Fei Liu",
    booktitle = "Proceedings of the 61st Annual Meeting of the 
                 Association for Computational Linguistics (ACL)",
    month = July,
    year = "2023",
    address = "Toronto, Canada",
    publisher = "Association for Computational Linguistics",
}
```

**Attribution (Required):**
```
Dataset: MeetingBank
Authors: Hu et al. (2023)
https://arxiv.org/abs/2305.17529
```

---

### LocalView Dataset (Harvard Dataverse)

**Organization:** Harvard University Mellon Urbanism Lab  
**Dataverse:** [Harvard Dataverse](https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/NJTBEM)  
**Website:** [LocalView.net](https://www.localview.net/)

**License:** Research use (Harvard Dataverse terms apply)

**Citation Required:**
```bibtex
@dataset{localview_2024,
  author = {{Harvard Mellon Urbanism Lab}},
  title = {LocalView: Municipal Meeting Videos and Transcripts},
  year = {2024},
  publisher = {Harvard Dataverse},
  doi = {10.7910/DVN/NJTBEM},
  url = {https://www.localview.net/}
}
```

**Requirements:**
- ✅ Must cite original research
- ✅ Research use license applies
- ❌ Cannot redistribute without permission

**Attribution (Required):**
```
Data source: LocalView Dataset
Harvard Mellon Urbanism Lab
https://www.localview.net/
```

---

### Council Data Project (CDP)

**Organization:** Open-source civic tech collaboration  
**GitHub:** [CouncilDataProject](https://github.com/CouncilDataProject)  
**Website:** [CouncilDataProject.org](https://councildataproject.org/)  
**License:** Open source (MIT)

**Usage Rights:**
- ✅ MIT License - permissive use
- ✅ Commercial and non-commercial use allowed

**Attribution (Required):**
```
Data source: Council Data Project
https://councildataproject.org/
License: MIT
```

---

### City Scrapers / Documenters.org

**Organization:** Documenters Network (civic journalism collaboration)  
**GitHub:** [City-Bureau](https://github.com/City-Bureau)  
**Website:** [Documenters.org](https://www.documenters.org/)  
**License:** Open source (MIT)

**Usage Rights:**
- ✅ MIT License - permissive use
- ✅ Commercial and non-commercial use allowed

**Attribution (Required):**
```
Data source: City Scrapers / Documenters Network
https://www.documenters.org/
License: MIT
```

---

### Roper Center for Public Opinion Research

**Organization:** Cornell University  
**Database:** [iPoll Database](https://ropercenter.cornell.edu/ipoll/)  
**License:** Free public search; full data requires institutional membership

**Usage Rights:**
- ✅ Metadata and question wording: Free
- ❌ Full survey data: Requires membership

**Citation (Required):**
```
Roper Center for Public Opinion Research, Cornell University.
iPoll Databank. https://ropercenter.cornell.edu/ipoll/
```

---

## 🗳️ Election Data Sources

### MIT Election Data + Science Lab

**Organization:** Massachusetts Institute of Technology  
**Repository:** [GitHub - MEDSL](https://github.com/MEDSL/official-returns)  
**Website:** [MIT Election Lab](https://electionlab.mit.edu/data)  
**License:** Free for research and commercial use

**Usage Rights:**
- ✅ Free to use and redistribute
- ✅ Commercial and non-commercial use allowed

**Attribution (Required):**
```
Data source: MIT Election Data and Science Lab
https://electionlab.mit.edu/data
```

---

### OpenElections

**Organization:** OpenElections Project  
**GitHub:** [OpenElections](https://github.com/openelections)  
**Website:** [OpenElections.net](https://openelections.net/)  
**License:** Open source (varies by state)

**Usage Rights:**
- ✅ Free to use with attribution
- ⚠️ Licensing varies by state

**Attribution (Required):**
```
Data source: OpenElections
https://openelections.net/
[Include state-specific attribution as applicable]
```

---

## 💰 Paid/Commercial Services (NOT USED)

### Ballotpedia API v3.0

**Organization:** Lucy Burns Institute  
**API Documentation:** [Ballotpedia API](https://ballotpedia.org/API_documentation)  
**License:** **Paid service - requires commercial license**

**Status:** ⚠️ **NOT USED in Open Navigator**

- Code in `discovery/ballotpedia_integration.py` is **reference only**
- Web scraping may violate Ballotpedia terms of service
- **Do not use without paid API license**

**Free Alternatives:**
- ✅ Google Civic Information API (25k requests/day free)
- ✅ Open States API (50k requests/month free)
- ✅ NCES (free for school boards)

**If You Have Paid Access:**
- Must comply with Ballotpedia API Terms of Use
- Contact Ballotpedia for licensing: https://ballotpedia.org/API_documentation

---

## ⚖️ Compliance Summary Table

| Provider | API Key | Rate Limit | Attribution Required | Share-Alike | Commercial Use |
|----------|---------|------------|---------------------|-------------|----------------|
| **IRS** | No | None | Recommended | No | Yes |
| **Census** | No* | 500/day | Recommended | No | Yes |
| **NCES** | No | None | Recommended | No | Yes |
| **FEC/OpenFEC** | Yes | 1k/hour | Yes | No | Yes** |
| **Google BigQuery** | Yes | 1TB/mo free | Yes | No | Yes |
| **Google Civic** | Yes | 25k/day | **YES** | No | Yes |
| **Google Data Commons** | No | None | **YES** | No | Yes |
| **Charity Navigator** | Yes | **1k/day** | **YES*** | No | Yes |
| **ProPublica (all)** | Varies | 5k/day | **YES** | No | Yes |
| **Open States** | Yes | 50k/mo | **YES** | No | Yes |
| **Wikidata** | No | ~1/sec | No | No | Yes |
| **DBpedia** | No | ~1-2/sec | **YES** | **YES** | Yes |
| **MeetingBank** | No | N/A | **YES** | No | Research |
| **LocalView** | No | N/A | **YES** | No | Research |

**Notes:**
- *Census: API key recommended for higher limits
- **FEC: Cannot use contributor data for commercial solicitation
- ***Charity Navigator: Extremely strict - must display "Powered by Charity Navigator", link all names, include trademark notice

---

## 📞 Contact Information for Providers

### Government Agencies
- **IRS:** https://www.irs.gov/charities-non-profits
- **Census Bureau:** https://www.census.gov/data/developers.html
- **FEC:** https://www.fec.gov/
- **NCES:** https://nces.ed.gov/

### Nonprofit Data
- **Charity Navigator:** https://www.charitynavigator.org/about-us/contact/
- **ProPublica:** data@propublica.org
- **GivingTuesday:** https://990data.givingtuesday.org/

### Civic APIs
- **Open States:** https://openstates.org/tos/
- **Google Civic:** https://developers.google.com/civic-information

### Academic Datasets
- **Harvard Dataverse:** https://dataverse.harvard.edu/
- **MIT Election Lab:** https://electionlab.mit.edu/

---

## ⚠️ Important Reminders

### Always Required
1. **Respect rate limits** - implement caching and delays
2. **Provide attribution** - credit data sources appropriately
3. **Read provider terms** - terms may change over time
4. **Set User-Agent** - identify your application in API requests

### Never Allowed
1. **Commercial solicitation** - Do not use FEC donor data for fundraising
2. **Circumvent limits** - Do not create multiple accounts to bypass quotas
3. **Remove attribution** - Do not strip required credits
4. **Violate redistribution terms** - Respect each provider's redistribution policies

### When in Doubt
- **Provide attribution** - over-attribution is safer than under-attribution
- **Contact the provider** - ask for clarification on unclear terms
- **Document your usage** - keep records of compliance efforts

---

## 🔄 Updates & Changes

This document is updated regularly to reflect:
- New data sources added
- Changes to provider terms of service
- Updated rate limits and pricing
- New attribution requirements

**Last Review Date:** April 28, 2026

**Subscribe to updates:**
- Watch our [GitHub repository](https://github.com/getcommunityone/open-navigator-for-engagement)
- Check this page periodically for updates

---

:::warning[Legal Requirement]
**Compliance with these terms is mandatory.** Violations may result in:
- Loss of API access from providers
- Termination of your use of Open Navigator
- Legal action by data providers
- Damage to the civic tech ecosystem

When in doubt, provide attribution and respect usage limits.
:::
