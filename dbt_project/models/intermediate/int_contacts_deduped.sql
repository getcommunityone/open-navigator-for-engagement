{{
    config(
        materialized='table'
    )
}}

/*
    Deduplicate bronze contacts
    
    Strategy:
    1. Group by normalized name + org
    2. Keep most recent extraction
    3. Prefer records with external IDs (Wikidata, OpenStates)
*/

WITH ranked_contacts AS (
    SELECT
        *,
        ROW_NUMBER() OVER (
            PARTITION BY 
                full_name_normalized,
                COALESCE(org_id, 'unknown')
            ORDER BY 
                -- Prefer records with external IDs
                CASE WHEN wikidata_qid IS NOT NULL THEN 1 ELSE 2 END,
                CASE WHEN openstates_person_id IS NOT NULL THEN 1 ELSE 2 END,
                -- Then most recent
                extracted_at DESC
        ) as row_num
    FROM {{ ref('stg_bronze_contacts') }}
)

SELECT 
    bronze_contact_id,
    source_event_id,
    source_ai_model,
    person_id,
    full_name,
    full_name_normalized,
    role,
    org_id,
    party_affiliation,
    is_lobbyist,
    lobbyist_registration_number,
    wikidata_qid,
    openstates_person_id,
    appeared_as,
    extracted_at
FROM ranked_contacts
WHERE row_num = 1
