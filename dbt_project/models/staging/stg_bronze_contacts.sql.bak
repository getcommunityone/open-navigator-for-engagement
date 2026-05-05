{{
    config(
        materialized='view'
    )
}}

/*
    Staging model for bronze_contacts
    
    - Cleans and normalizes contact names
    - Filters out invalid records
    - Prepares for entity resolution
*/

WITH source AS (
    SELECT * FROM {{ source('bronze', 'bronze_contacts') }}
),

cleaned AS (
    SELECT
        id as bronze_contact_id,
        source_event_id,
        source_ai_model,
        person_id,
        
        -- Name fields
        full_name,
        LOWER(TRIM(full_name)) as full_name_normalized,
        REGEXP_REPLACE(LOWER(TRIM(full_name)), '[^a-z0-9 ]', '', 'g') as full_name_alphanumeric,
        
        -- Role and organization
        role,
        org_id,
        
        -- Party and lobbying info
        party_affiliation,
        is_lobbyist,
        lobbyist_registration_number,
        lobbyist_clients,
        
        -- External identifiers
        wikidata_qid,
        person_id as openstates_person_id,
        
        -- Meeting context
        appeared_as,
        
        -- Metadata
        extracted_at
        
    FROM source
    
    WHERE 1=1
        -- Filter out invalid names
        AND full_name IS NOT NULL
        AND LENGTH(TRIM(full_name)) > 3
        AND full_name NOT ILIKE '%test%'
        AND full_name NOT ILIKE '%unknown%'
        
        -- Must have some identifying info
        AND (
            wikidata_qid IS NOT NULL
            OR person_id IS NOT NULL
            OR org_id IS NOT NULL
            OR role IS NOT NULL
        )
)

SELECT * FROM cleaned
