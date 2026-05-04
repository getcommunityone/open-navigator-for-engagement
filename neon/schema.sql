-- ============================================================================
-- NEON DATABASE SCHEMA FOR OPEN NAVIGATOR
-- Optimized for fast API queries on HuggingFace Spaces deployment
-- ============================================================================

-- Drop existing tables if rerunning (careful in production!)
DROP TABLE IF EXISTS stats_aggregates CASCADE;
DROP TABLE IF EXISTS nonprofits_search CASCADE;
DROP TABLE IF EXISTS jurisdictions_search CASCADE;
DROP TABLE IF EXISTS contacts_search CASCADE;
DROP TABLE IF EXISTS events_search CASCADE;
DROP TABLE IF EXISTS bills_search CASCADE;
DROP TABLE IF EXISTS reference_causes CASCADE;
DROP TABLE IF EXISTS reference_ntee_codes CASCADE;
DROP TABLE IF EXISTS last_sync CASCADE;

-- ============================================================================
-- AGGREGATE STATISTICS TABLES
-- Pre-computed stats for fast dashboard loading
-- ============================================================================

CREATE TABLE stats_aggregates (
    id SERIAL PRIMARY KEY,
    level VARCHAR(20) NOT NULL,  -- 'national', 'state', 'county', 'city'
    state_code VARCHAR(2),        -- Two-letter state code (e.g., 'AL', 'MA')
    state VARCHAR(50),            -- Full state name (e.g., 'Alabama', 'Massachusetts')
    county VARCHAR(100),          -- County name
    city VARCHAR(100),            -- City name
    
    -- Core metrics
    jurisdictions_count INTEGER DEFAULT 0,
    school_districts_count INTEGER DEFAULT 0,
    nonprofits_count INTEGER DEFAULT 0,
    events_count INTEGER DEFAULT 0,
    bills_count INTEGER DEFAULT 0,
    contacts_count INTEGER DEFAULT 0,
    
    -- Financial aggregates (from nonprofit data)
    total_revenue BIGINT DEFAULT 0,
    total_assets BIGINT DEFAULT 0,
    
    -- Metadata
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Unique constraint on geographic level
    UNIQUE (level, state_code, county, city)
);

-- Indexes for fast lookups by geography
CREATE INDEX idx_stats_level ON stats_aggregates(level);
CREATE INDEX idx_stats_state_code ON stats_aggregates(state_code) WHERE state_code IS NOT NULL;
CREATE INDEX idx_stats_state ON stats_aggregates(state) WHERE state IS NOT NULL;
CREATE INDEX idx_stats_state_county ON stats_aggregates(state_code, county) WHERE county IS NOT NULL;
CREATE INDEX idx_stats_state_city ON stats_aggregates(state_code, city) WHERE city IS NOT NULL;


-- ============================================================================
-- SEARCH-OPTIMIZED TABLES
-- Denormalized for fast full-text search
-- ============================================================================

