---
title: Open Navigator for Engagement
emoji: 🏛️
colorFrom: blue
colorTo: green
sdk: docker
pinned: true
license: mit
app_port: 7860
short_description: The open path to everything local
---

# 🏛️ Open Navigator for Engagement

**CommunityOne: The open path to everything local**

Open Navigator for Engagement is a comprehensive platform for discovering, analyzing, and tracking local government activities, nonprofit organizations, and civic engagement opportunities across the United States.

## 🎯 What's Included

This Space runs **three integrated applications**:

### 📊 **Documentation** → [/docs](/docs)
Complete platform documentation including:
- Getting started guides
- Data source explanations
- API reference
- Technical architecture

### 🚀 **Main Application** → [/](/​)
Interactive dashboard with:
- 925 jurisdictions tracked (cities, counties, states)
- 43,726 nonprofit organizations (5 states with full IRS BMF data)
- 6,913 meeting minutes analyzed
- Budget tracking
- Video transcript search

### 🔌 **API Backend** → [/api/docs](/api/docs)
RESTful API providing:
- Search endpoints
- Data retrieval
- Classification services
- Sentiment analysis

## 📈 Platform Scale

| Data Type | Coverage |
|-----------|----------|
| **Jurisdictions** | 925 (cities, counties, states) |
| **School Districts** | 306 districts |
| **Nonprofits** | 43,726 tax-exempt organizations |
| **Meeting Minutes** | 6,913 government meetings |
| **Elected Officials** | 362 tracked officials |
| **Churches** | 4,372 congregations |
| **States with IRS Data** | 5 states |

## 🎓 Who It's For

### Policy Makers & Advocates
- Track oral health policy mentions across jurisdictions
- Analyze budget allocations and funding trends
- Find advocacy opportunities in upcoming meetings
- Monitor nonprofit activities in specific areas

### Researchers & Journalists
- Access structured government data at scale
- Analyze policy patterns across jurisdictions
- Track issue evolution over time
- Export data for analysis

### Developers & Data Scientists
- RESTful API access to all data
- Python SDK for analysis
- Delta Lake storage for large-scale queries
- Open source codebase for customization

## 🚀 Quick Links

- **[View Documentation](/docs/intro)** - Learn about data sources and features
- **[Launch Application](/)** - Start exploring the platform
- **[API Documentation](/api/docs)** - Integrate with your tools
- **[GitHub Repository](https://github.com/getcommunityone/open-navigator-for-engagement)** - Source code and setup

## 🔧 Technology Stack

- **Frontend**: React + Vite + TypeScript
- **Documentation**: Docusaurus 3
- **Backend**: FastAPI + Python 3.11
- **Data**: Delta Lake (Bronze/Silver/Gold layers)
- **AI/ML**: OpenAI GPT-4, Claude, HuggingFace models
- **Search**: Qdrant vector database
- **Deployment**: Docker with nginx reverse proxy

## 📊 Example Use Cases

1. **Oral Health Advocacy**: Search meeting minutes for "dental", "fluoride", "oral health" mentions
2. **Budget Analysis**: Track health department funding across similar-sized cities
3. **Nonprofit Discovery**: Find organizations working on specific health issues
4. **Policy Research**: Analyze policy adoption patterns across states
5. **Community Engagement**: Identify upcoming meetings to attend

## 🔒 Privacy & Data

All data is sourced from:
- ✅ Public government records
- ✅ IRS Form 990 public filings
- ✅ Open data portals
- ✅ Public meeting recordings
- ✅ .gov domains and official sources

No personal information or private data is collected or stored.

## 📝 License

MIT License - Free for commercial and non-commercial use

## 🤝 Contributing

This is an open source project! Visit our [GitHub repository](https://github.com/getcommunityone/open-navigator-for-engagement) to contribute.

---

**Built with ❤️ for civic engagement and public health advocacy**
