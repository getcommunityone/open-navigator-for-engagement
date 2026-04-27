---
sidebar_position: 2
sidebar_label: Citations & Data Sources
---

# Citations & Data Sources

:::tip **Why This Page Matters**
**All data used in Open Navigator for Engagement is properly cited and attributed.** This page provides complete citations, licenses, BibTeX references, and links to original sources for academic research, government data, civic tech standards, and more.

**Use this page to:**
- ✅ Cite data sources in your research or publications
- ✅ Understand licensing and usage terms
- ✅ Find original dataset documentation
- ✅ Access API documentation and technical specs
:::

This page documents all data sources, standards, and research contributions used in **Open Navigator for Engagement**. All datasets and specifications are properly attributed with citations, licenses, and usage notes.

## 📑 Quick Navigation

<div style={{display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '15px', margin: '20px 0'}}>
  <a href="#-academic-research" className="card" style={{textDecoration: 'none', padding: '15px', borderLeft: '4px solid #2196F3'}}>
    <strong>🎓 Academic Research</strong><br/>
    <span style={{fontSize: '0.9em', color: '#666'}}>MeetingBank, LocalView, Roper Center, CDP, City Scrapers</span>
  </a>
  <a href="#government-data" className="card" style={{textDecoration: 'none', padding: '15px', borderLeft: '4px solid #4CAF50'}}>
    <strong>🏛️ Government Data</strong><br/>
    <span style={{fontSize: '0.9em', color: '#666'}}>U.S. Census, NCES, IRS</span>
  </a>
  <a href="#civic-tech-standards" className="card" style={{textDecoration: 'none', padding: '15px', borderLeft: '4px solid #FF9800'}}>
    <strong>🌐 Civic Tech Standards</strong><br/>
    <span style={{fontSize: '0.9em', color: '#666'}}>OCD-ID, Popolo, Schema.org, CEDS, OMOP CDM</span>
  </a>
  <a href="#election--advocacy" className="card" style={{textDecoration: 'none', padding: '15px', borderLeft: '4px solid #9C27B0'}}>
    <strong>🗳️ Election & Advocacy</strong><br/>
    <span style={{fontSize: '0.9em', color: '#666'}}>Ballotpedia, MIT Election Lab, OpenElections</span>
  </a>
  <a href="#nonprofit--philanthropy" className="card" style={{textDecoration: 'none', padding: '15px', borderLeft: '4px solid #F44336'}}>
    <strong>🏢 Nonprofit & Philanthropy</strong><br/>
    <span style={{fontSize: '0.9em', color: '#666'}}>ProPublica, IRS, Every.org, Findhelp, 211, Microsoft CDM</span>
  </a>
  <a href="#international-aid-transparency" className="card" style={{textDecoration: 'none', padding: '15px', borderLeft: '4px solid #00BCD4'}}>
    <strong>🌍 International Aid</strong><br/>
    <span style={{fontSize: '0.9em', color: '#666'}}>IATI Standard v2.03</span>
  </a>
  <a href="#-fact-checking" className="card" style={{textDecoration: 'none', padding: '15px', borderLeft: '4px solid #8BC34A'}}>
    <strong>✅ Fact-Checking</strong><br/>
    <span style={{fontSize: '0.9em', color: '#666'}}>Google, PolitiFact, FactCheck.org</span>
  </a>
  <a href="#-enterprise-tech-for-social-good" className="card" style={{textDecoration: 'none', padding: '15px', borderLeft: '4px solid #E91E63'}}>
    <strong>💼 Enterprise Tech for Social Good</strong><br/>
    <span style={{fontSize: '0.9em', color: '#666'}}>Microsoft, Google, AWS, Databricks, Snowflake, Salesforce</span>
  </a>
  <a href="#acknowledgments" className="card" style={{textDecoration: 'none', padding: '15px', borderLeft: '4px solid #607D8B'}}>
    <strong>🙏 Acknowledgments</strong><br/>
    <span style={{fontSize: '0.9em', color: '#666'}}>Organizations & individuals</span>
  </a>
</div>

---

## 🎓 Academic Research

### MeetingBank Dataset

**What we use:** 1,366 city council meetings from 6 U.S. cities with transcripts and summaries for meeting discovery, transcript analysis, and summarization benchmarking.

