-- GSA .gov rows in int_jurisdiction_websites with no jurisdiction_id (after URL, name, and domain-stem logic).
-- Run after: dbt run --select int_jurisdiction_websites
-- Compile only: dbt compile --select audit_gsa_unmapped_domains

SELECT
    domain_name,
    domain_type,
    state_code,
    organization_name,
    agency,
    city,
    website_url
FROM {{ ref('int_jurisdiction_websites') }}
WHERE website_source = 'gsa'
  AND jurisdiction_id IS NULL
ORDER BY state_code, domain_type, domain_name;
