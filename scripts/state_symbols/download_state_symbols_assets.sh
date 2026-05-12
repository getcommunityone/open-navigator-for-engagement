#!/usr/bin/env bash
# Download State Symbols USA reference assets into data/cache/state_symbols/.
# See website/docs/data-sources/citations.md (State Symbols USA reference).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
OUT="${ROOT}/data/cache/state_symbols"
UA="Mozilla/5.0 (compatible; OpenNavigatorStateSymbols/1.0; +https://github.com/getcommunityone/open-navigator-for-engagement)"
# Image appears on state-colors pages (e.g. California); same path used site-wide for that hero.
LICENSE_PLATE_URL="https://statesymbolsusa.org/sites/default/files/primary-images/colors_license_plate.jpg"
REFERER="https://statesymbolsusa.org/symbol-official-item/california/state-colors/blue-gold"
COLORS_CATEGORY_URL="https://statesymbolsusa.org/categories/colors"

mkdir -p "$OUT"

echo "Downloading license plate collage → ${OUT}/colors_license_plate.jpg"
curl -fsSL \
  -A "$UA" \
  -e "$REFERER" \
  -o "${OUT}/colors_license_plate.jpg" \
  "$LICENSE_PLATE_URL"

python3 - <<'PY' "$OUT" "$LICENSE_PLATE_URL" "$REFERER" "$COLORS_CATEGORY_URL"
import json, sys, datetime
out, img_url, example_page, category_url = sys.argv[1:5]
manifest = {
    "source_site": "https://statesymbolsusa.org/",
    "category_url": category_url,
    "assets": [
        {
            "filename": "colors_license_plate.jpg",
            "canonical_url": img_url,
            "example_page_url": example_page,
            "notes": "Collage of U.S. state license plates (primary image on State Colors content).",
        }
    ],
    "retrieved_utc": datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "attribution": "State Symbols USA (statesymbolsusa.org). Local cache for documentation and design reference; cite the live site in published materials.",
}
path = f"{out}/_manifest.json"
with open(path, "w", encoding="utf-8") as f:
    json.dump(manifest, f, indent=2)
    f.write("\n")
print(f"Wrote {path}")
PY

echo "Done."
