#!/usr/bin/env python3
"""
Export ``jurisdiction_mapping_quality_summary`` (+ optional counts) to JSON for the
**Jurisdiction mapping quality** dashboard (``frontend/public/data/jurisdiction_mapping_quality.json``).

Also writes capped **drill-down** lists from ``public.jurisdiction_mapping_analysis``:

- ``drilldown.unmapped`` — jurisdictions with no primary URL (sample; see ``unmapped_total``).
- ``drilldown.mapped_url_issues`` — mapped primaries failing static syntax / host heuristics (sample; see ``mapped_url_issues_total``).

**State rollups** for the entity-first dashboard (**State analysis** tab):

- ``entity_state_rollup`` — per-state totals and coverage for four slices aligned with the UI:
  ``county``, ``municipality_incorporated_city`` (cities), ``municipality_towns_and_cdp`` (towns/CDP/other),
  ``school_district``. Each value is a list of
  ``{ state_code, total_jurisdictions, with_primary_website, pct_with_primary_website }``.

Optional env caps (defaults in parentheses): ``JURIS_MAPPING_QUALITY_UNMAPPED_CAP`` (2500),
``JURIS_MAPPING_QUALITY_MAPPED_ISSUES_CAP`` (800).

Requires dbt mart tables built:
  ./scripts/dbt.sh run --select jurisdiction_mapping_analysis jurisdiction_mapping_analysis_sources \\
    jurisdiction_mapping_quality_summary jurisdiction_mapping_quality_summary_municipality_places \\
    jurisdiction_mapping_quality_summary_by_acs_population_tier \\
    jurisdiction_mapping_quality_summary_by_acs_income_level

Usage (repo root):
  .venv/bin/python scripts/datasources/jurisdictions/export_jurisdiction_mapping_quality_json.py
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "frontend" / "public" / "data" / "jurisdiction_mapping_quality.json"

# Capped lists for dashboard drill-down (keep JSON size reasonable; raise via env if needed).
_UNMAPPED_CAP = int(os.environ.get("JURIS_MAPPING_QUALITY_UNMAPPED_CAP", "2500"))
_MAPPED_ISSUES_CAP = int(os.environ.get("JURIS_MAPPING_QUALITY_MAPPED_ISSUES_CAP", "800"))


def _jsonify_value(v: object) -> object:
    """Coerce psycopg2 / Postgres types to JSON-friendly values."""
    if isinstance(v, Decimal):
        if v == v.to_integral_value():
            return int(v)
        return float(v)
    return v


def _json_default(obj: object) -> float | int:
    """Fallback for ``json.dumps`` if any ``Decimal`` slips through."""
    if isinstance(obj, Decimal):
        if obj == obj.to_integral_value():
            return int(obj)
        return float(obj)
    raise TypeError(f"Object of type {type(obj).__name__!r} is not JSON serializable")


def _db_url() -> str:
    load_dotenv(ROOT / ".env")
    return (
        (os.getenv("OPEN_NAVIGATOR_DATABASE_URL") or "").strip()
        or (os.getenv("NEON_DATABASE_URL_DEV") or "").strip()
        or (os.getenv("NEON_DATABASE_URL") or "").strip()
        or (os.getenv("DATABASE_URL") or "").strip()
        or "postgresql://postgres:password@localhost:5433/open_navigator"
    )


def main() -> int:
    url = _db_url()
    conn = psycopg2.connect(url)
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                SELECT jurisdiction_type::text AS jurisdiction_type,
                       total_jurisdictions,
                       with_primary_website,
                       pct_with_primary_website,
                       with_primary_url_syntax_ok,
                       pct_with_primary_url_syntax_ok,
                       with_primary_url_passes_basic_checks,
                       pct_with_primary_url_passes_basic_checks,
                       pct_syntax_ok_among_with_primary,
                       pct_basic_checks_ok_among_with_primary,
                       with_primary_url_likely_wrong_host,
                       jurisdictions_touching_naco,
                       jurisdictions_touching_uscm,
                       jurisdictions_touching_nces,
                       jurisdictions_touching_gsa,
                       jurisdictions_touching_override,
                       summary_generated_at::text AS summary_generated_at
                FROM public.jurisdiction_mapping_quality_summary
                ORDER BY jurisdiction_type
                """
            )
            summary_by_type = [
                {k: _jsonify_value(v) for k, v in dict(r).items()} for r in cur.fetchall()
            ]

            cur.execute(
                """
                SELECT municipality_place_kind::text AS municipality_place_kind,
                       total_jurisdictions,
                       with_primary_website,
                       pct_with_primary_website,
                       with_primary_url_syntax_ok,
                       pct_with_primary_url_syntax_ok,
                       with_primary_url_passes_basic_checks,
                       pct_with_primary_url_passes_basic_checks,
                       pct_syntax_ok_among_with_primary,
                       pct_basic_checks_ok_among_with_primary,
                       with_primary_url_likely_wrong_host,
                       jurisdictions_touching_naco,
                       jurisdictions_touching_uscm,
                       jurisdictions_touching_nces,
                       jurisdictions_touching_gsa,
                       jurisdictions_touching_override,
                       summary_generated_at::text AS summary_generated_at
                FROM public.jurisdiction_mapping_quality_summary_municipality_places
                ORDER BY
                    CASE municipality_place_kind
                        WHEN 'incorporated_city' THEN 1
                        WHEN 'census_designated_place' THEN 2
                        WHEN 'incorporated_other' THEN 3
                        WHEN 'unknown' THEN 4
                        ELSE 5
                    END
                """
            )
            summary_municipality_by_place_kind = [
                {k: _jsonify_value(v) for k, v in dict(r).items()} for r in cur.fetchall()
            ]

            cur.execute(
                """
                SELECT jurisdiction_type::text AS jurisdiction_type,
                       acs_population_tier::text AS acs_population_tier,
                       total_jurisdictions,
                       with_primary_website,
                       pct_with_primary_website,
                       with_primary_url_syntax_ok,
                       pct_with_primary_url_syntax_ok,
                       with_primary_url_passes_basic_checks,
                       pct_with_primary_url_passes_basic_checks,
                       pct_syntax_ok_among_with_primary,
                       pct_basic_checks_ok_among_with_primary,
                       with_primary_url_likely_wrong_host,
                       jurisdictions_touching_naco,
                       jurisdictions_touching_uscm,
                       jurisdictions_touching_nces,
                       jurisdictions_touching_gsa,
                       jurisdictions_touching_override,
                       summary_generated_at::text AS summary_generated_at
                FROM public.jurisdiction_mapping_quality_summary_by_acs_population_tier
                ORDER BY
                    jurisdiction_type,
                    CASE acs_population_tier
                        WHEN 'Very Large (1M+)' THEN 1
                        WHEN 'Large (250k-1M)' THEN 2
                        WHEN 'Mid (50k-250k)' THEN 3
                        WHEN 'Small (15k-50k)' THEN 4
                        WHEN 'Very Small (<15k)' THEN 5
                        ELSE 99
                    END
                """
            )
            summary_by_acs_population_tier = [
                {k: _jsonify_value(v) for k, v in dict(r).items()} for r in cur.fetchall()
            ]

            cur.execute(
                """
                SELECT jurisdiction_type::text AS jurisdiction_type,
                       acs_income_level::text AS acs_income_level,
                       total_jurisdictions,
                       with_primary_website,
                       pct_with_primary_website,
                       with_primary_url_syntax_ok,
                       pct_with_primary_url_syntax_ok,
                       with_primary_url_passes_basic_checks,
                       pct_with_primary_url_passes_basic_checks,
                       pct_syntax_ok_among_with_primary,
                       pct_basic_checks_ok_among_with_primary,
                       with_primary_url_likely_wrong_host,
                       jurisdictions_touching_naco,
                       jurisdictions_touching_uscm,
                       jurisdictions_touching_nces,
                       jurisdictions_touching_gsa,
                       jurisdictions_touching_override,
                       summary_generated_at::text AS summary_generated_at
                FROM public.jurisdiction_mapping_quality_summary_by_acs_income_level
                ORDER BY
                    jurisdiction_type,
                    CASE acs_income_level
                        WHEN 'High Earner' THEN 1
                        WHEN 'Middle Class' THEN 2
                        WHEN 'Lower Middle' THEN 3
                        WHEN 'Low Income' THEN 4
                        ELSE 99
                    END
                """
            )
            summary_by_acs_income_level = [
                {k: _jsonify_value(v) for k, v in dict(r).items()} for r in cur.fetchall()
            ]

            cur.execute(
                """
                SELECT website_source::text AS website_source,
                       COUNT(DISTINCT jurisdiction_id)::bigint AS distinct_jurisdictions
                FROM public.jurisdiction_mapping_analysis_sources
                GROUP BY website_source
                ORDER BY distinct_jurisdictions DESC
                """
            )
            candidates_by_source = [
                {k: _jsonify_value(v) for k, v in dict(r).items()} for r in cur.fetchall()
            ]

            cur.execute(
                "SELECT COUNT(*)::bigint AS n FROM public.jurisdiction_mapping_analysis_sources"
            )
            n_source_rows = int(_jsonify_value(cur.fetchone()["n"]))

            cur.execute(
                """
                SELECT COUNT(*)::bigint AS n
                FROM public.jurisdiction_mapping_analysis
                WHERE NOT COALESCE(has_primary_website, FALSE)
                """
            )
            unmapped_total = int(_jsonify_value(cur.fetchone()["n"]))

            cur.execute(
                """
                SELECT COUNT(*)::bigint AS n
                FROM public.jurisdiction_mapping_analysis
                WHERE COALESCE(has_primary_website, FALSE)
                  AND (
                      COALESCE(primary_url_syntax_ok, FALSE) = FALSE
                      OR COALESCE(primary_url_likely_wrong_host, FALSE) = TRUE
                      OR COALESCE(primary_url_passes_basic_checks, FALSE) = FALSE
                  )
                """
            )
            mapped_url_issues_total = int(_jsonify_value(cur.fetchone()["n"]))

            cur.execute(
                """
                SELECT jurisdiction_id::text AS jurisdiction_id,
                       name::text AS name,
                       state_code::text AS state_code,
                       jurisdiction_type::text AS jurisdiction_type,
                       geoid::text AS geoid,
                       municipality_place_kind::text AS municipality_place_kind,
                       COALESCE(n_website_candidate_rows, 0)::bigint AS n_website_candidate_rows,
                       COALESCE(has_naco_source, FALSE) AS has_naco_source,
                       COALESCE(has_uscm_source, FALSE) AS has_uscm_source,
                       COALESCE(has_nces_directory_source, FALSE) AS has_nces_directory_source,
                       COALESCE(has_gsa_source, FALSE) AS has_gsa_source,
                       COALESCE(has_override_source, FALSE) AS has_override_source,
                       acs_population_tier::text AS acs_population_tier,
                       acs_income_level::text AS acs_income_level
                FROM public.jurisdiction_mapping_analysis
                WHERE NOT COALESCE(has_primary_website, FALSE)
                ORDER BY jurisdiction_type, state_code, name
                LIMIT %s
                """,
                (_UNMAPPED_CAP,),
            )
            unmapped_sample = [{k: _jsonify_value(v) for k, v in dict(r).items()} for r in cur.fetchall()]

            cur.execute(
                """
                SELECT jurisdiction_id::text AS jurisdiction_id,
                       name::text AS name,
                       state_code::text AS state_code,
                       jurisdiction_type::text AS jurisdiction_type,
                       geoid::text AS geoid,
                       municipality_place_kind::text AS municipality_place_kind,
                       primary_website_url::text AS primary_website_url,
                       primary_website_source::text AS primary_website_source,
                       primary_url_syntax_ok,
                       primary_url_likely_wrong_host,
                       primary_url_passes_basic_checks
                FROM public.jurisdiction_mapping_analysis
                WHERE COALESCE(has_primary_website, FALSE)
                  AND (
                      COALESCE(primary_url_syntax_ok, FALSE) = FALSE
                      OR COALESCE(primary_url_likely_wrong_host, FALSE) = TRUE
                      OR COALESCE(primary_url_passes_basic_checks, FALSE) = FALSE
                  )
                ORDER BY primary_url_likely_wrong_host DESC NULLS LAST,
                         primary_url_syntax_ok ASC NULLS LAST,
                         jurisdiction_type,
                         state_code,
                         name
                LIMIT %s
                """,
                (_MAPPED_ISSUES_CAP,),
            )
            mapped_url_issues_sample = [
                {k: _jsonify_value(v) for k, v in dict(r).items()} for r in cur.fetchall()
            ]

            def _state_rollup(where_clause: str) -> list[dict[str, object]]:
                cur.execute(
                    f"""
                    SELECT state_code::text AS state_code,
                           COUNT(*)::bigint AS total_jurisdictions,
                           COUNT(*) FILTER (WHERE COALESCE(has_primary_website, FALSE))::bigint
                               AS with_primary_website,
                           CASE
                               WHEN COUNT(*) = 0 THEN NULL
                               ELSE ROUND(
                                   (100.0 * COUNT(*) FILTER (WHERE COALESCE(has_primary_website, FALSE)))
                                   / COUNT(*)::numeric,
                                   1
                               )
                           END AS pct_with_primary_website
                    FROM public.jurisdiction_mapping_analysis
                    WHERE {where_clause}
                    GROUP BY state_code
                    ORDER BY state_code
                    """
                )
                return [{k: _jsonify_value(v) for k, v in dict(r).items()} for r in cur.fetchall()]

            entity_state_rollup = {
                "county": _state_rollup("jurisdiction_type = 'county'"),
                "municipality_incorporated_city": _state_rollup(
                    "jurisdiction_type = 'municipality' AND municipality_place_kind = 'incorporated_city'"
                ),
                "municipality_towns_and_cdp": _state_rollup(
                    "jurisdiction_type = 'municipality' "
                    "AND municipality_place_kind IN ("
                    "'incorporated_other', 'unknown', 'census_designated_place'"
                    ")"
                ),
                "school_district": _state_rollup("jurisdiction_type = 'school_district'"),
            }

    finally:
        conn.close()

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "database_host": url.split("@")[-1] if "@" in url else url,
        "summary_by_type": summary_by_type,
        "summary_municipality_by_place_kind": summary_municipality_by_place_kind,
        "summary_by_acs_population_tier": summary_by_acs_population_tier,
        "summary_by_acs_income_level": summary_by_acs_income_level,
        "candidates_by_source": candidates_by_source,
        "n_source_detail_rows": n_source_rows,
        "sources_explained": {
            "naco": "County association directory (NACo) — https://naco.org/",
            "uscm": "Municipal directory / U.S. Conference of Mayors–style seed (USCM bronze)",
            "nces_directory": "NCES Common Core of Data school district directory",
            "gsa": "GSA .gov domain registry (local agencies)",
            "override": "Curated seed jurisdiction_website_url_overrides",
        },
        "entity_state_rollup": entity_state_rollup,
        "drilldown": {
            "unmapped_total": unmapped_total,
            "unmapped_sample_limit": _UNMAPPED_CAP,
            "unmapped": unmapped_sample,
            "mapped_url_issues_total": mapped_url_issues_total,
            "mapped_url_issues_sample_limit": _MAPPED_ISSUES_CAP,
            "mapped_url_issues": mapped_url_issues_sample,
            "mapped_url_fields_explained": {
                "primary_url_syntax_ok": "False = primary URL fails static shape check (http(s), non-empty dotted hostname, min length). Not HTTP reachability.",
                "primary_url_likely_wrong_host": "True = hostname matches social/wiki deny heuristics (Facebook, Wikipedia, etc.) — worth human review.",
                "primary_url_passes_basic_checks": "False = fails syntax OR hits wrong-host heuristic. True = passes both static checks.",
            },
            "unmapped_context_explained": {
                "n_website_candidate_rows": "Raw website candidate rows merged from directories (still may not win source-priority primary pick).",
                "has_*_source": "True if at least one candidate row exists from that directory for this jurisdiction.",
                "acs_population_tier": "ACS B01003 size bucket when joined; null if no ACS row.",
                "acs_income_level": "ACS B19013 income bucket when joined; null if missing income.",
            },
        },
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2, default=_json_default), encoding="utf-8")
    print(f"Wrote {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
