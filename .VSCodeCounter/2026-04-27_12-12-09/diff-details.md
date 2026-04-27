# Diff Details

Date : 2026-04-27 12:12:09

Directory /home/developer/projects/oral-health-policy-pulse

Total : 76 files,  12569 codes, 909 comments, 2305 blanks, all 15783 lines

[Summary](results.md) / [Details](details.md) / [Diff Summary](diff.md) / Diff Details

## Files
| filename | language | code | comment | blank | total |
| :--- | :--- | ---: | ---: | ---: | ---: |
| [.github/copilot-instructions.md](/.github/copilot-instructions.md) | Markdown | 38 | 0 | 11 | 49 |
| [.github/workflows/ci-build-test.yml](/.github/workflows/ci-build-test.yml) | YAML | 118 | 5 | 26 | 149 |
| [.github/workflows/deploy-huggingface.yml](/.github/workflows/deploy-huggingface.yml) | YAML | 51 | 2 | 10 | 63 |
| [.huggingface/nginx.conf](/.huggingface/nginx.conf) | Properties | 17 | 3 | 3 | 23 |
| [CITATIONS.md](/CITATIONS.md) | Markdown | 219 | 0 | 26 | 245 |
| [README.md](/README.md) | Markdown | 2 | 0 | 1 | 3 |
| [api/routes/auth.py](/api/routes/auth.py) | Python | 4 | 5 | 2 | 11 |
| [api/static/assets/index-BapuPuQU.js](/api/static/assets/index-BapuPuQU.js) | JavaScript | 172 | 0 | 1 | 173 |
| [api/static/assets/index-TOmu9Lxc.css](/api/static/assets/index-TOmu9Lxc.css) | PostCSS | 1 | 0 | 1 | 2 |
| [api/static/index.html](/api/static/index.html) | HTML | 17 | 0 | 1 | 18 |
| [config/settings.py](/config/settings.py) | Python | 3 | 1 | 1 | 5 |
| [deploy-huggingface.sh](/deploy-huggingface.sh) | Shell Script | 84 | 7 | 5 | 96 |
| [discovery/ballotpedia\_integration.py](/discovery/ballotpedia_integration.py) | Python | 361 | 215 | 104 | 680 |
| [discovery/dbpedia\_integration.py](/discovery/dbpedia_integration.py) | Python | 226 | 167 | 24 | 417 |
| [discovery/google\_civic\_integration.py](/discovery/google_civic_integration.py) | Python | 225 | 100 | 64 | 389 |
| [discovery/google\_data\_commons.py](/discovery/google_data_commons.py) | Python | 162 | 119 | 40 | 321 |
| [discovery/wikidata\_integration.py](/discovery/wikidata_integration.py) | Python | 247 | 182 | 33 | 462 |
| [docs/API\_INTEGRATION\_STATUS.md](/docs/API_INTEGRATION_STATUS.md) | Markdown | 364 | 0 | 110 | 474 |
| [docs/OAUTH\_HUGGINGFACE\_FIX.md](/docs/OAUTH_HUGGINGFACE_FIX.md) | Markdown | 189 | 0 | 57 | 246 |
| [docs/SOCIAL\_FEATURES.md](/docs/SOCIAL_FEATURES.md) | Markdown | 376 | 0 | 99 | 475 |
| [frontend/src/App.tsx](/frontend/src/App.tsx) | TypeScript JSX | 6 | 3 | 2 | 11 |
| [frontend/src/components/Layout.tsx](/frontend/src/components/Layout.tsx) | TypeScript JSX | 45 | 2 | 2 | 49 |
| [frontend/src/contexts/AuthContext.tsx](/frontend/src/contexts/AuthContext.tsx) | TypeScript JSX | -32 | -1 | -4 | -37 |
| [frontend/src/index.css](/frontend/src/index.css) | PostCSS | 10 | 0 | 1 | 11 |
| [frontend/src/pages/Explore.tsx](/frontend/src/pages/Explore.tsx) | TypeScript JSX | 346 | 24 | 26 | 396 |
| [frontend/src/pages/HomeModern.tsx](/frontend/src/pages/HomeModern.tsx) | TypeScript JSX | 698 | 33 | 49 | 780 |
| [frontend/tsconfig.json](/frontend/tsconfig.json) | JSON with Comments | 1 | 0 | 0 | 1 |
| [requirements.txt](/requirements.txt) | pip requirements | 0 | 6 | 1 | 7 |
| [scripts/upload\_to\_huggingface.py](/scripts/upload_to_huggingface.py) | Python | 0 | 1 | 0 | 1 |
| [setup-git-hooks.sh](/setup-git-hooks.sh) | Shell Script | 24 | 5 | 6 | 35 |
| [test-huggingface-build.sh](/test-huggingface-build.sh) | Shell Script | 130 | 13 | 26 | 169 |
| [website/blog/2026-04-06-data-model-expansion.md](/website/blog/2026-04-06-data-model-expansion.md) | Markdown | 57 | 0 | 25 | 82 |
| [website/blog/2026-04-13-citations-migration.md](/website/blog/2026-04-13-citations-migration.md) | Markdown | 92 | 0 | 31 | 123 |
| [website/blog/2026-04-20-homepage-navigation-fixes.md](/website/blog/2026-04-20-homepage-navigation-fixes.md) | Markdown | 122 | 0 | 39 | 161 |
| [website/blog/authors.yml](/website/blog/authors.yml) | YAML | -15 | -1 | 0 | -16 |
| [website/blog/tags.yml](/website/blog/tags.yml) | YAML | 12 | 0 | 4 | 16 |
| [website/docs/architecture.md](/website/docs/architecture.md) | Markdown | 1 | 0 | 0 | 1 |
| [website/docs/dashboard.md](/website/docs/dashboard.md) | Markdown | 2 | 0 | 0 | 2 |
| [website/docs/data-sources/ballot-election-sources.md](/website/docs/data-sources/ballot-election-sources.md) | Markdown | 304 | 0 | 73 | 377 |
| [website/docs/data-sources/census-data.md](/website/docs/data-sources/census-data.md) | Markdown | 3 | 0 | 1 | 4 |
| [website/docs/data-sources/citations.md](/website/docs/data-sources/citations.md) | Markdown | 1,212 | 0 | 328 | 1,540 |
| [website/docs/data-sources/data-model-erd.md](/website/docs/data-sources/data-model-erd.md) | Markdown | 2,830 | 0 | 385 | 3,215 |
| [website/docs/data-sources/factcheck-sources.md](/website/docs/data-sources/factcheck-sources.md) | Markdown | 522 | 0 | 127 | 649 |
| [website/docs/data-sources/huggingface-datasets.md](/website/docs/data-sources/huggingface-datasets.md) | Markdown | 3 | 0 | 1 | 4 |
| [website/docs/data-sources/jurisdiction-discovery.md](/website/docs/data-sources/jurisdiction-discovery.md) | Markdown | 3 | 0 | 1 | 4 |
| [website/docs/data-sources/nonprofit-sources.md](/website/docs/data-sources/nonprofit-sources.md) | Markdown | 3 | 0 | 1 | 4 |
| [website/docs/data-sources/open-source-repositories.md](/website/docs/data-sources/open-source-repositories.md) | Markdown | 3 | 0 | 1 | 4 |
| [website/docs/data-sources/overview.md](/website/docs/data-sources/overview.md) | Markdown | 10 | 0 | 3 | 13 |
| [website/docs/data-sources/polling-survey-sources.md](/website/docs/data-sources/polling-survey-sources.md) | Markdown | 411 | 0 | 117 | 528 |
| [website/docs/data-sources/url-datasets.md](/website/docs/data-sources/url-datasets.md) | Markdown | 3 | 0 | 1 | 4 |
| [website/docs/data-sources/video-channels.md](/website/docs/data-sources/video-channels.md) | Markdown | 3 | 0 | 1 | 4 |
| [website/docs/data-sources/video-sources.md](/website/docs/data-sources/video-sources.md) | Markdown | 3 | 0 | 1 | 4 |
| [website/docs/data-sources/youtube-discovery.md](/website/docs/data-sources/youtube-discovery.md) | Markdown | 3 | 0 | 1 | 4 |
| [website/docs/deployment/build-protection.md](/website/docs/deployment/build-protection.md) | Markdown | 246 | 0 | 88 | 334 |
| [website/docs/deployment/docker-troubleshooting.md](/website/docs/deployment/docker-troubleshooting.md) | Markdown | 279 | 0 | 103 | 382 |
| [website/docs/deployment/variable-migration.md](/website/docs/deployment/variable-migration.md) | Markdown | 121 | 0 | 56 | 177 |
| [website/docs/for-advocates.md](/website/docs/for-advocates.md) | Markdown | 13 | 0 | 3 | 16 |
| [website/docs/for-developers.md](/website/docs/for-developers.md) | Markdown | 15 | 0 | 3 | 18 |
| [website/docs/for-families.md](/website/docs/for-families.md) | Markdown | 317 | 0 | 97 | 414 |
| [website/docs/guides/accountability-strategy.md](/website/docs/guides/accountability-strategy.md) | Markdown | 3 | 0 | 1 | 4 |
| [website/docs/guides/enterprise-tech-integration.md](/website/docs/guides/enterprise-tech-integration.md) | Markdown | 213 | 0 | 85 | 298 |
| [website/docs/guides/impact-navigation.md](/website/docs/guides/impact-navigation.md) | Markdown | 3 | 0 | 1 | 4 |
| [website/docs/guides/political-economy.md](/website/docs/guides/political-economy.md) | Markdown | 3 | 0 | 1 | 4 |
| [website/docs/intro.md](/website/docs/intro.md) | Markdown | -140 | 0 | -54 | -194 |
| [website/docs/quick-reference.md](/website/docs/quick-reference.md) | Markdown | 1 | 0 | 0 | 1 |
| [website/docs/quickstart.md](/website/docs/quickstart.md) | Markdown | 1 | 0 | 0 | 1 |
| [website/docusaurus.config.ts](/website/docusaurus.config.ts) | TypeScript | 46 | 1 | 2 | 49 |
| [website/package-lock.json](/website/package-lock.json) | JSON | 1,278 | 0 | 0 | 1,278 |
| [website/package.json](/website/package.json) | JSON | 2 | 0 | 0 | 2 |
| [website/sidebars.ts](/website/sidebars.ts) | TypeScript | 201 | 5 | 2 | 208 |
| [website/src/components/ZoomableMermaid/index.tsx](/website/src/components/ZoomableMermaid/index.tsx) | TypeScript JSX | 64 | 0 | 3 | 67 |
| [website/src/components/ZoomableMermaid/styles.module.css](/website/src/components/ZoomableMermaid/styles.module.css) | PostCSS | 147 | 3 | 24 | 174 |
| [website/src/css/custom.css](/website/src/css/custom.css) | PostCSS | 95 | 9 | 18 | 122 |
| [website/src/pages/dashboard.tsx](/website/src/pages/dashboard.tsx) | TypeScript JSX | -45 | 0 | -2 | -47 |
| [website/src/pages/index.tsx](/website/src/pages/index.tsx) | TypeScript JSX | 2 | 0 | 0 | 2 |
| [website/test-admonition.md](/website/test-admonition.md) | Markdown | 13 | 0 | 5 | 18 |

[Summary](results.md) / [Details](details.md) / [Diff Summary](diff.md) / Diff Details