# Civic Data API Integration Status

Status of major civic data APIs in the Open Navigator for Engagement platform.

## ✅ Fully Integrated APIs

### 1. Open States API ✅
**Status:** INTEGRATED  
**File:** `discovery/openstates_sources.py`  
**API Docs:** https://openstates.org/api/  
**What it provides:**
- 50+ state legislatures
- State-level officials
- Legislative bills and votes
- Committee information
- Video sources (YouTube, Vimeo, Granicus)

**Usage:**
```bash
# Set API key in .env
OPENSTATES_API_KEY=your-key-here

# Run ingestion
python -m discovery.openstates_sources
```

**API Key:** Free tier - 50,000 requests/month  
**Sign up:** https://openstates.org/accounts/signup/

---

### 2. NCES District Search ✅
**Status:** INTEGRATED  
**File:** `discovery/nces_ingestion.py`  
**Data Source:** https://nces.ed.gov/ccd/  
**What it provides:**
- 13,000+ school districts nationwide
- School district boundaries
- Contact information
- Enrollment and demographic data
- Physical addresses

**Usage:**
```bash
# Run ingestion (downloads CSV from NCES)
python -m discovery.nces_ingestion
```

**API Key:** Not required (public CSV downloads)

---

## 🚧 Partially Integrated

### 3. Ballotpedia ⚠️
**Status:** PARTIAL - Web scraping implemented (no official API)  
**File:** `discovery/ballotpedia_integration.py`  
**Website:** https://ballotpedia.org  
**What it provides:**
- Elected officials (federal, state, local)
- Ballot measures and initiatives
- Election results
- Candidate information

