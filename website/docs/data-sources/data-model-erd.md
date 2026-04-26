---
displayed_sidebar: developersSidebar
sidebar_position: 1
---

# Data Model & Entity Relationship Diagram

Comprehensive overview of all data entities extracted, processed, and uploaded to HuggingFace datasets.

## 📊 Complete Data Model (ERD)

```mermaid
erDiagram
    %% ========================================
    %% CORE JURISDICTION ENTITIES
    %% ========================================
    
    JURISDICTION ||--o{ MEETING : hosts
    JURISDICTION ||--o{ LEADER : employs
    JURISDICTION ||--o{ YOUTUBE_CHANNEL : operates
    JURISDICTION ||--o{ SOCIAL_MEDIA : maintains
    JURISDICTION ||--o{ MEETING_PLATFORM : uses
    JURISDICTION {
        string jurisdiction_id PK
        string name
        string type "city|county|township"
        string state_code
        string county_name
        int population
        string website_url
        float latitude
        float longitude
        string fips_code
        int completeness_score
        timestamp discovered_at
    }
    
    %% ========================================
    %% CENSUS & GOVERNMENT DATA
    %% ========================================
    
    JURISDICTION ||--o| CENSUS_DATA : has
    CENSUS_DATA {
        string jurisdiction_id PK_FK
        int population_2020
        int population_2024
        string county_fips
        string place_fips
        float median_income
        float poverty_rate
        timestamp census_year
    }
    
    JURISDICTION ||--o| GSA_DOMAIN : uses
    GSA_DOMAIN {
        string domain PK
        string jurisdiction_id FK
        string domain_type "Federal|State|County|City|Special"
        string agency_name
        string organization_type
        string city
        string state
        timestamp created_date
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
        timestamp school_year
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
        string meeting_type "council|board|commission"
        datetime meeting_date
        string meeting_title
        string body_name
        string status "scheduled|completed|cancelled"
        string platform "legistar|suiteone|granicus"
        string source_url
        boolean oral_health_related
        timestamp extracted_at
    }
    
    AGENDA {
        string agenda_id PK
        string meeting_id FK
        string title
        text full_text
        string pdf_url
        int page_count
        array keywords_found
        timestamp published_at
    }
    
    MINUTES {
        string minutes_id PK
        string meeting_id FK
        text full_text
        string pdf_url
        string summary_text
        array action_items
        array votes
        timestamp approved_at
    }
    
    VIDEO {
        string video_id PK
        string meeting_id FK
        string platform "youtube|vimeo|granicus"
        string video_url
        string thumbnail_url
        int duration_seconds
        int view_count
        string transcript_text
        timestamp published_at
    }
    
    DOCUMENT {
        string document_id PK
        string meeting_id FK
        string document_type "resolution|ordinance|report|presentation"
        string title
        text content_text
        string file_url
        string file_type "pdf|docx|pptx"
        int file_size_bytes
        timestamp uploaded_at
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
        string position_type "elected|appointed|staff"
        string office
        string party_affiliation
        string email
        string phone
        string website
        string photo_url
        datetime term_start
        datetime term_end
        boolean is_active
        timestamp verified_at
    }
    
    VOTE {
        string vote_id PK
        string leader_id FK
        string meeting_id FK
        string item_description
        string vote_value "yes|no|abstain|absent"
        datetime vote_date
    }
    
    %% ========================================
    %% ORGANIZATIONS (NONPROFITS)
    %% ========================================
    
    ORGANIZATION ||--o{ SOCIAL_MEDIA : maintains
    ORGANIZATION ||--o{ LEADER : employs
    ORGANIZATION {
        string org_id PK
        string ein "IRS EIN"
        string name
        string ntee_code
        string org_type "501c3|501c4|government"
        string state_code
        string city
        string address
        float revenue_amount
        float assets_amount
        int employee_count
        string mission_statement
        string website
        boolean is_verified
        timestamp irs_filing_date
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
        timestamp last_scraped
    }
    
    SOCIAL_MEDIA {
        string account_id PK
        string entity_id FK "leader_id|org_id|jurisdiction_id"
        string entity_type "leader|organization|jurisdiction"
        string platform "twitter|facebook|instagram|linkedin"
        string handle
        string profile_url
        int follower_count
        int post_count
        boolean is_verified
        timestamp last_updated
    }
    
    MEETING_PLATFORM {
        string platform_id PK
        string jurisdiction_id FK
        string platform_name "legistar|suiteone|granicus|civicclerk"
        string base_url
        string api_endpoint
        string calendar_url
        string archive_url
        boolean has_api
        timestamp discovered_at
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
        string session_type "regular|special"
        datetime session_start
        datetime session_end
    }
    
    STATE_LEGISLATOR {
        string legislator_id PK
        string legislature_id FK
        string full_name
        string party
        string district
        string chamber "upper|lower"
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
        text summary
        string status
        array sponsors
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
        array members
    }
    
    %% ========================================
    %% WIKIDATA ENTITIES
    %% ========================================
    
    WIKIDATA_ENTITY ||--o{ WIKIDATA_RELATIONSHIP : source
    WIKIDATA_ENTITY ||--o{ WIKIDATA_RELATIONSHIP : target
    WIKIDATA_ENTITY {
        string wikidata_id PK "Q-number"
        string entity_type "person|organization|location|position"
        string label
        text description
        string wikipedia_url
        string image_url
        array aliases
        json properties
        timestamp last_updated
    }
    
    WIKIDATA_RELATIONSHIP {
        string relationship_id PK
        string source_id FK "wikidata_id"
        string target_id FK "wikidata_id"
        string predicate "position_held|member_of|located_in"
        datetime start_date
        datetime end_date
        json qualifiers
    }
    
    %% ========================================
    %% DBPEDIA ENTITIES
    %% ========================================
    
    DBPEDIA_RESOURCE {
        string resource_uri PK
        string label
        text description
        array categories
        array classes
        json infobox_properties
        string wikipedia_url
        int ref_count
        timestamp extracted_at
    }
    
    %% ========================================
    %% GOOGLE CIVIC DATA
    %% ========================================
    
    CIVIC_DIVISION ||--o{ CIVIC_REPRESENTATIVE : has
    CIVIC_DIVISION {
        string ocd_id PK "Open Civic Data ID"
        string division_name
        string division_type
        string state
        string county
        array office_types
        json boundaries_geojson
    }
    
    CIVIC_REPRESENTATIVE {
        string representative_id PK
        string ocd_id FK
        string name
        string office_name
        string party
        array phones
        array emails
        array urls
        array social_channels
        string photo_url
    }
    
    CIVIC_ELECTION {
        string election_id PK
        string name
        datetime election_day
        string ocd_division FK
        array contests
        json polling_locations
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
        timestamp created_at
    }
    
    USER_FOLLOW {
        int id PK
        int follower_id FK
        int following_id FK
        timestamp created_at
    }
    
    LEADER_FOLLOW {
        int id PK
        int user_id FK
        string leader_id FK
        timestamp created_at
    }
    
    ORG_FOLLOW {
        int id PK
        int user_id FK
        string org_id FK
        timestamp created_at
    }
    
    CAUSE ||--o{ CAUSE_FOLLOW : followed_by
    CAUSE {
        int cause_id PK
        string name
        string slug
        text description
        string category "health|education|housing"
        string icon_url
        string color
        int follower_count
    }
    
    CAUSE_FOLLOW {
        int id PK
        int user_id FK
        int cause_id FK
        timestamp created_at
    }
    
    %% ========================================
    %% MEETINGBANK (HUGGINGFACE DATASET)
    %% ========================================
    
    MEETINGBANK_MEETING {
        string instance_id PK
        string city_name
        datetime meeting_date
        text transcript_text
        text summary_text
        string source_url
        string split "train|validation|test"
        timestamp ingested_at
    }
```

