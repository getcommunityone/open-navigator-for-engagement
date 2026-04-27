---
displayed_sidebar: developersSidebar
sidebar_position: 1
---

import ZoomableMermaid from '@site/src/components/ZoomableMermaid';

# Data Model & Entity Relationship Diagram

Comprehensive overview of all data entities extracted, processed, and uploaded to HuggingFace datasets.

## 📊 Complete Data Model (ERD)

<ZoomableMermaid 
  title="Interactive Entity Relationship Diagram"
  value={`
erDiagram
    %% Core Jurisdiction Entities
    JURISDICTION ||--o{ MEETING : hosts
    JURISDICTION ||--o{ LEADER : employs
    JURISDICTION ||--o{ YOUTUBE_CHANNEL : operates
    JURISDICTION ||--o{ SOCIAL_MEDIA : maintains
    JURISDICTION ||--o{ MEETING_PLATFORM : uses
    JURISDICTION {
        string jurisdiction_id PK
        string name
        string jurisdiction_type
        string state_code
        string county_name
        int population
        string website_url
        float latitude
        float longitude
        string fips_code
        int completeness_score
        datetime discovered_at
    }
    
    %% Census and Government Data
    JURISDICTION ||--o| CENSUS_DATA : has
    CENSUS_DATA {
        string jurisdiction_id PK
        int population_2020
        int population_2024
        string county_fips
        string place_fips
        float median_income
        float poverty_rate
        datetime census_year
    }
    
    JURISDICTION ||--o| GSA_DOMAIN : uses
    GSA_DOMAIN {
        string domain PK
        string jurisdiction_id FK
        string domain_type
        string agency_name
        string organization_type
        string city
        string state
        datetime created_date
    }
    
    %% ========================================
    %% SCHOOL DISTRICTS (NCES)
    %% ========================================
    
    JURISDICTION ||--o{ SCHOOL_DISTRICT : contains
    SCHOOL_DISTRICT ||--o{ LEADER : governed_by
    SCHOOL_DISTRICT {
        string nces_id PK
        string district_name
        string jurisdiction_id FK
        string state_code
        string county_name
        string district_type
        int total_students
        int total_schools
        string phone
        string website
        string superintendent
        datetime school_year
    }
    
    %% ========================================
    %% MEETINGS & DOCUMENTS
    %% ========================================
    
    MEETING ||--o{ AGENDA : contains
    MEETING ||--o{ MINUTES : produces
    MEETING ||--o{ VIDEO : recorded_as
    MEETING ||--o{ DOCUMENT : references
    MEETING {
        string meeting_id PK
        string jurisdiction_id FK
        string meeting_type
        datetime meeting_date
        string meeting_title
        string body_name
        string status
        string platform
        string source_url
        boolean oral_health_related
        datetime extracted_at
    }
    
    AGENDA {
        string agenda_id PK
        string meeting_id FK
        string title
        string full_text
        string pdf_url
        int page_count
        string keywords_found
        datetime published_at
    }
    
    MINUTES {
        string minutes_id PK
        string meeting_id FK
        string full_text
        string pdf_url
        string summary_text
        string action_items
        string votes
        datetime approved_at
    }
    
    VIDEO {
        string video_id PK
        string meeting_id FK
        string platform
        string video_url
        string thumbnail_url
        int duration_seconds
        int view_count
        string transcript_text
        datetime published_at
    }
    
    DOCUMENT {
        string document_id PK
        string meeting_id FK
        string document_type
        string title
        string content_text
        string file_url
        string file_type
        int file_size_bytes
        datetime uploaded_at
    }
    
    %% ========================================
    %% LEADERS & OFFICIALS
    %% ========================================
    
    LEADER ||--o{ VOTE : casts
    LEADER ||--o{ SOCIAL_MEDIA : maintains
    LEADER {
        string leader_id PK
        string jurisdiction_id FK
        string full_name
        string title
        string position_type
        string office
        string party_affiliation
        string email
        string phone
        string website
        string photo_url
        datetime term_start
        datetime term_end
        boolean is_active
        datetime verified_at
    }
    
    VOTE {
        string vote_id PK
        string leader_id FK
        string meeting_id FK
        string item_description
        string vote_value
        datetime vote_date
    }
    
    %% ========================================
    %% ORGANIZATIONS (NONPROFITS)
    %% ========================================
    
    ORGANIZATION ||--o{ SOCIAL_MEDIA : maintains
    ORGANIZATION ||--o{ LEADER : employs
    ORGANIZATION {
        string org_id PK
        string ein
        string name
        string ntee_code
        string ntee_description
        string causes
        string org_type
        string state_code
        string city
        string address
        float revenue_amount
        float assets_amount
        int employee_count
        string mission_statement
        string description
        string logo_url
        string website
        boolean is_verified
        datetime irs_filing_date
    }
    
    %% ========================================
    %% MEDIA & COMMUNICATIONS
    %% ========================================
    
    YOUTUBE_CHANNEL {
        string channel_id PK
        string jurisdiction_id FK
        string channel_name
        string channel_url
        int subscriber_count
        int video_count
        int total_views
        string description
        datetime created_date
        datetime last_scraped
    }
    
    SOCIAL_MEDIA {
        string account_id PK
        string entity_id FK
        string entity_type
        string platform
        string handle
        string profile_url
        int follower_count
        int post_count
        boolean is_verified
        datetime last_updated
    }
    
    MEETING_PLATFORM {
        string platform_id PK
        string jurisdiction_id FK
        string platform_name
        string base_url
        string api_endpoint
        string calendar_url
        string archive_url
        boolean has_api
        datetime discovered_at
    }
    
    %% ========================================
    %% OPEN STATES (LEGISLATIVE DATA)
    %% ========================================
    
    STATE_LEGISLATURE ||--o{ STATE_LEGISLATOR : has_member
    STATE_LEGISLATURE ||--o{ STATE_BILL : introduces
    STATE_LEGISLATURE ||--o{ STATE_COMMITTEE : contains
    STATE_LEGISLATURE {
        string legislature_id PK
        string state_code
        string session_year
        string session_type
        datetime session_start
        datetime session_end
    }
    
    STATE_LEGISLATOR {
        string legislator_id PK
        string legislature_id FK
        string full_name
        string party
        string district
        string chamber
        string email
        string capitol_phone
        string photo_url
        string openstates_id
    }
    
    STATE_BILL {
        string bill_id PK
        string legislature_id FK
        string bill_number
        string title
        string summary
        string status
        string sponsors
        datetime introduced_date
        datetime last_action_date
        string openstates_url
    }
    
    STATE_COMMITTEE {
        string committee_id PK
        string legislature_id FK
        string name
        string chamber
        string parent_id FK
        string members
    }
    
    %% ========================================
    %% WIKIDATA ENTITIES
    %% ========================================
    
    WIKIDATA_ENTITY ||--o{ WIKIDATA_RELATIONSHIP : source
    WIKIDATA_ENTITY ||--o{ WIKIDATA_RELATIONSHIP : target
    WIKIDATA_ENTITY {
        string wikidata_id PK
        string entity_type
        string label
        string description
        string wikipedia_url
        string image_url
        string aliases
        string properties
        datetime last_updated
    }
    
    WIKIDATA_RELATIONSHIP {
        string relationship_id PK
        string source_id FK
        string target_id FK
        string predicate
        datetime start_date
        datetime end_date
        string qualifiers
    }
    
    %% ========================================
    %% DBPEDIA ENTITIES
    %% ========================================
    
    DBPEDIA_RESOURCE {
        string resource_uri PK
        string label
        string description
        string categories
        string classes
        string infobox_properties
        string wikipedia_url
        int ref_count
        datetime extracted_at
    }
    
    %% ========================================
    %% GOOGLE CIVIC DATA
    %% ========================================
    
    CIVIC_DIVISION ||--o{ CIVIC_REPRESENTATIVE : has
    CIVIC_DIVISION {
        string ocd_id PK
        string division_name
        string division_type
        string state
        string county
        string office_types
        string boundaries_geojson
    }
    
    CIVIC_REPRESENTATIVE {
        string representative_id PK
        string ocd_id FK
        string name
        string office_name
        string party
        string phones
        string emails
        string urls
        string social_channels
        string photo_url
    }
    
    CIVIC_ELECTION {
        string election_id PK
        string name
        datetime election_day
        string ocd_division FK
        string contests
        string polling_locations
    }
    
    %% ========================================
    %% USER & SOCIAL FEATURES
    %% ========================================
    
    USER ||--o{ USER_FOLLOW : follows
    USER ||--o{ LEADER_FOLLOW : follows_leader
    USER ||--o{ ORG_FOLLOW : follows_org
    USER ||--o{ CAUSE_FOLLOW : follows_cause
    USER {
        int user_id PK
        string email
        string username
        string full_name
        string oauth_provider
        string state
        string county
        string city
        string school_board
        boolean profile_completed
        datetime created_at
    }
    
    USER_FOLLOW {
        int id PK
        int follower_id FK
        int following_id FK
        datetime created_at
    }
    
    LEADER_FOLLOW {
        int id PK
        int user_id FK
        string leader_id FK
        datetime created_at
    }
    
    ORG_FOLLOW {
        int id PK
        int user_id FK
        string org_id FK
        datetime created_at
    }
    
    CAUSE ||--o{ CAUSE_FOLLOW : followed_by
    CAUSE {
        int cause_id PK
        string name
        string slug
        string description
        string category
        string icon_url
        string color
        int follower_count
    }
    
    CAUSE_FOLLOW {
        int id PK
        int user_id FK
        int cause_id FK
        datetime created_at
    }
    
    %% ========================================
    %% MEETINGBANK (HUGGINGFACE DATASET)
    %% ========================================
    
    MEETINGBANK_MEETING {
        string instance_id PK
        string city_name
        datetime meeting_date
        string transcript_text
        string summary_text
        string source_url
        string split
        datetime ingested_at
    }
    
    %% ========================================
    %% BALLOT MEASURES & ADVOCACY
    %% ========================================
    
    JURISDICTION ||--o{ BALLOT_MEASURE : hosts
    STATE_LEGISLATURE ||--o{ BALLOT_MEASURE : proposes
    POLICY_TOPIC ||--o{ BALLOT_MEASURE : addresses
    BALLOT_MEASURE {
        string measure_id PK
        string jurisdiction_id FK
        string state_code
        datetime election_date
        string measure_number
        string title
        string description
        string measure_type
        string topic_category
        string status
        string result
        int yes_votes
        int no_votes
        float yes_percentage
        string full_text_url
        string ballotpedia_url
        datetime created_at
    }
    
    POLICY_TOPIC ||--o{ MEETING : discussed_in
    POLICY_TOPIC ||--o{ LEGISLATION : addresses
    POLICY_TOPIC {
        string topic_id PK
        string topic_name
        string category
        string description
        string keywords
        int priority_level
        string icon
        int jurisdiction_count
    }
    
    JURISDICTION ||--o{ LEGISLATION : enacts
    STATE_LEGISLATURE ||--o{ LEGISLATION : proposes
    LEGISLATION {
        string bill_id PK
        string jurisdiction_id FK
        string state_code
        string bill_number
        string title
        string description
        string status
        string sponsor
        datetime introduced_date
        datetime passed_date
        datetime effective_date
        string full_text_url
        string openstates_url
        string topic_category
        string chamber
        int vote_yes
        int vote_no
    }
`}
/>

