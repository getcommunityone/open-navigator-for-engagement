# ⚠️ Important: Two Separate Sites

## You Are Currently On: Documentation Site (Port 3000)

This Docusaurus site provides **guides, documentation, and getting started instructions**.

## Looking for the Application?

### 🚀 **React Dashboard (Port 5173) - MAIN APPLICATION**

The **actual application interface** with all the features is at:

**http://localhost:5173**

Start it with:
```bash
cd frontend
npm install
npm run dev
```

### What's in the Dashboard (React App - Port 5173):
- ✅ **Search functionality** - Search documents, meetings, nonprofits
- ✅ **Filter capabilities** - Filter by urgency, topic, location, date
- ✅ **Interactive heatmap** - Geographic visualization of opportunities
- ✅ **Document explorer** - Browse and analyze meeting minutes
- ✅ **Nonprofit search** - Find local organizations
- ✅ **Opportunity tracker** - Advocacy opportunities with email generation
- ✅ **Real-time analytics** - Stats, charts, and visualizations

### What's in the Documentation Site (Docusaurus - Port 3000):
- 📖 **Getting started guides** - Installation and setup
- 📖 **API documentation** - Endpoint reference
- 📖 **Deployment guides** - Production deployment
- 📖 **Architecture docs** - How everything works
- 📖 **Contributing guidelines** - For developers

## Quick Reference

| What You Want | Where to Go | Port |
|---------------|-------------|------|
| **Search and filter data** | React Dashboard | 5173 |
| **View heatmap** | React Dashboard | 5173 |
| **Explore documents** | React Dashboard | 5173 |
| **Track opportunities** | React Dashboard | 5173 |
| **Search nonprofits** | React Dashboard | 5173 |
| Read documentation | Docusaurus Site | 3000 |
| View API docs | API Backend | 8000 |

## The React Dashboard Was NOT Replaced

**Important**: Adding the Docusaurus documentation site did NOT replace or remove the React dashboard. They are **two separate applications** that serve different purposes:

1. **Documentation Site** (this site) - For reading and learning
2. **Dashboard** (React app) - For using and interacting with data

Both work together as part of the Open Navigator platform.

## Start Everything at Once

```bash
./start-all.sh
```

This will launch:
- Documentation: http://localhost:3000
- **Dashboard: http://localhost:5173** ← Start here for the app
- API: http://localhost:8000

---

**See [ARCHITECTURE.md](../ARCHITECTURE.md) for detailed architecture explanation.**
