{{
    config(
        materialized='incremental',
        unique_key='id',
        on_schema_change='sync_all_columns'
    )
}}

/*
    contacts_search production table
    
    Merges:
    - AI-extracted contacts from bronze (gemini_ai_extraction)
    - OpenStates legislators (openstates_api) - loaded separately
    - IRS 990 nonprofit officers (irs_990) - loaded separately
    
    Strategy:
    - Don't override authoritative sources with AI data
    - Insert new AI contacts with confidence_score = 0.60
    - Flag fuzzy matches for review
*/

WITH bronze_contacts AS (
    SELECT * FROM {{ ref('int_contacts_deduped') }}
),

-- Get existing authoritative contacts to avoid duplicates
existing_authoritative AS (
    SELECT 
        id,
        name,
        {{ normalize_name('name') }} as name_normalized,
        datasource,
        datasource_id,
        organization_name,
        last_updated
    FROM contacts_search
    WHERE datasource IN {{ var('authoritative_sources') }}
),

-- New AI contacts that don't conflict with authoritative sources
new_ai_contacts AS (
    SELECT
        -- Contact info
        bc.full_name as name,
        bc.role as title,
        bc.org_id as organization_name,
        NULL::VARCHAR as organization_ein,
        
        -- Contact details (not yet extracted from transcripts)
        NULL::VARCHAR as email,
        NULL::VARCHAR as phone,
        NULL::TEXT as street_address,
        NULL::VARCHAR as city,
        NULL::VARCHAR as state_code,
        NULL::VARCHAR as state,
        NULL::VARCHAR as zip_code,
        
        -- Role classification
        CASE 
            WHEN bc.is_lobbyist THEN 'lobbyist'
            WHEN bc.role ILIKE '%mayor%' THEN 'government_official'
            WHEN bc.role ILIKE '%council%' THEN 'government_official'
            WHEN bc.role ILIKE '%commissioner%' THEN 'government_official'
            ELSE 'other'
        END as role_type,
        
        -- Compensation info (not available in bronze)
        NULL::BIGINT as compensation,
        NULL::DECIMAL as hours_per_week,
        
        -- Source tracking
        'gemini_ai_extraction'::VARCHAR as datasource,
        COALESCE(bc.wikidata_qid, bc.openstates_person_id)::VARCHAR as datasource_id,
        {{ calculate_confidence("'gemini_ai_extraction'") }} as confidence_score,
        FALSE as verified,
        FALSE as needs_review,
        NULL::TIMESTAMP as verification_date,
        NULL::TEXT as review_notes,
        
        -- Metadata
        CURRENT_TIMESTAMP as last_updated,
        
        -- For incremental processing
        bc.extracted_at
        
    FROM bronze_contacts bc
    LEFT JOIN existing_authoritative ea
        ON {{ normalize_name('bc.full_name') }} = ea.name_normalized
    WHERE ea.id IS NULL  -- No match with authoritative sources
    
    {% if is_incremental() %}
    -- Only process new extractions
    AND bc.extracted_at > (SELECT COALESCE(MAX(last_updated), '1970-01-01') FROM {{ this }})
    {% endif %}
)

SELECT 
    {{ dbt_utils.generate_surrogate_key(['name', 'organization_name', 'datasource']) }} as id,
    *
FROM new_ai_contacts
