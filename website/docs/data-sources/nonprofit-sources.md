# Nonprofit Data Sources & Reference Sites

This document lists all nonprofit data sources and reference websites used by Open Navigator for Engagement.

---

## 🏛️ Primary Data Source (Currently Implemented)

### ProPublica Nonprofit Explorer ⭐

**Source:** ProPublica  
**URL:** https://projects.propublica.org/nonprofits/  
**API:** https://projects.propublica.org/nonprofits/api  

**What It Contains:**
- **3M+ nonprofit organizations** (all IRS-registered 501(c) organizations)
- **IRS Form 990 data** - Complete financial disclosures
- Revenue, expenses, assets, and liabilities
- Executive compensation
- Mission statements and program descriptions
- Historical filings (10+ years of data)

**Why We Use It:**
> "ProPublica's Nonprofit Explorer provides the most comprehensive, free, public access to IRS Form 990 data. It includes every nonprofit that files with the IRS."

**Coverage:**
- ✅ **Volume:** 3M+ organizations
- ✅ **Free API:** No rate limits for non-commercial use
- ✅ **Data Quality:** Direct from IRS filings
- ✅ **Historical Data:** Multiple years available

---

## 📊 Reference Sites (Future Integration)

These sites provide additional nonprofit evaluation and ratings. They are not currently integrated but are listed as important reference resources.

### 1. Charity Navigator - The "Star Rating" Site

**Source:** Charity Navigator  
**URL:** https://www.charitynavigator.org/  
**API:** Available for partners  

**Focus:** Financial Health & Transparency

**What It Provides:**
- **4-star rating system** (easy for citizens to understand)
- Financial accountability scores
- Transparency ratings
- Impact measurements for large nonprofits
- CEO compensation analysis

**Coverage:**
- ~200,000 rated charities
- Focus on larger organizations (>$1M annual revenue)
- Most popular among individual donors

**Use Case for Open Navigator:**
- Add "Charity Navigator Rating" badge to nonprofit profiles
- Filter high-performing nonprofits by star rating
- Show financial health scores alongside Form 990 data

---

### 2. Candid (GuideStar) - The "Volume" Leader

**Source:** Candid (formerly GuideStar)  
**URL:** https://www.guidestar.org/ (now https://candid.org/)  
**API:** Available for partners  

**Focus:** Comprehensive Transparency Data

**What It Provides:**
- **Platinum, Gold, Silver, Bronze Seals of Transparency**
- Self-reported program data (beyond Form 990)
- Board composition and governance information
- Demographic data (staff diversity, equity practices)
- The industry standard for nonprofit verification

**Coverage:**
- 1.8M+ nonprofit profiles
- Most comprehensive volume
- Many nonprofits display "GuideStar Seals" on their websites

**Use Case for Open Navigator:**
- Verify nonprofit legitimacy with transparency seals
- Show governance and demographic data
- Link to detailed GuideStar profiles for more info

---

### 3. GiveWell - The "Impact" Authority

**Source:** GiveWell  
**URL:** https://www.givewell.org/  
**API:** No public API (data available on website)  

**Focus:** Cost-Effectiveness & Evidence-Based Impact

**What It Provides:**
- **Top Charity** recommendations (highly selective)
- Cost-per-life-saved calculations
- Evidence-based impact assessments
- Program effectiveness research
- Most influential for "Effective Altruism" movement

**Coverage:**
- ~10-20 "Top Charities" at any time
- Focus on global health and poverty interventions
- Extremely rigorous evaluation standards

**Use Case for Open Navigator:**
- Highlight GiveWell-recommended charities
- Show cost-effectiveness metrics for top performers
- Filter by "evidence-based impact" certification

---

## 🔗 Additional Reference Resources

### IRS Exempt Organizations Business Master File (BMF)

**Source:** IRS  
**URL:** https://www.irs.gov/charities-non-profits/exempt-organizations-business-master-file-extract-eo-bmf  

**What It Contains:**
- Complete list of all tax-exempt organizations
- EIN (Employer Identification Number)
- NTEE codes (National Taxonomy of Exempt Entities)
- Subsection code (501(c)(3), 501(c)(4), etc.)
- Raw data (no ratings or analysis)

**Use Case:**
- Cross-reference EINs for data accuracy
- Classify nonprofits by NTEE code (education, health, environment, etc.)

---

### National Center for Charitable Statistics (NCCS)

**Source:** Urban Institute  
**URL:** https://nccs.urban.org/  

**What It Contains:**
- Research on nonprofit sector trends
- Data tools and visualization dashboards
- Policy analysis and reports

**Use Case:**
- Background research on nonprofit sector
- Trend analysis for advocacy strategies

---

## 📈 Integration Roadmap

### Phase 1: ✅ **Implemented**
- ProPublica Nonprofit Explorer (3M+ orgs via API)
- Basic search by location and name
- Form 990 financial data display

### Phase 2: 🔄 **In Progress**
- Create nonprofit profile pages with financial summaries
- Add "words vs money" accountability analysis
- Show executive compensation comparisons

### Phase 3: 📋 **Planned**
- Integrate Charity Navigator API for star ratings
- Add transparency seal badges from Candid/GuideStar
- Display GiveWell recommendations for top charities

### Phase 4: 🔮 **Future**
- Real-time API integrations with all reference sites
- Unified nonprofit scoring system
- Automated alerts for rating changes

---

## 🎯 How to Use These Resources

### For Individual Users:
1. **Start with ProPublica** - See the raw financial data (Form 990)
2. **Check Charity Navigator** - Get the 4-star rating for financial health
3. **Verify with Candid** - Confirm transparency seal status
4. **Look for GiveWell** - If seeking highest-impact charities

### For Advocates:
- Use ProPublica data to find inconsistencies ("words vs money")
- Reference Charity Navigator ratings in advocacy materials
- Cite GuideStar seals as proof of transparency
- Highlight GiveWell recommendations for evidence-based giving

### For Researchers:
- Download raw data from IRS BMF
- Use NCCS for sector-wide analysis
- Cross-reference multiple sources for data validation

---

## 📞 Contact & Support

**ProPublica API Support:**  
- Email: data@propublica.org  
- Documentation: https://projects.propublica.org/nonprofits/api

**Charity Navigator:**  
- Partnership inquiries: https://www.charitynavigator.org/about-us/contact/

**Candid (GuideStar):**  
- API access: https://www.guidestar.org/api

**GiveWell:**  
- General inquiries: info@givewell.org

---

## ✅ Data Quality & Updates

- **ProPublica:** Updated annually when new Form 990s are filed with IRS
- **Charity Navigator:** Ratings updated quarterly
- **Candid:** Self-reported data updated by nonprofits continuously
- **GiveWell:** Top Charity list updated annually (November/December)

All data sources listed are **free and publicly accessible**. API access may require partnership agreements for commercial use.
