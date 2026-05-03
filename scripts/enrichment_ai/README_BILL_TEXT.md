# Bill Text Extraction Scripts

This directory contains scripts for downloading and extracting bill text from various sources.

## Prerequisites

**For Alabama automatic fallback** (optional - only needed for AL bills with broken URLs):
```bash
# Install Playwright for web scraping
pip install playwright
playwright install chromium
```

Without Playwright, Alabama bills will skip the scraper fallback (but other states will work fine).

## Main Scripts

### `download_bill_text.py` - Primary Method (Fast)

**Use this for all states.** Downloads bill text using direct URLs from OpenStates database, with automatic fallback to web scraping for Alabama.

```bash
# Download all available states (including Alabama with automatic scraper fallback)
python scripts/enrichment_ai/download_bill_text.py --states AL,GA,IN,MA,WA,WI

# Download specific state and year
python scripts/enrichment_ai/download_bill_text.py --states GA --year 2024 --limit 100

# Download recent bills only
python scripts/enrichment_ai/download_bill_text.py --states AL,GA --year 2024
```

**Features:**
- ✅ Fast (direct PDF/HTML downloads)
- ✅ Works with PDF, HTML, and text formats
- ✅ Tries state APIs first (Georgia SOAP API)
- ✅ Falls back to URL downloads
- ✅ **NEW: Automatically uses Alabama scraper for failed Alabama URLs**
- ✅ Handles Alabama 2017-2022 bills with broken URLs automatically

**Output:** `data/gold/bills_bill_text.parquet`

---

### `download_alabama_bills_scraper.py` - Alabama Backup (Manual Use)

**This is now automatically invoked by `download_bill_text.py` as a fallback.** You can also run it manually for Alabama-specific batch processing.

```bash
# Scrape specific session (old bills with broken URLs)
python scripts/enrichment_ai/download_alabama_bills_scraper.py --session 2017rs --limit 10

# Scrape multiple sessions
python scripts/enrichment_ai/download_alabama_bills_scraper.py --sessions 2017rs,2018rs,2019rs

# Scrape specific bills
python scripts/enrichment_ai/download_alabama_bills_scraper.py --session 2019rs --bills HB1,HB10,SB5

# Show browser window (for debugging)
python scripts/enrichment_ai/download_alabama_bills_scraper.py --session 2017rs --limit 5 --show-browser
```

**When to use manually:**
- Batch processing many Alabama bills from a specific session
- Debugging scraper behavior with `--show-browser`
- When you want more control over Alabama-specific downloads

**Automatic use:**
- `download_bill_text.py` automatically invokes this for AL bills when URL download fails

**Features:**
- ✅ Works when direct URLs are unavailable
- ✅ Navigates ALISON web interface
- ✅ Filters by year/session
- ⚠️ Slow (needs browser automation)
- ⚠️ Requires Playwright browsers installed

**Output:** Appends to `data/gold/bills_bill_text.parquet`

---

## Bill Text Sources

### By State

| State | Direct URLs | API Available | Notes |
|-------|-------------|---------------|-------|
| **AL** | ✅ 2024-2026<br>❌ 2017-2022 | ❌ | **Automatic scraper fallback** for broken old URLs |
| **GA** | ✅ All years | ⚠️ Partial (404s) | Georgia SOAP API attempted, PDFs work |
| **IN** | ✅ Varies | ❌ | Depends on session |
| **MA** | ✅ Varies | ❌ | Depends on session |
| **WA** | ✅ Varies | ❌ | Depends on session |
| **WI** | ✅ All years | ❌ | HTML and PDF versions |

### Alabama URL Migration

Alabama legislature changed domains:

**OLD (BROKEN):** `http://alisondb.legislature.state.al.us`
- Sessions: 2017-2022
- Status: DNS lookup fails
- Solution: Use `download_alabama_bills_scraper.py`

