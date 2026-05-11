#!/usr/bin/env python3
"""
Suggest (or optionally append) ``jurisdiction_website_url_overrides`` rows for counties whose
meetings scrape was **missing**, **failed** (zero HTML pages), or **shallow** (few pages).

Strategy (free tier, no paid APIs required for the core path):

1. Read targets from ``data/cache/scraped_meetings/{STATE}/county/*/`` manifests (or all AL FIPS
   with no folder when ``--mode`` includes ``missing``).
2. Load human county names from Postgres ``intermediate.int_jurisdictions``.
3. ``duckduckgo-search`` text search (DuckDuckGo HTML backend) for an official-site style query.
4. Prefer the first result whose host ends with ``.gov`` or ``.org`` and is not a generic blocklist
   (Wikipedia, Facebook, …). Light scoring boosts hosts that contain a slug derived from the
   county name.
5. Validate with ``httpx`` **HEAD** (fallback **GET** stream if HEAD is unsupported), optionally via
   ``WIKIDATA_HTTPS_PROXY`` (SOCKS5) when set — same knob as Wikidata loaders.
6. Optionally call **YouTube Data API v3** search when ``YOUTUBE_DATA_API_KEY`` is set (free quota)
   to capture a top meeting-ish video id/title for manual review context — not written to dbt.

Outputs a CSV under ``data/cache/enrichment/`` and optionally **appends** unique rows to
``dbt_project/seeds/jurisdiction_website_url_overrides.csv``. After append: run dbt seed + rebuild
``int_jurisdiction_websites`` (see repo dbt docs).

Examples::

    .venv/bin/python scripts/enrichment/enrich_jurisdiction_websites_search.py --state AL --dry-run

    WIKIDATA_HTTPS_PROXY=socks5h://127.0.0.1:9091 \\
      .venv/bin/python scripts/enrichment/enrich_jurisdiction_websites_search.py \\
      --state AL --apply-seed --skip-existing-seed
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
import time
from dataclasses import dataclass, fields
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Set, Tuple
from urllib.parse import urlparse, urlunparse

_root = Path(__file__).resolve().parents[2]
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from dotenv import load_dotenv

try:
    import psycopg2
except ImportError:
    psycopg2 = None  # type: ignore

import httpx
from bs4 import BeautifulSoup
from loguru import logger

from scripts.discovery.jurisdiction_discovery_pipeline import resolve_database_url

# Official AL county FIPS (01 + 3-digit county) — 67 counties.
_AL_COUNTY_3 = (
    "001,003,005,007,009,011,013,015,017,019,021,023,025,027,029,031,033,035,037,039,041,043,"
    "045,047,049,051,053,055,057,059,061,063,065,067,069,071,073,075,077,079,081,083,085,087,089,"
    "091,093,095,097,099,101,103,105,107,109,111,113,115,117,119,121,123,125,127,129,131,133"
).split(",")
AL_COUNTY_GEOIDS = [f"01{c}" for c in _AL_COUNTY_3]

_BLOCKLIST_HOST_FRAGMENTS = (
    "wikipedia.org",
    "wikimedia.org",
    "facebook.com",
    "fb.com",
    "instagram.com",
    "twitter.com",
    "x.com",
    "linkedin.com",
    "yelp.com",
    "google.com/maps",
    "bing.com/maps",
    "youtube.com",
    "youtu.be",
    "tiktok.com",
    "pinterest.com",
    "reddit.com",
    "amazon.com",
)


def _load_dotenv() -> None:
    load_dotenv(_root / ".env", override=False)


def _slug_from_county_name(name: str) -> str:
    base = (name or "").lower().replace("county", "").strip()
    base = re.sub(r"[^a-z0-9]+", "", base)
    return base[:32]


def _host_blocked(host: str) -> bool:
    h = (host or "").lower()
    return any(b in h for b in _BLOCKLIST_HOST_FRAGMENTS)


def _canonical_https(url: str) -> str:
    u = (url or "").strip()
    if not u:
        return ""
    if not u.lower().startswith(("http://", "https://")):
        u = "https://" + u
    if u.lower().startswith("http://"):
        p = urlparse(u)
        u = urlunparse(("https", p.netloc, p.path, p.params, p.query, p.fragment))
    return u.rstrip("/")


def _pick_gov_org_results(
    results: Sequence[Dict[str, Any]],
    county_slug: str,
    *,
    max_scan: int,
) -> List[Tuple[int, str, int]]:
    """
    Return list of (rank_0_based, href, score) for .gov / .org candidates in order of appearance.
    """
    out: List[Tuple[int, str, int]] = []
    for i, row in enumerate(results[:max_scan]):
        href = (row.get("href") or "").strip()
        if not href.startswith("http"):
            continue
        try:
            host = urlparse(href).netloc.lower()
        except ValueError:
            continue
        if _host_blocked(host):
            continue
        if not (host.endswith(".gov") or host.endswith(".org")):
            continue
        score = 0
        if host.endswith(".gov"):
            score += 5
        else:
            score += 3
        if county_slug and county_slug in re.sub(r"[^a-z0-9]", "", host):
            score += 10
        out.append((i, href, score))
    out.sort(key=lambda t: -t[2])
    return out


def _httpx_proxy() -> Optional[str]:
    return (os.getenv("WIKIDATA_HTTPS_PROXY") or os.getenv("ALL_PROXY") or "").strip() or None


def _validate_url(url: str, *, timeout_s: float = 20.0) -> Tuple[int, str, str]:
    """
    Return ``(status_or_0, final_url, detail)``. ``detail`` empty on success (2xx/3xx we treat as
    reachable for a government homepage — some sites 302 to CDN).
    """
    u = _canonical_https(url)
    if not u:
        return 0, "", "empty_url"
    headers = {
        "User-Agent": (
            "OpenNavigatorJurisdictionEnrichment/1.0 (+https://github.com/getcommunityone/open-navigator)"
        ),
        "Accept": "text/html,application/xhtml+xml;q=0.9,*/*;q=0.8",
    }
    proxy = _httpx_proxy()
    try:
        with httpx.Client(
            proxy=proxy,
            timeout=timeout_s,
            follow_redirects=True,
            headers=headers,
        ) as client:
            r = client.head(u)
            if r.status_code in (405, 501):
                r = client.get(u)
            return r.status_code, str(r.url), ""
    except httpx.RequestError as exc:
        return 0, u, f"request_error:{type(exc).__name__}:{exc!r}"


def _extract_contact_hint(html: str, page_url: str) -> str:
    """Short text snippet: first mailto + stripped title (best-effort, not authoritative)."""
    try:
        soup = BeautifulSoup(html[:800_000], "html.parser")
        title = (soup.title.string or "").strip() if soup.title else ""
        mail = ""
        for a in soup.find_all("a", href=True):
            h = a.get("href") or ""
            if h.lower().startswith("mailto:"):
                mail = h.split(":", 1)[-1].split("?")[0][:120]
                break
        bits = [b for b in (title, mail) if b]
        return " | ".join(bits)[:500]
    except Exception as exc:
        return f"(parse_error:{type(exc).__name__})"


def _youtube_top_video(
    query: str,
    *,
    api_key: Optional[str],
    timeout_s: float = 15.0,
) -> Tuple[Optional[str], Optional[str], str]:
    if not api_key:
        return None, None, "no_api_key"
    try:
        from googleapiclient.discovery import build

        yt = build("youtube", "v3", developerKey=api_key, cache_discovery=False)
        req = yt.search().list(
            q=query,
            part="id,snippet",
            type="video",
            maxResults=3,
        )
        res = req.execute()
        items = res.get("items") or []
        if not items:
            return None, None, "empty_results"
        vid = (items[0].get("id") or {}).get("videoId")
        sn = items[0].get("snippet") or {}
        title = (sn.get("title") or "").strip()
        return vid, title, ""
    except Exception as exc:
        return None, None, f"youtube_error:{type(exc).__name__}:{exc!r}"


def _manifest_paths(state: str, scraped_root: Path) -> List[Path]:
    d = scraped_root / state.upper() / "county"
    if not d.is_dir():
        return []
    return sorted(d.glob("county_*/_manifest.json"))


def _read_manifest_pages(path: Path) -> int:
    try:
        d = json.loads(path.read_text(encoding="utf-8"))
        return len(d.get("pages_fetched") or [])
    except Exception:
        return -1


def _collect_targets(
    *,
    state: str,
    scraped_root: Path,
    modes: Set[str],
    shallow_max_pages: int,
    extra_geoids: Sequence[str],
) -> List[str]:
    """Return county 5-digit GEOIDs (e.g. 01001) to enrich."""
    want: Set[str] = set()

    present_dirs: Set[str] = set()
    if scraped_root.is_dir():
        for p in (scraped_root / state.upper() / "county").glob("county_*"):
            if p.is_dir():
                present_dirs.add(p.name.replace("county_", ""))

    if "missing" in modes and state.upper() == "AL":
        for g in AL_COUNTY_GEOIDS:
            if g not in present_dirs:
                want.add(g)

    for mf in _manifest_paths(state, scraped_root):
        geoid = mf.parent.name.replace("county_", "")
        n = _read_manifest_pages(mf)
        if n < 0:
            continue
        if "failed" in modes and n == 0:
            want.add(geoid)
        if "shallow" in modes and 0 < n < shallow_max_pages:
            want.add(geoid)

    for g in extra_geoids:
        g = g.strip()
        if g.isdigit() and len(g) <= 5:
            want.add(g.zfill(5))

    return sorted(want, key=lambda x: int(x))


def _load_county_names(geoids: Sequence[str]) -> Dict[str, Tuple[str, str]]:
    """geoid -> (jurisdiction_id, county_name)"""
    if psycopg2 is None:
        raise RuntimeError("psycopg2 is required for --state DB name lookup")
    out: Dict[str, Tuple[str, str]] = {}
    if not geoids:
        return out
    db = resolve_database_url()
    ids = [f"county_{g}" for g in geoids]
    sql = """
        SELECT jurisdiction_id, name, state_code
        FROM intermediate.int_jurisdictions
        WHERE jurisdiction_id = ANY(%s)
          AND LOWER(TRIM(jurisdiction_type)) = 'county'
    """
    with psycopg2.connect(db) as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (ids,))
            for jid, name, st in cur.fetchall():
                m = re.match(r"^county_(.+)$", str(jid or ""), re.I)
                if not m:
                    continue
                g = m.group(1).strip()
                out[g] = (str(jid), str(name or "").strip())
    return out


def _existing_override_geoids(seed_path: Path) -> Set[str]:
    if not seed_path.is_file():
        return set()
    seen: Set[str] = set()
    with seed_path.open(newline="", encoding="utf-8") as fp:
        r = csv.DictReader(fp)
        for row in r:
            jid = (row.get("jurisdiction_id") or "").strip()
            m = re.match(r"^county_(.+)$", jid, re.I)
            if m:
                seen.add(m.group(1))
    return seen


@dataclass
class EnrichmentRow:
    jurisdiction_id: str
    geoid: str
    county_name: str
    state_code: str
    search_query: str
    chosen_url: str
    chosen_rank: str
    ddg_href: str
    ddg_title: str
    head_status: str
    head_final_url: str
    validation_detail: str
    contact_hint: str
    youtube_video_id: str
    youtube_title: str
    youtube_detail: str
    manual_review: str
    notes: str


def _run_ddg(query: str, *, max_results: int, proxy: Optional[str]) -> List[Dict[str, Any]]:
    from duckduckgo_search import DDGS

    kwargs: Dict[str, Any] = {"timeout": 25}
    if proxy:
        kwargs["proxy"] = proxy
    with DDGS(**kwargs) as ddgs:
        return list(ddgs.text(query, max_results=max_results))


def main() -> None:
    _load_dotenv()
    parser = argparse.ArgumentParser(
        description="Suggest county website URLs via DuckDuckGo + HEAD validation for dbt overrides.",
    )
    parser.add_argument("--state", default="AL", help="USPS state code (default AL)")
    parser.add_argument(
        "--scraped-root",
        type=Path,
        default=None,
        help="Root of scraped meetings cache (default: repo data/cache/scraped_meetings)",
    )
    parser.add_argument(
        "--mode",
        default="failed,missing,shallow",
        help=(
            "Comma list: failed (0 pages), shallow (1..N-1 pages), missing (AL only: no county folder). "
            "--geoids is always merged. Default: failed,missing,shallow"
        ),
    )
    parser.add_argument("--shallow-max-pages", type=int, default=5)
    parser.add_argument(
        "--geoids",
        default="",
        help="Comma-separated 5-digit county GEOIDs (always unioned into targets, e.g. 01011,01127)",
    )
    parser.add_argument(
        "--apply-seed",
        action="store_true",
        help="Append validated rows to dbt_project/seeds/jurisdiction_website_url_overrides.csv "
        "(use --append-seed PATH for a different file)",
    )
    parser.add_argument("--max-ddg-results", type=int, default=12)
    parser.add_argument("--sleep", type=float, default=2.0, help="Seconds between DDG queries (politeness)")
    parser.add_argument("--output", type=Path, default=None, help="CSV output path")
    parser.add_argument(
        "--append-seed",
        type=Path,
        default=None,
        help="Append high-confidence rows (manual_review=false, HEAD ok) to this overrides CSV",
    )
    parser.add_argument("--skip-existing-seed", action="store_true", help="Skip GEOIDs already in overrides seed")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--fetch-contact-hint", action="store_true", help="GET homepage and extract title/mailto")
    args = parser.parse_args()

    state = args.state.strip().upper()
    scraped_root = (
        args.scraped_root.expanduser()
        if args.scraped_root
        else _root / "data/cache/scraped_meetings"
    )
    modes = {m.strip().lower() for m in args.mode.split(",") if m.strip()}
    if "manual" in modes:
        modes.add("manual")
    extra_geoids = [x.strip() for x in args.geoids.split(",") if x.strip()]

    targets = _collect_targets(
        state=state,
        scraped_root=scraped_root,
        modes=modes,
        shallow_max_pages=max(2, args.shallow_max_pages),
        extra_geoids=extra_geoids,
    )

    seed_default = _root / "dbt_project" / "seeds" / "jurisdiction_website_url_overrides.csv"
    seed_write: Optional[Path] = None
    if args.append_seed:
        seed_write = args.append_seed.expanduser()
    elif args.apply_seed:
        seed_write = seed_default
    existing_seed = _existing_override_geoids(seed_write or seed_default) if args.skip_existing_seed else set()

    if not targets:
        logger.warning("No target counties after mode filter — nothing to do.")
        return

    names = _load_county_names(targets)
    proxy = _httpx_proxy()
    yt_key = (os.getenv("YOUTUBE_DATA_API_KEY") or "").strip()

    out_path = args.output
    if out_path is None:
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        out_dir = _root / "data/cache/enrichment"
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / f"jurisdiction_website_enrichment_{state.lower()}_{ts}.csv"

    rows_out: List[EnrichmentRow] = []
    append_rows: List[Tuple[str, str]] = []

    for geoid in targets:
        if geoid in existing_seed:
            logger.info("skip_existing_seed geoid={}", geoid)
            continue
        meta = names.get(geoid)
        if not meta:
            rows_out.append(
                EnrichmentRow(
                    jurisdiction_id=f"county_{geoid}",
                    geoid=geoid,
                    county_name="",
                    state_code=state,
                    search_query="",
                    chosen_url="",
                    chosen_rank="",
                    ddg_href="",
                    ddg_title="",
                    head_status="",
                    head_final_url="",
                    validation_detail="no_int_jurisdictions_row",
                    contact_hint="",
                    youtube_video_id="",
                    youtube_title="",
                    youtube_detail="",
                    manual_review="true",
                    notes="Add county to int_jurisdictions or fix GEOID",
                )
            )
            continue

        jid, cname = meta
        slug = _slug_from_county_name(cname)
        state_long = "Alabama" if state == "AL" else state
        query = f'"{cname}" {state_long} official county government website'
        yt_query = f"{cname} county commission meeting {state}"

        manual = "true"
        notes: List[str] = []
        chosen = ""
        rank_s = ""
        dhref = ""
        dtitle = ""
        st_s = ""
        fin = ""
        val_detail = ""
        contact = ""
        yid = ""
        ytitle = ""
        ydetail = ""

        try:
            ddg_results = _run_ddg(query, max_results=args.max_ddg_results, proxy=proxy)
        except Exception as exc:
            val_detail = f"ddg_error:{type(exc).__name__}:{exc!r}"
            notes.append("duckduckgo_failed")
        else:
            ranked = _pick_gov_org_results(ddg_results, slug, max_scan=args.max_ddg_results)
            if not ranked:
                notes.append("no_gov_org_in_results")
            for rnk, href, _score in ranked:
                dhref = href
                # title from matching result row
                dtitle = ""
                for row in ddg_results:
                    if (row.get("href") or "").strip() == href:
                        dtitle = (row.get("title") or "")[:300]
                        break
                st, fin, val_detail = _validate_url(href)
                st_s = str(st)
                if 200 <= st < 400:
                    chosen = _canonical_https(fin or href)
                    rank_s = str(rnk)
                    manual = "false"
                    break
                notes.append(f"candidate_http_{st}")

        if chosen and args.fetch_contact_hint:
            try:
                with httpx.Client(proxy=proxy, timeout=30.0, follow_redirects=True, headers={"User-Agent": "OpenNavigatorEnrichment/1.0"}) as c:
                    r = c.get(chosen)
                    if r.status_code == 200 and "text/html" in (r.headers.get("content-type") or "").lower():
                        contact = _extract_contact_hint(r.text, chosen)
            except Exception as exc:
                contact = f"(get_error:{type(exc).__name__})"

        yid, ytitle, ydetail = _youtube_top_video(yt_query, api_key=yt_key or None)

        if manual == "true" and not notes:
            notes.append("needs_manual_pick")

        rows_out.append(
            EnrichmentRow(
                jurisdiction_id=jid,
                geoid=geoid,
                county_name=cname,
                state_code=state,
                search_query=query,
                chosen_url=chosen,
                chosen_rank=rank_s,
                ddg_href=dhref,
                ddg_title=dtitle,
                head_status=st_s,
                head_final_url=fin,
                validation_detail=val_detail,
                contact_hint=contact,
                youtube_video_id=yid or "",
                youtube_title=ytitle or "",
                youtube_detail=ydetail,
                manual_review=manual,
                notes=";".join(notes),
            )
        )

        if seed_write and manual == "false" and chosen and not args.dry_run:
            append_rows.append((jid, chosen))

        time.sleep(max(0.0, float(args.sleep)))

    fieldnames = [f.name for f in fields(EnrichmentRow)]
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", newline="", encoding="utf-8") as fp:
        w = csv.DictWriter(fp, fieldnames=fieldnames)
        w.writeheader()
        for row in rows_out:
            w.writerow(row.__dict__)

    logger.success("Wrote {} suggestion rows → {}", len(rows_out), out_path)

    if append_rows and seed_write and not args.dry_run:
        with seed_write.open("a", newline="", encoding="utf-8") as fp:
            w = csv.writer(fp)
            for jid, url in append_rows:
                w.writerow([jid, url])
        logger.success("Appended {} rows → {}", len(append_rows), seed_write)
        logger.info(
            "Next: cd dbt_project && dbt seed --select jurisdiction_website_url_overrides && "
            "dbt run --select int_jurisdiction_websites",
        )


if __name__ == "__main__":
    main()
