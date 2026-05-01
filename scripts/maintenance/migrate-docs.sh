#!/bin/bash

# Create organized directory structure
mkdir -p website/docs/guides
mkdir -p website/docs/data-sources
mkdir -p website/docs/integrations
mkdir -p website/docs/deployment
mkdir -p website/docs/development

# Data sources
cp docs/DATA_SOURCES.md website/docs/data-sources/overview.md
cp docs/JURISDICTION_DISCOVERY.md website/docs/data-sources/jurisdiction-discovery.md
cp docs/CENSUS_DATA_FIX.md website/docs/data-sources/census-data.md
cp docs/CIVIC_TECH_URL_SOURCES.md website/docs/data-sources/civic-tech-sources.md
cp docs/ANSWER_URL_DATASETS.md website/docs/data-sources/url-datasets.md
cp docs/URL_DATASETS_CONFIRMED.md website/docs/data-sources/confirmed-datasets.md
cp docs/HUGGINGFACE_DATASETS_ANALYSIS.md website/docs/data-sources/huggingface-datasets.md
cp docs/VIDEO_SOURCES_COMPLETE.md website/docs/data-sources/video-sources.md
cp docs/VIDEO_CHANNEL_DISCOVERY.md website/docs/data-sources/video-channels.md
cp docs/YOUTUBE_DISCOVERY_IMPROVEMENTS.md website/docs/data-sources/youtube-discovery.md

# Integrations
cp docs/INTEGRATION_GUIDE.md website/docs/integrations/overview.md
cp docs/FRONTEND_INTEGRATION_GUIDE.md website/docs/integrations/frontend.md
cp docs/DATAVERSE_INTEGRATION.md website/docs/integrations/dataverse.md
cp docs/DATAVERSE_INTEGRATION_SUMMARY.md website/docs/integrations/dataverse-summary.md
cp docs/LOCALVIEW_INTEGRATION_GUIDE.md website/docs/integrations/localview.md
cp docs/EBOARD_AUTOMATED_SOLUTIONS.md website/docs/integrations/eboard-automated.md
cp docs/EBOARD_COOKIE_GUIDE.md website/docs/integrations/eboard-cookies.md
cp docs/EBOARD_MANUAL_DOWNLOAD.md website/docs/integrations/eboard-manual.md

# Deployment
cp docs/JURISDICTION_DISCOVERY_DEPLOYMENT.md website/docs/deployment/jurisdiction-discovery.md
cp docs/RUNNING_DISCOVERY_AT_SCALE.md website/docs/deployment/scale.md
cp docs/COST_BREAKDOWN.md website/docs/deployment/costs.md
cp docs/COST_EFFECTIVE_STORAGE.md website/docs/deployment/storage.md

# Guides
cp docs/JURISDICTION_DISCOVERY_SETUP.md website/docs/guides/jurisdiction-setup.md
cp docs/ACCOUNTABILITY_DASHBOARD_STRATEGY.md website/docs/guides/accountability-strategy.md
cp docs/IMPACT_NAVIGATION_GUIDE.md website/docs/guides/impact-navigation.md
cp docs/POLITICAL_ECONOMY_ANALYSIS.md website/docs/guides/political-economy.md
cp docs/HANDLING_MULTIPLE_FORMATS.md website/docs/guides/handling-formats.md
cp docs/INSTALLING_DOCUMENT_LIBRARIES.md website/docs/guides/document-libraries.md
cp docs/SCRAPER_IMPROVEMENTS.md website/docs/guides/scraper-improvements.md
cp docs/SCALE_AND_SEARCH_PATTERNS.md website/docs/guides/search-patterns.md
cp docs/SPLIT_SCREEN_SYSTEM.md website/docs/guides/split-screen.md

# Development
cp docs/CHANGELOG_DISCOVERY_V2.md website/docs/development/changelog.md
cp docs/MIGRATION_SUMMARY_V2.md website/docs/development/migration-v2.md
cp docs/NEW_CAPABILITIES.md website/docs/development/new-capabilities.md
cp docs/ENHANCEMENT_OFFICIAL_SOURCES.md website/docs/development/enhancements.md
cp docs/INTEGRATION_STATUS.md website/docs/development/integration-status.md

# HuggingFace specific
cp docs/HUGGINGFACE_FEATURE_SUMMARY.md website/docs/guides/huggingface-features.md
cp docs/HUGGINGFACE_FILE_LIMITS.md website/docs/guides/huggingface-limits.md
cp docs/HUGGINGFACE_PUBLISHING.md website/docs/guides/huggingface-publishing.md
cp docs/HUGGINGFACE_QUICK_START.md website/docs/guides/huggingface-quickstart.md

echo "✅ Documentation migrated successfully!"
