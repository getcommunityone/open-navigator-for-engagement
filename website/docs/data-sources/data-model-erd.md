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
    
    %% Government Finances
    JURISDICTION ||--o{ GOVERNMENT_BUDGET : has
    GOVERNMENT_BUDGET {
        string budget_id PK
        string jurisdiction_id FK
        int fiscal_year
        float total_revenue
        float total_expenditures
        float total_debt
        float property_tax_revenue
        float sales_tax_revenue
        float federal_grants
        float state_grants
        float general_fund_balance
        string budget_document_url
        datetime published_date
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
        float total_revenue
        float total_expenditures
        float per_pupil_spending
        float federal_revenue
        float state_revenue
        float local_revenue
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
        string event_category
        datetime meeting_date
        datetime end_date
        string meeting_title
        string body_name
        string status
        string platform
        string source_url
        boolean oral_health_related
        string training_topic
        string target_audience
        string presenter
        boolean requires_registration
        float registration_fee
        int max_capacity
        string location_type
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
    ORGANIZATION ||--o{ NONPROFIT_FINANCES : files
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
        int employee_count
        string mission_statement
        string description
        string logo_url
        string website
        boolean is_verified
    }
    
    %% Nonprofit 990 Financial Data
    NONPROFIT_FINANCES {
        string filing_id PK
        string ein FK
        int tax_year
        float total_revenue
        float total_expenses
        float total_assets
        float total_liabilities
        float net_assets
        float program_expenses
        float admin_expenses
        float fundraising_expenses
        float grants_paid
        float contributions_received
        float government_grants
        float foundation_grants
        float corporate_donations
        float individual_donations
        float membership_dues
        float special_events_revenue
        float program_service_revenue
        float investment_income
        float rental_income
        float sale_of_assets
        float other_revenue
        float employee_compensation
        int employee_count
        int volunteer_count
        float overhead_ratio
        float fundraising_efficiency
        string form_990_url
        datetime filing_date
    }
    
    %% Grant Transactions (Individual Grants)
    ORGANIZATION ||--o{ GRANT : receives
    JURISDICTION ||--o{ GRANT : awards
    GRANT {
        string grant_id PK
        string recipient_ein FK
        string recipient_name
        string recipient_type
        string funder_name
        string funder_ein
        string funder_type
        float grant_amount
        string grant_purpose
        string program_area
        datetime award_date
        datetime start_date
        datetime end_date
        int grant_duration_months
        string grant_status
        string funding_source
        boolean multi_year
        string restrictions
        string reporting_requirements
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
    %% Data Sources: Ballotpedia (comprehensive measures), 
    %%               MIT Election Lab (federal results),
    %%               OpenElections (certified state results)
    %% See: ballot-election-sources.md
    %% ========================================
    
    JURISDICTION ||--o{ BALLOT_MEASURE : hosts
    STATE_LEGISLATURE ||--o{ BALLOT_MEASURE : proposes
    POLICY_TOPIC ||--o{ BALLOT_MEASURE : addresses
    BALLOT_MEASURE {
        string measure_id PK
        string jurisdiction_id FK "OCD-ID format"
        string state_code "Two-letter code"
        datetime election_date
        string measure_number "Proposition 15, Question 2"
        string title "Measure title"
        string description "Full description"
        string measure_type "Initiative, Referendum, Bond"
        string topic_category "fluoridation, education, tax"
        string status "qualified, certified, passed, failed"
        string result "passed, failed, pending"
        int yes_votes "Total yes votes"
        int no_votes "Total no votes"
        float yes_percentage "Yes vote percentage"
        string full_text_url "Official measure text"
        string ballotpedia_url "Ballotpedia reference"
        string openelections_source "OpenElections CSV file"
        datetime created_at
    }
    
    POLICY_TOPIC ||--o{ MEETING : discussed_in
    POLICY_TOPIC ||--o{ LEGISLATION : addresses
    POLICY_TOPIC {
        string topic_id PK
        string topic_name "Water Fluoridation Support"
        string category "health_policy"
        string description "Public opinion on fluoridation"
        string keywords "fluoride, water treatment"
        int priority_level "1-10 importance ranking"
        string icon "🦷"
        int jurisdiction_count "How many jurisdictions discuss"
        string validated_question_text "Scientifically tested question from Roper"
        string question_source "Gallup Poll, March 2015"
        float national_support_pct "67.0 (percentage)"
        string roper_ipoll_id "USGALLUP.031915.R12A reference"
        datetime created_at
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
open-navigator-data/
├── jurisdictions/          # 🏛️ Core jurisdiction data
│   ├── cities              # 19,000+ incorporated places
│   ├── counties            # 3,144 U.S. counties
│   ├── states              # 50 states + DC, territories
│   ├── school_districts    # 13,000+ districts (NCES data)
│   ├── census_data         # Basic population & geographic data
│   └── demographics        # 👥 Comprehensive demographics (race, age, income, education, etc.)
│
├── social/                 # 📱 Social media presence
│   ├── twitter             # Twitter/X accounts
│   ├── facebook            # Facebook pages
│   ├── instagram           # Instagram accounts
│   └── linkedin            # LinkedIn pages
│
├── videos/                 # 📹 Video & streaming platforms
│   ├── youtube_channels    # Government YouTube channels
│   ├── vimeo              # Vimeo accounts
│   └── livestreams        # Live meeting streams
│
├── platforms/              # 🖥️ Meeting management systems
│   ├── legistar           # Legistar URLs
│   ├── granicus           # Granicus links
│   ├── suiteone           # SuiteOne systems
│   └── civicplus          # CivicPlus platforms
│
├── domains/                # 🌐 Official government websites
│   ├── gsa_domains        # .gov domain registry
│   ├── municipal_websites # City/county websites
│   └── state_portals      # State government sites
│
├── meetings/               # 📋 Meetings, events & trainings
│   ├── government_meetings # City council, school board, etc.
│   ├── public_hearings    # Public comment sessions
│   ├── community_events   # Town halls, forums, engagement
│   ├── trainings          # Professional development, workshops
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
├── nonprofits/             # 🏢 Nonprofit organizations
│   ├── irs_nonprofits     # IRS 990 data (3M+ organizations)
│   ├── propublica_data    # ProPublica API (financials, NTEE codes)
│   ├── everyorg_data      # Every.org API (missions, causes, logos)
│   └── nonprofit_990s     # Detailed Form 990 financials (yearly filings)
│
├── grants/                 # 💵 Grant funding transactions
│   ├── nonprofit_grants   # Grants to nonprofits (from 990 Schedule I)
│   ├── government_grants  # Government grants to orgs/jurisdictions
│   ├── foundation_grants  # Private foundation grants
│   └── federal_grants     # Federal funding programs
│
├── causes/                 # 🎯 Cause & category taxonomy
│   ├── ntee_codes         # IRS NTEE classification system
│   └── everyorg_causes    # Every.org cause tags
│
├── budgets/                # 💰 Government budgets & finances
│   ├── city_budgets       # City/municipal budgets & spending
│   ├── county_budgets     # County budgets & expenditures
│   ├── state_budgets      # State government finances
│   ├── school_budgets     # School district finances (NCES F-33)
│   └── bond_debt          # Municipal bonds & debt obligations
│
├── civic/                  # 🗳️ Google Civic & Wikidata
│   ├── civic_divisions    # OCD divisions
│   ├── representatives    # From Google Civic API
│   ├── wikidata_entities  # Structured entities
│   └── dbpedia_resources  # Wikipedia infobox data
│
├── ballots/                # 🗳️ Ballot initiatives & referendums
│   ├── state_measures      # State propositions (fluoridation votes!)
│   ├── local_measures      # City/county ballot questions
│   └── election_results    # Historical voting outcomes
│
├── legislation/            # 📜 Bills, ordinances, resolutions
│   ├── state_bills         # From Open States API (52 states)
│   ├── local_ordinances    # Municipal codes & resolutions
│   └── policy_tracking     # Bill status & outcomes
│
└── topics/                 # 🎯 Advocacy causes & campaigns
    ├── topic_definitions   # Validated survey questions from Roper Center
    ├── survey_questions    # Public opinion question wording library
    ├── jurisdiction_topics # What each city is discussing
    └── advocacy_alerts     # Opportunities for engagement
```

### Parquet File Naming Convention

**Rule:** Use underscores (`_`) consistently, NOT hyphens (`-`)

**Format:** `{category}_{subcategory}.parquet`

**Examples:**
```
✅ CORRECT (using underscores):
jurisdictions_cities.parquet
jurisdictions_counties.parquet
jurisdictions_states.parquet
jurisdictions_school_districts.parquet
social_twitter.parquet
social_facebook.parquet
videos_youtube_channels.parquet
meetings_government_meetings.parquet
nonprofits_irs_nonprofits.parquet
grants_federal_grants.parquet
budgets_city_budgets.parquet
surveys_national_polls.parquet
surveys_roper_questions.parquet
factchecks_claim_reviews.parquet
factchecks_politifact.parquet

❌ INCORRECT (using hyphens):
jurisdictions-cities.parquet
social-twitter.parquet
meetings-government-meetings.parquet
surveys-national-polls.parquet
factchecks-claim-reviews.parquet
```

**Why Underscores?**
- ✅ Python-friendly variable names (can use `data.jurisdictions_cities`)
- ✅ SQL-compatible column names
- ✅ Consistent with folder structure (`school_districts`, not `school-districts`)
- ✅ Better for programmatic access
- ✅ Avoids shell escaping issues

**Repository Name Exception:**
- HuggingFace repo: `CommunityOne/open-navigator-data` (hyphen is fine for URLs)
- File names inside repo: Use underscores (`jurisdictions_cities.parquet`)

## 🔄 Data Extraction Pipeline

### Phase 1: Discovery (Bronze Layer)
1. **Census Data** → Jurisdictions list
2. **GSA Domains** → Government websites
3. **NCES** → School districts with financial data (F-33 forms)
4. **IRS TEOS** → Nonprofit EINs (3M+ organizations)
5. **Census of Governments** → Municipal budgets & finances
6. **URL Discovery** → Meeting platforms, YouTube, budget PDFs
7. **Social Media** → Twitter, Facebook accounts

### Phase 2: Enrichment (Silver Layer)
1. **ProPublica Nonprofit Explorer** → Financial data, NTEE codes, 990 filings
2. **Every.org API** → Nonprofit causes, missions, logos
3. **NCES F-33 Finance Survey** → School district budgets, per-pupil spending
4. **Census Annual Survey** → State/local government finances
5. **Municipal Securities Rulemaking Board (EMMA)** → Bond debt data
6. **YouTube API** → Channel statistics
7. **Open States** → Legislative data
8. **Wikidata SPARQL** → Entity relationships
9. **DBpedia** → Wikipedia structured data
10. **Google Civic** → Representatives

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
| School District Budgets | 13,000+ | NCES F-33 Finance Survey |
| Government Budgets | 22,000+ | Census of Governments |
| Municipal Bonds | TBD | EMMA (MSRB) |
| Nonprofits | 3,000,000+ | IRS TEOS |
| Nonprofit 990 Filings | 10,000,000+ | ProPublica (10+ years) |
| Grants (Individual Awards) | TBD | IRS 990-I, USASpending.gov, Foundation Center |
| Federal Grants | 100,000+ | USASpending.gov API |
| Nonprofit Causes | 600+ | NTEE + Every.org |
| YouTube Channels | 5,000+ | Discovery pipeline |
| Meeting Platforms | 10,000+ | URL detection |
| State Legislators | 7,300+ | Open States |
| Meetings & Events | 500,000+ | Scraped (govt, hearings, events, trainings) |
| Trainings | TBD | Professional development, workshops |
| Documents | 2,000,000+ | PDF extraction |
| Ballot Measures | TBD | State/local election sites |
| State Bills | 100,000+ | Open States API |
| Policy Topics | ~50 | Curated + extracted |

## � Meeting & Event Types

### Event Categories in the MEETING Entity

The MEETING entity tracks **4 main event categories** to capture all civic engagement opportunities:

#### 1. **Government Meetings** (`event_category: "government_meeting"`)
- City council meetings, school board meetings, county commissions
- Official business conducted by elected bodies
- **Fields:** `body_name`, `meeting_type` (regular, special, emergency)
- **Example:** "Tuscaloosa City Council Regular Meeting - 3rd Tuesday"

#### 2. **Public Hearings** (`event_category: "public_hearing"`)
- Public comment sessions on specific issues
- Budget hearings, zoning hearings, policy feedback
- **Fields:** `meeting_type` (budget, zoning, policy)
- **Example:** "Public Hearing on FY2026 Water System Fluoridation Budget"

#### 3. **Community Events** (`event_category: "community_event"`)
- Town halls, community forums, listening sessions
- Informal engagement between government and citizens
- **Fields:** `location_type` (in-person, virtual, hybrid)
- **Example:** "Town Hall on Community Health Priorities"

#### 4. **Trainings** (`event_category: "training"`) ⭐ NEW
- Professional development workshops
- Continuing education for healthcare workers, teachers, officials
- Certification courses, skill-building sessions
- **Fields:**
  - `training_topic` - Subject matter (e.g., "Pediatric Oral Health", "Water Fluoridation Safety")
  - `target_audience` - Who should attend (e.g., "Dental Hygienists", "School Nurses", "Water Operators")
  - `presenter` - Trainer/instructor name or organization
  - `requires_registration` - Boolean flag
  - `registration_fee` - Cost to attend (0 for free)
  - `max_capacity` - Attendance limit
  - `end_date` - Training end time (multi-day events)
- **Example:** "Fluoride Varnish Application Training for School Nurses (3 CEU)"

### Why Trainings Matter for Advocacy

**Capacity Building:**
- ✅ Identify training gaps ("No fluoride varnish training in past 2 years")
- ✅ Track professional development opportunities
- ✅ Monitor continuing education credits (CEUs) offered

**Stakeholder Engagement:**
- ✅ Find healthcare workers trained in specific skills
- ✅ Identify champions (frequent training attendees)
- ✅ Target outreach to trained professionals

**Policy Implementation:**
- ✅ "City wants dental screenings but no trained staff" → Show available trainings
- ✅ Track certification status (who's qualified to implement policy)
- ✅ Link training availability to policy feasibility

**Example Questions Now Answerable:**
1. "What oral health trainings are offered in Alabama?" → Filter by `training_topic` LIKE '%oral%'
2. "Which jurisdictions offer free fluoride training?" → `registration_fee = 0` AND `training_topic` LIKE '%fluoride%'
3. "How many school nurses attended varnish training last year?" → Count attendees by `target_audience`
4. "Are there upcoming water fluoridation operator trainings?" → `training_topic` AND `meeting_date` > TODAY

### Meeting Types Within Each Category

**Government Meetings:**
- Regular sessions, special sessions, emergency meetings
- Work sessions, committee meetings, executive sessions

**Public Hearings:**
- Budget hearings, zoning hearings, policy feedback sessions
- Environmental impact hearings, license applications

**Community Events:**
- Town halls, listening sessions, community forums
- Neighborhood meetings, stakeholder roundtables

**Trainings:**
- Professional development workshops
- Certification courses (CPR, fluoride application, etc.)
- Continuing education (CEU/CME credits)
- Skill-building sessions (motivational interviewing, cultural competency)

## �💰 Nonprofit Funding Source Tracking

### Revenue Source Breakdown (Form 990 Data)

The NONPROFIT_FINANCES entity tracks **10 different revenue sources** to understand how nonprofits are funded:

#### 1. **Grant Revenue** (Institutional Funding)
- `government_grants` - Federal, state, local government grants
- `foundation_grants` - Private foundation grants (Gates, Ford, etc.)
- **Why it matters:** Grant-dependent orgs may be less sustainable, more restrictive

#### 2. **Donation Revenue** (Community Funding)
- `individual_donations` - Direct donations from people
- `corporate_donations` - Corporate giving programs
- `membership_dues` - Member subscriptions/fees
- **Why it matters:** Grassroots funding = community support, more flexible use

#### 3. **Earned Revenue** (Self-Sufficiency)
- `program_service_revenue` - Fees for services (clinic visits, classes, etc.)
- `special_events_revenue` - Galas, fundraisers, events
- `rental_income` - Property rentals
- `sale_of_assets` - Asset sales
- **Why it matters:** Self-generated revenue = sustainability, independence

#### 4. **Investment Revenue**
- `investment_income` - Interest, dividends, capital gains
- **Why it matters:** Endowment size, financial health

#### 5. **Other Revenue**
- `other_revenue` - Miscellaneous sources
- **Why it matters:** Unusual funding patterns

### Calculated Metrics

- **`overhead_ratio`** = (admin_expenses + fundraising_expenses) / total_expenses
  - Lower = more efficient (more goes to programs)
  - Industry benchmark: &lt;25% overhead is "good"

- **`fundraising_efficiency`** = contributions_received / fundraising_expenses
  - Higher = better (more money raised per dollar spent)
  - Industry benchmark: $4+ raised per $1 spent

### Why This Matters for Advocacy

**Find sustainable partners:**
- ✅ High individual donations = community trust
- ✅ Diversified revenue = financial stability
- ⚠️ Single-grant dependent = risky partnership

**Evaluate efficiency:**
- ✅ Low overhead ratio = more program dollars
- ✅ High fundraising efficiency = good stewardship
- ⚠️ High admin costs = potential waste

**Identify funding gaps:**
- Compare similar nonprofits' revenue mix
- Find underutilized funding sources (e.g., membership programs)
- Target corporate donation opportunities

**Example Questions Now Answerable:**
1. "Which dental nonprofits have the most individual donors?" (community support)
2. "What's the average overhead for oral health organizations?" (efficiency benchmark)
3. "Are dental nonprofits more grant-dependent or self-sufficient?" (sustainability)
4. "Which funders support oral health work?" (foundation grants analysis)

## 💵 Grant Tracking System

### Individual Grant Transactions (GRANT Entity)

The GRANT entity tracks **individual grant awards** beyond just aggregate 990 financials. This provides transaction-level detail for:

#### Grant Fields
- **Recipient Info:** `recipient_ein`, `recipient_name`, `recipient_type` (nonprofit, government, etc.)
- **Funder Info:** `funder_name`, `funder_ein`, `funder_type` (foundation, government, corporate)
- **Grant Details:** `grant_amount`, `grant_purpose`, `program_area`
- **Timeline:** `award_date`, `start_date`, `end_date`, `grant_duration_months`
- **Status:** `grant_status` (active, completed, terminated)
- **Type:** `funding_source` (federal, state, foundation, corporate)
- **Restrictions:** `multi_year`, `restrictions`, `reporting_requirements`

#### Data Sources

**IRS Form 990 Schedule I:**
- Grants PAID by nonprofits to other organizations
- Required for organizations granting >$5,000/year
- Shows foundation giving patterns

**USASpending.gov API (FREE):**
- All federal grants to states, localities, nonprofits
- Contract and grant transactions $25K+
- Real-time data updated daily

**Foundation Center/Candid:**
- Private foundation grants (990-PF data)
- Grant descriptions, amounts, recipients

**State Grant Databases:**
- State-level grant programs
- Varies by state

### Why Grant Tracking Matters

**Follow the Money:**
- ✅ "Who funds oral health work in Alabama?" → Track all grants by `program_area`
- ✅ "Which foundations support fluoridation?" → Search grant purposes
- ✅ "How much federal money goes to dental access?" → Sum `funding_source = federal`

**Find Funding Opportunities:**
- ✅ Identify active grant programs (similar grants to similar orgs)
- ✅ Discover new funders entering a program area
- ✅ Track grant sizes and typical durations

**Partnership Intelligence:**
- ✅ "Who else is this foundation funding?" → Find collaborators
- ✅ "What's this nonprofit's grant portfolio?" → Assess stability
- ✅ Multi-year grants = long-term commitment signal

**Policy Implementation:**
- ✅ "Is there grant funding for this program?" → Search active grants
- ✅ "Which jurisdictions received similar grants?" → Learn from others
- ✅ Track grant requirements and restrictions

#### Example Questions Now Answerable:

1. **"What federal grants support dental health in Alabama schools?"**
   → `funding_source = 'federal'` AND `program_area` LIKE '%dental%' AND `recipient_type = 'school_district'`

2. **"Which foundations give the largest oral health grants?"**
   → GROUP BY `funder_name` WHERE `program_area` LIKE '%oral health%' ORDER BY SUM(`grant_amount`)

3. **"How long do typical dental access grants last?"**
   → AVG(`grant_duration_months`) WHERE `program_area` = 'dental access'

4. **"Which nonprofits receive multi-year fluoridation funding?"**
   → `multi_year = true` AND `grant_purpose` LIKE '%fluoride%'

5. **"What grants end in the next 6 months?"**
   → `end_date` BETWEEN NOW() AND NOW() + 6 MONTHS (renewal opportunities!)

### Dataset Structure

```
grants/
├── nonprofit_grants    # Grants TO nonprofits (Schedule I recipients)
├── government_grants   # Federal/state grants to jurisdictions
├── foundation_grants   # Private foundation giving (990-PF)
└── federal_grants      # USASpending.gov federal grants
```

## ⏰ Time Dimension Modeling

To enable robust time-series analysis, trend tracking, and temporal comparisons, we implement a comprehensive time dimension alongside our fact tables.

### Time Dimension Table

```sql
DATE_DIMENSION {
    date date PK
    year int
    quarter int
    quarter_name string
    month int
    month_name string
    month_abbr string
    day_of_month int
    day_of_week int
    day_name string
    day_abbr string
    week_of_year int
    fiscal_year int
    fiscal_quarter int
    fiscal_month int
    is_weekend boolean
    is_holiday boolean
    holiday_name string
    is_business_day boolean
    days_in_month int
    year_month string
    year_quarter string
}
```

### Temporal Relationships

All time-bound entities link to the date dimension for consistent temporal analysis:

```mermaid
erDiagram
    DATE_DIMENSION ||--o{ MEETING : "meeting_date"
    DATE_DIMENSION ||--o{ GOVERNMENT_BUDGET : "fiscal_year_start"
    DATE_DIMENSION ||--o{ BALLOT_MEASURE : "election_date"
    DATE_DIMENSION ||--o{ LEGISLATION : "introduced_date"
    DATE_DIMENSION ||--o{ GRANT : "start_date, end_date"
    DATE_DIMENSION ||--o{ NONPROFIT_FILING : "tax_period_end"
    DATE_DIMENSION ||--o{ POLICY_TRACKER : "tracked_date"
    DATE_DIMENSION ||--o{ SURVEY : "field_date_start, field_date_end"
    DATE_DIMENSION ||--o{ FACT_CHECK : "published_date"
    
    DATE_DIMENSION {
        date date PK
        year int
        quarter int
        month int
        fiscal_year int
        is_business_day boolean
    }
```

### Temporal Analysis Patterns

**Year-over-Year Comparisons:**
```sql
SELECT 
    d.year,
    d.quarter_name,
    COUNT(m.meeting_id) as meeting_count,
    COUNT(m.meeting_id) - LAG(COUNT(m.meeting_id)) OVER (ORDER BY d.year, d.quarter) as yoy_change
FROM MEETING m
JOIN DATE_DIMENSION d ON m.meeting_date = d.date
WHERE d.year BETWEEN 2023 AND 2025
GROUP BY d.year, d.quarter, d.quarter_name
ORDER BY d.year, d.quarter;
```

**Fiscal Period Aggregation:**
```sql
SELECT 
    d.fiscal_year,
    d.fiscal_quarter,
    SUM(b.total_expenditures) as total_spending,
    AVG(b.total_expenditures) as avg_spending
FROM GOVERNMENT_BUDGET b
JOIN DATE_DIMENSION d ON b.fiscal_year = d.fiscal_year
WHERE b.jurisdiction_type = 'city'
GROUP BY d.fiscal_year, d.fiscal_quarter;
```

**Trend Detection:**
```sql
-- Identify growing advocacy momentum
SELECT 
    d.year_month,
    COUNT(DISTINCT pt.topic_id) as active_topics,
    COUNT(m.meeting_id) as related_meetings,
    COUNT(bm.measure_id) as ballot_initiatives
FROM DATE_DIMENSION d
LEFT JOIN MEETING m ON m.meeting_date = d.date AND m.oral_health_related = true
LEFT JOIN POLICY_TRACKER pt ON d.date BETWEEN pt.start_date AND COALESCE(pt.end_date, CURRENT_DATE)
LEFT JOIN BALLOT_MEASURE bm ON bm.election_date = d.date
WHERE d.date >= DATE_SUB(CURRENT_DATE, INTERVAL 24 MONTH)
GROUP BY d.year_month
ORDER BY d.year_month;
```

## 📊 Metric Views

Metric views provide pre-aggregated, analysis-ready datasets combining multiple source tables with built-in dimensions, measures, and filters.

### Core Metric View Components

| Component | Description | Example |
|-----------|-------------|---------|
| **Source** | Base table, view, or SQL query containing the data | `MEETING`, `GOVERNMENT_BUDGET`, `NONPROFIT_FILING` |
| **Dimensions** | Column attributes used to segment or group metrics | `jurisdiction_type`, `fiscal_year`, `policy_topic` |
| **Measures** | Column aggregations that produce metrics | `COUNT(meeting_id) as meeting_count`, `SUM(grant_amount) as total_funding` |
| **Filters** | Conditions applied to source data to define scope | `oral_health_related = true`, `fiscal_year > 2020` |
| **Joins** | Relationships between tables to enrich data | `JOIN JURISDICTION ON meeting.jurisdiction_id = jurisdiction.jurisdiction_id` |

### Example Metric Views

#### 1. Advocacy Activity Metrics

**Purpose:** Track oral health advocacy momentum across jurisdictions

```sql
CREATE VIEW metric_advocacy_activity AS
SELECT 
    -- Dimensions
    j.jurisdiction_id,
    j.jurisdiction_type,
    j.state_code,
    j.county_name,
    d.year,
    d.quarter_name,
    d.month_name,
    pt.topic_name,
    
    -- Measures
    COUNT(DISTINCT m.meeting_id) as meeting_count,
    COUNT(DISTINCT bm.measure_id) as ballot_measure_count,
    COUNT(DISTINCT l.bill_id) as legislation_count,
    COUNT(DISTINCT fc.claim_id) as fact_check_count,
    
    -- Calculated Metrics
    SUM(CASE WHEN m.oral_health_related THEN 1 ELSE 0 END) as oral_health_meeting_count,
    AVG(CASE WHEN bm.result = 'passed' THEN 1 ELSE 0 END) as ballot_success_rate,
    COUNT(DISTINCT n.nonprofit_id) as active_nonprofit_count

FROM JURISDICTION j
JOIN DATE_DIMENSION d ON d.date BETWEEN DATE_SUB(CURRENT_DATE, INTERVAL 365 DAY) AND CURRENT_DATE
LEFT JOIN MEETING m ON m.jurisdiction_id = j.jurisdiction_id AND m.meeting_date = d.date
LEFT JOIN POLICY_TRACKER pt ON pt.jurisdiction_id = j.jurisdiction_id
LEFT JOIN BALLOT_MEASURE bm ON bm.jurisdiction_id = j.jurisdiction_id AND bm.election_date = d.date
LEFT JOIN LEGISLATION l ON l.state_code = j.state_code AND l.introduced_date = d.date
LEFT JOIN FACT_CHECK fc ON fc.published_date = d.date
LEFT JOIN NONPROFIT n ON n.jurisdiction_id = j.jurisdiction_id

WHERE 
    -- Filters
    d.is_business_day = true
    AND (
        m.oral_health_related = true 
        OR pt.topic_area LIKE '%oral health%'
        OR pt.topic_area LIKE '%dental%'
        OR pt.topic_area LIKE '%fluoride%'
    )

GROUP BY 
    j.jurisdiction_id, j.jurisdiction_type, j.state_code, j.county_name,
    d.year, d.quarter_name, d.month_name, pt.topic_name;
```

**Usage:**
```sql
-- Find top 10 most active jurisdictions for oral health advocacy
SELECT 
    jurisdiction_id,
    state_code,
    jurisdiction_type,
    SUM(meeting_count) as total_meetings,
    SUM(ballot_measure_count) as total_ballot_measures,
    SUM(oral_health_meeting_count) as oral_health_meetings
FROM metric_advocacy_activity
WHERE year = 2025
GROUP BY jurisdiction_id, state_code, jurisdiction_type
ORDER BY total_meetings DESC
LIMIT 10;
```

#### 2. Government Spending Metrics

**Purpose:** Analyze government budget allocations and trends

```sql
CREATE VIEW metric_government_spending AS
SELECT 
    -- Dimensions
    j.jurisdiction_id,
    j.jurisdiction_type,
    j.state_code,
    j.population,
    d.fiscal_year,
    d.fiscal_quarter,
    bc.category_name as budget_category,
    
    -- Measures
    SUM(gb.total_revenue) as total_revenue,
    SUM(gb.total_expenditures) as total_expenditures,
    SUM(gb.total_debt) as total_debt,
    SUM(gb.property_tax_revenue) as property_tax_revenue,
    SUM(gb.federal_grants) as federal_grants,
    SUM(gb.state_grants) as state_grants,
    
    -- Calculated Metrics
    SUM(gb.total_revenue) / NULLIF(j.population, 0) as revenue_per_capita,
    SUM(gb.total_expenditures) / NULLIF(j.population, 0) as spending_per_capita,
    SUM(gb.total_debt) / NULLIF(j.population, 0) as debt_per_capita,
    (SUM(gb.total_revenue) - SUM(gb.total_expenditures)) as budget_surplus_deficit,
    SUM(bc.amount) / NULLIF(SUM(gb.total_expenditures), 0) * 100 as category_pct_of_budget

FROM JURISDICTION j
JOIN DATE_DIMENSION d ON d.fiscal_year BETWEEN 2020 AND 2025
JOIN GOVERNMENT_BUDGET gb ON gb.jurisdiction_id = j.jurisdiction_id AND gb.fiscal_year = d.fiscal_year
LEFT JOIN BUDGET_CATEGORY bc ON bc.budget_id = gb.budget_id

WHERE 
    -- Filters
    gb.total_expenditures > 0
    AND j.population > 0

GROUP BY 
    j.jurisdiction_id, j.jurisdiction_type, j.state_code, j.population,
    d.fiscal_year, d.fiscal_quarter, bc.category_name;
```

**Usage:**
```sql
-- Compare spending per capita across jurisdiction types
SELECT 
    jurisdiction_type,
    fiscal_year,
    AVG(spending_per_capita) as avg_spending_per_capita,
    AVG(revenue_per_capita) as avg_revenue_per_capita,
    AVG(debt_per_capita) as avg_debt_per_capita
FROM metric_government_spending
GROUP BY jurisdiction_type, fiscal_year
ORDER BY fiscal_year DESC, avg_spending_per_capita DESC;
```

#### 3. Nonprofit Impact Metrics

**Purpose:** Measure nonprofit activity, funding, and service delivery

```sql
CREATE VIEW metric_nonprofit_impact AS
SELECT 
    -- Dimensions
    n.nonprofit_id,
    n.organization_name,
    n.state,
    n.city,
    nc.ntee_code,
    nc.category_name,
    d.tax_year,
    
    -- Measures
    SUM(nf.total_revenue) as total_revenue,
    SUM(nf.total_expenses) as total_expenses,
    SUM(nf.total_assets) as total_assets,
    SUM(nf.program_service_expenses) as program_expenses,
    SUM(nf.fundraising_expenses) as fundraising_expenses,
    SUM(nf.management_expenses) as management_expenses,
    COUNT(DISTINCT g.grant_id) as grants_received_count,
    SUM(g.grant_amount) as total_grants_received,
    
    -- Calculated Metrics
    SUM(nf.program_service_expenses) / NULLIF(SUM(nf.total_expenses), 0) * 100 as program_expense_ratio,
    SUM(nf.fundraising_expenses) / NULLIF(SUM(nf.total_revenue), 0) * 100 as fundraising_efficiency,
    (SUM(nf.total_revenue) - SUM(nf.total_expenses)) as net_income,
    COUNT(DISTINCT nf.year) as years_active

FROM NONPROFIT n
JOIN DATE_DIMENSION d ON d.year BETWEEN 2020 AND 2025
JOIN NONPROFIT_FILING nf ON nf.ein = n.ein AND nf.tax_year = d.year
LEFT JOIN NONPROFIT_CAUSE nc ON nc.cause_id = n.primary_cause_id
LEFT JOIN GRANT g ON g.recipient_ein = n.ein AND g.tax_year = d.year

WHERE 
    -- Filters
    nf.total_revenue > 0
    AND (
        nc.category_name LIKE '%health%'
        OR nc.category_name LIKE '%dental%'
        OR n.mission_statement LIKE '%oral health%'
    )

GROUP BY 
    n.nonprofit_id, n.organization_name, n.state, n.city,
    nc.ntee_code, nc.category_name, d.tax_year;
```

**Usage:**
```sql
-- Identify high-performing health nonprofits by program efficiency
SELECT 
    organization_name,
    state,
    tax_year,
    total_revenue,
    program_expense_ratio,
    fundraising_efficiency
FROM metric_nonprofit_impact
WHERE 
    tax_year = 2024
    AND total_revenue > 1000000
    AND program_expense_ratio > 75  -- More than 75% goes to programs
ORDER BY program_expense_ratio DESC, total_revenue DESC
LIMIT 20;
```

### Metric View Best Practices

1. **Grain Definition**: Clearly define the granularity of each metric view (e.g., per jurisdiction per month)
2. **Performance**: Pre-aggregate expensive calculations to improve query performance
3. **Incremental Updates**: Design views to support incremental refresh rather than full rebuilds
4. **Documentation**: Document all dimension values, measure calculations, and filter logic
5. **Naming Convention**: Use `metric_` prefix followed by descriptive name (e.g., `metric_advocacy_activity`)
6. **Testing**: Validate measure calculations against source data to ensure accuracy

### Query Optimization

For large-scale analytics, metric views can be materialized:

```sql
-- Materialize for fast querying
CREATE MATERIALIZED VIEW metric_advocacy_activity_mat AS
SELECT * FROM metric_advocacy_activity;

-- Refresh incrementally
REFRESH MATERIALIZED VIEW metric_advocacy_activity_mat;

-- Add indexes on common filter/join columns
CREATE INDEX idx_advocacy_state_year 
ON metric_advocacy_activity_mat(state_code, year);

CREATE INDEX idx_advocacy_jurisdiction 
ON metric_advocacy_activity_mat(jurisdiction_id);
```

## 🎯 Missing Datasets to Add

### High Priority
- [x] **Ballot Measures** - ✅ Added to data model! Fluoridation votes, bond measures
- [x] **State Legislation** - ✅ Added to data model! Open States API (FREE)
- [x] **Policy Topics** - ✅ Added to data model! Oral health advocacy tracking
- [x] **Government Finances** - ✅ Added to data model! City/county/state budgets, Census of Governments
- [x] **School Finances** - ✅ Added to data model! NCES F-33 per-pupil spending, revenues
- [x] **Nonprofit Financials** - ✅ Added to data model! Form 990 detailed financials (10M+ filings)
- [ ] **Census Demographics** - Full census data per jurisdiction (beyond population)
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
