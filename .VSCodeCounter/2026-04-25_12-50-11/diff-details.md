# Diff Details

Date : 2026-04-25 12:50:11

Directory /home/developer/projects/oral-health-policy-pulse

Total : 175 files,  364263 codes, 1846 comments, 7262 blanks, all 373371 lines

[Summary](results.md) / [Details](details.md) / [Diff Summary](diff.md) / Diff Details

## Files
| filename | language | code | comment | blank | total |
| :--- | :--- | ---: | ---: | ---: | ---: |
| [ARCHITECTURE.md](/ARCHITECTURE.md) | Markdown | 160 | 0 | 43 | 203 |
| [DASHBOARD\_REDESIGN.md](/DASHBOARD_REDESIGN.md) | Markdown | 84 | 0 | 21 | 105 |
| [DOCS\_MIGRATION.md](/DOCS_MIGRATION.md) | Markdown | 70 | 0 | 22 | 92 |
| [Dockerfile](/Dockerfile) | Docker | 1 | 0 | 0 | 1 |
| [Makefile](/Makefile) | Makefile | 33 | 0 | 5 | 38 |
| [PORT\_GUIDE.md](/PORT_GUIDE.md) | Markdown | 122 | 0 | 40 | 162 |
| [QUICKSTART.md](/QUICKSTART.md) | Markdown | 18 | 0 | 7 | 25 |
| [README.md](/README.md) | Markdown | 379 | 0 | 111 | 490 |
| [TUSCALOOSA\_PIPELINE\_GUIDE.md](/TUSCALOOSA_PIPELINE_GUIDE.md) | Markdown | 867 | 0 | 267 | 1,134 |
| [agents/\_\_init\_\_.py](/agents/__init__.py) | Python | 4 | 0 | 0 | 4 |
| [agents/base.py](/agents/base.py) | Python | 1 | 0 | 0 | 1 |
| [agents/debate\_grader.py](/agents/debate_grader.py) | Python | 305 | 64 | 56 | 425 |
| [agents/scraper.py](/agents/scraper.py) | Python | 1,168 | 156 | 231 | 1,555 |
| [agents/scraper\_undetected.py](/agents/scraper_undetected.py) | Python | 173 | 46 | 43 | 262 |
| [api/app.py](/api/app.py) | Python | 238 | 69 | 47 | 354 |
| [api/main.py](/api/main.py) | Python | 283 | 67 | 59 | 409 |
| [debug\_eboard.py](/debug_eboard.py) | Python | 89 | 15 | 30 | 134 |
| [discovery/README\_NONPROFIT\_DISCOVERY.md](/discovery/README_NONPROFIT_DISCOVERY.md) | Markdown | 338 | 0 | 102 | 440 |
| [discovery/census\_ingestion.py](/discovery/census_ingestion.py) | Python | 13 | 8 | 4 | 25 |
| [discovery/comprehensive\_discovery\_pipeline.py](/discovery/comprehensive_discovery_pipeline.py) | Python | 4 | 0 | 1 | 5 |
| [discovery/nonprofit\_discovery.py](/discovery/nonprofit_discovery.py) | Python | 375 | 154 | 112 | 641 |
| [discovery/social\_media\_discovery.py](/discovery/social_media_discovery.py) | Python | 18 | 20 | 7 | 45 |
| [discovery/youtube\_channel\_discovery.py](/discovery/youtube_channel_discovery.py) | Python | 42 | 17 | 9 | 68 |
| [docs/ACCOUNTABILITY\_DASHBOARD\_STRATEGY.md](/docs/ACCOUNTABILITY_DASHBOARD_STRATEGY.md) | Markdown | 178 | 0 | 76 | 254 |
| [docs/COST\_EFFECTIVE\_STORAGE.md](/docs/COST_EFFECTIVE_STORAGE.md) | Markdown | 9 | 0 | 4 | 13 |
| [docs/DEBATE\_GRADER\_GUIDE.md](/docs/DEBATE_GRADER_GUIDE.md) | Markdown | 241 | 0 | 67 | 308 |
| [docs/EBOARD\_AUTOMATED\_SOLUTIONS.md](/docs/EBOARD_AUTOMATED_SOLUTIONS.md) | Markdown | 304 | 0 | 98 | 402 |
| [docs/EBOARD\_COOKIE\_GUIDE.md](/docs/EBOARD_COOKIE_GUIDE.md) | Markdown | 184 | 0 | 63 | 247 |
| [docs/EBOARD\_MANUAL\_DOWNLOAD.md](/docs/EBOARD_MANUAL_DOWNLOAD.md) | Markdown | 95 | 0 | 31 | 126 |
| [docs/FRONTEND\_INTEGRATION\_GUIDE.md](/docs/FRONTEND_INTEGRATION_GUIDE.md) | Markdown | 332 | 0 | 113 | 445 |
| [docs/HANDLING\_MULTIPLE\_FORMATS.md](/docs/HANDLING_MULTIPLE_FORMATS.md) | Markdown | 508 | 0 | 152 | 660 |
| [docs/HUGGINGFACE\_PUBLISHING.md](/docs/HUGGINGFACE_PUBLISHING.md) | Markdown | 10 | 0 | 1 | 11 |
| [docs/HUGGINGFACE\_QUICK\_START.md](/docs/HUGGINGFACE_QUICK_START.md) | Markdown | 6 | 0 | 1 | 7 |
| [docs/IMPACT\_NAVIGATION\_GUIDE.md](/docs/IMPACT_NAVIGATION_GUIDE.md) | Markdown | 249 | 0 | 100 | 349 |
| [docs/INSTALLING\_DOCUMENT\_LIBRARIES.md](/docs/INSTALLING_DOCUMENT_LIBRARIES.md) | Markdown | 118 | 0 | 44 | 162 |
| [docs/POLITICAL\_ECONOMY\_ANALYSIS.md](/docs/POLITICAL_ECONOMY_ANALYSIS.md) | Markdown | 266 | 0 | 89 | 355 |
| [docs/SPLIT\_SCREEN\_SYSTEM.md](/docs/SPLIT_SCREEN_SYSTEM.md) | Markdown | 293 | 0 | 81 | 374 |
| [examples/process\_multiple\_formats.py](/examples/process_multiple_formats.py) | Python | 93 | 33 | 36 | 162 |
| [examples/tuscaloosa\_accountability\_report.py](/examples/tuscaloosa_accountability_report.py) | Python | 488 | 166 | 115 | 769 |
| [examples/tuscaloosa\_decision\_analysis.py](/examples/tuscaloosa_decision_analysis.py) | Python | 159 | 28 | 44 | 231 |
| [examples/tuscaloosa\_political\_economy.py](/examples/tuscaloosa_political_economy.py) | Python | 279 | 76 | 105 | 460 |
| [extraction/accountability\_dashboards.py](/extraction/accountability_dashboards.py) | Python | 391 | 137 | 87 | 615 |
| [extraction/budget\_analyzer.py](/extraction/budget_analyzer.py) | Python | 155 | 202 | 23 | 380 |
| [extraction/decision\_analyzer.py](/extraction/decision_analyzer.py) | Python | 336 | 106 | 44 | 486 |
| [extraction/temporal\_analyzer.py](/extraction/temporal_analyzer.py) | Python | 226 | 65 | 55 | 346 |
| [extraction/universal\_extractor.py](/extraction/universal_extractor.py) | Python | 248 | 65 | 71 | 384 |
| [frontend/README.md](/frontend/README.md) | Markdown | 8 | 0 | 5 | 13 |
| [frontend/package-lock.json](/frontend/package-lock.json) | JSON | 5,124 | 0 | 1 | 5,125 |
| [frontend/policy-dashboards/README.md](/frontend/policy-dashboards/README.md) | Markdown | 174 | 0 | 78 | 252 |
| [frontend/policy-dashboards/package-lock.json](/frontend/policy-dashboards/package-lock.json) | JSON | 17,457 | 0 | 1 | 17,458 |
| [frontend/policy-dashboards/package.json](/frontend/policy-dashboards/package.json) | JSON | 36 | 0 | 1 | 37 |
| [frontend/policy-dashboards/public/index.html](/frontend/policy-dashboards/public/index.html) | HTML | 17 | 0 | 1 | 18 |
| [frontend/policy-dashboards/src/App.jsx](/frontend/policy-dashboards/src/App.jsx) | JavaScript JSX | 1,277 | 30 | 49 | 1,356 |
| [frontend/policy-dashboards/src/components/EndlessStudyLoop.jsx](/frontend/policy-dashboards/src/components/EndlessStudyLoop.jsx) | JavaScript JSX | 139 | 13 | 11 | 163 |
| [frontend/policy-dashboards/src/components/HomePage.jsx](/frontend/policy-dashboards/src/components/HomePage.jsx) | JavaScript JSX | 274 | 8 | 10 | 292 |
| [frontend/policy-dashboards/src/components/ImpactDashboard.jsx](/frontend/policy-dashboards/src/components/ImpactDashboard.jsx) | JavaScript JSX | 243 | 20 | 18 | 281 |
| [frontend/policy-dashboards/src/components/NonprofitCard.jsx](/frontend/policy-dashboards/src/components/NonprofitCard.jsx) | JavaScript JSX | 273 | 9 | 9 | 291 |
| [frontend/policy-dashboards/src/components/SplitScreenView.jsx](/frontend/policy-dashboards/src/components/SplitScreenView.jsx) | JavaScript JSX | 347 | 12 | 17 | 376 |
| [frontend/policy-dashboards/src/components/Summary.jsx](/frontend/policy-dashboards/src/components/Summary.jsx) | JavaScript JSX | 168 | 9 | 7 | 184 |
| [frontend/policy-dashboards/src/components/TopicNavigation.jsx](/frontend/policy-dashboards/src/components/TopicNavigation.jsx) | JavaScript JSX | 488 | 11 | 13 | 512 |
| [frontend/policy-dashboards/src/components/WhereMoneyWent.jsx](/frontend/policy-dashboards/src/components/WhereMoneyWent.jsx) | JavaScript JSX | 146 | 9 | 8 | 163 |
| [frontend/policy-dashboards/src/components/WhoIsInCharge.jsx](/frontend/policy-dashboards/src/components/WhoIsInCharge.jsx) | JavaScript JSX | 141 | 11 | 11 | 163 |
| [frontend/policy-dashboards/src/components/WordsVsDollars.jsx](/frontend/policy-dashboards/src/components/WordsVsDollars.jsx) | JavaScript JSX | 134 | 10 | 8 | 152 |
| [frontend/policy-dashboards/src/components/shared/BarMeter.jsx](/frontend/policy-dashboards/src/components/shared/BarMeter.jsx) | JavaScript JSX | 28 | 4 | 3 | 35 |
| [frontend/policy-dashboards/src/components/shared/Compare.jsx](/frontend/policy-dashboards/src/components/shared/Compare.jsx) | JavaScript JSX | 51 | 4 | 4 | 59 |
| [frontend/policy-dashboards/src/components/shared/DashboardTile.jsx](/frontend/policy-dashboards/src/components/shared/DashboardTile.jsx) | JavaScript JSX | 148 | 14 | 10 | 172 |
| [frontend/policy-dashboards/src/components/shared/DecisionCard.jsx](/frontend/policy-dashboards/src/components/shared/DecisionCard.jsx) | JavaScript JSX | 236 | 8 | 10 | 254 |
| [frontend/policy-dashboards/src/components/shared/FilterPanel.jsx](/frontend/policy-dashboards/src/components/shared/FilterPanel.jsx) | JavaScript JSX | 225 | 6 | 10 | 241 |
| [frontend/policy-dashboards/src/components/shared/InsightBox.jsx](/frontend/policy-dashboards/src/components/shared/InsightBox.jsx) | JavaScript JSX | 30 | 4 | 4 | 38 |
| [frontend/policy-dashboards/src/components/shared/MetricCard.jsx](/frontend/policy-dashboards/src/components/shared/MetricCard.jsx) | JavaScript JSX | 30 | 4 | 3 | 37 |
| [frontend/policy-dashboards/src/index.css](/frontend/policy-dashboards/src/index.css) | PostCSS | 26 | 0 | 6 | 32 |
| [frontend/policy-dashboards/src/index.js](/frontend/policy-dashboards/src/index.js) | JavaScript | 10 | 0 | 2 | 12 |
| [frontend/src/App.tsx](/frontend/src/App.tsx) | TypeScript JSX | 8 | 0 | 0 | 8 |
| [frontend/src/components/Layout.tsx](/frontend/src/components/Layout.tsx) | TypeScript JSX | 60 | 4 | 3 | 67 |
| [frontend/src/main.tsx](/frontend/src/main.tsx) | TypeScript JSX | 5 | 0 | 0 | 5 |
| [frontend/src/pages/Dashboard.tsx](/frontend/src/pages/Dashboard.tsx) | TypeScript JSX | 36 | 1 | 1 | 38 |
| [frontend/src/pages/DebateGrader.tsx](/frontend/src/pages/DebateGrader.tsx) | TypeScript JSX | 245 | 8 | 22 | 275 |
| [frontend/src/pages/Documents.tsx](/frontend/src/pages/Documents.tsx) | TypeScript JSX | 37 | 1 | 3 | 41 |
| [frontend/src/pages/Home.tsx](/frontend/src/pages/Home.tsx) | TypeScript JSX | 225 | 10 | 16 | 251 |
| [frontend/src/pages/Nonprofits.tsx](/frontend/src/pages/Nonprofits.tsx) | TypeScript JSX | 280 | 5 | 24 | 309 |
| [frontend/src/pages/PeopleFinder.tsx](/frontend/src/pages/PeopleFinder.tsx) | TypeScript JSX | 315 | 5 | 20 | 340 |
| [frontend/tailwind.config.js](/frontend/tailwind.config.js) | JavaScript | 16 | 0 | 0 | 16 |
| [install.sh](/install.sh) | Shell Script | 26 | 1 | 2 | 29 |
| [main.py](/main.py) | Python | 34 | 2 | 4 | 40 |
| [migrate-docs.sh](/migrate-docs.sh) | Shell Script | 46 | 8 | 9 | 63 |
| [output/tuscaloosa/generic\_20260423\_180616.json](/output/tuscaloosa/generic_20260423_180616.json) | JSON | 1,052 | 0 | 0 | 1,052 |
| [output/tuscaloosa/generic\_20260423\_180619.json](/output/tuscaloosa/generic_20260423_180619.json) | JSON | 1 | 0 | 0 | 1 |
| [output/tuscaloosa/granicus\_20260423\_180621.json](/output/tuscaloosa/granicus_20260423_180621.json) | JSON | 1 | 0 | 0 | 1 |
| [output/tuscaloosa/legistar\_20260423\_180620.json](/output/tuscaloosa/legistar_20260423_180620.json) | JSON | 1 | 0 | 0 | 1 |
| [output/tuscaloosa/suiteonemedia\_20260423\_181708.json](/output/tuscaloosa/suiteonemedia_20260423_181708.json) | JSON | 512 | 0 | 0 | 512 |
| [output/tuscaloosa/suiteonemedia\_20260423\_182340.json](/output/tuscaloosa/suiteonemedia_20260423_182340.json) | JSON | 748 | 0 | 0 | 748 |
| [output/tuscaloosa/suiteonemedia\_20260423\_182351.json](/output/tuscaloosa/suiteonemedia_20260423_182351.json) | JSON | 748 | 0 | 0 | 748 |
| [output/tuscaloosa/suiteonemedia\_20260423\_210412.json](/output/tuscaloosa/suiteonemedia_20260423_210412.json) | JSON | 375 | 0 | 0 | 375 |
| [output/tuscaloosa/suiteonemedia\_20260423\_210613.json](/output/tuscaloosa/suiteonemedia_20260423_210613.json) | JSON | 375 | 0 | 0 | 375 |
| [output/tuscaloosa/suiteonemedia\_20260424\_112916.json](/output/tuscaloosa/suiteonemedia_20260424_112916.json) | JSON | 96,372 | 0 | 0 | 96,372 |
| [output/tuscaloosa/suiteonemedia\_20260424\_144825.json](/output/tuscaloosa/suiteonemedia_20260424_144825.json) | JSON | 96,338 | 0 | 0 | 96,338 |
| [output/tuscaloosa/suiteonemedia\_20260424\_224908.json](/output/tuscaloosa/suiteonemedia_20260424_224908.json) | JSON | 96,531 | 0 | 0 | 96,531 |
| [output/tuscaloosa\_city\_schools/eboard\_20260423\_223435.json](/output/tuscaloosa_city_schools/eboard_20260423_223435.json) | JSON | 1 | 0 | 0 | 1 |
| [output/tuscaloosa\_city\_schools/eboard\_20260423\_224726.json](/output/tuscaloosa_city_schools/eboard_20260423_224726.json) | JSON | 1 | 0 | 0 | 1 |
| [output/tuscaloosa\_city\_schools/eboard\_20260423\_224818.json](/output/tuscaloosa_city_schools/eboard_20260423_224818.json) | JSON | 1 | 0 | 0 | 1 |
| [output/tuscaloosa\_city\_schools/eboard\_20260423\_231344.json](/output/tuscaloosa_city_schools/eboard_20260423_231344.json) | JSON | 1 | 0 | 0 | 1 |
| [output/tuscaloosa\_city\_schools/eboard\_20260423\_231421.json](/output/tuscaloosa_city_schools/eboard_20260423_231421.json) | JSON | 1 | 0 | 0 | 1 |
| [output/tuscaloosa\_city\_schools/eboard\_20260423\_231511.json](/output/tuscaloosa_city_schools/eboard_20260423_231511.json) | JSON | 1 | 0 | 0 | 1 |
| [output/tuscaloosa\_city\_schools/eboard\_20260424\_151807.json](/output/tuscaloosa_city_schools/eboard_20260424_151807.json) | JSON | 1 | 0 | 0 | 1 |
| [output/tuscaloosa\_city\_schools/eboard\_20260424\_155458.json](/output/tuscaloosa_city_schools/eboard_20260424_155458.json) | JSON | 1 | 0 | 0 | 1 |
| [output/tuscaloosa\_city\_schools/eboard\_20260424\_155609.json](/output/tuscaloosa_city_schools/eboard_20260424_155609.json) | JSON | 1 | 0 | 0 | 1 |
| [output/tuscaloosa\_city\_schools/generic\_20260423\_223006.json](/output/tuscaloosa_city_schools/generic_20260423_223006.json) | JSON | 1 | 0 | 0 | 1 |
| [pipeline/huggingface\_publisher.py](/pipeline/huggingface_publisher.py) | Python | 17 | 1 | 2 | 20 |
| [requirements.txt](/requirements.txt) | pip requirements | 8 | 1 | 1 | 10 |
| [scripts/discover\_tuscaloosa\_nonprofits.py](/scripts/discover_tuscaloosa_nonprofits.py) | Python | 79 | 19 | 21 | 119 |
| [scripts/run\_tuscaloosa\_pipeline.sh](/scripts/run_tuscaloosa_pipeline.sh) | Shell Script | 214 | 31 | 57 | 302 |
| [start-all.sh](/start-all.sh) | Shell Script | 116 | 21 | 31 | 168 |
| [stop-all.sh](/stop-all.sh) | Shell Script | 41 | 6 | 13 | 60 |
| [website/README.md](/website/README.md) | Markdown | 49 | 0 | 25 | 74 |
| [website/blog/authors.yml](/website/blog/authors.yml) | YAML | 23 | 1 | 2 | 26 |
| [website/blog/tags.yml](/website/blog/tags.yml) | YAML | 16 | 0 | 4 | 20 |
| [website/docs/dashboard.md](/website/docs/dashboard.md) | Markdown | 84 | 0 | 34 | 118 |
| [website/docs/data-sources/census-data.md](/website/docs/data-sources/census-data.md) | Markdown | 69 | 0 | 32 | 101 |
| [website/docs/data-sources/civic-tech-sources.md](/website/docs/data-sources/civic-tech-sources.md) | Markdown | 188 | 0 | 67 | 255 |
| [website/docs/data-sources/confirmed-datasets.md](/website/docs/data-sources/confirmed-datasets.md) | Markdown | 250 | 0 | 91 | 341 |
| [website/docs/data-sources/huggingface-datasets.md](/website/docs/data-sources/huggingface-datasets.md) | Markdown | 278 | 0 | 91 | 369 |
| [website/docs/data-sources/jurisdiction-discovery.md](/website/docs/data-sources/jurisdiction-discovery.md) | Markdown | 450 | 0 | 131 | 581 |
| [website/docs/data-sources/nonprofit-sources.md](/website/docs/data-sources/nonprofit-sources.md) | Markdown | 161 | 0 | 64 | 225 |
| [website/docs/data-sources/open-source-repositories.md](/website/docs/data-sources/open-source-repositories.md) | Markdown | 281 | 0 | 90 | 371 |
| [website/docs/data-sources/overview.md](/website/docs/data-sources/overview.md) | Markdown | 191 | 0 | 67 | 258 |
| [website/docs/data-sources/url-datasets.md](/website/docs/data-sources/url-datasets.md) | Markdown | 155 | 0 | 50 | 205 |
| [website/docs/data-sources/video-channels.md](/website/docs/data-sources/video-channels.md) | Markdown | 458 | 0 | 151 | 609 |
| [website/docs/data-sources/video-sources.md](/website/docs/data-sources/video-sources.md) | Markdown | 313 | 0 | 125 | 438 |
| [website/docs/data-sources/youtube-discovery.md](/website/docs/data-sources/youtube-discovery.md) | Markdown | 337 | 0 | 102 | 439 |
| [website/docs/deployment/costs.md](/website/docs/deployment/costs.md) | Markdown | 176 | 0 | 61 | 237 |
| [website/docs/deployment/jurisdiction-discovery.md](/website/docs/deployment/jurisdiction-discovery.md) | Markdown | 150 | 0 | 60 | 210 |
| [website/docs/deployment/scale.md](/website/docs/deployment/scale.md) | Markdown | 410 | 0 | 126 | 536 |
| [website/docs/deployment/storage.md](/website/docs/deployment/storage.md) | Markdown | 389 | 0 | 159 | 548 |
| [website/docs/development/changelog.md](/website/docs/development/changelog.md) | Markdown | 112 | 0 | 38 | 150 |
| [website/docs/development/enhancements.md](/website/docs/development/enhancements.md) | Markdown | 175 | 0 | 79 | 254 |
| [website/docs/development/integration-status.md](/website/docs/development/integration-status.md) | Markdown | 172 | 0 | 58 | 230 |
| [website/docs/development/migration-v2.md](/website/docs/development/migration-v2.md) | Markdown | 193 | 0 | 77 | 270 |
| [website/docs/development/new-capabilities.md](/website/docs/development/new-capabilities.md) | Markdown | 256 | 0 | 89 | 345 |
| [website/docs/guides/accountability-strategy.md](/website/docs/guides/accountability-strategy.md) | Markdown | 178 | 0 | 76 | 254 |
| [website/docs/guides/document-libraries.md](/website/docs/guides/document-libraries.md) | Markdown | 118 | 0 | 44 | 162 |
| [website/docs/guides/handling-formats.md](/website/docs/guides/handling-formats.md) | Markdown | 508 | 0 | 152 | 660 |
| [website/docs/guides/huggingface-features.md](/website/docs/guides/huggingface-features.md) | Markdown | 186 | 0 | 76 | 262 |
| [website/docs/guides/huggingface-limits.md](/website/docs/guides/huggingface-limits.md) | Markdown | 338 | 0 | 111 | 449 |
| [website/docs/guides/huggingface-publishing.md](/website/docs/guides/huggingface-publishing.md) | Markdown | 318 | 0 | 129 | 447 |
| [website/docs/guides/huggingface-quickstart.md](/website/docs/guides/huggingface-quickstart.md) | Markdown | 290 | 0 | 112 | 402 |
| [website/docs/guides/impact-navigation.md](/website/docs/guides/impact-navigation.md) | Markdown | 249 | 0 | 100 | 349 |
| [website/docs/guides/jurisdiction-setup.md](/website/docs/guides/jurisdiction-setup.md) | Markdown | 408 | 0 | 151 | 559 |
| [website/docs/guides/political-economy.md](/website/docs/guides/political-economy.md) | Markdown | 266 | 0 | 89 | 355 |
| [website/docs/guides/scraper-improvements.md](/website/docs/guides/scraper-improvements.md) | Markdown | 234 | 0 | 71 | 305 |
| [website/docs/guides/search-patterns.md](/website/docs/guides/search-patterns.md) | Markdown | 684 | 0 | 170 | 854 |
| [website/docs/guides/split-screen.md](/website/docs/guides/split-screen.md) | Markdown | 293 | 0 | 81 | 374 |
| [website/docs/integrations/dataverse-summary.md](/website/docs/integrations/dataverse-summary.md) | Markdown | 170 | 0 | 57 | 227 |
| [website/docs/integrations/dataverse.md](/website/docs/integrations/dataverse.md) | Markdown | 334 | 0 | 112 | 446 |
| [website/docs/integrations/eboard-automated.md](/website/docs/integrations/eboard-automated.md) | Markdown | 304 | 0 | 98 | 402 |
| [website/docs/integrations/eboard-cookies.md](/website/docs/integrations/eboard-cookies.md) | Markdown | 184 | 0 | 63 | 247 |
| [website/docs/integrations/eboard-manual.md](/website/docs/integrations/eboard-manual.md) | Markdown | 95 | 0 | 31 | 126 |
| [website/docs/integrations/frontend.md](/website/docs/integrations/frontend.md) | Markdown | 332 | 0 | 113 | 445 |
| [website/docs/integrations/localview.md](/website/docs/integrations/localview.md) | Markdown | 177 | 0 | 76 | 253 |
| [website/docs/integrations/overview.md](/website/docs/integrations/overview.md) | Markdown | 450 | 0 | 107 | 557 |
| [website/docs/intro.md](/website/docs/intro.md) | Markdown | 124 | 0 | 54 | 178 |
| [website/docusaurus.config.ts](/website/docusaurus.config.ts) | TypeScript | 134 | 16 | 11 | 161 |
| [website/package-lock.json](/website/package-lock.json) | JSON | 19,524 | 0 | 1 | 19,525 |
| [website/package.json](/website/package.json) | JSON | 49 | 0 | 1 | 50 |
| [website/sidebars.ts](/website/sidebars.ts) | TypeScript | 58 | 0 | 3 | 61 |
| [website/src/components/HomepageFeatures/index.tsx](/website/src/components/HomepageFeatures/index.tsx) | TypeScript JSX | 67 | 0 | 5 | 72 |
| [website/src/components/HomepageFeatures/styles.module.css](/website/src/components/HomepageFeatures/styles.module.css) | PostCSS | 10 | 0 | 2 | 12 |
| [website/src/css/custom.css](/website/src/css/custom.css) | PostCSS | 101 | 16 | 19 | 136 |
| [website/src/pages/dashboard.tsx](/website/src/pages/dashboard.tsx) | TypeScript JSX | 117 | 2 | 10 | 129 |
| [website/src/pages/index.module.css](/website/src/pages/index.module.css) | PostCSS | 16 | 4 | 4 | 24 |
| [website/src/pages/index.tsx](/website/src/pages/index.tsx) | TypeScript JSX | 165 | 0 | 10 | 175 |
| [website/static/img/logo.svg](/website/static/img/logo.svg) | XML | 1 | 0 | 0 | 1 |
| [website/static/img/undraw\_docusaurus\_mountain.svg](/website/static/img/undraw_docusaurus_mountain.svg) | XML | 171 | 0 | 1 | 172 |
| [website/static/img/undraw\_docusaurus\_react.svg](/website/static/img/undraw_docusaurus_react.svg) | XML | 170 | 0 | 1 | 171 |
| [website/static/img/undraw\_docusaurus\_tree.svg](/website/static/img/undraw_docusaurus_tree.svg) | XML | 40 | 0 | 1 | 41 |
| [website/tsconfig.json](/website/tsconfig.json) | JSON with Comments | 9 | 3 | 1 | 13 |

[Summary](results.md) / [Details](details.md) / [Diff Summary](diff.md) / Diff Details