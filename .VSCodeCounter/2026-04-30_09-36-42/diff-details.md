# Diff Details

Date : 2026-04-30 09:36:42

Directory /home/developer/projects/oral-health-policy-pulse

Total : 46 files,  1861 codes, 635 comments, 489 blanks, all 2985 lines

[Summary](results.md) / [Details](details.md) / [Diff Summary](diff.md) / Diff Details

## Files
| filename | language | code | comment | blank | total |
| :--- | :--- | ---: | ---: | ---: | ---: |
| [.huggingface/nginx.conf](/.huggingface/nginx.conf) | Properties | 9 | 3 | 3 | 15 |
| [.huggingface/start.sh](/.huggingface/start.sh) | Shell Script | 10 | 1 | 1 | 12 |
| [.huggingface/supervisord.conf](/.huggingface/supervisord.conf) | Properties | 9 | 0 | 0 | 9 |
| [CITATIONS.md](/CITATIONS.md) | Markdown | 55 | 0 | 8 | 63 |
| [Dockerfile](/Dockerfile) | Docker | 4 | 1 | 1 | 6 |
| [README\_HF.md](/README_HF.md) | Markdown | -20 | 0 | -2 | -22 |
| [api/errors.py](/api/errors.py) | Python | 112 | 24 | 19 | 155 |
| [api/main.py](/api/main.py) | Python | 187 | 13 | 12 | 212 |
| [api/routes/bills.py](/api/routes/bills.py) | Python | 93 | 262 | 12 | 367 |
| [api/routes/search.py](/api/routes/search.py) | Python | 18 | 56 | 10 | 84 |
| [api/static/assets/index-BHoE4WiJ.css](/api/static/assets/index-BHoE4WiJ.css) | PostCSS | 1 | 0 | 1 | 2 |
| [api/static/assets/index-BdRFjxIK.css](/api/static/assets/index-BdRFjxIK.css) | PostCSS | -1 | 0 | -1 | -2 |
| [api/static/assets/index-C\_zb597X.js](/api/static/assets/index-C_zb597X.js) | JavaScript | 191 | 0 | 3 | 194 |
| [api/static/assets/index-kjd3WXCN.js](/api/static/assets/index-kjd3WXCN.js) | JavaScript | -187 | 0 | -3 | -190 |
| [check-hf-vars.py](/check-hf-vars.py) | Python | 40 | 9 | 9 | 58 |
| [delete\_and\_publish\_all\_datasets.py](/delete_and_publish_all_datasets.py) | Python | 7 | 1 | 1 | 9 |
| [deploy-huggingface.sh](/deploy-huggingface.sh) | Shell Script | 14 | 4 | 6 | 24 |
| [docs/TERMINAL\_CORRUPTION\_FIX.md](/docs/TERMINAL_CORRUPTION_FIX.md) | Markdown | 71 | 0 | 25 | 96 |
| [force-hf-rebuild.sh](/force-hf-rebuild.sh) | Shell Script | 17 | 3 | 6 | 26 |
| [frontend/package-lock.json](/frontend/package-lock.json) | JSON | -283 | 0 | 0 | -283 |
| [frontend/package.json](/frontend/package.json) | JSON | -1 | 0 | 0 | -1 |
| [frontend/src/App.tsx](/frontend/src/App.tsx) | TypeScript JSX | 2 | 0 | 0 | 2 |
| [frontend/src/components/USMap.tsx](/frontend/src/components/USMap.tsx) | TypeScript JSX | 129 | 10 | 6 | 145 |
| [frontend/src/lib/api.ts](/frontend/src/lib/api.ts) | TypeScript | 88 | 8 | 19 | 115 |
| [frontend/src/pages/BillDetail.tsx](/frontend/src/pages/BillDetail.tsx) | TypeScript JSX | 235 | 6 | 14 | 255 |
| [frontend/src/pages/HomeModern.tsx](/frontend/src/pages/HomeModern.tsx) | TypeScript JSX | 83 | 8 | 12 | 103 |
| [frontend/src/pages/JurisdictionsSearch.tsx](/frontend/src/pages/JurisdictionsSearch.tsx) | TypeScript JSX | -101 | -2 | -3 | -106 |
| [frontend/src/pages/PolicyMap.tsx](/frontend/src/pages/PolicyMap.tsx) | TypeScript JSX | 4 | 0 | 0 | 4 |
| [frontend/src/pages/UnifiedSearch.tsx](/frontend/src/pages/UnifiedSearch.tsx) | TypeScript JSX | -77 | 3 | 2 | -72 |
| [frontend/tsconfig.json](/frontend/tsconfig.json) | JSON with Comments | -5 | -1 | -1 | -7 |
| [scripts/aggregate\_bill\_statistics.py](/scripts/aggregate_bill_statistics.py) | Python | 117 | 32 | 39 | 188 |
| [scripts/aggregate\_bills\_from\_postgres.py](/scripts/aggregate_bills_from_postgres.py) | Python | 241 | 170 | 33 | 444 |
| [scripts/cleanup\_frontend\_junk.sh](/scripts/cleanup_frontend_junk.sh) | Shell Script | 24 | 4 | 4 | 32 |
| [scripts/prevent\_terminal\_corruption.sh](/scripts/prevent_terminal_corruption.sh) | Shell Script | 16 | 8 | 7 | 31 |
| [scripts/regen\_simple.py](/scripts/regen_simple.py) | Python | 12 | 6 | 5 | 23 |
| [verify-hf-deployment.sh](/verify-hf-deployment.sh) | Shell Script | 61 | 6 | 10 | 77 |
| [website/blog/2026-04-06-data-model-expansion.md](/website/blog/2026-04-06-data-model-expansion.md) | Markdown | 1 | 0 | 1 | 2 |
| [website/blog/2026-04-13-citations-migration.md](/website/blog/2026-04-13-citations-migration.md) | Markdown | 1 | 0 | 1 | 2 |
| [website/blog/2026-04-20-homepage-navigation-fixes.md](/website/blog/2026-04-20-homepage-navigation-fixes.md) | Markdown | 1 | 0 | 1 | 2 |
| [website/docs/data-sources/citations.md](/website/docs/data-sources/citations.md) | Markdown | 75 | 0 | 14 | 89 |
| [website/docs/development/api-logging-errors.md](/website/docs/development/api-logging-errors.md) | Markdown | 225 | 0 | 67 | 292 |
| [website/docs/development/terminal-corruption-prevention.md](/website/docs/development/terminal-corruption-prevention.md) | Markdown | 76 | 0 | 26 | 102 |
| [website/docs/guides/specialized-ai-models.md](/website/docs/guides/specialized-ai-models.md) | Markdown | 306 | 0 | 121 | 427 |
| [website/docs/legal-compliance.md](/website/docs/legal-compliance.md) | Markdown | 1 | 0 | 0 | 1 |
| [website/docs/legal/README.md](/website/docs/legal/README.md) | Markdown | -103 | 0 | -35 | -138 |
| [website/docs/legal/\_README.md](/website/docs/legal/_README.md) | Markdown | 103 | 0 | 35 | 138 |

[Summary](results.md) / [Details](details.md) / [Diff Summary](diff.md) / Diff Details