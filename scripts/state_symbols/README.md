# State Symbols USA (reference assets)

Scripts here download **attribution-friendly reference imagery** from [State Symbols USA](https://statesymbolsusa.org/) for local caches (see [Citations — State Symbols USA](../../website/docs/data-sources/citations.md#state-symbols-usa-reference)).

## What gets cached

| File | Source |
|------|--------|
| `data/cache/state_symbols/colors_license_plate.jpg` | Site asset used on state-colors content (collage of U.S. license plates). Canonical URL is recorded in `_manifest.json`. |

The [State Colors category](https://statesymbolsusa.org/categories/colors) links official and symbolic color designations by state.

## Run

From the repository root:

```bash
./scripts/state_symbols/download_state_symbols_assets.sh
```

Requirements: `curl`, `python3` (for writing JSON manifest only).

`data/` is gitignored; run the script on each machine that needs the cache.
