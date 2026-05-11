#!/usr/bin/env bash
# Supporting indexes for intermediate.int_jurisdictions (speeds joins in int_jurisdiction_websites, etc.).
# CREATE INDEX CONCURRENTLY cannot run inside dbt's transaction — run via psql after dbt builds the table.
#
# Usage (repo root or dbt_project/):
#   bash dbt_project/scripts/ensure_int_jurisdictions_indexes.sh
#
# Connection: same as other scripts — OPEN_NAVIGATOR_DATABASE_URL, NEON_DATABASE_URL_DEV,
# NEON_DATABASE_URL, or DATABASE_URL. Loads repo .env when present.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
ENV_FILE="${ROOT}/.env"
if [[ -f "${ENV_FILE}" ]]; then
  set -a
  # shellcheck disable=SC1090
  source "${ENV_FILE}" 2>/dev/null || true
  set +a
fi

DB_URL="${OPEN_NAVIGATOR_DATABASE_URL:-${NEON_DATABASE_URL_DEV:-${NEON_DATABASE_URL:-${DATABASE_URL:-}}}}"
if [[ -z "${DB_URL}" ]]; then
  echo "ensure_int_jurisdictions_indexes: no database URL in env; skip."
  exit 0
fi

if ! command -v psql >/dev/null 2>&1; then
  echo "ensure_int_jurisdictions_indexes: psql not found; skip."
  exit 0
fi

regclass="$(psql "${DB_URL}" -tAc "SELECT to_regclass('intermediate.int_jurisdictions')::text" 2>/dev/null | tr -d '[:space:]' || true)"
if [[ -z "${regclass}" ]]; then
  echo "ensure_int_jurisdictions_indexes: intermediate.int_jurisdictions does not exist yet; skip."
  exit 0
fi

psql "${DB_URL}" -v ON_ERROR_STOP=1 <<'SQL'
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_int_jurisdictions_state_type
  ON intermediate.int_jurisdictions (state_code, jurisdiction_type);
SQL

echo "ensure_int_jurisdictions_indexes: idx_int_jurisdictions_state_type ensured."
