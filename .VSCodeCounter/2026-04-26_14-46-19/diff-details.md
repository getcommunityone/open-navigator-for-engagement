# Diff Details

Date : 2026-04-26 14:46:19

Directory /home/developer/projects/oral-health-policy-pulse

Total : 95 files,  6379 codes, 437 comments, 1431 blanks, all 8247 lines

[Summary](results.md) / [Details](details.md) / [Diff Summary](diff.md) / Diff Details

## Files
| filename | language | code | comment | blank | total |
| :--- | :--- | ---: | ---: | ---: | ---: |
| [.dockerignore](/.dockerignore) | Ignore | 62 | 13 | 13 | 88 |
| [.github/copilot-instructions.md](/.github/copilot-instructions.md) | Markdown | 96 | 0 | 33 | 129 |
| [.huggingface/README.md](/.huggingface/README.md) | Markdown | 92 | 0 | 30 | 122 |
| [.huggingface/nginx.conf](/.huggingface/nginx.conf) | Properties | 59 | 5 | 13 | 77 |
| [.huggingface/start.sh](/.huggingface/start.sh) | Shell Script | 11 | 2 | 3 | 16 |
| [.huggingface/supervisord.conf](/.huggingface/supervisord.conf) | Properties | 18 | 0 | 3 | 21 |
| [ARCHITECTURE.md](/ARCHITECTURE.md) | Markdown | -160 | 0 | -43 | -203 |
| [CITATIONS.md](/CITATIONS.md) | Markdown | 77 | 0 | 27 | 104 |
| [DASHBOARD\_REDESIGN.md](/DASHBOARD_REDESIGN.md) | Markdown | -84 | 0 | -21 | -105 |
| [DATABRICKS\_APP\_GUIDE.md](/DATABRICKS_APP_GUIDE.md) | Markdown | -295 | 0 | -103 | -398 |
| [DATABRICKS\_MIGRATION.md](/DATABRICKS_MIGRATION.md) | Markdown | -221 | 0 | -52 | -273 |
| [DOCS\_MIGRATION.md](/DOCS_MIGRATION.md) | Markdown | -70 | 0 | -22 | -92 |
| [Dockerfile](/Dockerfile) | Docker | 24 | 6 | 5 | 35 |
| [PORT\_GUIDE.md](/PORT_GUIDE.md) | Markdown | -122 | 0 | -40 | -162 |
| [QUICKSTART.md](/QUICKSTART.md) | Markdown | -140 | 0 | -63 | -203 |
| [QUICKSTART\_DATABRICKS\_APP.md](/QUICKSTART_DATABRICKS_APP.md) | Markdown | -156 | 0 | -53 | -209 |
| [QUICK\_REFERENCE.md](/QUICK_REFERENCE.md) | Markdown | -89 | 0 | -28 | -117 |
| [REACT\_REFACTORING.md](/REACT_REFACTORING.md) | Markdown | -430 | 0 | -117 | -547 |
| [README.md](/README.md) | Markdown | -651 | 0 | -166 | -817 |
| [README\_HF.md](/README_HF.md) | Markdown | 92 | 0 | 30 | 122 |
| [REFACTORING\_SUMMARY.md](/REFACTORING_SUMMARY.md) | Markdown | -374 | 0 | -112 | -486 |
| [TUSCALOOSA\_COMPLETE\_REPORT.md](/TUSCALOOSA_COMPLETE_REPORT.md) | Markdown | -266 | 0 | -85 | -351 |
| [TUSCALOOSA\_DISCOVERY\_REPORT.md](/TUSCALOOSA_DISCOVERY_REPORT.md) | Markdown | -332 | 0 | -112 | -444 |
| [TUSCALOOSA\_PIPELINE\_GUIDE.md](/TUSCALOOSA_PIPELINE_GUIDE.md) | Markdown | -867 | 0 | -267 | -1,134 |
| [api/auth.py](/api/auth.py) | Python | 74 | 52 | 28 | 154 |
| [api/database.py](/api/database.py) | Python | 35 | 18 | 10 | 63 |
| [api/main.py](/api/main.py) | Python | 130 | 8 | 11 | 149 |
| [api/models.py](/api/models.py) | Python | 148 | 41 | 64 | 253 |
| [api/routes/\_\_init\_\_.py](/api/routes/__init__.py) | Python | 0 | 3 | 1 | 4 |
| [api/routes/auth.py](/api/routes/auth.py) | Python | 306 | 45 | 75 | 426 |
| [api/routes/social.py](/api/routes/social.py) | Python | 393 | 43 | 109 | 545 |
| [api/static/communityone\_logo.svg](/api/static/communityone_logo.svg) | XML | 13 | 5 | 5 | 23 |
| [api/static/index.html](/api/static/index.html) | HTML | 17 | 0 | 1 | 18 |
| [api/static/privacyfacebook.html](/api/static/privacyfacebook.html) | HTML | 244 | 0 | 33 | 277 |
| [deploy-huggingface.sh](/deploy-huggingface.sh) | Shell Script | 110 | 18 | 21 | 149 |
| [discovery/meetingbank\_ingestion.py](/discovery/meetingbank_ingestion.py) | Python | 0 | 20 | 0 | 20 |
| [frontend/index.html](/frontend/index.html) | HTML | 2 | 0 | 0 | 2 |
| [frontend/policy-dashboards/public/communityone\_logo.svg](/frontend/policy-dashboards/public/communityone_logo.svg) | XML | 13 | 5 | 5 | 23 |
| [frontend/public/communityone\_logo.svg](/frontend/public/communityone_logo.svg) | XML | 13 | 5 | 5 | 23 |
| [frontend/public/privacyfacebook.html](/frontend/public/privacyfacebook.html) | HTML | 244 | 0 | 33 | 277 |
| [frontend/src/App.tsx](/frontend/src/App.tsx) | TypeScript JSX | 2 | 0 | 0 | 2 |
| [frontend/src/components/AddressLookup.tsx](/frontend/src/components/AddressLookup.tsx) | TypeScript JSX | 394 | 19 | 40 | 453 |
| [frontend/src/components/FollowButton.tsx](/frontend/src/components/FollowButton.tsx) | TypeScript JSX | 147 | 4 | 10 | 161 |
| [frontend/src/components/Layout.tsx](/frontend/src/components/Layout.tsx) | TypeScript JSX | 246 | 7 | 6 | 259 |
| [frontend/src/components/RegistrationModal.tsx](/frontend/src/components/RegistrationModal.tsx) | TypeScript JSX | 192 | 7 | 18 | 217 |
| [frontend/src/components/SocialStats.tsx](/frontend/src/components/SocialStats.tsx) | TypeScript JSX | 106 | 2 | 14 | 122 |
| [frontend/src/contexts/AuthContext.tsx](/frontend/src/contexts/AuthContext.tsx) | TypeScript JSX | 134 | 7 | 21 | 162 |
| [frontend/src/contexts/LocationContext.tsx](/frontend/src/contexts/LocationContext.tsx) | TypeScript JSX | 66 | 4 | 12 | 82 |
| [frontend/src/main.tsx](/frontend/src/main.tsx) | TypeScript JSX | 6 | 0 | 0 | 6 |
| [frontend/src/pages/Documents.tsx](/frontend/src/pages/Documents.tsx) | TypeScript JSX | 83 | 1 | 1 | 85 |
| [frontend/src/pages/Home.tsx](/frontend/src/pages/Home.tsx) | TypeScript JSX | 160 | 3 | 13 | 176 |
| [frontend/src/pages/PeopleFinder.tsx](/frontend/src/pages/PeopleFinder.tsx) | TypeScript JSX | 10 | 1 | 1 | 12 |
| [frontend/src/pages/Profile.tsx](/frontend/src/pages/Profile.tsx) | TypeScript JSX | 381 | 9 | 20 | 410 |
| [frontend/src/pages/Settings.tsx](/frontend/src/pages/Settings.tsx) | TypeScript JSX | 88 | 9 | 8 | 105 |
| [frontend/src/vite-env.d.ts](/frontend/src/vite-env.d.ts) | TypeScript | 6 | 2 | 3 | 11 |
| [hf-dataset-cleanup.sh](/hf-dataset-cleanup.sh) | Shell Script | 28 | 4 | 7 | 39 |
| [requirements.txt](/requirements.txt) | pip requirements | 4 | 1 | 1 | 6 |
| [scripts/migrate\_social\_features.py](/scripts/migrate_social_features.py) | Python | 28 | 14 | 9 | 51 |
| [setup-huggingface.sh](/setup-huggingface.sh) | Shell Script | 111 | 12 | 23 | 146 |
| [start-all.sh](/start-all.sh) | Shell Script | 25 | 3 | 1 | 29 |
| [test-huggingface-build.sh](/test-huggingface-build.sh) | Shell Script | 8 | 9 | 4 | 21 |
| [test\_oauth\_flow.py](/test_oauth_flow.py) | Python | 52 | 6 | 13 | 71 |
| [update-repo-urls.sh](/update-repo-urls.sh) | Shell Script | 36 | 5 | 7 | 48 |
| [website/DOCUMENTATION\_MIGRATION.md](/website/DOCUMENTATION_MIGRATION.md) | Markdown | 167 | 0 | 37 | 204 |
| [website/docs/architecture.md](/website/docs/architecture.md) | Markdown | 163 | 0 | 44 | 207 |
| [website/docs/case-studies/tuscaloosa-complete.md](/website/docs/case-studies/tuscaloosa-complete.md) | Markdown | 269 | 0 | 86 | 355 |
| [website/docs/case-studies/tuscaloosa-discovery.md](/website/docs/case-studies/tuscaloosa-discovery.md) | Markdown | 335 | 0 | 113 | 448 |
| [website/docs/case-studies/tuscaloosa-pipeline.md](/website/docs/case-studies/tuscaloosa-pipeline.md) | Markdown | 870 | 0 | 268 | 1,138 |
| [website/docs/dashboard.md](/website/docs/dashboard.md) | Markdown | 10 | 0 | 6 | 16 |
| [website/docs/data-sources/\_civic-tech-sources.md](/website/docs/data-sources/_civic-tech-sources.md) | Markdown | 189 | 0 | 67 | 256 |
| [website/docs/data-sources/\_confirmed-datasets.md](/website/docs/data-sources/_confirmed-datasets.md) | Markdown | 250 | 0 | 91 | 341 |
| [website/docs/data-sources/civic-tech-sources.md](/website/docs/data-sources/civic-tech-sources.md) | Markdown | -188 | 0 | -67 | -255 |
| [website/docs/data-sources/confirmed-datasets.md](/website/docs/data-sources/confirmed-datasets.md) | Markdown | -250 | 0 | -91 | -341 |
| [website/docs/data-sources/overview.md](/website/docs/data-sources/overview.md) | Markdown | 14 | 0 | 4 | 18 |
| [website/docs/deployment/authentication-setup.md](/website/docs/deployment/authentication-setup.md) | Markdown | 326 | 0 | 124 | 450 |
| [website/docs/deployment/databricks-apps.md](/website/docs/deployment/databricks-apps.md) | Markdown | 298 | 0 | 104 | 402 |
| [website/docs/deployment/databricks-migration.md](/website/docs/deployment/databricks-migration.md) | Markdown | 224 | 0 | 53 | 277 |
| [website/docs/deployment/huggingface-spaces.md](/website/docs/deployment/huggingface-spaces.md) | Markdown | 253 | 0 | 92 | 345 |
| [website/docs/deployment/oauth-providers-setup.md](/website/docs/deployment/oauth-providers-setup.md) | Markdown | 342 | 0 | 143 | 485 |
| [website/docs/deployment/quickstart-databricks.md](/website/docs/deployment/quickstart-databricks.md) | Markdown | 159 | 0 | 54 | 213 |
| [website/docs/deployment/rename-repository.md](/website/docs/deployment/rename-repository.md) | Markdown | 219 | 0 | 89 | 308 |
| [website/docs/development/dashboard-redesign.md](/website/docs/development/dashboard-redesign.md) | Markdown | 87 | 0 | 22 | 109 |
| [website/docs/development/docs-migration.md](/website/docs/development/docs-migration.md) | Markdown | 73 | 0 | 23 | 96 |
| [website/docs/development/port-guide.md](/website/docs/development/port-guide.md) | Markdown | 125 | 0 | 41 | 166 |
| [website/docs/development/react-refactoring.md](/website/docs/development/react-refactoring.md) | Markdown | 433 | 0 | 118 | 551 |
| [website/docs/development/readme-migration.md](/website/docs/development/readme-migration.md) | Markdown | 131 | 0 | 40 | 171 |
| [website/docs/development/refactoring-summary.md](/website/docs/development/refactoring-summary.md) | Markdown | 377 | 0 | 113 | 490 |
| [website/docs/for-advocates.md](/website/docs/for-advocates.md) | Markdown | 141 | 0 | 67 | 208 |
| [website/docs/for-developers.md](/website/docs/for-developers.md) | Markdown | 315 | 0 | 109 | 424 |
| [website/docs/intro.md](/website/docs/intro.md) | Markdown | 215 | 0 | 65 | 280 |
| [website/docs/quick-reference.md](/website/docs/quick-reference.md) | Markdown | 92 | 0 | 29 | 121 |
| [website/docs/quickstart.md](/website/docs/quickstart.md) | Markdown | 143 | 0 | 64 | 207 |
| [website/sidebars.ts](/website/sidebars.ts) | TypeScript | 69 | 11 | 2 | 82 |
| [website/src/pages/index.tsx](/website/src/pages/index.tsx) | TypeScript JSX | 186 | 3 | 10 | 199 |
| [website/static/img/communityone\_logo.svg](/website/static/img/communityone_logo.svg) | XML | 13 | 5 | 5 | 23 |

[Summary](results.md) / [Details](details.md) / [Diff Summary](diff.md) / Diff Details