-- GSA domain_type values seen in bronze that are not in int_jurisdiction_websites domain_type_map
-- (excludes federal rows filtered in int_jurisdiction_websites). Use to extend the VALUES map.
-- Run: dbt compile --select analysis:audit_gsa_domain_types_not_in_map  then run compiled SQL in warehouse.

WITH domain_type_map(gsa_domain_type) AS (
    SELECT * FROM (VALUES
        ('City'),
        ('Town'),
        ('Village'),
        ('Borough'),
        ('County'),
        ('State'),
        ('School District'),
        ('Township')
    ) AS t(gsa_domain_type)
),
bronze_local AS (
    SELECT DISTINCT TRIM(domain_type) AS domain_type
    FROM {{ source('bronze', 'bronze_gov_domains') }}
    WHERE domain_name IS NOT NULL
      AND TRIM(domain_name) <> ''
      AND (
          domain_type IS NULL
          OR TRIM(domain_type) NOT IN (
              'Federal Agency',
              'Federal Agency - Executive',
              'Federal Agency - Legislative',
              'Federal Agency - Judicial'
          )
      )
)
SELECT
    b.domain_type,
    COUNT(*) AS row_count
FROM bronze_local b
LEFT JOIN domain_type_map m
    ON UPPER(TRIM(b.domain_type)) = UPPER(TRIM(m.gsa_domain_type))
WHERE m.gsa_domain_type IS NULL
  AND b.domain_type IS NOT NULL
  AND TRIM(b.domain_type) <> ''
GROUP BY 1
ORDER BY row_count DESC, 1;
