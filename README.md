# oral-health-policy-pulse

Repository name: `oral-health-policy-pulse`  
Project concept name: **Local Policy Oral Health Finder & Fixer**

The **Local Policy Oral Health Finder & Fixer** is a multi-agent system designed to scrape and analyze thousands of local government meeting minutes and public notes across the country. It identifies where fluoridation, school dental screenings, and funding for low-income dental care are being debated—or ignored—so advocacy teams can act during high-impact policy windows.

## Why this matters
- **Business applicability:** High-value for advocacy groups and lobbyists by identifying policy windows of opportunity.
- **Data relevance:** Built for **Lakehouse-scale** unstructured text ingestion and **Agent Bricks**-powered summarization of legislative trends.
- **Creativity:** Focuses on legislative bottlenecks that block oral health outcomes at the policy source.
- **Thoroughness:** Produces an **Advocacy Heatmap** to show where oral health is active on local ballots and agendas.

## Multi-agent architecture
1. **Scrape/Parse Agent**  
   Collects and normalizes municipal meeting minutes, agendas, and notes from diverse local government sources.
2. **Policy Classification Agent**  
   Classifies sentiment and policy posture for oral-health topics (fluoridation, school screenings, and low-income care funding).
3. **Advocacy Drafting Agent**  
   Drafts targeted advocacy emails and outreach briefs aligned to local legislative context and urgency.

## Platform terms
- **Lakehouse-scale:** Centralized analytics storage designed for very large, mixed-format datasets.
- **Agent Bricks:** Modular AI agent components used to build task-specific workflows.
