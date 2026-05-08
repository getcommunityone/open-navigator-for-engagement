{{ config(
    materialized='view',
    tags=['intermediate', 'localview', 'jurisdictions']
) }}

/*
Map LocalView jurisdictions (place_name + state) onto Census Gazetteer place GEOIDs,
and then onto counties via the place→county crosswalk.

Primary target is municipalities (places). Fallback to school districts when a
place match is not found.
*/

WITH localview_places AS (
    SELECT DISTINCT
        e.state_code,
        e.jurisdiction_name AS place_name_raw
    FROM {{ source('bronze', 'bronze_events_localview') }} e
    WHERE e.state_code IS NOT NULL
      AND e.jurisdiction_name IS NOT NULL
),

normalized AS (
    SELECT
        state_code,
        place_name_raw,
        LOWER(
            REGEXP_REPLACE(
                REGEXP_REPLACE(TRIM(place_name_raw), '\\s+(city|town|village|borough|cdp|county)$', '', 1, 0, 'i'),
                '\\s+(?:town|city)\\s*', ' ', 1, 0, 'i'
            )
        ) AS place_name_clean
    FROM localview_places
),

muni_norm AS (
    SELECT
        m.geoid AS place_geoid,
        m.usps  AS state_code,
        m.name  AS muni_name_raw,
        LOWER(
            REGEXP_REPLACE(
                REGEXP_REPLACE(TRIM(m.name), '\\s+(city|town|village|borough|cdp|county)$', '', 1, 0, 'i'),
                '\\s+(?:town|city)\\s*', ' ', 1, 0, 'i'
            )
        ) AS muni_name_clean,
        m.aland_sqmi
    FROM {{ source('bronze', 'bronze_jurisdictions_municipalities') }} m
),

sd_norm AS (
    SELECT
        sd.geoid AS school_district_geoid,
        sd.usps  AS state_code,
        sd.name  AS sd_name_raw,
        LOWER(TRIM(sd.name)) AS sd_name_clean
    FROM {{ source('bronze', 'bronze_jurisdictions_school_districts') }} sd
),

muni_matches AS (
    SELECT
        n.state_code,
        n.place_name_raw,
        n.place_name_clean,
        mn.place_geoid,
        'municipality'::TEXT AS matched_type,
        ROW_NUMBER() OVER (
            PARTITION BY n.state_code, n.place_name_clean
            ORDER BY mn.aland_sqmi DESC NULLS LAST
        ) AS rn
    FROM normalized n
    JOIN muni_norm mn
      ON mn.state_code = n.state_code
     AND mn.muni_name_clean = n.place_name_clean
),

best_muni AS (
    SELECT * FROM muni_matches WHERE rn = 1
),

sd_matches AS (
    SELECT
        n.state_code,
        n.place_name_raw,
        n.place_name_clean,
        sn.school_district_geoid,
        'school_district'::TEXT AS matched_type,
        ROW_NUMBER() OVER (
            PARTITION BY n.state_code, n.place_name_clean
            ORDER BY sn.school_district_geoid
        ) AS rn
    FROM normalized n
    JOIN sd_norm sn
      ON sn.state_code = n.state_code
     AND sn.sd_name_clean = n.place_name_clean
),

best_sd AS (
    SELECT * FROM sd_matches WHERE rn = 1
),

resolved AS (
    SELECT
        n.state_code,
        n.place_name_raw,
        n.place_name_clean,
        bm.place_geoid,
        NULL::VARCHAR(7) AS school_district_geoid,
        bm.matched_type
    FROM normalized n
    LEFT JOIN best_muni bm
      ON bm.state_code = n.state_code
     AND bm.place_name_clean = n.place_name_clean

    UNION ALL

    SELECT
        n.state_code,
        n.place_name_raw,
        n.place_name_clean,
        NULL::VARCHAR(7) AS place_geoid,
        bs.school_district_geoid,
        bs.matched_type
    FROM normalized n
    LEFT JOIN best_muni bm
      ON bm.state_code = n.state_code
     AND bm.place_name_clean = n.place_name_clean
    JOIN best_sd bs
      ON bs.state_code = n.state_code
     AND bs.place_name_clean = n.place_name_clean
    WHERE bm.place_geoid IS NULL
),

place_counties AS (
    SELECT
        r.state_code,
        r.place_name_raw,
        r.place_name_clean,
        r.place_geoid,
        r.school_district_geoid,
        r.matched_type,
        pc.county_geoid,
        pc.is_primary,
        pc.overlap_pct
    FROM resolved r
    LEFT JOIN {{ source('bronze', 'bronze_jurisdictions_place_county') }} pc
      ON r.place_geoid = pc.place_geoid
)

SELECT
    state_code,
    place_name_raw,
    place_name_clean,
    place_geoid,
    school_district_geoid,
    matched_type,
    MAX(CASE WHEN is_primary THEN county_geoid END) AS primary_county_geoid,
    ARRAY_AGG(county_geoid ORDER BY overlap_pct DESC NULLS LAST) FILTER (WHERE county_geoid IS NOT NULL) AS county_geoids
FROM place_counties
GROUP BY 1,2,3,4,5,6

