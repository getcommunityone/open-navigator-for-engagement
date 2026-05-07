#!/usr/bin/env bash
# Migrate schemas 'bronze' and 'public' from NEON_DATABASE_URL to NEON_DATABASE_URL_DEV.
# Creates schemas in the target if missing. Safe to re-run (uses --clean --if-exists).
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="$SCRIPT_DIR/../../.env"

# Load .env, stripping Windows CRLF and skipping comments/blank lines
if [[ -f "$ENV_FILE" ]]; then
  while IFS= read -r line; do
    line="${line%$'\r'}"                   # strip CR
    [[ -z "$line" || "$line" == \#* ]] && continue
    [[ "$line" != *=* ]] && continue
    key="${line%%=*}"
    value="${line#*=}"
    [[ "$key" =~ ^[a-zA-Z_][a-zA-Z0-9_]*$ ]] || continue
    export "$key=$value"
  done < "$ENV_FILE"
fi

: "${NEON_DATABASE_URL:?NEON_DATABASE_URL is not set}"
: "${NEON_DATABASE_URL_DEV:?NEON_DATABASE_URL_DEV is not set}"

SCHEMAS=("public" "bronze")

# Prefer pg_dump/pg_restore/psql that matches the server version (17)
PG_DUMP="pg_dump"
PG_RESTORE="pg_restore"
PSQL="psql"
for v in 17 16; do
  if command -v "/usr/lib/postgresql/$v/bin/pg_dump" &>/dev/null; then
    PG_DUMP="/usr/lib/postgresql/$v/bin/pg_dump"
    PG_RESTORE="/usr/lib/postgresql/$v/bin/pg_restore"
    PSQL="/usr/lib/postgresql/$v/bin/psql"
    break
  fi
done
echo "==> Using: $PG_DUMP"
DUMP_FILE="$(mktemp /tmp/neon_migration_XXXXXX.dump)"
trap 'rm -f "$DUMP_FILE"' EXIT

echo "==> Source:  $NEON_DATABASE_URL"
echo "==> Target:  $NEON_DATABASE_URL_DEV"
echo "==> Schemas: ${SCHEMAS[*]}"
echo ""

# Build --schema flags for pg_dump
SCHEMA_FLAGS=()
for schema in "${SCHEMAS[@]}"; do
  SCHEMA_FLAGS+=("--schema=$schema")
done

echo "[1/3] Dumping schemas from source..."
"$PG_DUMP" \
  --format=custom \
  --no-owner \
  --no-acl \
  "${SCHEMA_FLAGS[@]}" \
  "$NEON_DATABASE_URL" \
  --file="$DUMP_FILE"
echo "      Dump written to $DUMP_FILE ($(du -sh "$DUMP_FILE" | cut -f1))"

echo ""
echo "[2/3] Ensuring schemas exist in target..."
for schema in "${SCHEMAS[@]}"; do
  "$PSQL" "$NEON_DATABASE_URL_DEV" \
    --command="CREATE SCHEMA IF NOT EXISTS \"$schema\";" \
    --quiet
  echo "      Schema '$schema' ready."
done

echo ""
echo "[3/3] Restoring into target..."
# Convert to SQL, strip v17-only SET commands unknown to older targets, pipe to psql
"$PG_RESTORE" \
  --format=custom \
  --no-owner \
  --no-acl \
  --clean \
  --if-exists \
  --file=- \
  "$DUMP_FILE" \
| grep -v 'transaction_timeout' \
| "$PSQL" --set ON_ERROR_STOP=0 "$NEON_DATABASE_URL_DEV"

echo ""
echo "Migration complete."
