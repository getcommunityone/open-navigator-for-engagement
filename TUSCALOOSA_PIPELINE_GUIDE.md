# Tuscaloosa Policy Pulse Pipeline Guide

This guide shows how to run the complete 4-step pipeline for Tuscaloosa, AL.

## Prerequisites

```bash
source .venv/bin/activate
cd /home/developer/projects/oral-health-policy-pulse
```

---

## Step 1: GATHER - Collect Meeting Data

### 1.1 Tuscaloosa City Government (✅ Working)

```bash
python main.py scrape \
  --state AL \
  --municipality "Tuscaloosa" \
  --url https://tuscaloosaal.suiteonemedia.com \
  --platform suiteonemedia \
  --max-events 0 \
  --start-year 0 \
  --include-social
```

**Output:** `output/tuscaloosa/suiteonemedia_*.json`

### 1.2 Tuscaloosa City Schools (⚠️ Requires Manual Cookies)

The eBoard platform requires browser cookies to bypass Incapsula protection:

1. Visit https://simbli.eboardsolutions.com/SB_Meetings/SB_MeetingListing.aspx?S=2088
2. Complete any verification
3. Export cookies with [EditThisCookie](https://chrome.google.com/webstore/detail/editthiscookie/fngmhnnpilhplaeedifhccceomclgfbg)
4. Save to `eboard_cookies.json`

Then run:

```bash
python main.py scrape \
  --state AL \
  --municipality "Tuscaloosa City Schools" \
  --url http://simbli.eboardsolutions.com/index.aspx?s=2088 \
  --platform eboard \
  --max-events 0 \
  --start-year 0 \
  --no-include-social
```

**Output:** `output/tuscaloosa_city_schools/eboard_*.json`

### 1.3 Consolidate Data

Combine all Tuscaloosa sources:

```bash
python -c "
import json
from pathlib import Path

# Load all Tuscaloosa documents
all_docs = []
for json_file in Path('output/tuscaloosa').glob('*.json'):
    with open(json_file) as f:
        docs = json.load(f)
        all_docs.extend(docs)

for json_file in Path('output/tuscaloosa_city_schools').glob('*.json'):
    with open(json_file) as f:
        docs = json.load(f)
        all_docs.extend(docs)

print(f'✓ Gathered {len(all_docs)} documents from Tuscaloosa')

# Save consolidated data
with open('output/tuscaloosa_all.json', 'w') as f:
    json.dump(all_docs, f, indent=2)
"
```

---

## Step 2: STRUCTURE - Process with AI

### 2.1 Load Data into Delta Lake (Bronze Layer)

```python
from pipeline.delta_lake import DeltaLakePipeline
import json

pipeline = DeltaLakePipeline()

# Load raw documents
with open('output/tuscaloosa_all.json') as f:
    documents = json.load(f)

# Write to Bronze layer (raw data)
pipeline.write_raw_documents(documents)

print(f"✓ Loaded {len(documents)} documents to Bronze layer")
```

### 2.2 Classify Documents (Silver Layer)

Run the classifier agent to tag documents by topic:

```bash
python -c "
import asyncio
from agents.classifier import ClassifierAgent
from pipeline.delta_lake import DeltaLakePipeline

async def classify_tuscaloosa():
    pipeline = DeltaLakePipeline()
    classifier = ClassifierAgent()
    
    # Get documents from Bronze
    spark = pipeline.get_spark_session()
    df = spark.read.format('delta').load('data/delta/bronze/documents')
    
    # Filter to Tuscaloosa only
    tuscaloosa_df = df.filter(
        (df.municipality.like('%Tuscaloosa%')) | 
        (df.state == 'AL')
    )
    
    documents = tuscaloosa_df.collect()
    print(f'Classifying {len(documents)} Tuscaloosa documents...')
    
    classified = []
    for doc in documents:
        result = await classifier.classify(
            content=doc.content,
            municipality=doc.municipality
        )
        classified.append({**doc.asDict(), **result})
    
    # Write to Silver layer
    pipeline.write_classified_documents(classified)
    print(f'✓ Classified {len(classified)} documents')

asyncio.run(classify_tuscaloosa())
"
```

**Classifications include:**
- Health policy topics (dental health, vaccination, nutrition, etc.)
- Education topics
- Budget/finance
- Infrastructure
- Public safety

### 2.3 Sentiment Analysis (Silver Layer)

```bash
python -c "
import asyncio
from agents.sentiment import SentimentAgent
from pipeline.delta_lake import DeltaLakePipeline

async def analyze_sentiment():
    pipeline = DeltaLakePipeline()
    sentiment_agent = SentimentAgent()
    
    # Get classified documents
    spark = pipeline.get_spark_session()
    df = spark.read.format('delta').load('data/delta/silver/classified_documents')
    
    tuscaloosa_df = df.filter(df.municipality.like('%Tuscaloosa%'))
    documents = tuscaloosa_df.collect()
    
    print(f'Analyzing sentiment for {len(documents)} documents...')
    
    enriched = []
    for doc in documents:
        sentiment = await sentiment_agent.analyze(doc.content)
        enriched.append({**doc.asDict(), 'sentiment': sentiment})
    
    pipeline.write_enriched_documents(enriched)
    print(f'✓ Sentiment analysis complete')

asyncio.run(analyze_sentiment())
"
```

---

## Step 3: ANALYZE - Extract Insights

### 3.1 Health Policy Analysis

Find all health-related policies in Tuscaloosa:

```python
from pipeline.delta_lake import DeltaLakePipeline

pipeline = DeltaLakePipeline()
spark = pipeline.get_spark_session()

# Query Gold layer
df = spark.read.format('delta').load('data/delta/gold/policy_insights')

# Filter to health topics in Tuscaloosa
health_df = df.filter(
    (df.municipality.like('%Tuscaloosa%')) &
    (df.topic.isin(['dental_health', 'health', 'vaccination', 'nutrition']))
)

# Aggregate by topic
summary = health_df.groupBy('topic').agg(
    {'document_id': 'count', 'sentiment_score': 'avg'}
).collect()

print("\n=== Tuscaloosa Health Policy Summary ===")
for row in summary:
    print(f"{row.topic}: {row['count(document_id)']} documents, "
          f"avg sentiment: {row['avg(sentiment_score)']:.2f}")
```

### 3.2 Time Series Analysis

Track policy trends over time:

```python
from pyspark.sql.functions import year, month, count

df = spark.read.format('delta').load('data/delta/gold/policy_insights')

tuscaloosa_df = df.filter(df.municipality.like('%Tuscaloosa%'))

# Group by year and topic
trends = tuscaloosa_df.groupBy(
    year('meeting_date').alias('year'),
    month('meeting_date').alias('month'),
    'topic'
).agg(count('*').alias('count')).orderBy('year', 'month')

trends.show(50)
```

### 3.3 Cross-Jurisdiction Comparison

Compare Tuscaloosa to similar cities:

```python
# Find cities with similar population
similar_cities_df = df.filter(
    (df.state == 'AL') |  # Other Alabama cities
    (df.municipality.like('%Mobile%')) |
    (df.municipality.like('%Montgomery%'))
)

# Compare health policy volume
comparison = similar_cities_df.groupBy('municipality').agg(
    count('*').alias('total_policies'),
    countDistinct('topic').alias('unique_topics')
).orderBy('total_policies', ascending=False)

comparison.show()
```

---

## Step 4: DELIVER - Create Insights Products

### 4.1 Executive Briefing

Generate a policy briefing for Tuscaloosa leaders:

```bash
python -c "
from datetime import datetime, timedelta
from pipeline.delta_lake import DeltaLakePipeline

pipeline = DeltaLakePipeline()
spark = pipeline.get_spark_session()

df = spark.read.format('delta').load('data/delta/gold/policy_insights')

# Last 90 days
recent_date = datetime.now() - timedelta(days=90)
recent_df = df.filter(
    (df.municipality.like('%Tuscaloosa%')) &
    (df.meeting_date >= recent_date)
)

print('\\n' + '='*60)
print('TUSCALOOSA POLICY BRIEFING - Last 90 Days')
print('='*60)

# Top topics
topics = recent_df.groupBy('topic').count().orderBy('count', ascending=False).take(10)
print('\\nTop Policy Topics:')
for i, row in enumerate(topics, 1):
    print(f'{i}. {row.topic}: {row.count} items')

# Recent highlights
highlights = recent_df.orderBy('meeting_date', ascending=False).take(5)
print('\\nRecent Highlights:')
for doc in highlights:
    print(f'\\n- {doc.meeting_date.strftime(\"%Y-%m-%d\")}: {doc.title[:80]}')
    print(f'  Topic: {doc.topic}, Sentiment: {doc.sentiment}')
"
```

### 4.2 Searchable Dashboard Data

Export data for a web dashboard:

```bash
python -c "
import json
from pipeline.delta_lake import DeltaLakePipeline

pipeline = DeltaLakePipeline()
spark = pipeline.get_spark_session()

df = spark.read.format('delta').load('data/delta/gold/policy_insights')
tuscaloosa_df = df.filter(df.municipality.like('%Tuscaloosa%'))

# Convert to JSON for web dashboard
dashboard_data = []
for row in tuscaloosa_df.collect():
    dashboard_data.append({
        'id': row.document_id,
        'date': row.meeting_date.isoformat(),
        'title': row.title,
        'topic': row.topic,
        'sentiment': row.sentiment,
        'url': row.source_url,
        'municipality': row.municipality
    })

# Save for frontend
with open('frontend/src/data/tuscaloosa_policies.json', 'w') as f:
    json.dump(dashboard_data, f, indent=2)

print(f'✓ Exported {len(dashboard_data)} policies for dashboard')
"
```

### 4.3 Monitoring Alerts

Set up keyword monitoring for specific topics:

```bash
python -c "
from alerts.keyword_monitor import KeywordMonitor

monitor = KeywordMonitor()

# Monitor health-related keywords
health_keywords = [
    'dental', 'dentist', 'tooth', 'teeth', 'fluoride',
    'oral health', 'school nurse', 'vaccination', 'immunization'
]

monitor.watch_jurisdiction(
    municipality='Tuscaloosa',
    state='AL',
    keywords=health_keywords,
    alert_email='your-email@example.com'
)

print('✓ Monitoring alerts configured for Tuscaloosa health policies')
"
```

### 4.4 Publish to HuggingFace

Share Tuscaloosa data with researchers:

```bash
python main.py publish-to-hf --dataset tuscaloosa
```

This creates a public dataset at: `huggingface.co/datasets/your-org/tuscaloosa-policy-pulse`

---

## Quick Start: Run Complete Pipeline

```bash
#!/bin/bash
# complete_tuscaloosa_pipeline.sh

set -e

echo "=== TUSCALOOSA POLICY PULSE PIPELINE ==="

# Step 1: Gather
echo "Step 1: Gathering data..."
python main.py scrape \
  --state AL \
  --municipality "Tuscaloosa" \
  --url https://tuscaloosaal.suiteonemedia.com \
  --platform suiteonemedia \
  --max-events 0 \
  --start-year 0 \
  --include-social

# Note: eBoard scraping requires manual cookies (see Step 1.2 above)

# Step 2: Structure
echo "Step 2: Loading to Delta Lake..."
python -c "
from pipeline.delta_lake import DeltaLakePipeline
import json
from pathlib import Path

pipeline = DeltaLakePipeline()
all_docs = []

for json_file in Path('output/tuscaloosa').glob('*.json'):
    with open(json_file) as f:
        all_docs.extend(json.load(f))

pipeline.write_raw_documents(all_docs)
print(f'✓ Loaded {len(all_docs)} documents')
"

echo "Step 3: Classifying documents..."
python -c "
import asyncio
from agents.classifier import ClassifierAgent
from pipeline.delta_lake import DeltaLakePipeline

async def run():
    classifier = ClassifierAgent()
    pipeline = DeltaLakePipeline()
    spark = pipeline.get_spark_session()
    
    df = spark.read.format('delta').load('data/delta/bronze/documents')
    docs = df.filter(df.municipality.like('%Tuscaloosa%')).collect()
    
    classified = []
    for doc in docs:
        result = await classifier.classify(doc.content, doc.municipality)
        classified.append({**doc.asDict(), **result})
    
    pipeline.write_classified_documents(classified)
    print(f'✓ Classified {len(classified)} documents')

asyncio.run(run())
"

# Step 4: Deliver
echo "Step 4: Generating briefing..."
python -c "
from pipeline.delta_lake import DeltaLakePipeline

pipeline = DeltaLakePipeline()
spark = pipeline.get_spark_session()

df = spark.read.format('delta').load('data/delta/silver/classified_documents')
tuscaloosa = df.filter(df.municipality.like('%Tuscaloosa%'))

print('\\n=== TUSCALOOSA POLICY SUMMARY ===')
topics = tuscaloosa.groupBy('topic').count().orderBy('count', ascending=False)
topics.show()
"

echo "✓ Pipeline complete!"
```

---

## Monitoring & Maintenance

### Daily Updates

Run scraper daily to get new meetings:

```bash
# Add to crontab
0 6 * * * cd /home/developer/projects/oral-health-policy-pulse && source .venv/bin/activate && python main.py scrape --state AL --municipality Tuscaloosa --url https://tuscaloosaal.suiteonemedia.com --platform suiteonemedia --max-events 10
```

### View Current Status

```bash
python -c "
from pipeline.delta_lake import DeltaLakePipeline

pipeline = DeltaLakePipeline()
spark = pipeline.get_spark_session()

print('\\n=== DATA PIPELINE STATUS ===')
print('\\nBronze Layer (Raw):')
bronze = spark.read.format('delta').load('data/delta/bronze/documents')
print(f'  Total documents: {bronze.count()}')
print(f'  Tuscaloosa documents: {bronze.filter(bronze.municipality.like(\"%Tuscaloosa%\")).count()}')

print('\\nSilver Layer (Classified):')
silver = spark.read.format('delta').load('data/delta/silver/classified_documents')
print(f'  Total classified: {silver.count()}')
print(f'  Tuscaloosa classified: {silver.filter(silver.municipality.like(\"%Tuscaloosa%\")).count()}')
"
```

---

## Next Steps

1. **Expand Sources**: Add more Tuscaloosa data sources (school board, county commission, etc.)
2. **Deep Analysis**: Use LLM to extract specific policy details (budgets, votes, impacts)
3. **Build Dashboard**: Create interactive visualization with the frontend
4. **Set Alerts**: Monitor for specific keywords or topics
5. **Share Insights**: Publish findings to HuggingFace or local news outlets

For questions, see:
- [QUICKSTART.md](QUICKSTART.md) - General setup
- [docs/EBOARD_COOKIE_GUIDE.md](docs/EBOARD_COOKIE_GUIDE.md) - eBoard scraping
- [DATABRICKS_MIGRATION.md](DATABRICKS_MIGRATION.md) - Scaling to Databricks
