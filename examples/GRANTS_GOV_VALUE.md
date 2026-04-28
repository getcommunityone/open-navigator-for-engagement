# Grants.gov Integration - Data Comparison

## What You Currently Have vs. What You'll Get

### Current Data (IRS Form 990)

| Category | What You Have | Limitations |
|----------|---------------|-------------|
| **Grants Received** | Total government grants $ amount | ❌ No program names |
| | Total foundation grants $ amount | ❌ No grant details |
| | Revenue breakdown by source | ❌ No eligibility info |
| **Timeline** | Historical (past tax years) | ❌ No future opportunities |
| **Granularity** | Aggregate annual totals | ❌ No individual grants |
| **Use Case** | "Who got funded?" | ❌ Can't alert before deadlines |

### New Data (Grants.gov API)

| Category | What You'll Get | Benefits |
|----------|-----------------|----------|
| **Grant Opportunities** | Specific program names & numbers | ✅ Exact grant details |
| | Detailed descriptions | ✅ Purpose and goals |
| | Eligibility requirements | ✅ Who can apply |
| | Award amounts & ceilings | ✅ Funding expectations |
| | Application deadlines | ✅ Time to prepare |
| **Timeline** | Current & future opportunities | ✅ Proactive alerts |
| **Granularity** | Individual grant programs | ✅ Detailed matching |
| **Use Case** | "What's available NOW?" | ✅ Alert before deadlines |

## Complete Grant Lifecycle

```
                     TIME →

PAST                 PRESENT              FUTURE
─────────────────────────────────────────────────────

IRS Form 990         Dashboard            Grants.gov
(Received Grants)    (Matching)           (Opportunities)
│                    │                    │
├─ $500k govt grants ├─ Alert MA orgs    ├─ HRSA Oral Health
├─ $200k foundation  ├─ Match eligibility ├─ Deadline: Dec 31
├─ Tax year 2023     ├─ Send emails       ├─ Award: $500k-$2M
│                    │                    ├─ Posted: Oct 15
│                    │                    │
└─→ "Who got funded?"└─→ "Match & Alert"  └─→ "What's available?"
```

## Example: Massachusetts Dental Clinic

### Without Grants.gov Integration

```
MA Dental Clinic: "We need funding"
  ↓
Search Google for grants (manual, time-consuming)
  ↓
Miss deadlines, outdated information
  ↓
❌ Lost opportunity
```

### With Grants.gov Integration

```
Grants.gov API (automated daily)
  ↓
"HRSA Oral Health Workforce Grant"
  • Deadline: Dec 31, 2024
  • Award: $500k-$2M
  • Eligibility: Community health centers
  ↓
Your Dashboard (automated matching)
  • Match: MA dental clinics (NTEE code)
  • Filter: Organizations with 10+ employees
  • Benchmark: Similar orgs received avg $800k
  ↓
Email Alert (automated notification)
  ↓
MA Dental Clinic: "Perfect! Apply by Dec 31"
  ↓
✅ Increased funding success rate
```

## Data Schema Comparison

### IRS Form 990 Schedule I (Your Current Data - EMPTY)

```python
{
  'ein': '12-3456789',
  'organization_name': 'MA Dental Health Clinic',
  'tax_year': 2023,
  'total_revenue': 5000000,
  'government_grants': 800000,        # ← Total only, no details
  'foundation_grants': 200000,        # ← Total only, no details
  'program_service_revenue': 3500000,
  'investment_income': 50000
}
```

### Grants.gov API (NEW Data)

```python
{
  'id': 289999,
  'opportunityNumber': 'HRSA-24-123',
  'opportunityTitle': 'Oral Health Workforce Development Grant',  # ← Specific program
  'agencyCode': 'HHS-HRSA',
  'agencyName': 'Health Resources & Services Administration',
  'synopsis': 'Funding to expand oral health services...',        # ← Details
  'eligibility': {
    'applicantTypes': ['Community Health Centers', 'FQHCs'],     # ← Who can apply
    'geographic': ['State', 'Local']
  },
  'fundingDetails': {
    'awardCeiling': 2000000,        # ← Max award
    'awardFloor': 500000,           # ← Min award
    'estimatedAwards': 25           # ← How many grants
  },
  'dates': {
    'posted': '2024-10-15',         # ← When announced
    'close': '2024-12-31'           # ← Deadline!
  },
  'opportunityStatus': 'posted',    # ← Current status
  'cfdaList': [{'cfdaNumber': '93.224'}]  # ← Program identifier
}
```

## Use Case Examples

### 1. Grant Opportunity Dashboard

**Before:**
- "Here are MA nonprofits" (static list)

**After:**
- "5 NEW oral health grants posted this week!"
- "Deadline Alert: HRSA grant closes in 10 days"
- "Your organization is eligible for 12 federal grants"

### 2. Email Alerts

**Before:**
- Monthly newsletter with general updates

**After:**
- "NEW Grant Alert: $2M available for dental clinics in MA"
- "Deadline Reminder: Apply by Dec 31"
- "Similar organizations received avg $800k from this program"

### 3. Strategic Planning

**Before:**
- Review past grants (IRS 990)
- Manual web searches for opportunities

**After:**
- Compare: "Are we applying to all eligible grants?"
- Analyze: "What's the success rate for our org type?"
- Benchmark: "Similar orgs got $800k - we should apply"

### 4. Policy Analysis

**Before:**
- Track oral health spending (historical)

**After:**
- Track federal priorities (future focus areas)
- Identify: "Fluoridation funding decreased 20% this year"
- Forecast: "School-based programs getting more grants"

## ROI Analysis

### Implementation Effort

- **Code:** Already written (discovery/grants_gov_integration.py)
- **API Key:** NOT REQUIRED (public endpoints)
- **Setup Time:** 5 minutes (pip install requests)
- **Maintenance:** Minimal (API is stable)

### Value Delivered

- **For Nonprofits:**
  - Earlier awareness of opportunities
  - Better preparation time
  - Higher success rate

- **For Your Platform:**
  - Differentiation (unique feature)
  - User engagement (regular alerts)
  - Data completeness (full grant lifecycle)

- **For Analysis:**
  - Trend tracking (what grants are prioritized)
  - Gap analysis (unfunded needs)
  - Success metrics (application → award rate)

## Quick Test

Try it now:

```bash
# Install if needed
pip install requests loguru pandas pyarrow

# Run demo
python examples/demo_grants_gov.py
```

This will:
1. ✅ Fetch current oral health grants
2. ✅ Show breakdown by agency and status
3. ✅ Match to MA nonprofits (if you have the data)
4. ✅ Save results to data/gold/grants/

## Bottom Line

| Question | IRS 990 Answer | Grants.gov Answer |
|----------|---------------|-------------------|
| Who received grants? | ✅ Yes | ❌ No |
| How much did they receive? | ✅ Yes (totals) | ✅ Yes (ranges) |
| Which specific programs? | ❌ Limited | ✅ Yes (detailed) |
| What grants are available? | ❌ No | ✅ Yes |
| When are deadlines? | ❌ No | ✅ Yes |
| Who is eligible? | ❌ No | ✅ Yes |
| What are requirements? | ❌ No | ✅ Yes |

**Both data sources are complementary!** Use Grants.gov for FUTURE opportunities and IRS 990 for PAST awards.
