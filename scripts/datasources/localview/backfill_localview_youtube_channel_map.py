#!/usr/bin/env python3
"""
Backfill LocalView YouTube video → channel mapping into an intermediate table.

Creates/updates: intermediate.int_localview_youtube_video_channels

This is intentionally NOT written back onto bronze.bronze_events_localview. The
bronze table should store raw event metadata; derived YouTube attributes live in
intermediate.

How it works:
- Reads LocalView parquet files (which contain vid_id + channel_id directly)
- Upserts channel_id/channel_title into intermediate.int_localview_youtube_video_channels

Requirements:
- Parquet cache present under data/cache/localview (created by LocalView download step)
"""

import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Iterable, List, Dict, Optional, Tuple

import pandas as pd
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
LOCALVIEW_DIR = Path("data/cache/localview")


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


def extract_parquet_mappings(limit: int) -> List[Dict[str, Optional[str]]]:
    parquet_files = sorted(LOCALVIEW_DIR.glob("meetings.*.parquet"))
    if not parquet_files:
        raise FileNotFoundError(f"No parquet files found in {LOCALVIEW_DIR}")

    mappings: Dict[str, Tuple[Optional[str], Optional[str]]] = {}
    for pf in parquet_files:
        df = pd.read_parquet(pf, columns=["vid_id", "channel_id", "channel_title"])
        df = df[df["vid_id"].notna() & df["channel_id"].notna()].copy()
        if df.empty:
            continue

        for vid, ch_id, ch_title in zip(df["vid_id"], df["channel_id"], df["channel_title"]):
            if vid is None or ch_id is None:
                continue
            vid_s = str(vid).strip()
            ch_s = str(ch_id).strip()
            if not vid_s or not ch_s:
                continue
            if vid_s not in mappings:
                mappings[vid_s] = (ch_s, str(ch_title).strip() if ch_title is not None else None)

        if len(mappings) >= limit:
            break

    out: List[Dict[str, Optional[str]]] = []
    for vid, (ch_id, ch_title) in list(mappings.items())[:limit]:
        out.append(
            {
                "video_id": vid,
                "youtube_url": f"https://www.youtube.com/watch?v={vid}",
                "channel_id": ch_id,
                "channel_title": ch_title,
            }
        )
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

        logger.info("Extracting vid_id→channel_id mappings from LocalView parquet cache…")
        mappings = extract_parquet_mappings(limit=args.limit)
        logger.info(f"Mappings extracted: {len(mappings):,}")
        if not mappings:
            logger.warning("No mappings extracted (check parquet columns: vid_id/channel_id/channel_title).")
            return 0

        n = upsert_mappings(conn, mappings)
        logger.success(f"✓ Upserted {n:,} video→channel mappings")
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    raise SystemExit(main())

