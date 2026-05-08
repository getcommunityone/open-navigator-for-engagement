#!/usr/bin/env python3
"""
Backfill LocalView YouTube video → channel mapping into an intermediate table.

Creates/updates: intermediate.int_localview_youtube_video_channels

This is intentionally NOT written back onto bronze.bronze_events_localview. The
bronze table should store raw event metadata; derived YouTube attributes live in
intermediate.

How it works:
- Reads LocalView video IDs from bronze.bronze_events_localview.datasource_id
- Calls YouTube videos API (part=snippet) in batches of 50
- Upserts channel_id/channel_title into intermediate.int_localview_youtube_video_channels

Requirements:
- Run inside the repo venv (so google-api-python-client is available)
- Set YOUTUBE_API_KEY in environment (.env is fine)
"""

import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Iterable, List, Dict, Optional

import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from loguru import logger  # type: ignore
except ModuleNotFoundError:  # pragma: no cover
    import logging

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    logger = logging.getLogger("localview_youtube_channel_map")


load_dotenv()

DATABASE_URL = os.getenv(
    "NEON_DATABASE_URL_DEV",
    "postgresql://postgres:password@localhost:5433/open_navigator",
)
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")


CREATE_TABLE_SQL = """
CREATE SCHEMA IF NOT EXISTS intermediate;

CREATE TABLE IF NOT EXISTS intermediate.int_localview_youtube_video_channels (
    video_id       VARCHAR(255) PRIMARY KEY,
    youtube_url    TEXT,
    channel_id     VARCHAR(255) NOT NULL,
    channel_title  VARCHAR(500),
    fetched_at     TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_ilvyvc_channel_id
  ON intermediate.int_localview_youtube_video_channels(channel_id);
"""


DROP_BRONZE_CHANNEL_ID_SQL = """
DO $$
BEGIN
  IF EXISTS (
    SELECT 1
    FROM information_schema.columns
    WHERE table_schema = 'bronze'
      AND table_name = 'bronze_events_localview'
      AND column_name = 'channel_id'
  ) THEN
    ALTER TABLE bronze.bronze_events_localview DROP COLUMN channel_id;
  END IF;
END $$;
"""


def chunked(xs: List[str], n: int) -> Iterable[List[str]]:
    for i in range(0, len(xs), n):
        yield xs[i : i + n]


def get_missing_video_ids(conn, limit: int) -> List[str]:
    cur = conn.cursor()
    cur.execute(
        """
        SELECT DISTINCT e.datasource_id
        FROM bronze.bronze_events_localview e
        LEFT JOIN intermediate.int_localview_youtube_video_channels m
          ON e.datasource_id = m.video_id
        WHERE e.datasource = 'localview'
          AND e.datasource_id IS NOT NULL
          AND e.datasource_id != ''
          AND m.video_id IS NULL
        LIMIT %s
        """,
        (limit,),
    )
    rows = cur.fetchall()
    cur.close()
    return [r[0] for r in rows]


def fetch_video_snippets(video_ids: List[str]) -> Dict[str, Dict[str, Optional[str]]]:
    if not YOUTUBE_API_KEY:
        raise RuntimeError("Missing YOUTUBE_API_KEY in environment")

    from googleapiclient.discovery import build  # imported lazily

    youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)

    out: Dict[str, Dict[str, Optional[str]]] = {}
    for batch in chunked(video_ids, 50):
        resp = (
            youtube.videos()
            .list(part="snippet", id=",".join(batch), maxResults=len(batch))
            .execute()
        )
        for item in resp.get("items", []):
            vid = item.get("id")
            snippet = item.get("snippet", {}) or {}
            out[vid] = {
                "channel_id": snippet.get("channelId"),
                "channel_title": snippet.get("channelTitle"),
            }

    return out


def upsert_mappings(conn, mappings: List[Dict[str, Optional[str]]]) -> int:
    if not mappings:
        return 0

    rows = [
        (
            m["video_id"],
            m.get("youtube_url"),
            m["channel_id"],
            m.get("channel_title"),
            datetime.now(),
        )
        for m in mappings
        if m.get("video_id") and m.get("channel_id")
    ]
    if not rows:
        return 0

    cur = conn.cursor()
    execute_values(
        cur,
        """
        INSERT INTO intermediate.int_localview_youtube_video_channels
          (video_id, youtube_url, channel_id, channel_title, fetched_at)
        VALUES %s
        ON CONFLICT (video_id) DO UPDATE SET
          youtube_url = COALESCE(EXCLUDED.youtube_url, intermediate.int_localview_youtube_video_channels.youtube_url),
          channel_id = EXCLUDED.channel_id,
          channel_title = COALESCE(EXCLUDED.channel_title, intermediate.int_localview_youtube_video_channels.channel_title),
          fetched_at = EXCLUDED.fetched_at
        """,
        rows,
        page_size=500,
    )
    conn.commit()
    n = cur.rowcount
    cur.close()
    return n


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Backfill LocalView video→channel mapping table")
    parser.add_argument("--limit", type=int, default=5000, help="Max LocalView video IDs to fetch this run")
    parser.add_argument("--drop-bronze-channel-id", action="store_true", help="Drop bronze.bronze_events_localview.channel_id if present")
    args = parser.parse_args()

    logger.info("Connecting to database…")
    conn = psycopg2.connect(DATABASE_URL)
    logger.success("✓ Connected")

    try:
        cur = conn.cursor()
        cur.execute(CREATE_TABLE_SQL)
        conn.commit()
        cur.close()

        if args.drop_bronze_channel_id:
            logger.warning("Dropping bronze.bronze_events_localview.channel_id (if exists)…")
            cur = conn.cursor()
            cur.execute(DROP_BRONZE_CHANNEL_ID_SQL)
            conn.commit()
            cur.close()

        missing = get_missing_video_ids(conn, limit=args.limit)
        logger.info(f"Missing mappings to fetch: {len(missing):,}")
        if not missing:
            return 0

        logger.info("Calling YouTube videos API…")
        snippets = fetch_video_snippets(missing)

        mappings: List[Dict[str, Optional[str]]] = []
        for vid in missing:
            s = snippets.get(vid)
            if not s:
                continue
            channel_id = s.get("channel_id")
            if not channel_id:
                continue
            mappings.append(
                {
                    "video_id": vid,
                    "youtube_url": f"https://www.youtube.com/watch?v={vid}",
                    "channel_id": channel_id,
                    "channel_title": s.get("channel_title"),
                }
            )

        n = upsert_mappings(conn, mappings)
        logger.success(f"✓ Upserted {n:,} video→channel mappings")
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    raise SystemExit(main())

