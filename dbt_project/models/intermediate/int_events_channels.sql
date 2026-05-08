{{ config(
    materialized='table',
    tags=['intermediate', 'youtube', 'channels']
) }}

/*
Intermediate model: derived channel registry.

`bronze_events_channels` is not guaranteed to exist in all environments.
Instead, derive the set of channels from `bronze_events_localview` and enrich
with any available metadata from `bronze_events_youtube`.
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

    -- Jurisdiction associations (JSONB)
    NULL::JSONB   AS jurisdictions,

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
