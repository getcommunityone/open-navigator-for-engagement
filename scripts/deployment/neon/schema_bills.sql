-- Bills Map Aggregates Schema for Neon PostgreSQL
-- LIGHTWEIGHT: Only stores state-level aggregates (not full bills)
-- Saves ~99% storage: 5 rows vs 150K+ bills
--
-- Full bills remain in parquet files for drill-down queries

-- Drop table if exists
DROP TABLE IF EXISTS bills_map_aggregates CASCADE;

-- Map aggregates for fast choropleth visualization
CREATE TABLE bills_map_aggregates (
    id SERIAL PRIMARY KEY,
    state_code VARCHAR(2) NOT NULL,
    topic VARCHAR(100) DEFAULT 'all',
    total_bills INTEGER DEFAULT 0,
    
    -- Type counts (flattened for fast queries)
    type_bill INTEGER DEFAULT 0,
    type_resolution INTEGER DEFAULT 0,
    type_concurrent_resolution INTEGER DEFAULT 0,
    type_joint_resolution INTEGER DEFAULT 0,
    type_constitutional_amendment INTEGER DEFAULT 0,
    
    -- Status counts (simplified - we don't track status in current data)
    status_enacted INTEGER DEFAULT 0,
    status_failed INTEGER DEFAULT 0,
    status_pending INTEGER DEFAULT 0,
    
    -- Primary categorization
    primary_type VARCHAR(50),
    primary_status VARCHAR(50) DEFAULT 'pending',
    map_category VARCHAR(50),
    
    -- Sample bills (JSON array - limit to 3 per state to save space)
    sample_bills JSONB,
    
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    UNIQUE(state_code, topic)
);

CREATE INDEX idx_map_agg_state ON bills_map_aggregates(state_code);
CREATE INDEX idx_map_agg_topic ON bills_map_aggregates(topic);

-- Sync metadata (shared with other tables)
CREATE TABLE IF NOT EXISTS neon_sync_log (
    id SERIAL PRIMARY KEY,
    table_name VARCHAR(100) NOT NULL,
    rows_inserted INTEGER,
    rows_updated INTEGER,
    sync_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    status VARCHAR(50),
    error_message TEXT
);

-- Comments for documentation
COMMENT ON TABLE bills_map_aggregates IS 'Pre-aggregated state-level data for policy map (detailed bills in parquet)';
COMMENT ON COLUMN bills_map_aggregates.sample_bills IS 'JSON array of 3 sample bills per state for tooltips';
COMMENT ON COLUMN bills_map_aggregates.topic IS 'Bill topic filter (all, dental, health, etc.)';
