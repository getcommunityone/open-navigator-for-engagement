# AI Enrichment Scripts

Scripts for AI-powered legislative analysis using Intel Arc Graphics optimization.

## 🎯 What's Here

- **intel_llm_setup.sh** - One-command setup for Intel Arc GPU + NPU optimization
- **legislative_analysis_intel.py** - DuckDB + Llama for bill & testimony analysis
- **batch_analyze_bills.py** - Batch process bills with incremental support ⭐
- **query_analysis_results.py** - Query and export analysis results from Parquet ⭐
- **duckdb_vss_demo.py** - Vector similarity search benchmarking

## 📊 Data Pipeline Architecture

**Why Parquet + DuckDB?**

```
Source Data (Parquet)
    ↓
DuckDB Query Engine (10-100x faster than Postgres!)
    ↓
AI Analysis (Llama 3.2/3.3)
    ↓
Results (Parquet) ← Incremental appends, portable, version-controlled
```

**Benefits:**
- ✅ **Parquet storage** - portable, fast, works with Pandas/Spark/DuckDB
- ✅ **DuckDB queries** - no database server, 10-100x faster than Postgres
- ✅ **Incremental processing** - skip already-analyzed bills, resume after failures
- ✅ **Version control** - track analysis results in git (if small) or DVC

## ⚡ Your Hardware

You have: **Intel Core Ultra 7 165H**
- ✅ Arc Graphics (integrated GPU)
- ✅ NPU (Neural Processing Unit)
- ✅ Perfect for running Llama models locally

## 🚀 Quick Start

### 1. Run the Setup Script

```bash
cd /home/developer/projects/open-navigator
./scripts/enrichment_ai/intel_llm_setup.sh
```

This will:
- Create `.venv-intel` virtual environment
- Install Intel Extension for PyTorch (IPEX)
- Install OpenVINO for Arc GPU acceleration
- Install DuckDB with VSS (Vector Similarity Search)
- Install Llama model libraries

### 2. Activate the Environment

```bash
source .venv-intel/bin/activate
```

### 3. Run Demo (Shows Incremental Processing)

```bash
# See architecture and check for existing analysis
python scripts/enrichment_ai/legislative_analysis_intel.py
```

### 4. Batch Analyze Bills (Saves to Parquet!)

```bash
# Analyze 10 Georgia fluoride bills (incremental - skips already-analyzed)
python scripts/enrichment_ai/batch_analyze_bills.py --state GA --topic fluorid --limit 10

# Analyze 50 Alabama bills  
python scripts/enrichment_ai/batch_analyze_bills.py --state AL --limit 50

# Re-analyze everything (disable incremental)
python scripts/enrichment_ai/batch_analyze_bills.py --state GA --no-incremental
```

### 5. Query Results

```bash
# View analysis summary and recent results
python scripts/enrichment_ai/query_analysis_results.py

# Filter by state
python scripts/enrichment_ai/query_analysis_results.py --state GA

# Find specific organizations
python scripts/enrichment_ai/query_analysis_results.py --group "Dental Association"
```

**Using DuckDB CLI:**
```bash
# Show all results
duckdb -c "SELECT * FROM read_parquet('data/gold/analysis/interest_groups_analysis.parquet') LIMIT 5"

# Find opposing groups
duckdb -c "SELECT group_name, bill_id, stance_score FROM read_parquet('data/gold/analysis/*.parquet') WHERE stance='oppose' ORDER BY stance_score LIMIT 10"

# Export to CSV
duckdb -c "COPY (SELECT * FROM read_parquet('data/gold/analysis/*.parquet')) TO 'results.csv' (HEADER, DELIMITER ',')"
```

**Using Python/Pandas:**
```python
import pandas as pd

# Read Parquet directly
df = pd.read_parquet('data/gold/analysis/interest_groups_analysis.parquet')

# Filter and analyze
support = df[df['stance'] == 'support']
oppose = df[df['stance'] == 'oppose']

print(f"Supporting: {len(support)}, Opposing: {len(oppose)}")

# Export
df.to_csv('analysis_results.csv', index=False)
df.to_json('analysis_results.json', orient='records')
```

## 📦 What Gets Installed

The setup script installs from `requirements-intel.txt`:

**Core AI Libraries:**
- `intel-extension-for-pytorch` - GPU acceleration for Arc Graphics
- `optimum[openvino]` - Intel's optimized inference engine
- `transformers` - Hugging Face model library
- `sentence-transformers` - Embedding generation

**Database:**
- `duckdb` - Fast analytical queries (10-100x faster than Postgres)
- VSS extension - Vector similarity search with HNSW index

**Models Supported:**
- Llama 3.2 (3B, 8B models)
- Llama 3.3 (via Ollama)
- Any Hugging Face model

## 🎯 Performance Expectations

On your Intel Core Ultra 7 165H:

| Task | Speed |
|------|-------|
| LLM inference | 350-1,200 tokens/sec |
| Vector search (10K records) | ~18ms |
| Context injection (100 bills) | ~20ms |
| Full testimony analysis | ~80ms |

## ⚠️ Important Notes

**Did You Download the Right Bundle?**

✅ **YES** if you have:
- Intel Core Ultra 7 165H (you do!)
- Requirements file: `requirements-intel.txt` (you do!)
- Setup script: `intel_llm_setup.sh` (you do!)

❌ **NO** if you're using:
- `requirements.txt` (generic, no Intel optimization)
- `requirements-cpu.txt` (CPU-only, slower)

**Next Steps:**
1. Run `./scripts/enrichment_ai/intel_llm_setup.sh`
2. Activate with `source .venv-intel/bin/activate`
3. Test with vector search demo
4. Run legislative analysis

## 🔧 Environment Variables (Optional)

For maximum performance, set these before running:

```bash
export ZES_ENABLE_SYSMAN=1        # Enable GPU monitoring
export IPEX_LLM_NUM_GPU=1         # Use Arc Graphics
export OLLAMA_NUM_GPU=999         # If using Ollama
```

## 📖 Usage Examples

See the Python files for detailed examples:
- Vector search patterns
- LLM prompt engineering
- Structured data extraction
- Bill & testimony analysis
