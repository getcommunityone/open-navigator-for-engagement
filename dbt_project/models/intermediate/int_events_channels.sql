{{ config(
    materialized='table',
    tags=['intermediate', 'youtube', 'channels']
) }}

/*
Intermediate model: derived channel registry.

`bronze_events_channels` is not guaranteed to exist in all environments.
Instead, derive the set of channels from `bronze_events_localview` and enrich
with any available metadata from `bronze_events_youtube`.

`jurisdictions` JSONB: distinct `intermediate.int_jurisdictions` rows matched via
`int_localview_channel_geography` (place / school district / township / county GEOIDs).
Shape matches Python loaders: jurisdiction_id, jurisdiction_name, state_code, state,
jurisdiction_type, geoid.
*/

WITH base_channels AS (
    SELECT DISTINCT
        channel_id
    FROM {{ ref('int_events_localview') }}
    WHERE channel_id IS NOT NULL
      AND channel_id != ''
),

youtube_meta AS (
    SELECT
        channel_id,
        MAX(channel_url)  AS channel_url,
        MAX(channel_type) AS channel_type,
        MAX(last_updated) AS last_updated
    FROM {{ source('bronze', 'bronze_events_youtube') }}
    WHERE channel_id IS NOT NULL
      AND channel_id != ''
    GROUP BY channel_id
),

localview_meta AS (
    SELECT
        channel_id,
        MAX(loaded_at) AS loaded_at
    FROM {{ ref('int_events_localview') }}
    WHERE channel_id IS NOT NULL
      AND channel_id != ''
    GROUP BY channel_id
),

/*
Expand LocalView channel geography to typed GEOIDs, then resolve canonical
jurisdiction_id (e.g. municipality_0607500) from int_jurisdictions.
*/
channel_geoid_candidates AS (
    SELECT DISTINCT
        lg.channel_id,
        lg.state_code,
        'municipality'::TEXT    AS jurisdiction_type,
        lg.place_geoid::TEXT    AS geoid
    FROM {{ ref('int_localview_channel_geography') }} lg
    WHERE lg.place_geoid IS NOT NULL
      AND BTRIM(lg.place_geoid::TEXT) != ''

    UNION

    SELECT DISTINCT
        lg.channel_id,
        lg.state_code,
        'school_district'::TEXT,
        lg.school_district_geoid::TEXT
    FROM {{ ref('int_localview_channel_geography') }} lg
    WHERE lg.school_district_geoid IS NOT NULL
      AND BTRIM(lg.school_district_geoid::TEXT) != ''

    UNION

    SELECT DISTINCT
        lg.channel_id,
        lg.state_code,
        'township'::TEXT,
        lg.township_geoid::TEXT
    FROM {{ ref('int_localview_channel_geography') }} lg
    WHERE lg.township_geoid IS NOT NULL
      AND BTRIM(lg.township_geoid::TEXT) != ''

    UNION

    SELECT DISTINCT
        lg.channel_id,
        lg.state_code,
        'county'::TEXT,
        lg.primary_county_geoid::TEXT
    FROM {{ ref('int_localview_channel_geography') }} lg
    WHERE lg.primary_county_geoid IS NOT NULL
      AND BTRIM(lg.primary_county_geoid::TEXT) != ''

    UNION

    SELECT DISTINCT
        lg.channel_id,
        lg.state_code,
        'county'::TEXT,
        u.c_geoid::TEXT
    FROM {{ ref('int_localview_channel_geography') }} lg
    CROSS JOIN LATERAL unnest(lg.county_geoids) AS u(c_geoid)
    WHERE lg.county_geoids IS NOT NULL
      AND CARDINALITY(lg.county_geoids) > 0
),

channel_jurisdictions AS (
    SELECT DISTINCT
        cgc.channel_id,
        j.jurisdiction_id,
        j.name              AS jurisdiction_name,
        j.state_code,
        j.state,
        j.jurisdiction_type,
        j.geoid
    FROM channel_geoid_candidates cgc
    INNER JOIN {{ ref('int_jurisdictions') }} j
        ON j.state_code = cgc.state_code
       AND j.geoid = cgc.geoid
       AND j.jurisdiction_type = cgc.jurisdiction_type
),

jurisdictions_by_channel AS (
    SELECT
        channel_id,
        jsonb_agg(
            jsonb_build_object(
                'jurisdiction_id',       jurisdiction_id,
                'jurisdiction_name',     jurisdiction_name,
                'state_code',            state_code,
                'state',                 state,
                'jurisdiction_type',     jurisdiction_type,
                'geoid',                 geoid
            )
            ORDER BY jurisdiction_id
        ) AS jurisdictions,
        array_agg(jurisdiction_id ORDER BY jurisdiction_id) AS jurisdiction_ids
    FROM channel_jurisdictions
    GROUP BY channel_id
)

SELECT
    bc.channel_id AS id,
    bc.channel_id,
    ym.channel_url,
    NULL::TEXT    AS channel_title,
    ym.channel_type,
    NULL::BIGINT  AS subscriber_count,
    NULL::BIGINT  AS video_count,

    -- Source flags (which datasets validate this channel)
    TRUE          AS in_localview,
    FALSE         AS in_jurisdictions_details,
    FALSE         AS on_public_website,
    FALSE         AS in_wikidata,

    -- Discovery information
    'derived_from_localview'::TEXT AS discovery_method,
    NULL::DATE                    AS discovery_date,
    0.85::DOUBLE PRECISION        AS confidence_score,

    -- Jurisdiction associations (JSONB array of resolved int_jurisdictions rows)
    jbc.jurisdictions,
    jbc.jurisdiction_ids,

    -- Quality indicators
    NULL::BOOLEAN AS is_verified,
    NULL::BOOLEAN AS is_government,
    FALSE         AS flagged_as_junk,
    NULL::TEXT    AS flag_reason,

    -- Timestamps
    lm.loaded_at,
    COALESCE(ym.last_updated, lm.loaded_at) AS last_updated

FROM base_channels bc
LEFT JOIN youtube_meta ym ON bc.channel_id = ym.channel_id
LEFT JOIN localview_meta lm ON bc.channel_id = lm.channel_id
LEFT JOIN jurisdictions_by_channel jbc ON bc.channel_id = jbc.channel_id
