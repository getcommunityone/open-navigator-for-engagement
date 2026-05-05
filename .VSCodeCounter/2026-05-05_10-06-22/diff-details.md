# Diff Details

Date : 2026-05-05 10:06:22

Directory /home/developer/projects/open-navigator

Total : 90 files,  5647 codes, 911 comments, 1404 blanks, all 7962 lines

[Summary](results.md) / [Details](details.md) / [Diff Summary](diff.md) / Diff Details

## Files
| filename | language | code | comment | blank | total |
| :--- | :--- | ---: | ---: | ---: | ---: |
| [.github/copilot-instructions.md](/.github/copilot-instructions.md) | Markdown | 33 | 0 | 7 | 40 |
| [dbt\_project/dbt\_project.yml](/dbt_project/dbt_project.yml) | YAML | 45 | 18 | 14 | 77 |
| [dbt\_project/macros/calculate\_confidence.sql](/dbt_project/macros/calculate_confidence.sql) | MS SQL | 11 | 8 | 1 | 20 |
| [dbt\_project/macros/normalize\_bill\_number.sql](/dbt_project/macros/normalize_bill_number.sql) | MS SQL | 14 | 11 | 1 | 26 |
| [dbt\_project/macros/normalize\_name.sql](/dbt_project/macros/normalize_name.sql) | MS SQL | 11 | 11 | 1 | 23 |
| [dbt\_project/models/intermediate/\_intermediate.yml](/dbt_project/models/intermediate/_intermediate.yml) | YAML | 19 | 0 | 2 | 21 |
| [dbt\_project/models/intermediate/int\_contacts\_deduped.sql](/dbt_project/models/intermediate/int_contacts_deduped.sql) | MS SQL | 37 | 10 | 4 | 51 |
| [dbt\_project/models/marts/\_marts.yml](/dbt_project/models/marts/_marts.yml) | YAML | 54 | 0 | 11 | 65 |
| [dbt\_project/models/marts/contacts\_search\_ai.sql](/dbt_project/models/marts/contacts_search_ai.sql) | MS SQL | 65 | 23 | 14 | 102 |
| [dbt\_project/models/staging/\_staging.yml](/dbt_project/models/staging/_staging.yml) | YAML | 97 | 0 | 9 | 106 |
| [dbt\_project/models/staging/stg\_bronze\_bills.sql](/dbt_project/models/staging/stg_bronze_bills.sql) | MS SQL | 38 | 12 | 12 | 62 |
| [dbt\_project/models/staging/stg\_bronze\_contacts.sql](/dbt_project/models/staging/stg_bronze_contacts.sql) | MS SQL | 41 | 15 | 14 | 70 |
| [dbt\_project/models/staging/stg\_bronze\_organizations.sql](/dbt_project/models/staging/stg_bronze_organizations.sql) | MS SQL | 37 | 15 | 15 | 67 |
| [neon/README.md](/neon/README.md) | Markdown | -252 | 0 | -65 | -317 |
| [neon/calculate\_stats\_only.py](/neon/calculate_stats_only.py) | Python | -131 | -21 | -40 | -192 |
| [neon/migrate.py](/neon/migrate.py) | Python | -814 | -97 | -168 | -1,079 |
| [neon/migrate\_bills.py](/neon/migrate_bills.py) | Python | -158 | -64 | -49 | -271 |
| [neon/regenerate\_bills\_map.py](/neon/regenerate_bills_map.py) | Python | -73 | -13 | -18 | -104 |
| [neon/schema.sql](/neon/schema.sql) | MS SQL | -290 | -77 | -80 | -447 |
| [neon/schema\_bills.sql](/neon/schema_bills.sql) | MS SQL | -35 | -13 | -12 | -60 |
| [neon/update\_stats.py](/neon/update_stats.py) | Python | -141 | -24 | -41 | -206 |
| [prompts/policy\_analysis.md](/prompts/policy_analysis.md) | Markdown | 37 | 0 | 2 | 39 |
| [scripts/datasources/census/acs\_ingestion.py](/scripts/datasources/census/acs_ingestion.py) | Python | -214 | -134 | -79 | -427 |
| [scripts/datasources/census/census\_ingestion.py](/scripts/datasources/census/census_ingestion.py) | Python | -217 | -110 | -61 | -388 |
| [scripts/datasources/census/download\_acs\_to\_d\_drive.py](/scripts/datasources/census/download_acs_to_d_drive.py) | Python | -232 | -75 | -66 | -373 |
| [scripts/datasources/census/download\_county\_mappings.py](/scripts/datasources/census/download_county_mappings.py) | Python | -147 | -64 | -50 | -261 |
| [scripts/datasources/census/download\_shapefiles.py](/scripts/datasources/census/download_shapefiles.py) | Python | -150 | -66 | -43 | -259 |
| [scripts/datasources/census/load\_acs.py](/scripts/datasources/census/load_acs.py) | Python | 214 | 134 | 79 | 427 |
| [scripts/datasources/census/load\_acs\_data.py](/scripts/datasources/census/load_acs_data.py) | Python | 232 | 75 | 66 | 373 |
| [scripts/datasources/census/load\_census.py](/scripts/datasources/census/load_census.py) | Python | 217 | 110 | 61 | 388 |
| [scripts/datasources/census/load\_county\_mappings.py](/scripts/datasources/census/load_county_mappings.py) | Python | 147 | 64 | 50 | 261 |
| [scripts/datasources/census/load\_shapefiles.py](/scripts/datasources/census/load_shapefiles.py) | Python | 150 | 66 | 43 | 259 |
| [scripts/datasources/fec/bulk\_download\_fec.py](/scripts/datasources/fec/bulk_download_fec.py) | Python | -302 | -141 | -70 | -513 |
| [scripts/datasources/fec/load\_fec\_bulk.py](/scripts/datasources/fec/load_fec_bulk.py) | Python | 302 | 141 | 70 | 513 |
| [scripts/datasources/gemini/README.md](/scripts/datasources/gemini/README.md) | Markdown | 198 | 0 | 58 | 256 |
| [scripts/datasources/gemini/README\_BRONZE\_MERGE.md](/scripts/datasources/gemini/README_BRONZE_MERGE.md) | Markdown | 183 | 0 | 63 | 246 |
| [scripts/datasources/gemini/analyze\_meeting\_transcripts.py](/scripts/datasources/gemini/analyze_meeting_transcripts.py) | Python | -501 | -188 | -49 | -738 |
| [scripts/datasources/gemini/cleanup\_null\_records.py](/scripts/datasources/gemini/cleanup_null_records.py) | Python | -88 | -20 | -35 | -143 |
| [scripts/datasources/gemini/compare\_model\_extractions.py](/scripts/datasources/gemini/compare_model_extractions.py) | Python | 162 | 37 | 42 | 241 |
| [scripts/datasources/gemini/entity\_resolution.py](/scripts/datasources/gemini/entity_resolution.py) | Python | 228 | 122 | 93 | 443 |
| [scripts/datasources/gemini/extract\_to\_bronze.py](/scripts/datasources/gemini/extract_to_bronze.py) | Python | -530 | -54 | -70 | -654 |
| [scripts/datasources/gemini/load\_meeting\_transcripts.py](/scripts/datasources/gemini/load_meeting_transcripts.py) | Python | 501 | 188 | 49 | 738 |
| [scripts/datasources/gemini/load\_meeting\_transcripts\_bronze.py](/scripts/datasources/gemini/load_meeting_transcripts_bronze.py) | Python | 670 | 54 | 70 | 794 |
| [scripts/datasources/gemini/merge\_bronze\_to\_production.py](/scripts/datasources/gemini/merge_bronze_to_production.py) | Python | 356 | 65 | 68 | 489 |
| [scripts/datasources/gemini/migrations/README.md](/scripts/datasources/gemini/migrations/README.md) | Markdown | 65 | 0 | 28 | 93 |
| [scripts/datasources/gemini/migrations/backfill\_ntee\_from\_arguments.py](/scripts/datasources/gemini/migrations/backfill_ntee_from_arguments.py) | Python | 139 | 16 | 23 | 178 |
| [scripts/datasources/gemini/migrations/backfill\_ntee\_to\_topics.py](/scripts/datasources/gemini/migrations/backfill_ntee_to_topics.py) | Python | 108 | 15 | 20 | 143 |
| [scripts/datasources/gemini/migrations/cleanup\_null\_records.py](/scripts/datasources/gemini/migrations/cleanup_null_records.py) | Python | 88 | 20 | 35 | 143 |
| [scripts/datasources/gemini/migrations/infer\_ntee\_from\_topics.py](/scripts/datasources/gemini/migrations/infer_ntee_from_topics.py) | Python | 144 | 16 | 30 | 190 |
| [scripts/datasources/gemini/migrations/migrate\_add\_ntee\_to\_topics.py](/scripts/datasources/gemini/migrations/migrate_add_ntee_to_topics.py) | Python | 109 | 17 | 22 | 148 |
| [scripts/datasources/gemini/migrations/migrate\_add\_secondary\_ntee.py](/scripts/datasources/gemini/migrations/migrate_add_secondary_ntee.py) | Python | 102 | 8 | 20 | 130 |
| [scripts/datasources/gemini/migrations/migrate\_multimodel\_support.py](/scripts/datasources/gemini/migrations/migrate_multimodel_support.py) | Python | 154 | 158 | 31 | 343 |
| [scripts/datasources/gemini/migrations/repopulate\_ntee\_codes.py](/scripts/datasources/gemini/migrations/repopulate_ntee_codes.py) | Python | 293 | 40 | 53 | 386 |
| [scripts/datasources/gemini/moa\_synthesize.py](/scripts/datasources/gemini/moa_synthesize.py) | Python | 273 | 155 | 41 | 469 |
| [scripts/datasources/hifld/download\_arcgis\_dataset.py](/scripts/datasources/hifld/download_arcgis_dataset.py) | Python | -193 | -88 | -52 | -333 |
| [scripts/datasources/hifld/load\_arcgis\_hifld.py](/scripts/datasources/hifld/load_arcgis_hifld.py) | Python | 193 | 88 | 52 | 333 |
| [scripts/datasources/irs/irs\_bmf\_ingestion.py](/scripts/datasources/irs/irs_bmf_ingestion.py) | Python | -163 | -119 | -60 | -342 |
| [scripts/datasources/irs/load\_irs\_bmf.py](/scripts/datasources/irs/load_irs_bmf.py) | Python | 163 | 119 | 60 | 342 |
| [scripts/datasources/localview/download\_localview.py](/scripts/datasources/localview/download_localview.py) | Python | -74 | -16 | -22 | -112 |
| [scripts/datasources/localview/load\_localview.py](/scripts/datasources/localview/load_localview.py) | Python | 74 | 16 | 22 | 112 |
| [scripts/datasources/localview/load\_localview\_data.py](/scripts/datasources/localview/load_localview_data.py) | Python | 301 | 100 | 76 | 477 |
| [scripts/datasources/localview/localview\_ingestion.py](/scripts/datasources/localview/localview_ingestion.py) | Python | -301 | -100 | -76 | -477 |
| [scripts/datasources/meetingbank/load\_meetingbank.py](/scripts/datasources/meetingbank/load_meetingbank.py) | Python | 256 | 128 | 81 | 465 |
| [scripts/datasources/meetingbank/meetingbank\_ingestion.py](/scripts/datasources/meetingbank/meetingbank_ingestion.py) | Python | -256 | -128 | -81 | -465 |
| [scripts/datasources/nccs/bulk\_download\_nccs.py](/scripts/datasources/nccs/bulk_download_nccs.py) | Python | -515 | -149 | -105 | -769 |
| [scripts/datasources/nccs/load\_nccs\_bulk.py](/scripts/datasources/nccs/load_nccs_bulk.py) | Python | 515 | 149 | 105 | 769 |
| [scripts/datasources/nces/load\_nces.py](/scripts/datasources/nces/load_nces.py) | Python | 292 | 144 | 61 | 497 |
| [scripts/datasources/nces/nces\_ingestion.py](/scripts/datasources/nces/nces_ingestion.py) | Python | -292 | -144 | -61 | -497 |
| [scripts/datasources/ntee/README.md](/scripts/datasources/ntee/README.md) | Markdown | 163 | 0 | 49 | 212 |
| [scripts/datasources/ntee/\_\_init\_\_.py](/scripts/datasources/ntee/__init__.py) | Python | 0 | 10 | 1 | 11 |
| [scripts/datasources/ntee/load\_to\_postgres.py](/scripts/datasources/ntee/load_to_postgres.py) | Python | 183 | 49 | 57 | 289 |
| [scripts/datasources/openstates/bulk\_legislative\_download.py](/scripts/datasources/openstates/bulk_legislative_download.py) | Python | -293 | -153 | -82 | -528 |
| [scripts/datasources/openstates/download\_documents.py](/scripts/datasources/openstates/download_documents.py) | Python | -470 | -198 | -108 | -776 |
| [scripts/datasources/openstates/load\_openstates\_bulk.py](/scripts/datasources/openstates/load_openstates_bulk.py) | Python | 293 | 153 | 82 | 528 |
| [scripts/datasources/openstates/load\_openstates\_documents.py](/scripts/datasources/openstates/load_openstates_documents.py) | Python | 470 | 198 | 108 | 776 |
| [scripts/deployment/neon/README.md](/scripts/deployment/neon/README.md) | Markdown | 252 | 0 | 65 | 317 |
| [scripts/deployment/neon/calculate\_stats\_only.py](/scripts/deployment/neon/calculate_stats_only.py) | Python | 131 | 21 | 40 | 192 |
| [scripts/deployment/neon/migrate.py](/scripts/deployment/neon/migrate.py) | Python | 889 | 108 | 180 | 1,177 |
| [scripts/deployment/neon/migrate\_bills.py](/scripts/deployment/neon/migrate_bills.py) | Python | 158 | 64 | 49 | 271 |
| [scripts/deployment/neon/migrations/001\_add\_datasource\_fields.sql](/scripts/deployment/neon/migrations/001_add_datasource_fields.sql) | MS SQL | 178 | 52 | 59 | 289 |
| [scripts/deployment/neon/migrations/001\_add\_datasource\_fields\_rollback.sql](/scripts/deployment/neon/migrations/001_add_datasource_fields_rollback.sql) | MS SQL | 38 | 13 | 9 | 60 |
| [scripts/deployment/neon/regenerate\_bills\_map.py](/scripts/deployment/neon/regenerate_bills_map.py) | Python | 73 | 13 | 18 | 104 |
| [scripts/deployment/neon/schema.sql](/scripts/deployment/neon/schema.sql) | MS SQL | 287 | 81 | 77 | 445 |
| [scripts/deployment/neon/schema\_bills.sql](/scripts/deployment/neon/schema_bills.sql) | MS SQL | 35 | 13 | 12 | 60 |
| [scripts/deployment/neon/update\_stats.py](/scripts/deployment/neon/update_stats.py) | Python | 141 | 24 | 41 | 206 |
| [website/docs/development/ai-model-evaluation.md](/website/docs/development/ai-model-evaluation.md) | Markdown | 277 | 0 | 81 | 358 |
| [website/docs/development/ai-model-merging.md](/website/docs/development/ai-model-merging.md) | Markdown | 396 | 0 | 124 | 520 |
| [website/docs/development/backlog.md](/website/docs/development/backlog.md) | Markdown | 374 | 0 | 143 | 517 |
| [website/docs/development/bronze-to-production-merge.md](/website/docs/development/bronze-to-production-merge.md) | Markdown | 328 | 0 | 83 | 411 |
| [website/docs/development/dbt-etl-strategy.md](/website/docs/development/dbt-etl-strategy.md) | Markdown | 445 | 0 | 90 | 535 |

[Summary](results.md) / [Details](details.md) / [Diff Summary](diff.md) / Diff Details