## 📦 HuggingFace Dataset Structure

### Current Datasets Being Uploaded

```
oral-health-policy-data/
├── jurisdictions/          # 🏛️ Core jurisdiction data
│   ├── cities              # 19,000+ incorporated places
│   ├── counties            # 3,144 U.S. counties
│   ├── states              # 50 states + DC, territories
│   ├── school_districts    # 13,000+ districts (NCES data)
│   └── census_data         # Demographics, population, income
│
├── social_media/           # 📱 Social media presence
│   ├── twitter             # Twitter/X accounts
│   ├── facebook            # Facebook pages
│   ├── instagram           # Instagram accounts
│   └── linkedin            # LinkedIn pages
│
├── video_platforms/        # 📹 Video & streaming
│   ├── youtube_channels    # Government YouTube channels
│   ├── vimeo              # Vimeo accounts
│   └── livestreams        # Live meeting streams
│
├── meeting_platforms/      # 🖥️ Meeting management systems
│   ├── legistar           # Legistar URLs
│   ├── granicus           # Granicus links
│   ├── suiteone           # SuiteOne systems
│   └── civicplus          # CivicPlus platforms
│
├── government_domains/     # 🌐 Official websites
│   ├── gsa_domains        # .gov domain registry
│   ├── municipal_websites # City/county websites
│   └── state_portals      # State government sites
│
├── meetings/               # 📋 Meeting data
│   ├── agendas            # Meeting agendas (text extracted)
│   ├── minutes            # Meeting minutes (text extracted)
│   ├── videos             # YouTube/Vimeo video metadata
│   └── documents          # Associated documents
│
├── officials/              # 👥 Elected officials & leaders
│   ├── local_officials    # City/county officials (mayors, councils)
│   ├── state_legislators  # From Open States API
│   └── school_board       # School board members
│
├── organizations/          # 🏢 Nonprofits & charities
│   ├── irs_nonprofits     # IRS 990 data (3M+ organizations)
│   ├── propublica_data    # ProPublica API (financials, NTEE codes)
│   ├── everyorg_data      # Every.org API (missions, causes, logos)
│   └── nonprofit_causes   # NTEE taxonomy + Every.org causes
│
├── civic_data/            # 🗳️ Google Civic & Wikidata
│   ├── civic_divisions    # OCD divisions
│   ├── representatives    # From Google Civic API
│   ├── wikidata_entities  # Structured entities
│   └── dbpedia_resources  # Wikipedia infobox data
│
├── ballot_measures/        # 🗳️ Ballot initiatives & referendums
│   ├── state_measures      # State propositions (fluoridation votes!)
│   ├── local_measures      # City/county ballot questions
│   └── election_results    # Historical voting outcomes
│
├── legislation/            # 📜 Bills, ordinances, resolutions
│   ├── state_bills         # From Open States API (52 states)
│   ├── local_ordinances    # Municipal codes & resolutions
│   └── policy_tracking     # Bill status & outcomes
│
└── policy_topics/          # 🎯 Advocacy causes & campaigns
    ├── topic_definitions   # Oral health, fluoridation, dental access
    ├── jurisdiction_topics # What each city is discussing
    └── advocacy_alerts     # Opportunities for engagement
```