**Current Implementation:**
- ✅ Web scraping with rate limiting
- ✅ Leader search by name
- ✅ City officials discovery
- ✅ Ballot measures by state/year
- ❌ No official API (Ballotpedia doesn't offer free public API)

**Usage:**
```python
from discovery.ballotpedia_integration import BallotpediaDiscovery

discovery = BallotpediaDiscovery()

# Search for a leader
leader = await discovery.search_leader("Walt Maddox", "Alabama")

# Get city officials
officials = await discovery.get_city_officials("Tuscaloosa", "Alabama")

# Get ballot measures
measures = await discovery.get_ballot_measures("Alabama", year=2024)
```

**Notes:**
- Uses respectful web scraping (2-second delays between requests)
- For production use, contact Ballotpedia for data partnership
- Ballotpedia API page: https://ballotpedia.org/Ballotpedia_API (limited availability)

---

## ❌ Not Yet Integrated

### 4. Google Civic Information API ❌
**Status:** NOT INTEGRATED  
**API Docs:** https://developers.google.com/civic-information  
**What it would provide:**
- Address-to-representative mapping
- Elected officials by address
- Election data
- Polling locations
- Voter information

**Why integrate:**
- Best API for "who represents this address?"
- Official election information
- Comprehensive official contact info
- Free tier: 25,000 requests/day

**API Key Required:** Yes (Google Cloud Console)  
**Free Tier:** 25,000 requests/day  
**Sign up:** https://console.cloud.google.com/

**Next Steps:**
1. Create `discovery/google_civic_integration.py`
2. Add API key to `.env`: `GOOGLE_CIVIC_API_KEY=your-key`
3. Implement endpoints:
   - `representativeInfoByAddress(address)`
   - `elections()`
   - `voterInfoQuery(address)`

---

### 5. Cicero API ❌
**Status:** NOT INTEGRATED  
**API Docs:** https://cicerodata.com  
**What it would provide:**
- Local district boundaries (very accurate)
- Contact info for local officials
- Non-legislative officials (school boards, water districts, etc.)
- Real-time updates

**Why integrate:**
- Professional-grade district mapping
- Best source for local officials
- Includes special districts (school boards, water, transit, etc.)
- Very accurate boundary data

**API Key Required:** Yes (paid service)  
**Pricing:** Enterprise/professional (not free)  
**Sign up:** https://cicerodata.com/contact

**Next Steps:**
1. Evaluate cost vs. value (this is a paid service)
2. Consider for enterprise deployment
3. Alternative: Use Google Civic API + Ballotpedia (free)

---

## 📊 Integration Summary

| API | Status | Free? | File | Key Required? |
|-----|--------|-------|------|---------------|
| **Open States** | ✅ Integrated | Yes | `openstates_sources.py` | Yes (free) |
| **NCES** | ✅ Integrated | Yes | `nces_ingestion.py` | No |
| **Ballotpedia** | ⚠️ Partial | Yes | `ballotpedia_integration.py` | No (scraping) |
| **Google Civic** | ❌ Not Yet | Yes | - | Yes (free) |
| **Cicero** | ❌ Not Yet | No | - | Yes (paid) |

---

## 🎯 Recommended Integration Priority

### High Priority (Free + High Value)
1. ✅ **Open States** - Already done
2. ✅ **NCES** - Already done
3. ⚠️ **Ballotpedia** - Partial (web scraping works, needs cleanup)
4. 🔴 **Google Civic API** - Should integrate next (best for address→officials)

### Medium Priority (Value vs. Cost)
5. 🟡 **Cicero API** - Evaluate cost for enterprise deployment

---

## 🚀 Quick Start: Adding Google Civic API

The highest-value missing integration is **Google Civic Information API**.

### Step 1: Get API Key
```bash
# Visit Google Cloud Console
open https://console.cloud.google.com/

# Create project
# Enable "Google Civic Information API"
# Create API key
```

### Step 2: Add to Environment
```bash
# Add to .env
echo "GOOGLE_CIVIC_API_KEY=your-key-here" >> .env
```

### Step 3: Create Integration (stub provided below)
See `discovery/google_civic_integration.py` (to be created)

---

## 📝 Example: Google Civic Integration Stub

```python
"""
Google Civic Information API Integration

Best for address-to-representative mapping.

API: https://developers.google.com/civic-information
Free Tier: 25,000 requests/day
"""
import httpx
from typing import Dict, List, Optional
from loguru import logger
from config.settings import settings


class GoogleCivicAPI:
    BASE_URL = "https://www.googleapis.com/civicinfo/v2"
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.google_civic_api_key
    
    async def get_representatives(self, address: str) -> Dict:
        """Get elected officials for an address."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.BASE_URL}/representatives",
                params={"address": address, "key": self.api_key}
            )
            return response.json()
    
    async def get_elections(self) -> Dict:
        """Get upcoming elections."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.BASE_URL}/elections",
                params={"key": self.api_key}
            )
            return response.json()
```

---

## 🔍 What Each API is Best For

**Open States:** State legislature bills, votes, committees  
**NCES:** School district boundaries and demographics  
**Ballotpedia:** Elected officials, ballot measures, elections  
**Google Civic:** Address → representatives (best for this!)  
**Cicero:** Local district boundaries (enterprise-grade)

---

## 📚 Additional Resources

- **Open States Documentation:** https://docs.openstates.org/
- **NCES Common Core of Data:** https://nces.ed.gov/ccd/files.asp
- **Ballotpedia Sample Pages:** https://ballotpedia.org/Main_Page
- **Google Civic API Guide:** https://developers.google.com/civic-information/docs/using_api
- **Cicero Use Cases:** https://cicerodata.com/use-cases

---

## ✅ Next Steps

1. **Test Ballotpedia integration:**
   ```bash
   cd /home/developer/projects/oral-health-policy-pulse
   source .venv/bin/activate
   python discovery/ballotpedia_integration.py
   ```

2. **Create Google Civic integration:**
   - Get API key from Google Cloud Console
   - Create `discovery/google_civic_integration.py`
   - Add to API routes in `api/main.py`

3. **Evaluate Cicero:**
   - Contact cicerodata.com for pricing
   - Decide if worth the cost for enterprise deployment

4. **Update frontend:**
   - Add "Find My Representatives" feature using Google Civic
   - Show ballot measures from Ballotpedia
   - Link to school board from NCES data
