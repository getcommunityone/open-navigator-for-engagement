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

### **Open States API**
- State and local legislative information
- Source: https://openstates.org/
- License: Various (check per state)
- API Key: Required for access

### **Harvard Dataverse**
- Meeting datasets and civic engagement research
- Source: https://dataverse.harvard.edu/
- License: Varies by dataset

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

If you use Open Navigator for Engagement in your research, please cite:

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

## 📝 **License Compliance**

This project respects all dataset licenses and terms of use. See [LICENSE](LICENSE) for this project's MIT license.

For dataset-specific licenses, please refer to the original sources listed above.
