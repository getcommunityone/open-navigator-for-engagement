-- Add mayor-related columns to jurisdictions_details_search

ALTER TABLE jurisdictions_details_search 
ADD COLUMN IF NOT EXISTS current_mayor VARCHAR(200),
ADD COLUMN IF NOT EXISTS mayor_election_date DATE,
ADD COLUMN IF NOT EXISTS usmayors_last_updated TIMESTAMP;

CREATE INDEX IF NOT EXISTS idx_jurisdictions_details_current_mayor 
ON jurisdictions_details_search(current_mayor) WHERE current_mayor IS NOT NULL;

COMMENT ON COLUMN jurisdictions_details_search.current_mayor IS 'Current or incoming mayor name from USCM election results';
COMMENT ON COLUMN jurisdictions_details_search.mayor_election_date IS 'Date of most recent mayoral election';
COMMENT ON COLUMN jurisdictions_details_search.usmayors_last_updated IS 'Last update from U.S. Conference of Mayors data';
