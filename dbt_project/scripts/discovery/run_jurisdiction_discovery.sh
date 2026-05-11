#!/usr/bin/env bash
# Run from dbt_project or anywhere: finds repo root + Python, then runs discovery.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" && pwd)"
ROOT="$SCRIPT_DIR"
while [[ "$ROOT" != "/" && ! -f "$ROOT/scripts/discovery/jurisdiction_discovery_pipeline.py" ]]; do
  ROOT="$(dirname "$ROOT")"
done
if [[ ! -f "$ROOT/scripts/discovery/jurisdiction_discovery_pipeline.py" ]]; then
  echo "error: could not find open-navigator repo root from $SCRIPT_DIR" >&2
  exit 1
fi
cd "$ROOT"

if [[ -x "$ROOT/.venv/bin/python" ]]; then
  PY="$ROOT/.venv/bin/python"
elif command -v python3 >/dev/null 2>&1; then
  PY="$(command -v python3)"
else
  echo "error: need $ROOT/.venv/bin/python or python3 on PATH" >&2
  exit 1
fi

exec "$PY" -m scripts.discovery.jurisdiction_discovery_pipeline "$@"