## 🔄 Data Extraction Pipeline

### Phase 1: Discovery (Bronze Layer)
1. **Census Data** → Jurisdictions list
2. **GSA Domains** → Government websites
3. **NCES** → School districts
4. **IRS TEOS** → Nonprofit EINs (3M+ organizations)
5. **URL Discovery** → Meeting platforms, YouTube
6. **Social Media** → Twitter, Facebook accounts

### Phase 2: Enrichment (Silver Layer)
1. **ProPublica Nonprofit Explorer** → Financial data, NTEE codes, 990 filings
2. **Every.org API** → Nonprofit causes, missions, logos
3. **YouTube API** → Channel statistics
4. **Open States** → Legislative data
5. **Wikidata SPARQL** → Entity relationships
6. **DBpedia** → Wikipedia structured data
7. **Google Civic** → Representatives

### Phase 3: Processing (Gold Layer)
1. **Meeting Extraction** → Agenda/minutes text
2. **Video Transcripts** → YouTube captions
3. **Document Analysis** → Keyword detection
4. **Relationship Mapping** → Entity connections
5. **Oral Health Filtering** → Topic classification

## 📊 Data Statistics

| Entity Type | Estimated Count | Source |
|------------|----------------|--------|
| Jurisdictions | 22,000+ | Census Gazetteer |
| Counties | 3,144 | FIPS codes |
| Cities | 19,000+ | Incorporated places |
| School Districts | 13,000+ | NCES CCD |
| Nonprofits | 3,000,000+ | IRS TEOS |
| Nonprofit Causes | 600+ | NTEE + Every.org |
| YouTube Channels | 5,000+ | Discovery pipeline |
| Meeting Platforms | 10,000+ | URL detection |
| State Legislators | 7,300+ | Open States |
| Meetings | 500,000+ | Scraped |
| Documents | 2,000,000+ | PDF extraction |
| Ballot Measures | TBD | State/local election sites |
| State Bills | 100,000+ | Open States API |
| Policy Topics | ~50 | Curated + extracted |