-- Nonprofits search table (most frequently searched)
CREATE TABLE nonprofits_search (
    ein VARCHAR(20) PRIMARY KEY,
    name TEXT NOT NULL,
    street_address TEXT,
    city VARCHAR(100),
    state_code VARCHAR(2),        -- Two-letter state code (e.g., 'AL', 'MA')
    state VARCHAR(50),            -- Full state name (e.g., 'Alabama', 'Massachusetts')
    zip_code VARCHAR(10),
    county VARCHAR(100),
    
    -- Classification
    ntee_code VARCHAR(10),
    ntee_description TEXT,
    subsection_code VARCHAR(10),
    affiliation_code VARCHAR(10),
    classification_code VARCHAR(20),
    
    -- Financial (most recent year)
    revenue BIGINT,
    assets BIGINT,
    income BIGINT,
    
    -- Status
    ruling_date DATE,
    foundation_code VARCHAR(10),
    pf_filing_requirement_code VARCHAR(10),
    accounting_period VARCHAR(10),
    asset_code VARCHAR(10),
    income_code VARCHAR(10),
    filing_requirement_code VARCHAR(10),
    exempt_organization_status_code VARCHAR(10),
    tax_period VARCHAR(10),
    asset_amount BIGINT,
    income_amount BIGINT,
    form_990_revenue_amount BIGINT,
    
    -- Metadata
    source VARCHAR(50) DEFAULT 'irs_bmf',
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Full-text search indexes
CREATE INDEX idx_nonprofits_name_search ON nonprofits_search USING GIN (to_tsvector('english', name));
CREATE INDEX idx_nonprofits_state_code ON nonprofits_search(state_code);
CREATE INDEX idx_nonprofits_state ON nonprofits_search(state);
CREATE INDEX idx_nonprofits_city_state ON nonprofits_search(city, state_code);
CREATE INDEX idx_nonprofits_county ON nonprofits_search(county);
CREATE INDEX idx_nonprofits_ntee ON nonprofits_search(ntee_code);
CREATE INDEX idx_nonprofits_zip ON nonprofits_search(zip_code);


-- Jurisdictions search table (cities, counties, townships)
CREATE TABLE jurisdictions_search (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    type VARCHAR(50) NOT NULL,  -- 'city', 'county', 'township', 'school_district'
    state_code VARCHAR(2) NOT NULL,  -- Two-letter state code (e.g., 'AL', 'MA')
    state VARCHAR(50) NOT NULL,      -- Full state name (e.g., 'Alabama', 'Massachusetts')
    county VARCHAR(100),
    
    -- Geographic identifiers
    geoid VARCHAR(20),
    fips_code VARCHAR(20),
    
    -- Population/size
    population INTEGER,
    area_sq_miles DECIMAL(12, 2),
    
    -- Metadata
    source VARCHAR(50) DEFAULT 'census',
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Unique constraint
    UNIQUE (name, type, state_code, county)
);

CREATE INDEX idx_jurisdictions_name_search ON jurisdictions_search USING GIN (to_tsvector('english', name));
CREATE INDEX idx_jurisdictions_state_code ON jurisdictions_search(state_code);
CREATE INDEX idx_jurisdictions_state ON jurisdictions_search(state);
CREATE INDEX idx_jurisdictions_type ON jurisdictions_search(type);
CREATE INDEX idx_jurisdictions_state_type ON jurisdictions_search(state_code, type);


-- Contacts search table (nonprofit officers, legislators, etc.)
CREATE TABLE contacts_search (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    title VARCHAR(200),
    organization_name TEXT,
    organization_ein VARCHAR(20),
    
    -- Contact info
    email VARCHAR(255),
    phone VARCHAR(50),
    
    -- Address
    street_address TEXT,
    city VARCHAR(100),
    state_code VARCHAR(2),        -- Two-letter state code (e.g., 'AL', 'MA')
    state VARCHAR(50),            -- Full state name (e.g., 'Alabama', 'Massachusetts')
    zip_code VARCHAR(10),
    
    -- Role/classification
    role_type VARCHAR(50),  -- 'officer', 'legislator', 'board_member', etc.
    compensation BIGINT,
    hours_per_week DECIMAL(5, 1),
    
    -- Metadata
    source VARCHAR(50) DEFAULT 'irs_990',
    tax_year INTEGER,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_contacts_name_search ON contacts_search USING GIN (to_tsvector('english', name));
CREATE INDEX idx_contacts_org_name_search ON contacts_search USING GIN (to_tsvector('english', organization_name));
CREATE INDEX idx_contacts_state_code ON contacts_search(state_code);
CREATE INDEX idx_contacts_state ON contacts_search(state);
CREATE INDEX idx_contacts_ein ON contacts_search(organization_ein);
CREATE INDEX idx_contacts_role ON contacts_search(role_type);


-- Events search table (meetings, hearings, events)
CREATE TABLE events_search (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    event_date DATE,
    event_time TIME,
    
    -- Organization
    jurisdiction_id VARCHAR(50),
    channel_id VARCHAR(50),          -- YouTube channel ID for per-channel tracking
    jurisdiction_name VARCHAR(200),
    jurisdiction_type VARCHAR(50),
    state_code VARCHAR(2),        -- Two-letter state code (e.g., 'AL', 'MA')
    state VARCHAR(50),            -- Full state name (e.g., 'Alabama', 'Massachusetts')
    city VARCHAR(100),
    
    -- Meeting details
    location TEXT,
    meeting_type VARCHAR(100),
    status VARCHAR(50),
    
    -- Documents/links
    agenda_url TEXT,
    minutes_url TEXT,
    video_url TEXT UNIQUE,        -- Unique constraint prevents duplicate videos
    
    -- Metadata
    source VARCHAR(50) DEFAULT 'legistar',
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_events_title_search ON events_search USING GIN (to_tsvector('english', title));
CREATE INDEX idx_events_date ON events_search(event_date DESC);
CREATE INDEX idx_events_state_code ON events_search(state_code);
CREATE INDEX idx_events_state ON events_search(state);
CREATE INDEX idx_events_jurisdiction ON events_search(jurisdiction_name);
CREATE INDEX idx_events_jurisdiction_id ON events_search(jurisdiction_id);
CREATE INDEX idx_events_channel_id ON events_search(channel_id);
CREATE INDEX idx_events_date_state ON events_search(event_date, state_code);


-- Events text search table (video transcripts)
CREATE TABLE events_text_search (
    id SERIAL PRIMARY KEY,
    event_id INTEGER REFERENCES events_search(id) ON DELETE CASCADE,
    video_id VARCHAR(20) NOT NULL UNIQUE,
    raw_text TEXT,
    segments JSONB,  -- Structured transcript with timestamps: [{"text": "...", "start": 0.0, "duration": 2.5}, ...]
    language VARCHAR(10),
    is_auto_generated BOOLEAN DEFAULT FALSE,
    transcript_source VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_events_text_event_id ON events_text_search(event_id);
CREATE INDEX idx_events_text_video_id ON events_text_search(video_id);
CREATE INDEX idx_events_text_search_gin ON events_text_search USING GIN (to_tsvector('english', COALESCE(raw_text, '')));


-- Bills search table (legislative bills from all states)
CREATE TABLE bills_search (
    id SERIAL PRIMARY KEY,
    bill_id VARCHAR(255) UNIQUE NOT NULL,
    bill_number VARCHAR(50) NOT NULL,
    title TEXT NOT NULL,
    
    -- Classification
    classification VARCHAR(100),  -- 'bill', 'resolution', etc.
    
    -- Session info
    session VARCHAR(50),
    session_name TEXT,
    jurisdiction_name VARCHAR(200),
    state_code VARCHAR(2),        -- Two-letter state code (e.g., 'AL', 'MA')
    state VARCHAR(50),            -- Full state name (e.g., 'Alabama', 'Massachusetts'),
    
    -- Dates
    first_action_date DATE,
    latest_action_date DATE,
    latest_action_description TEXT,
    
    -- Content
    abstract TEXT,
    source_url TEXT,
    
    -- Metadata
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    last_synced TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_bills_title_search ON bills_search USING GIN (to_tsvector('english', title));
CREATE INDEX idx_bills_abstract_search ON bills_search USING GIN (to_tsvector('english', COALESCE(abstract, '')));
CREATE INDEX idx_bills_number ON bills_search(bill_number);
CREATE INDEX idx_bills_state_code ON bills_search(state_code);
CREATE INDEX idx_bills_state ON bills_search(state);
CREATE INDEX idx_bills_session ON bills_search(session);
CREATE INDEX idx_bills_latest_action_date ON bills_search(latest_action_date DESC);
CREATE INDEX idx_bills_state_session ON bills_search(state_code, session);


-- ============================================================================
-- REFERENCE DATA TABLES
-- Lookup tables for causes, NTEE codes, etc.
-- ============================================================================

CREATE TABLE reference_causes (
    id SERIAL PRIMARY KEY,
    cause_slug VARCHAR(100) UNIQUE NOT NULL,
    cause_name TEXT NOT NULL,
    description TEXT,
    parent_category VARCHAR(100),
    
    -- Metadata
    source VARCHAR(50) DEFAULT 'everyorg',
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_causes_slug ON reference_causes(cause_slug);
CREATE INDEX idx_causes_name_search ON reference_causes USING GIN (to_tsvector('english', cause_name));


CREATE TABLE reference_ntee_codes (
    code VARCHAR(10) PRIMARY KEY,
    description TEXT NOT NULL,
    category VARCHAR(50),
    subcategory VARCHAR(100),
    
    -- Metadata
    source VARCHAR(50) DEFAULT 'irs',
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_ntee_description_search ON reference_ntee_codes USING GIN (to_tsvector('english', description));


-- ============================================================================
-- SYNC TRACKING TABLE
-- Track when data was last synced from parquet files
-- ============================================================================

CREATE TABLE last_sync (
    table_name VARCHAR(100) PRIMARY KEY,
    last_sync_time TIMESTAMP NOT NULL,
    records_synced INTEGER DEFAULT 0,
    sync_status VARCHAR(50) DEFAULT 'success',
    error_message TEXT
);


-- ============================================================================
-- HELPER VIEWS FOR COMMON QUERIES
-- ============================================================================

-- Active nonprofits with basic info
CREATE VIEW nonprofits_active AS
SELECT 
    ein,
    name,
    city,
    state,
    ntee_code,
    ntee_description,
    revenue,
    assets
FROM nonprofits_search
WHERE exempt_organization_status_code IS NULL 
   OR exempt_organization_status_code NOT IN ('T', 'X')  -- Exclude terminated
ORDER BY revenue DESC NULLS LAST;


-- Recent events (last 30 days + upcoming)
CREATE VIEW events_recent AS
SELECT 
    id,
    title,
    description,
    event_date,
    jurisdiction_name,
    state,
    city,
    status,
    agenda_url
FROM events_search
WHERE event_date >= CURRENT_DATE - INTERVAL '30 days'
ORDER BY event_date DESC;


-- Top nonprofits by state
CREATE VIEW nonprofits_top_by_state AS
SELECT 
    state,
    ein,
    name,
    city,
    revenue,
    ROW_NUMBER() OVER (PARTITION BY state ORDER BY revenue DESC NULLS LAST) as rank
FROM nonprofits_search
WHERE revenue IS NOT NULL
ORDER BY state, rank;


-- ============================================================================
-- GRANT PERMISSIONS (adjust as needed for your user)
-- ============================================================================

-- Grant SELECT to your application user if needed
-- GRANT SELECT ON ALL TABLES IN SCHEMA public TO your_app_user;
-- GRANT SELECT ON ALL SEQUENCES IN SCHEMA public TO your_app_user;
