{{ config(
    materialized='view',
    tags=['intermediate', 'localview', 'events']
) }}

/*
Intermediate model: LocalView events with derived channel_id.

`bronze_events_localview` should not carry derived YouTube channel identifiers.
Derive channel_id by joining:
- `intermediate.int_localview_youtube_video_channels` (video_id → channel_id) when present
- fallback: `bronze_events_youtube` (video_id → channel_id) when available
*/

SELECT
    e.event_id,
    e.event_date,
    e.jurisdiction_name,
    e.jurisdiction_type,
    e.city_name,
    e.state_code,
    e.state,
    e.meeting_type,
    e.title,
    e.video_url,
    COALESCE(m.channel_id, y.channel_id) AS channel_id,
    e.datasource,
    e.datasource_id,
    e.loaded_at
FROM {{ source('bronze', 'bronze_events_localview') }} e
LEFT JOIN intermediate.int_localview_youtube_video_channels m
    ON e.datasource_id = m.video_id
LEFT JOIN {{ source('bronze', 'bronze_events_youtube') }} y
    ON e.datasource_id = y.video_id
