-- High-level GSA mapping coverage by state (matched vs null jurisdiction_id).
-- Run after: dbt run --select int_jurisdiction_websites

SELECT
    state_code,
    COUNT(*) FILTER (WHERE jurisdiction_id IS NOT NULL) AS gsa_matched,
    COUNT(*) FILTER (WHERE jurisdiction_id IS NULL) AS gsa_unmapped,
    COUNT(*) AS gsa_rows
FROM {{ ref('int_jurisdiction_websites') }}
WHERE website_source = 'gsa'
GROUP BY 1
ORDER BY gsa_unmapped DESC, state_code;