**Citation:**
> Yebowen Hu, Tim Ganter, Hanieh Deilamsalehy, Franck Dernoncourt, Hassan Foroosh, Fei Liu. "MeetingBank: A Benchmark Dataset for Meeting Summarization" In Proceedings of the 61st Annual Meeting of the Association for Computational Linguistics (ACL), July 2023, Toronto, Canada.

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
- [📄 Paper](https://arxiv.org/abs/2305.17529)
- [💾 Dataset](https://huggingface.co/datasets/huuuyeah/meetingbank)
- [📦 Zenodo](https://zenodo.org/record/7989108)

---

### LocalView Dataset (Harvard Dataverse)

**Organization:** Harvard University Mellon Urbanism Lab  
**What we use:** 1,000+ municipalities with meeting videos and automated transcripts for large-scale civic data analysis.

- **Website:** https://www.localview.net/
- **Dataverse:** https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/NJTBEM
- **GitHub:** https://mellonurbanism.harvard.edu/localview
- **Coverage:** Thousands of U.S. jurisdictions with continuous data collection
- **Data Included:**
  - Meeting videos (YouTube URLs)
  - Automated transcripts via speech-to-text
  - Metadata (meeting dates, agencies, agendas)
  - Quality tracking per jurisdiction
- **License:** Research use (Harvard Dataverse)
- **Research-grade:** Designed for large-scale quantitative analysis

**BibTeX:**
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

---

### Council Data Project (CDP)

**Organization:** Open-source civic tech collaboration  
**What we use:** 20+ cities with complete data pipelines - meeting transcripts, videos, voting records, and legislation tracking.

- **Website:** https://councildataproject.org/
- **GitHub:** https://github.com/CouncilDataProject
- **Coverage:** 20+ major U.S. cities with full infrastructure
- **Data Included:**
  - Meeting transcripts (searchable, indexed)
  - Video recordings with timestamps
  - Voting records and roll calls
  - Legislation text and tracking
  - Councilmember information
- **Infrastructure:** Complete ETL pipelines for each city
- **License:** Open source (MIT)
- **API:** Per-city deployments (e.g., https://councildataproject.org/seattle)

**BibTeX:**
```bibtex
@software{council_data_project,
  title = {Council Data Project},
  author = {{Council Data Project Contributors}},
  year = {2024},
  url = {https://councildataproject.org/},
  license = {MIT}
}
```

---

### City Scrapers / Documenters.org

**Organization:** Documenters Network (civic journalism collaboration)  
**What we use:** 100-500 validated government agency URLs across 5 major cities for automated meeting discovery.

- **Website:** https://cityscrapers.org/
- **Documenters:** https://www.documenters.org/
- **GitHub:** https://github.com/City-Bureau
- **Coverage:** Chicago, Pittsburgh, Detroit, Cleveland, Los Angeles
- **Data Included:**
  - Government agency URLs (start_urls from spider files)
  - Granicus video page URLs with YouTube embeds
  - Meeting event schemas
  - Scraper patterns for common platforms
- **Cities Covered:**
  - Chicago City Scrapers
  - Pittsburgh City Scrapers
  - Detroit Documenters
  - Cleveland City Scrapers
  - LA Metro Documenters
- **License:** Open source (MIT)
- **Use Case:** Pre-validated URLs for quality meeting discovery

**BibTeX:**
```bibtex
@software{city_scrapers,
  title = {City Scrapers},
  author = {{City Bureau and Documenters Network}},
  year = {2024},
  url = {https://cityscrapers.org/},
  license = {MIT}
}
```

---

### Roper Center for Public Opinion Research

**Organization:** Cornell University  
**What we use:** Scientifically validated survey questions and public opinion baselines for topic definitions and messaging optimization.

- **Source:** https://ropercenter.cornell.edu/
- **iPoll Database:** https://ropercenter.cornell.edu/ipoll/
- **Coverage:** 500,000+ survey questions from 1930s-present, all major polling organizations
- **License:** Free public search (metadata and question wording), full data requires institutional membership
- **Citation:** "Roper Center for Public Opinion Research, Cornell University. iPoll Databank. https://ropercenter.cornell.edu/ipoll/"

---

## 🏛️ Government Data

### U.S. Census Bureau

**What we use:** Geographic boundaries, demographic data, population estimates, and economic indicators.

- **Source:** https://www.census.gov/
- **License:** Public Domain (U.S. Government)
- **Datasets:** Census Gazetteer, American Community Survey (ACS), Decennial Census
- **Coverage:** All 50 states, 3,144 counties, 19,000+ incorporated places

### Harvard Dataverse

**What we use:** Meeting datasets and civic engagement research.

- **Source:** https://dataverse.harvard.edu/
- **License:** Varies by dataset
- **Coverage:** Academic research datasets on local government, public meetings, civic participation

---

## 🌐 Civic Tech Standards

### Open Civic Data (OCD) Standards

**What we use:** Standardized jurisdiction identifiers for cross-platform compatibility.

**Standard:** [OCDEP 2 - Division Identifiers](https://open-civic-data.readthedocs.io/en/latest/proposals/0002.html)

- **Repository:** https://github.com/opencivicdata/ocd-division-ids
- **License:** Open source
- **Format:** `ocd-division/country:us/state:al/place:birmingham`
- **Coverage:** All U.S. jurisdictions (cities, counties, states, school districts)

**Example Implementation:**
```
ocd-division/country:us/state:al                      # State
ocd-division/country:us/state:al/county:jefferson     # County
ocd-division/country:us/state:al/place:birmingham     # City
ocd-division/country:us/state:al/school_district:birmingham_city  # School District
```

### Popolo Project

**What we use:** International open government data specification for people, organizations, and elected positions.

- **Specification:** https://www.popoloproject.com/
- **GitHub:** https://github.com/popolo-project/popolo-spec
- **License:** Creative Commons Attribution 4.0 International
- **Adoption:** Used by Civic Commons, OpenNorth, mySociety, Sunlight Foundation, and 30+ civic tech organizations worldwide

**Popolo Classes Implemented:**

| Popolo Class | Our Entity | Use Case |
|--------------|------------|----------|
| **Person** | LEADER | Elected officials, appointees |
| **Organization** | ORGANIZATION | Nonprofits, government agencies |
| **Membership** | LEADER ↔ ORGANIZATION | Relationships with roles and terms |
| **Post** | LEADER.position_type | Positions like "Mayor", "Council Member" |
| **VoteEvent** | VOTE | Voting records on motions/bills |
| **Motion** | AGENDA, LEGISLATION | Formal proposals |
| **Area** | JURISDICTION | Geographic/political boundaries |
| **Event** | MEETING | Public meetings with agendas |

<details>
<summary><strong>Popolo Dependencies (15 W3C/IETF Standards)</strong></summary>

| Standard | Prefix | Use Case |
|----------|--------|----------|
| [FOAF](http://xmlns.com/foaf/0.1/) | `foaf` | People, social networks |
| [vCard](https://www.rfc-editor.org/rfc/rfc6350.html) | `vcard` | Contact information (IETF RFC 6350) |
| [Schema.org](https://schema.org/) | `schema` | Structured web data |
| [DCMI Terms](https://www.dublincore.org/specifications/dublin-core/dcmi-terms/) | `dcterms` | Metadata, provenance |
| [W3C Organization Ontology](https://www.w3.org/TR/vocab-org/) | `org` | Organizational structures |
| [ISA Location](https://www.w3.org/ns/locn) | `locn` | Addresses, geographic data |
| [GeoNames](http://www.geonames.org/ontology/) | `gn` | Geographic identifiers |
| [SKOS](https://www.w3.org/2004/02/skos/) | `skos` | Taxonomies, classification |
| [BIO](http://purl.org/vocab/bio/0.1/) | `bio` | Life events, relationships |
| [BIBFRAME](https://www.loc.gov/bibframe/) | `bf` | Bibliographic references |
| [W3C Contact](http://www.w3.org/2000/10/swap/pim/contact#) | `con` | Contact utility concepts |
| [NEPOMUK Calendar](http://www.semanticdesktop.org/ontologies/ncal/) | `ncal` | Events, meetings |
| [ISA Person](http://www.w3.org/ns/person) | `person` | Person attributes |
| [RDF Schema](https://www.w3.org/TR/rdf-schema/) | `rdfs` | Semantic web foundation |
| [ODRS](http://schema.theodi.org/odrs) | `odrs` | Data licensing |

</details>

### Schema.org

**Organization:** W3C Community Group (sponsors: Google, Microsoft, Yahoo, Yandex)  
**What we use:** SEO-optimized structured data, JSON-LD exports, semantic web compatibility.

- **Source:** https://schema.org/
- **License:** Creative Commons Attribution-ShareAlike License (CC BY-SA 3.0)
- **Coverage:** 800+ types, 1,400+ properties

**Our Schema.org Type Mappings:**

| Our Entity | Schema.org Type | Use Case |
|------------|----------------|----------|
| JURISDICTION | [AdministrativeArea](https://schema.org/AdministrativeArea) | City/county pages |
| MEETING | [Event](https://schema.org/Event) | Google Calendar rich results |
| LEADER | [Person](https://schema.org/Person) + [GovernmentOfficial](https://schema.org/GovernmentOfficial) | Official profiles |
| ORGANIZATION | [Organization](https://schema.org/Organization) + [NGO](https://schema.org/NGO) | Nonprofit listings |
| LEGISLATION | [Legislation](https://schema.org/Legislation) | Bill tracking |
| BALLOT_MEASURE | [Legislation](https://schema.org/Legislation) | Ballot guides |
| VOTE | [VoteAction](https://schema.org/VoteAction) | Voting records |
| FACT_CHECK | [ClaimReview](https://schema.org/ClaimReview) | Google Fact Check Explorer |
| SCHOOL_DISTRICT | [EducationalOrganization](https://schema.org/EducationalOrganization) | School district info |
| VIDEO | [VideoObject](https://schema.org/VideoObject) | YouTube integration |
| DOCUMENT | [DigitalDocument](https://schema.org/DigitalDocument) | Document library |
| CONSTITUENT | [Person](https://schema.org/Person) | Donor/volunteer profiles |
| DONATION | [DonateAction](https://schema.org/DonateAction) | Donation receipts |
| CAMPAIGN | [FundingScheme](https://schema.org/FundingScheme) | Fundraising campaigns |
| PROGRAM_DELIVERY | [Service](https://schema.org/Service) | Program catalog |

**Benefits:**
- ✅ Google Search rich results
- ✅ Voice assistant compatibility (Alexa, Google Assistant)
- ✅ Knowledge Graph integration
- ✅ Cross-platform (Apple, Bing, Yandex)

### Common Education Data Standards (CEDS)

**Organization:** U.S. Department of Education, National Center for Education Statistics (NCES)  
**What we use:** School district data modeling, NCES interoperability, education finance tracking.

- **Source:** https://ceds.ed.gov/
- **GitHub:** https://github.com/CEDStandards
- **License:** Public Domain (U.S. Government)
- **Coverage:** 2,300+ data elements, 500+ option sets

**CEDS Alignment:**

| Our Field | CEDS Element ID | CEDS Element Name |
|-----------|----------------|-------------------|
| `nces_id` | 000827 | LEA Identifier (NCES) |
| `district_name` | 000168 | Name of Institution |
| `total_students` | 001475 | Student Count |
| `total_revenue` | 000612 | Total Revenue |
| `per_pupil_spending` | 000613 | Expenditure per Student |

**Benefits:**
- ✅ NCES Common Core of Data (CCD) compatibility
- ✅ F-33 Finance Survey alignment
- ✅ Federal grant reporting (ESSA, Title I, IDEA)

---

### OMOP Common Data Model (OHDSI)

**Organization:** Observational Health Data Sciences and Informatics (OHDSI)  
**What we use:** Vocabulary and terminology standardization system - CONCEPT, VOCABULARY, CONCEPT_CLASS, CONCEPT_RELATIONSHIP tables for consistent data classification.

- **Source:** https://ohdsi.github.io/CommonDataModel/
- **GitHub:** https://github.com/OHDSI/CommonDataModel
- **Vocabulary Documentation:** https://ohdsi.github.io/TheBookOfOhdsi/StandardizedVocabularies.html
- **License:** Apache License 2.0
- **Coverage:** Comprehensive vocabulary system for standardizing concepts across domains

**OMOP CDM Tables We Implement:**

| Table | Purpose | Our Use Case |
|-------|---------|-------------|
| **CONCEPT** | Master vocabulary list | Standardized codes for topics, demographics, classifications |
| **VOCABULARY** | Source vocabularies | Track origin of concepts (NTEE, FIPS, Schema.org, etc.) |
| **CONCEPT_CLASS** | Categorization | Group concepts by type (demographic, geographic, topic) |
| **CONCEPT_RELATIONSHIP** | Linkages | Map relationships between concepts (is-a, maps-to, subsumes) |

**Our OMOP-Inspired Vocabularies:**

| Vocabulary ID | Description | Concept Count |
|---------------|-------------|---------------|
| `NTEE` | National Taxonomy of Exempt Entities | 600+ |
| `FIPS` | Federal Information Processing Standards | 90,000+ |
| `Schema.org` | Structured data types | 800+ |
| `Popolo` | Open government data specs | 15+ |
| `OCD-ID` | Open Civic Data identifiers | 22,000+ |
| `CEDS` | Common Education Data Standards | 2,300+ |
| `CENSUS` | U.S. Census categories | 1,000+ |
| `INTERNAL` | Custom platform classifications | 500+ |

**Example Implementation:**
```sql
-- CONCEPT table: standardized demographics
concept_id | concept_name              | vocabulary_id | concept_class_id
-----------|---------------------------|---------------|------------------
100001     | Race: White               | CENSUS        | Demographic
100002     | Race: Black/African Amer. | CENSUS        | Demographic
100003     | Hispanic/Latino Ethnicity | CENSUS        | Demographic
100004     | Gender: Male              | CENSUS        | Demographic

-- CONCEPT_RELATIONSHIP: hierarchies
concept_id_1 | concept_id_2 | relationship_id
-------------|--------------|----------------
100002       | 100000       | Is a           # Race category
100003       | 100010       | Is a           # Ethnicity category
```

**Benefits:**
- ✅ Consistent terminology across all datasets
- ✅ Hierarchical concept relationships
- ✅ Traceable concept provenance (source vocabularies)
- ✅ Industry-standard approach used by healthcare and research institutions
- ✅ Supports multiple classification systems simultaneously

**BibTeX:**
```bibtex
@misc{ohdsi_omop_cdm,
  author = {{Observational Health Data Sciences and Informatics (OHDSI)}},
  title = {OMOP Common Data Model},
  year = {2024},
  url = {https://ohdsi.github.io/CommonDataModel/},
  license = {Apache-2.0}
}
```

---

## 🗳️ Election & Advocacy

### Ballotpedia

**Organization:** Lucy Burns Institute  
**What we use:** Ballot measures, referendums, propositions for fluoridation tracking and health policy analysis.

- **Source:** https://ballotpedia.org/
- **API:** https://ballotpedia.org/API-documentation
- **Coverage:** All 50 states, historical measures back to 1990s
- **License:** API access limited at scale (paid tier available)

### MIT Election Data + Science Lab

**Organization:** Massachusetts Institute of Technology  
**What we use:** County-level election results for political composition analysis.

- **Source:** https://electionlab.mit.edu/data
- **Repository:** https://github.com/MEDSL/official-returns
- **Coverage:** 1976-present, presidential/congressional/gubernatorial results
- **License:** Free for research and commercial use

### OpenElections

**What we use:** State-by-state certified election results in standardized CSV format.

- **Source:** https://openelections.net/
- **GitHub:** https://github.com/openelections
- **Coverage:** All 50 states (various completion levels), precinct-level data
- **License:** Open source (varies by state)

### Open States API

**What we use:** State and local legislative information, bill tracking.

- **Source:** https://openstates.org/
- **Coverage:** 100,000+ state bills, 7,300+ state legislators
- **License:** Varies by state
- **API Key:** Required for access

---

## 🏢 Nonprofit & Philanthropy

### ProPublica Nonprofit Explorer

**Organization:** ProPublica, Inc.  
**What we use:** **PRIMARY SOURCE** for nonprofit financial data - IRS Form 990 filings, revenue, expenses, executive compensation, NTEE codes.

- **Source:** https://projects.propublica.org/nonprofits/
- **API Documentation:** https://projects.propublica.org/nonprofits/api
- **Coverage:** 3,000,000+ organizations, 10+ years of historical data
- **Data Included:**
  - Total revenue, expenses, assets, liabilities
  - Executive compensation (top 5 highest paid)
  - Program service expenses vs. administrative overhead
  - NTEE classification codes (National Taxonomy of Exempt Entities)
  - EIN (Employer Identification Number) for verification
- **Rate Limits:** Free, unlimited access (respectful use recommended: ~1 req/sec)
- **License:** Free for research and commercial use

**BibTeX:**
```bibtex
@misc{propublica_nonprofits,
  author = {{ProPublica}},
  title = {Nonprofit Explorer},
  year = {2024},
  url = {https://projects.propublica.org/nonprofits/},
  note = {Accessed: 2024}
}
```

---

### IRS Tax-Exempt Organization Search (TEOS)

**Organization:** Internal Revenue Service (IRS), U.S. Department of Treasury  
**What we use:** Official tax-exempt status verification, Pub 78 deductibility data, bulk downloads of all U.S. nonprofits.

- **Source:** https://www.irs.gov/charities-non-profits/tax-exempt-organization-search
- **Bulk Data Downloads:** https://www.irs.gov/charities-non-profits/tax-exempt-organization-search-bulk-data-downloads
- **Coverage:** All registered 501(c)(3) and other tax-exempt organizations
- **Update Frequency:** Monthly
- **License:** Public domain (U.S. government data)

**Note:** ProPublica API already includes this data in a more accessible format. Direct IRS access primarily used for bulk downloads and verification.

---

### Every.org Charity API

**Organization:** Every.org (Public Benefit Corporation)  
**What we use:** Human-readable mission statements, organization logos, cause categories, cleaner metadata than raw IRS filings.

- **API Documentation:** https://www.every.org/nonprofit-api
- **Coverage:** 1,000,000+ verified nonprofits
- **Data Included:**
  - Mission statements and descriptions
  - Organization logos and images
  - Cause tags (health, education, environment, etc.)
  - Social media links
- **Access:** API key required (free tier available)
- **License:** API Terms of Service

---

### Findhelp.org (Aunt Bertha)

**Organization:** Findhelp (formerly Aunt Bertha)  
**What we use:** Comprehensive directory of local social services - specific programs, hours, eligibility requirements, contact information.

- **Source:** https://www.findhelp.org/
- **Coverage:** 400,000+ community programs across the United States
- **Data Included:**
  - Program descriptions and services offered
  - Days/hours of operation
  - Eligibility requirements
  - Languages spoken
  - Insurance accepted
  - Contact information (phone, email, address)
- **Access:** Public search available, API access by request
- **Use Case:** Manual enrichment of ProPublica financial data with service delivery details

**Example:** https://www.findhelp.org/search?query=dental&location=Tuscaloosa,%20AL

---

### 211 Regional Directories

**What we use:** Regional social services directories with detailed program information, crisis hotlines, local resources.

- **Source:** https://www.211.org/ (national network)
- **Example:** https://www.211connects.org (Alabama)
- **Coverage:** Local services in most U.S. cities and counties
- **Data Included:**
  - Specific services and programs
  - Hours of operation
  - Eligibility criteria
  - Languages and accessibility
- **Access:** Public search, some regions offer data partnerships
- **License:** Varies by region

---

### Microsoft Common Data Model for Nonprofits

**Organization:** Microsoft Corporation  
**What we use:** Nonprofit data standardization, constituent relationship management, donor tracking, program outcome measurement.

- **Repository:** https://github.com/microsoft/Nonprofits/tree/master/CommonDataModelforNonprofits
- **ERD Documentation:** [common-data-model-for-nonprofits-erds.pdf](https://github.com/microsoft/Nonprofits/blob/master/CommonDataModelforNonprofits/Documents/common-data-model-for-nonprofits-erds.pdf)
- **License:** MIT License
- **Coverage:** Donor management, fundraising, program delivery, volunteer management, impact measurement

**Microsoft CDM Entities Implemented:**

| Microsoft CDM Entity | Our Entity | Description |
|---------------------|------------|-------------|
| Constituent | CONSTITUENT | Donors, volunteers, members, beneficiaries |
| Donation | DONATION | Financial contributions and in-kind gifts |
| Campaign | CAMPAIGN | Fundraising campaigns and appeals |
| Designation | DESIGNATION | Fund allocation (unrestricted, restricted, endowment) |
| Membership | MEMBERSHIP | Member enrollment and renewals |
| Volunteer Preference | VOLUNTEER_ACTIVITY | Volunteer hours and activities |
| Delivery Framework | PROGRAM_DELIVERY | Programs and services delivered |
| Objective | PROGRAM_OUTCOME | Measurable impact and KPIs |

**Integration Benefits:**
- ✅ Dynamics 365 Nonprofit compatibility
- ✅ Power Platform (Power BI, Power Apps, Power Automate)
- ✅ Azure Synapse analytics
- ✅ Constituent 360 view

---

## 🌍 International Aid Transparency

### IATI Standard (International Aid Transparency Initiative)

**Organization:** IATI Secretariat  
**What we use:** International development funding transparency, grant tracking, humanitarian aid flows, outcome measurement.

- **Source:** https://iatistandard.org/
- **Current Version:** IATI Standard v2.03
- **Specification:** https://iatistandard.org/en/iati-standard/203/
- **License:** Open Data Commons Attribution License (ODC-By)
- **Coverage:** 1,300+ publishers, $1+ trillion in development aid tracked
- **Used for:** Grant funding transparency, international nonprofit activities, humanitarian response tracking

**IATI Core Concepts:**

| IATI Element | Description | Our Implementation |
|--------------|-------------|-------------------|
| **iati-activity** | A single development/humanitarian activity or project | PROGRAM_DELIVERY entity |
| **iati-organisation** | Publisher of aid data (donor, recipient, implementer) | ORGANIZATION entity |
| **transaction** | Financial movement (commitment, disbursement, expenditure) | DONATION, GOVERNMENT_BUDGET transactions |
| **result** | Outputs, outcomes, and impacts of activities | PROGRAM_OUTCOME entity |
| **participating-org** | Organizations involved (funders, implementers, partners) | ORGANIZATION relationships |
| **sector** | Sector classification (health, education, water) | NTEE codes, policy topics |
| **budget** | Planned spending over time | GOVERNMENT_BUDGET, CAMPAIGN budgets |
| **location** | Geographic coordinates and administrative areas | JURISDICTION geographic data |

**IATI Activity Mappings:**

| IATI Field | Our Field | Description |
|------------|-----------|-------------|
| `iati-identifier` | `program_id` | Unique activity identifier |
| `title` | `program_name` | Activity title |
| `description` | `description` | Narrative description |
| `activity-status` | `status` | Active, Completed, On Hold, Cancelled |
| `activity-date[@type='start-planned']` | `start_date` | Planned start date |
| `activity-date[@type='end-actual']` | `end_date` | Actual end date |
| `budget[@type='original']` | `program_budget` | Original budget |
| `transaction[@type='4' (expenditure)]` | `program_expenses` | Actual spending |
| `recipient-country` | `jurisdiction_id` | Geographic targeting |
| `sector[@vocabulary='DAC']` | `program_type` | OECD DAC sector codes |
| `result/indicator` | PROGRAM_OUTCOME | Impact indicators |

**IATI Transaction Types:**

| Code | Type | Our Mapping |
|------|------|-------------|
| 1 | Incoming Funds | DONATION (received) |
| 2 | Outgoing Commitment | DONATION (pledged) |
| 3 | Disbursement | GOVERNMENT_BUDGET expenditures |
| 4 | Expenditure | PROGRAM_DELIVERY expenses |
| 11 | Incoming Commitment | CAMPAIGN pledges |
| 12 | Outgoing Pledge | Grant commitments |
| 13 | Reimbursement | Budget adjustments |

**IATI Result/Indicator Mappings:**

```xml
<!-- IATI Result Structure -->
<result type="1" aggregation-status="true">
  <title>
    <narrative>Improved access to clean water</narrative>
  </title>
  <indicator measure="1" ascending="true">
    <title>
      <narrative>Number of people with access to clean water</narrative>
    </title>
    <baseline year="2023" value="5000"/>
    <period>
      <period-start iso-date="2024-01-01"/>
      <period-end iso-date="2024-12-31"/>
      <target value="10000"/>
      <actual value="8500"/>
    </period>
  </indicator>
</result>
```

**Maps to our PROGRAM_OUTCOME:**
- `outcome_name` = "Number of people with access to clean water"
- `metric_type` = "Count"
- `target_value` = 10000
- `actual_value` = 8500
- `measurement_period` = "Annual"
- `measurement_date` = "2024-12-31"

**IATI Organization Types:**

| Code | Organization Type | Our `org_type` |
|------|------------------|----------------|
| 10 | Government | Government agency |
| 21 | International NGO | Nonprofit (international) |
| 22 | National NGO | Nonprofit (domestic) |
| 23 | Regional NGO | Nonprofit (regional) |
| 30 | Public-Private Partnership | Partnership |
| 40 | Multilateral (UN, World Bank) | International org |
| 60 | Foundation | Foundation (501c3) |
| 70 | Private Sector | For-profit |
| 80 | Academic/Research | Educational org |

**Benefits of IATI Alignment:**
- ✅ **Global Transparency:** Compatible with 1,300+ international aid publishers
- ✅ **D-Portal Integration:** Data queryable via https://d-portal.org/
- ✅ **OECD DAC Compatibility:** Aligned with Development Assistance Committee standards
- ✅ **Humanitarian Response:** Track emergency aid, disaster relief, crisis response
- ✅ **UN SDG Mapping:** Link activities to Sustainable Development Goals
- ✅ **Country Systems:** Compatible with recipient country aid management platforms

**Example IATI Use Cases:**
1. **International Nonprofits:** Track dental health programs funded by USAID, Gates Foundation
2. **Government Grants:** Monitor federal aid to state/local health departments
3. **Foundation Giving:** Publish grant disbursements to oral health organizations
4. **Cross-border Activities:** Track U.S. nonprofits working internationally
5. **Impact Measurement:** Standardized indicators for water fluoridation outcomes

**IATI Registry & d-Portal:**
- **Registry:** https://iatiregistry.org/ - Central repository of IATI data files
- **d-Portal:** https://d-portal.org/ - Query engine for IATI data
- **Datastore:** https://iatidatastore.iatistandard.org/ - API for querying IATI data

**Citation:**
> "IATI Standard Version 2.03. International Aid Transparency Initiative. https://iatistandard.org/"

---

## ✅ Fact-Checking

### Google Fact Check Tools API

**Organization:** Google LLC  
**What we use:** Aggregated fact-checking data for verifying claims from meetings and legislation.

- **Source:** https://toolbox.google.com/factcheck/explorer
- **API:** https://developers.google.com/fact-check/tools/api
- **Schema:** https://developers.google.com/search/docs/appearance/structured-data/factcheck
- **Coverage:** 100+ fact-checking organizations worldwide
- **License:** Free API (10,000 queries/day quota)

### FactCheck.org

**Organization:** Annenberg Public Policy Center, University of Pennsylvania  
**What we use:** Nonpartisan fact-checking of political claims and health policy verification.

- **Source:** https://www.factcheck.org/
- **Coverage:** National politics, health claims, science, viral content (2003-present)
- **License:** Free (web scraping allowed with rate limiting)

### PolitiFact

**Organization:** Poynter Institute (Pulitzer Prize-winning)  
**What we use:** State-level fact-checking, Truth-O-Meter ratings for ballot measures.

- **Source:** https://www.politifact.com/
- **Coverage:** All 50 states, federal politics (2007-present)
- **Rating Scale:** True, Mostly True, Half True, Mostly False, False, Pants on Fire
- **License:** Free (web scraping allowed with rate limiting)

---

## � Enterprise Tech for Social Good

### Cloud & Data Platforms

#### Microsoft: Tech for Social Impact

**Organization:** Microsoft Corporation  
**What we use:** Nonprofit Common Data Model (CDM) for donor management, campaign tracking, and program outcomes.

- **Program:** https://microsoft.com/nonprofit
- **Nonprofit CDM GitHub:** https://github.com/microsoft/Industry-Accelerator-Nonprofit
- **License:** MIT License
- **Coverage:** 8 core entities (CONSTITUENT, DONATION, CAMPAIGN, DESIGNATION, MEMBERSHIP, VOLUNTEER_ACTIVITY, PROGRAM_DELIVERY, PROGRAM_OUTCOME)

**Implementation Status:** ✅ **Active** - See [Nonprofit & Philanthropy](#nonprofit--philanthropy) section for full CDM integration.

---

#### Google: Data Commons

**Organization:** Google LLC  
**What we use:** Knowledge Graph API for jurisdiction demographics, economic indicators, and civic data variables.

- **Source:** https://datacommons.org
- **API Documentation:** https://docs.datacommons.org/api/
- **REST API:** https://api.datacommons.org/
- **Python Library:** `pip install datacommons datacommons-pandas`
- **Coverage:** 100+ variables per jurisdiction (income, education, health, housing)
- **License:** Free API (rate limits apply)

**Data Commons Variables for Jurisdictions:**

| Variable | Example Stat Variable | Description |
|----------|----------------------|-------------|
| Population | `Count_Person` | Total population |
| Demographics | `Count_Person_Male`, `Count_Person_Female` | Gender breakdown |
| Age | `Median_Age_Person` | Median age |
| Income | `Median_Income_Household` | Median household income |
| Education | `Count_Person_EducationalAttainmentBachelorsDegreeOrHigher` | College graduates |
| Employment | `UnemploymentRate_Person` | Unemployment rate |
| Housing | `Median_Price_SoldHome` | Median home price |
| Health | `Count_Person_WithHealthInsurance` | Health insurance coverage |

**Implementation Recommendation:**
```python
import datacommons_pandas as dcpd

# Get demographics for a city
df = dcpd.build_time_series(
    place="geoId/0107000",  # Birmingham, AL
    stat_vars=[
        "Median_Income_Household",
        "Count_Person",
        "UnemploymentRate_Person"
    ]
)
```

**Status:** 🔄 **Recommended** - Replace manual Census API calls with Data Commons for simplified jurisdiction enrichment.

---

#### AWS: Open Data for Good

**Organization:** Amazon Web Services (AWS)  
**What we use:** Best practices for hosting large-scale public datasets in Parquet format on S3.

- **Program:** https://registry.opendata.aws
- **Documentation:** https://aws.amazon.com/opendata/
- **Examples:** Census data, satellite imagery, geospatial data
- **Storage Format:** Parquet (columnar, optimized for analytics)
- **License:** Varies by dataset (most public domain)

**AWS Best Practices for `/exports` Folder:**
- Use Parquet with Snappy compression
- Partition by `state/county/year` for efficient queries
- Enable S3 versioning for data lineage
- Use AWS Glue Data Catalog for schema management
- Implement Athena for SQL queries without ETL

**Status:** 🔄 **Planned** - Apply AWS Registry patterns to our HuggingFace dataset exports.

---

### Enterprise Data Engineering Solutions

#### Databricks: Databricks for Good

**Organization:** Databricks, Inc.  
**What we use:** Unity Catalog for data governance, Delta Lake for lakehouse architecture, MLflow for agent deployment, Solution Accelerators for NLP pipelines.

- **Program:** https://databricks.com/for-good
- **Solution Accelerators:** https://www.databricks.com/solutions/accelerators
- **Unity Catalog:** https://docs.databricks.com/en/data-governance/unity-catalog/index.html
- **License:** Commercial (Free Community Edition available)

**Our Databricks Implementation:**

| Component | Purpose | File Location |
|-----------|---------|---------------|
| **Delta Lake Pipeline** | Bronze/Silver/Gold data layers | `pipeline/delta_lake.py` |
| **MLflow Agents** | Policy classifier, sentiment analysis | `agents/mlflow_classifier.py`, `agents/mlflow_base.py` |
| **Unity Catalog** | Model registry and governance | `databricks/deployment.py` |
| **Agent Bricks** | Mosaic AI Agent Framework | `databricks/notebooks/01_agent_bricks_quickstart.py` |
| **Model Serving** | Auto-scaling REST endpoints | `databricks/deployment.py` |

**Implementation Status:** ✅ **Active** - Full Databricks integration for data engineering and ML workflows.

**Delta Sharing for `/exports`:**
```python
# Share Gold layer tables externally
from databricks import delta_sharing

share = delta_sharing.SharingClient()
share.create_share(
    name="one_civic_data",
    tables=["gold.jurisdictions", "gold.meetings", "gold.nonprofits"]
)
```

**Citation:**
```bibtex
@misc{databricks_for_good,
  author = {{Databricks, Inc.}},
  title = {Databricks for Good},
  year = {2024},
  url = {https://databricks.com/for-good}
}
```

---

#### Snowflake: Snowflake for Good

**Organization:** Snowflake Inc.  
**What we use:** Data Marketplace for Census, ESG, and demographic data; data sharing capabilities.

- **Program:** https://snowflake.com/for-good
- **Data Marketplace:** https://www.snowflake.com/data-marketplace/
- **Free Datasets:** U.S. Census (Knoema), OpenStreetMap, COVID-19 data
- **License:** Commercial (Free trial available)

**Status:** 🔄 **Evaluation** - Consider for enterprise data sharing and collaboration.

---

#### Oracle: NetSuite Social Impact

**Organization:** Oracle Corporation  
**What we use:** Fund accounting models and grant tracking patterns for nonprofit financial data.

- **Program:** https://netsuite.com/social-impact
- **Features:** Fund accounting, grant management, donor databases
- **License:** Commercial

**Status:** 📚 **Reference** - Inspiration for nonprofit financial data modeling.

---

#### Salesforce: Salesforce.org

**Organization:** Salesforce, Inc.  
**What we use:** Nonprofit Success Pack (NPSP) data model patterns for constituent relationship management.

- **Program:** https://salesforce.org/npsp
- **GitHub:** https://github.com/SalesforceFoundation/NPSP
- **Features:** Household accounts, recurring donations, program engagement
- **License:** Open Source (BSD-3-Clause)

**NPSP Object Mappings:**

| NPSP Object | Our Entity | Use Case |
|-------------|------------|----------|
| Contact | CONSTITUENT | Donor, volunteer, beneficiary |
| Opportunity | DONATION | Financial contributions |
| Campaign | CAMPAIGN | Fundraising campaigns |
| Engagement Plan | VOLUNTEER_ACTIVITY | Volunteer tracking |
| Program Cohort | PROGRAM_DELIVERY | Program participants |

**Status:** 📚 **Reference** - Inspiration for constituent engagement data model.

---

### Infrastructure, AI & Blockchain

#### Cisco: Crisis Response

**Organization:** Cisco Systems, Inc.  
**What we use:** Network resilience patterns for ensuring platform uptime during community emergencies.

- **Program:** https://cisco.com/crisis-response
- **Focus:** Connectivity, communications, resilient systems
- **License:** Varies by initiative

**Status:** 📚 **Reference** - Inspiration for platform reliability during crises.

---

#### IBM: Science for Social Good

**Organization:** IBM Corporation  
**What we use:** AI/ML use case patterns for civic applications.

- **Program:** https://ibm.com/social-good
- **Technologies:** Watson AI, Blockchain, Quantum computing
- **License:** Varies by project

**Status:** 📚 **Reference** - Inspiration for AI-powered civic analysis.

---

#### Meta: Data for Good

**Organization:** Meta Platforms, Inc.  
**What we use:** Population density and social connectivity mapping patterns.

- **Program:** https://dataforgood.facebook.com
- **Datasets:** High-Resolution Population Density Maps, Social Connectedness Index
- **License:** Free (Terms of Use apply)

**Status:** 🔄 **Evaluation** - Consider for population modeling and demographic analysis.

---

## �🙏 Acknowledgments

We are grateful to the following organizations and individuals:

**Academic Institutions:**
- Association for Computational Linguistics (ACL) for MeetingBank
- Harvard University Mellon Urbanism Lab for LocalView
- Cornell University Roper Center for public opinion research
- MIT Election Data + Science Lab for election data
- University of Pennsylvania Annenberg Center for fact-checking

**Civic Tech Community:**
- **GroundVue** - Partner organization inspiring community accountability work
- **Code for America** - Civic technology movement and brigade network
- **City Bureau** - Documenters Network and City Scrapers project
- **Council Data Project** - Open-source municipal data infrastructure
- **U.S. Digital Response** - Emergency civic technology support
- **Civic Tech Field Guide** - Community resource and project directory

**Standards Bodies:**
- W3C Community Group for Schema.org
- Open Civic Data for jurisdiction identifiers (OCDEP 2)
- Popolo Project for open government data standards
- IATI Secretariat for international aid transparency
- U.S. Department of Education for CEDS

**Enterprise Tech for Social Good:**
- **Microsoft** - Tech for Social Impact (Nonprofit CDM)
- **Google** - Data Commons (Knowledge Graph & Civic Data API)
- **AWS** - Open Data for Good (Registry best practices)
- **Databricks** - Databricks for Good (Unity Catalog, Delta Lake, MLflow, Agent Bricks)
- **Snowflake** - Snowflake for Good (Data Marketplace)
- **Oracle** - NetSuite Social Impact (Fund accounting models)
- **Salesforce** - Salesforce.org (Nonprofit Success Pack)
- **Cisco** - Crisis Response (Network resilience)
- **IBM** - Science for Social Good (AI use cases)
- **Meta** - Data for Good (Population mapping)

**Data Platforms & Organizations:**
- HuggingFace for dataset hosting
- ProPublica for nonprofit financial data (3M+ organizations)
- Open States for legislative data
- OHDSI for OMOP Common Data Model (vocabulary system)
- Every.org for charity metadata and mission statements
- Findhelp.org for local social services directory (400K+ programs)

**Government:**
- U.S. Census Bureau for demographic data
- National Center for Education Statistics (NCES)
- IRS for tax-exempt organization data
- CISA for .gov domain registry
- All municipal governments providing open access to meeting records

**Special Thanks:**
- All civic technologists building open government tools
- Municipal staff maintaining public meeting archives
- Journalists and community advocates holding power accountable


---

## 📖 How to Cite This Project

If you use **Open Navigator for Engagement** in your research, please cite:

```
Open Navigator for Engagement
GitHub: https://github.com/getcommunityone/open-navigator-for-engagement
License: MIT
```

**BibTeX:**
```bibtex
@software{open-navigator-2026,
    title = {Open Navigator for Engagement},
    author = {Community One},
    year = {2026},
    url = {https://github.com/getcommunityone/open-navigator-for-engagement},
    license = {MIT}
}
```

---

## 📝 License Compliance

This project respects all dataset licenses and terms of use. See [LICENSE](https://github.com/getcommunityone/open-navigator-for-engagement/blob/main/LICENSE) for this project's MIT license.

For dataset-specific licenses, please refer to the original sources listed above.