## 📦 HuggingFace Dataset Structure

### Current Datasets Being Uploaded

```
oral-health-policy-data/
├── discovery/              # Jurisdiction discovery results
│   ├── jurisdiction_info   # 22,000+ cities & counties
│   ├── youtube_channels    # Government YouTube channels
│   ├── meeting_platforms   # Legistar, SuiteOne, Granicus
│   └── social_media       # Twitter, Facebook accounts
│
├── meetings/               # Meeting data
│   ├── agendas            # Meeting agendas (text extracted)
│   ├── minutes            # Meeting minutes (text extracted)
│   ├── videos             # YouTube/Vimeo video metadata
│   └── documents          # Associated documents
│
├── officials/              # Elected officials & leaders
│   ├── local_officials    # City/county officials
│   ├── state_legislators  # From Open States
│   └── school_board       # School board members
│
├── organizations/          # Nonprofits & charities
│   ├── irs_nonprofits     # IRS 990 data
│   └── organizational_data
│
├── civic_data/            # Google Civic & Wikidata
│   ├── civic_divisions    # OCD divisions
│   ├── representatives    # From Google Civic API
│   ├── wikidata_entities  # Structured entities
│   └── dbpedia_resources  # Wikipedia infobox data
│
└── schools/               # School districts
    └── nces_districts     # NCES Common Core Data
```

## 🔄 Data Extraction Pipeline

### Phase 1: Discovery (Bronze Layer)
1. **Census Data** → Jurisdictions list
2. **GSA Domains** → Government websites
3. **NCES** → School districts
4. **URL Discovery** → Meeting platforms, YouTube
5. **Social Media** → Twitter, Facebook accounts

### Phase 2: Enrichment (Silver Layer)
1. **YouTube API** → Channel statistics
2. **Open States** → Legislative data
3. **Wikidata SPARQL** → Entity relationships
4. **DBpedia** → Wikipedia structured data
5. **Google Civic** → Representatives

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
| YouTube Channels | 5,000+ | Discovery pipeline |
| Meeting Platforms | 10,000+ | URL detection |
| State Legislators | 7,300+ | Open States |
| Meetings | 500,000+ | Scraped |
| Documents | 2,000,000+ | PDF extraction |

## 🎯 Missing Datasets to Add

### High Priority
- [ ] **Census Demographics** - Full census data per jurisdiction
- [ ] **Budget Documents** - Municipal budgets & spending
- [ ] **Procurement Records** - Government contracts
- [ ] **Election Results** - Historical voting data
- [ ] **Property Records** - Public assessment data
- [ ] **Crime Statistics** - UCR/NIBRS data
- [ ] **Health Outcomes** - CDC PLACES data
- [ ] **Environmental Data** - EPA monitoring

### Medium Priority
- [ ] **Business Licenses** - Local business registrations
- [ ] **Building Permits** - Construction activity
- [ ] **Code Violations** - Inspection records
- [ ] **Police Reports** - Public safety incidents
- [ ] **Fire Department Data** - Emergency response
- [ ] **Parks & Recreation** - Facilities & programs
- [ ] **Transportation Data** - Traffic & transit

### Integration Improvements
- [ ] **Full Wikidata Sync** - All civic entities
- [ ] **DBpedia Expansion** - Complete local government coverage
- [ ] **Ballotpedia Data** - (if budget allows) Electoral info
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