## 🎯 Missing Datasets to Add

### High Priority
- [x] **Ballot Measures** - ✅ Added to data model! Fluoridation votes, bond measures
- [x] **State Legislation** - ✅ Added to data model! Open States API (FREE)
- [x] **Policy Topics** - ✅ Added to data model! Oral health advocacy tracking
- [ ] **Census Demographics** - Full census data per jurisdiction
- [ ] **Budget Documents** - Municipal budgets & spending
- [ ] **Procurement Records** - Government contracts
- [ ] **Election Results** - Historical voting data
- [ ] **Health Outcomes** - CDC PLACES data (oral health metrics!)
- [ ] **Environmental Data** - EPA water quality (fluoridation levels)

### Medium Priority
- [ ] **Property Records** - Public assessment data
- [ ] **Crime Statistics** - UCR/NIBRS data
- [ ] **Business Licenses** - Local business registrations (dental clinics!)
- [ ] **Building Permits** - Construction activity
- [ ] **Code Violations** - Inspection records
- [ ] **Police Reports** - Public safety incidents
- [ ] **Fire Department Data** - Emergency response
- [ ] **Parks & Recreation** - Facilities & programs
- [ ] **Transportation Data** - Traffic & transit

### Integration Improvements
- [ ] **Full Wikidata Sync** - All civic entities
- [ ] **DBpedia Expansion** - Complete local government coverage
- [ ] **Ballotpedia Data** - (if budget allows) Electoral info & analysis
- [ ] **Court Records** - Public dockets
- [ ] **Tax Records** - Property tax data

## 🚀 Implementation Status

### ✅ Completed
- Jurisdiction discovery pipeline
- YouTube channel discovery
- Meeting platform detection
- NCES school district ingestion
- Open States API integration
- Wikidata SPARQL queries
- DBpedia Lookup API
- Google Civic API (code ready)
- Social media discovery
- HuggingFace upload pipeline

### 🔨 In Progress
- Meeting minutes extraction (Tuscaloosa pilot)
- Video transcript processing
- Document keyword detection
- Nonprofit data enrichment

### 📋 Planned
- Automated meeting scraping at scale
- Real-time meeting notifications
- Budget document parsing
- Full census integration
- Health outcome correlation

## 📚 Related Documentation

- [HuggingFace Publishing Guide](../guides/huggingface-publishing.md)
- [Data Sources Overview](./overview.md)
- [Discovery Pipeline](./jurisdiction-discovery.md)
- [API Integration Status](../../docs/API_INTEGRATION_STATUS.md)

---

**Last Updated:** {new Date().toISOString().split('T')[0]}

**Data Model Version:** 2.0
