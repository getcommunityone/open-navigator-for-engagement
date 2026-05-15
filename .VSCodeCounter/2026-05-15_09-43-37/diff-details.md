# Diff Details

Date : 2026-05-15 09:43:37

Directory /home/developer/projects/open-navigator

Total : 42 files,  1416 codes, 254 comments, -196 blanks, all 1474 lines

[Summary](results.md) / [Details](details.md) / [Diff Summary](diff.md) / Diff Details

## Files
| filename | language | code | comment | blank | total |
| :--- | :--- | ---: | ---: | ---: | ---: |
| [agents/scraper.py](/agents/scraper.py) | Python | -1,505 | -286 | -323 | -2,114 |
| [api/static/assets/index-BqWDe\_X1.css](/api/static/assets/index-BqWDe_X1.css) | PostCSS | 1 | 0 | 1 | 2 |
| [api/static/assets/index-CQteqSZT.js](/api/static/assets/index-CQteqSZT.js) | JavaScript | 223 | 0 | 21 | 244 |
| [api/static/assets/index-D6f4KWLi.css](/api/static/assets/index-D6f4KWLi.css) | PostCSS | -1 | 0 | -1 | -2 |
| [api/static/assets/index-D7B1TH1H.js](/api/static/assets/index-D7B1TH1H.js) | JavaScript | -223 | 0 | -21 | -244 |
| [dbt\_project/macros/jurisdiction\_acs\_exists.sql](/dbt_project/macros/jurisdiction_acs_exists.sql) | MS SQL | -1 | 0 | 0 | -1 |
| [dbt\_project/macros/jurisdiction\_mapping\_primary\_from\_source\_columns.sql](/dbt_project/macros/jurisdiction_mapping_primary_from_source_columns.sql) | MS SQL | 8 | 0 | 1 | 9 |
| [dbt\_project/models/intermediate/\_intermediate.yml](/dbt_project/models/intermediate/_intermediate.yml) | YAML | 1 | 0 | 0 | 1 |
| [dbt\_project/models/intermediate/int\_jurisdiction\_websites.sql](/dbt_project/models/intermediate/int_jurisdiction_websites.sql) | MS SQL | 144 | 5 | 5 | 154 |
| [dbt\_project/models/intermediate/int\_jurisdictions.sql](/dbt_project/models/intermediate/int_jurisdictions.sql) | MS SQL | 26 | 1 | 1 | 28 |
| [dbt\_project/models/marts/\_marts.yml](/dbt_project/models/marts/_marts.yml) | YAML | -437 | 0 | -68 | -505 |
| [dbt\_project/models/marts/jurisdiction\_mapping\_analysis.sql](/dbt_project/models/marts/jurisdiction_mapping_analysis.sql) | MS SQL | 19 | 1 | 0 | 20 |
| [dbt\_project/models/marts/jurisdiction\_mapping\_quality\_summary.sql](/dbt_project/models/marts/jurisdiction_mapping_quality_summary.sql) | MS SQL | 2 | 0 | 0 | 2 |
| [dbt\_project/models/marts/jurisdiction\_mapping\_quality\_summary\_by\_acs\_income\_level.sql](/dbt_project/models/marts/jurisdiction_mapping_quality_summary_by_acs_income_level.sql) | MS SQL | 2 | 0 | 0 | 2 |
| [dbt\_project/models/marts/jurisdiction\_mapping\_quality\_summary\_by\_acs\_population\_tier.sql](/dbt_project/models/marts/jurisdiction_mapping_quality_summary_by_acs_population_tier.sql) | MS SQL | 2 | 0 | 0 | 2 |
| [dbt\_project/models/marts/jurisdiction\_mapping\_quality\_summary\_municipality\_places.sql](/dbt_project/models/marts/jurisdiction_mapping_quality_summary_municipality_places.sql) | MS SQL | 2 | 0 | 0 | 2 |
| [dbt\_project/models/staging/\_staging.yml](/dbt_project/models/staging/_staging.yml) | YAML | 1 | 0 | 1 | 2 |
| [frontend/src/components/DataExplorerLayout.tsx](/frontend/src/components/DataExplorerLayout.tsx) | TypeScript JSX | 14 | 0 | 0 | 14 |
| [frontend/src/index.css](/frontend/src/index.css) | PostCSS | 617 | 4 | 20 | 641 |
| [frontend/src/pages/JurisdictionMappingQualityPage.tsx](/frontend/src/pages/JurisdictionMappingQualityPage.tsx) | TypeScript JSX | -1,306 | 0 | -58 | -1,364 |
| [frontend/src/pages/jurisdiction-quality/EntityQualityDashboard.tsx](/frontend/src/pages/jurisdiction-quality/EntityQualityDashboard.tsx) | TypeScript JSX | 2,552 | 17 | 114 | 2,683 |
| [prompts/applying\_wicked\_to\_communityone.md](/prompts/applying_wicked_to_communityone.md) | Markdown | 21 | 0 | 21 | 42 |
| [scripts/datasources/census/download\_census\_acs\_data.py](/scripts/datasources/census/download_census_acs_data.py) | Python | -22 | 0 | -1 | -23 |
| [scripts/datasources/census/export\_census\_map\_static.py](/scripts/datasources/census/export_census_map_static.py) | Python | -16 | -2 | -4 | -22 |
| [scripts/datasources/census/load\_jurisdiction\_acs\_gold.py](/scripts/datasources/census/load_jurisdiction_acs_gold.py) | Python | -392 | -93 | -45 | -530 |
| [scripts/datasources/jurisdictions/export\_jurisdiction\_mapping\_quality\_json.py](/scripts/datasources/jurisdictions/export_jurisdiction_mapping_quality_json.py) | Python | 245 | 60 | -5 | 300 |
| [scripts/datasources/jurisdictions/state\_acs\_mapping\_quality.py](/scripts/datasources/jurisdictions/state_acs_mapping_quality.py) | Python | 309 | 21 | 42 | 372 |
| [scripts/datasources/leagueofcities/download\_league\_city\_directories.py](/scripts/datasources/leagueofcities/download_league_city_directories.py) | Python | 266 | 15 | 31 | 312 |
| [scripts/datasources/leagueofcities/load\_league\_city\_directories\_to\_bronze.py](/scripts/datasources/leagueofcities/load_league_city_directories_to_bronze.py) | Python | 395 | 471 | 36 | 902 |
| [scripts/datasources/wikidata/load\_jurisdictions\_wikidata\_colab.ipynb](/scripts/datasources/wikidata/load_jurisdictions_wikidata_colab.ipynb) | JSON | 4 | 0 | 1 | 5 |
| [scripts/datasources/youtube/backfill\_bronze\_youtube\_publish\_dates.py](/scripts/datasources/youtube/backfill_bronze_youtube_publish_dates.py) | Python | -31 | -4 | -1 | -36 |
| [scripts/datasources/youtube/run\_backfill\_priority\_states\_youtube.sh](/scripts/datasources/youtube/run_backfill_priority_states_youtube.sh) | Shell Script | -28 | -17 | -8 | -53 |
| [scripts/deployment/neon/migrations/026\_create\_public\_jurisdiction\_acs\_place.sql](/scripts/deployment/neon/migrations/026_create_public_jurisdiction_acs_place.sql) | MS SQL | -16 | -2 | -4 | -22 |
| [scripts/deployment/neon/migrations/027\_replace\_jurisdiction\_acs\_place\_with\_unified\_jurisdiction\_acs.sql](/scripts/deployment/neon/migrations/027_replace_jurisdiction_acs_place_with_unified_jurisdiction_acs.sql) | MS SQL | -32 | -3 | -8 | -43 |
| [scripts/deployment/neon/migrations/028\_add\_income\_level\_to\_jurisdiction\_acs.sql](/scripts/deployment/neon/migrations/028_add_income_level_to_jurisdiction_acs.sql) | MS SQL | -5 | -2 | -3 | -10 |
| [scripts/deployment/neon/migrations/029\_create\_bronze\_jurisdictions\_municipalities\_league.sql](/scripts/deployment/neon/migrations/029_create_bronze_jurisdictions_municipalities_league.sql) | MS SQL | 50 | 13 | 11 | 74 |
| [scripts/deployment/neon/migrations/030\_league\_bronze\_columns\_raw\_row.sql](/scripts/deployment/neon/migrations/030_league_bronze_columns_raw_row.sql) | MS SQL | 33 | 4 | 5 | 42 |
| [scripts/deployment/neon/migrations/031\_rename\_league\_state\_columns.sql](/scripts/deployment/neon/migrations/031_rename_league_state_columns.sql) | MS SQL | 23 | 3 | 2 | 28 |
| [scripts/discovery/comprehensive\_discovery\_pipeline\_meetings.py](/scripts/discovery/comprehensive_discovery_pipeline_meetings.py) | Python | 411 | 49 | 32 | 492 |
| [scripts/discovery/meetings\_platform\_heuristics.py](/scripts/discovery/meetings_platform_heuristics.py) | Python | 45 | 2 | 3 | 50 |
| [scripts/localview/scrape\_youtube\_channels.py](/scripts/localview/scrape_youtube_channels.py) | Python | -5 | -4 | 0 | -9 |
| [tests/test\_state\_acs\_mapping\_quality.py](/tests/test_state_acs_mapping_quality.py) | Python | 20 | 1 | 6 | 27 |

[Summary](results.md) / [Details](details.md) / [Diff Summary](diff.md) / Diff Details