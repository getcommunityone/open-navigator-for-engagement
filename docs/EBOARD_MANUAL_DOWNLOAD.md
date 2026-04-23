# eBoard Platform Manual Download Guide

## Issue: Incapsula Bot Protection

eBoard Solutions (https://simbli.eboardsolutions.com) uses **Incapsula** anti-bot protection that blocks automated scraping, even with advanced tools like Playwright. The platform requires manual interaction to access meeting documents.

## Affected School Districts

### Tuscaloosa City Schools
- **URL**: http://simbli.eboardsolutions.com/index.aspx?s=2088
- **Meetings**: http://simbli.eboardsolutions.com/SB_Meetings/SB_MeetingListing.aspx?S=2088

### Tuscaloosa County Schools
- **URL**: https://simbli.eboardsolutions.com/SB_Meetings/SB_MeetingListing.aspx?S=2092
- **Website**: https://www.tcss.net/board-of-education (links to eBoard)

## Manual Download Steps

### 1. Access Meeting Listings
1. Visit the meetings URL above in your browser
2. You'll see a calendar or list of board meetings
3. Each meeting shows the date and has document links

### 2. Download Documents
For each meeting:
- Click on the meeting date to view details
- Look for:
  - **Agenda** (usually PDF)
  - **Minutes** (usually PDF)
  - **Packets** (supporting materials)
- Right-click each document → "Save As"

### 3. Organize Downloads
Save files with naming pattern:
```
tuscaloosa_city_schools_YYYY-MM-DD_agenda.pdf
tuscaloosa_city_schools_YYYY-MM-DD_minutes.pdf
```

### 4. Import into System

Once downloaded, you can import them manually:

```python
from pipeline.delta_lake import DeltaLakePipeline
from agents.scraper import ScraperAgent
import asyncio

async def import_manual_pdfs(pdf_directory: str):
    """Import manually downloaded PDFs into the system."""
    scraper = ScraperAgent()
    async with scraper:
        documents = []
        
        for pdf_path in Path(pdf_directory).glob("*.pdf"):
            # Extract content from PDF
            content = await scraper._scrape_pdf_document(str(pdf_path))
            
            if content:
                # Parse filename for metadata
                parts = pdf_path.stem.split('_')
                date_str = parts[2] if len(parts) > 2 else ""
                doc_type = parts[3] if len(parts) > 3 else "document"
                
                doc = {
                    'document_id': hashlib.md5(str(pdf_path).encode()).hexdigest(),
                    'source_url': f'file://{pdf_path}',
                    'municipality': 'Tuscaloosa City Schools',
                    'state': 'AL',
                    'meeting_date': date_str,
                    'meeting_type': 'Board Meeting',
                    'title': pdf_path.stem,
                    'content': content,
                    'metadata': {'source': 'manual_download', 'platform': 'eboard'}
                }
                documents.append(doc)
        
        # Write to Delta Lake
        pipeline = DeltaLakePipeline()
        pipeline.write_raw_documents(documents)
        
        return documents

# Usage:
# asyncio.run(import_manual_pdfs('/path/to/downloaded/pdfs'))
```

## Alternative: RSS Feeds

Some eBoard installations offer RSS feeds or calendar exports:
1. Look for RSS icon on meetings page
2. Look for "Subscribe" or "Export to Calendar" options
3. These may bypass the web interface restrictions

## Future Enhancement Ideas

1. **Browser Extension**: Create a Chrome extension that scrapes while you browse
2. **API Discovery**: Research if eBoard has any undocumented APIs
3. **Selenium Grid**: Use residential proxy services for more sophisticated bot evasion
4. **Contact District**: Request bulk export of meeting documents directly

## Why Automation Fails

eBoard's Incapsula protection includes:
- Browser fingerprinting (detects headless browsers)
- IP reputation checking
- JavaScript challenges (requires full browser execution)
- Session tracking (blocks rapid sequential requests)
- Rate limiting per IP address

Even with Playwright running in visible mode, subsequent page navigations get blocked once the system detects automated patterns.

## Recommended Approach

For comprehensive school district data:
1. **Prioritize**: Focus on city government data (working well)
2. **Manual collection**: Download key school board meetings manually
3. **Selective import**: Import only the most relevant documents
4. **Direct contact**: Reach out to school district IT for data sharing agreement

## Status

- ✅ **Tuscaloosa City Government**: Automated scraping works (SuiteOne Media platform)
- ❌ **Tuscaloosa City Schools**: Manual download required (eBoard + Incapsula)
- ❌ **Tuscaloosa County Schools**: Manual download required (eBoard + Incapsula)
