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
  <a href="#academic-research" className="card" style={{textDecoration: 'none', padding: '15px', borderLeft: '4px solid #2196F3'}}>
    <strong>🎓 Academic Research</strong><br/>
    <span style={{fontSize: '0.9em', color: '#666'}}>MeetingBank, Roper Center</span>
  </a>
  <a href="#government-data" className="card" style={{textDecoration: 'none', padding: '15px', borderLeft: '4px solid #4CAF50'}}>
    <strong>🏛️ Government Data</strong><br/>
    <span style={{fontSize: '0.9em', color: '#666'}}>U.S. Census, NCES, IRS</span>
  </a>
  <a href="#civic-tech-standards" className="card" style={{textDecoration: 'none', padding: '15px', borderLeft: '4px solid #FF9800'}}>
    <strong>🌐 Civic Tech Standards</strong><br/>
    <span style={{fontSize: '0.9em', color: '#666'}}>OCD-ID, Popolo, Schema.org, CEDS</span>
  </a>
  <a href="#election--advocacy" className="card" style={{textDecoration: 'none', padding: '15px', borderLeft: '4px solid #9C27B0'}}>
    <strong>🗳️ Election & Advocacy</strong><br/>
    <span style={{fontSize: '0.9em', color: '#666'}}>Ballotpedia, MIT Election Lab, OpenElections</span>
  </a>
  <a href="#nonprofit--philanthropy" className="card" style={{textDecoration: 'none', padding: '15px', borderLeft: '4px solid #F44336'}}>
    <strong>🏢 Nonprofit & Philanthropy</strong><br/>
    <span style={{fontSize: '0.9em', color: '#666'}}>Microsoft CDM for Nonprofits</span>
  </a>
  <a href="#international-aid-transparency" className="card" style={{textDecoration: 'none', padding: '15px', borderLeft: '4px solid #00BCD4'}}>
    <strong>🌍 International Aid</strong><br/>
    <span style={{fontSize: '0.9em', color: '#666'}}>IATI Standard v2.03</span>
  </a>
  <a href="#-fact-checking" className="card" style={{textDecoration: 'none', padding: '15px', borderLeft: '4px solid #8BC34A'}}>
    <strong>✅ Fact-Checking</strong><br/>
    <span style={{fontSize: '0.9em', color: '#666'}}>Google, PolitiFact, FactCheck.org</span>
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

## 🙏 Acknowledgments

We are grateful to the following organizations and individuals:

**Academic Institutions:**
- Association for Computational Linguistics (ACL) for MeetingBank
- Cornell University Roper Center for public opinion research
- MIT Election Data + Science Lab for election data
- University of Pennsylvania Annenberg Center for fact-checking

**Standards Bodies:**
- W3C Community Group for Schema.org
- Open Civic Data for jurisdiction identifiers
- Popolo Project for open government data standards
- IATI Secretariat for international aid transparency
- U.S. Department of Education for CEDS

**Data Platforms:**
- HuggingFace for dataset hosting
- Open States for legislative data
- Microsoft for nonprofit Common Data Model
- Google for Fact Check Tools API

**Government:**
- U.S. Census Bureau for demographic data
- National Center for Education Statistics (NCES)
- All municipal governments providing open access to meeting records

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