**NEW (WORKING):** `https://alison.legislature.state.al.us`
- Sessions: 2024-2026
- Status: Direct PDF downloads work
- Solution: Use `download_bill_text.py`

---

## Output Format

Both scripts create/update: `data/gold/bills_bill_text.parquet`

**Schema:**
```
- bill_id: str (link to bills_bills.parquet)
- state: str (two-letter code)
- session: str (e.g., '2024rs', '2025_26')
- bill_number: str (e.g., 'HB 1', 'SB 10')
- version_note: str ('Introduced', 'Enrolled', etc.)
- text: str (full bill text in plain text)
- source_url: str (origin URL)
- source_type: str ('state_api', 'url_download', 'alison_scraper')
- extracted_date: str (ISO format timestamp)
- text_format: str ('txt', 'html', 'pdf')
- character_count: int
- word_count: int
```

**Storage:**
- Format: Parquet with zstd compression level 3
- Deduplication: By (bill_id, version_note)
- Location: `data/gold/bills_bill_text.parquet`

---

## Recommended Workflow

### Step 1: Download Accessible Bills (Fast)

```bash
# Download all states with working URLs
python scripts/enrichment_ai/download_bill_text.py --states AL,GA,IN,MA,WA,WI
```

This will:
- ✅ Download AL 2024-2026
- ✅ Download all GA, IN, MA, WA, WI bills
- ⚠️ Skip AL 2017-2022 (broken URLs)

### Step 2: Backfill Alabama 2017-2022 (Slow)

```bash
# Download old Alabama bills using web scraper
python scripts/enrichment_ai/download_alabama_bills_scraper.py \
  --sessions 2017rs,2018rs,2019rs,2020rs,2021rs,2022rs \
  --limit 100
```

This uses Playwright to navigate ALISON and download PDFs.

### Step 3: Verify Results

```bash
# Check what was downloaded
python -c "
import polars as pl
df = pl.read_parquet('data/gold/bills_bill_text.parquet')
print(f'Total bills: {len(df):,}')
print(f'\nBy state:')
print(df.group_by('state').agg(pl.count().alias('count')).sort('state'))
print(f'\nBy source type:')
print(df.group_by('source_type').agg(pl.count().alias('count')))
"
```

---

## Troubleshooting

### "Name or service not known" for Alabama

**Problem:** Old Alabama URLs (`alisondb.legislature.state.al.us`) are no longer accessible.

**Solution:** Use the scraper:
```bash
python scripts/enrichment_ai/download_alabama_bills_scraper.py --session 2017rs
```

### "Playwright browsers not installed"

**Problem:** Playwright needs browsers downloaded.

**Solution:**
```bash
playwright install chromium
```

### PDF extraction returns empty text

**Problem:** Some PDFs are scanned images without text.

**Solution:** These bills would need OCR (pytesseract), currently skipped.

### Slow scraping for Alabama

**Problem:** Web scraping is inherently slower than direct downloads.

**Optimization:**
- Use `--limit` to test with small batches
- Run overnight for large sessions
- Each bill takes ~2-3 seconds (navigation + download)

---

## Data Quality Notes

### Text Extraction Quality

| Format | Quality | Notes |
|--------|---------|-------|
| **PDF** | ✅ Excellent | Preserves line numbers, formatting |
| **HTML** | ✅ Good | Clean text, may lose some formatting |
| **Text** | ✅ Perfect | Already plain text |

### Known Issues

1. **Alabama 2017-2022**: Requires web scraping (slow)
2. **Georgia API**: Returns 404 for most bills (falls back to PDFs)
3. **PDF scans**: Some old bills are image-based (no text extraction)

### Coverage by State

Based on current data:
- **AL**: 13,305 bills (need scraper for 53% from 2017-2022)
- **GA**: 33,698 bills (PDFs work for all)
- **IN**: 12,502 bills
- **MA**: 75,217 bills  
- **WA**: 16,753 bills
- **WI**: 12,157 bills

**Total**: 163,632 bills across 6 states
