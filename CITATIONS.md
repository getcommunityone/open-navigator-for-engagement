# Citations and Acknowledgments

This project uses several open datasets and research contributions. Please cite the following works when using or referencing this project.

## 📚 **Datasets**

### **MeetingBank Dataset**

We use the MeetingBank benchmark dataset for meeting summarization and analysis.

**Citation:**
```
Yebowen Hu, Tim Ganter, Hanieh Deilamsalehy, Franck Dernoncourt, Hassan Foroosh, Fei Liu.
"MeetingBank: A Benchmark Dataset for Meeting Summarization"
In Proceedings of the 61st Annual Meeting of the Association for Computational Linguistics (ACL),
July 2023, Toronto, Canada.
```

**BibTeX:**
```bibtex
@inproceedings{hu-etal-2023-meetingbank,
    title = "MeetingBank: A Benchmark Dataset for Meeting Summarization",
    author = "Yebowen Hu and Tim Ganter and Hanieh Deilamsalehy and Franck Dernoncourt and Hassan Foroosh and Fei Liu",
    booktitle = "Proceedings of the 61st Annual Meeting of the Association for Computational Linguistics (ACL)",
    month = July,
    year = "2023",
    address = "Toronto, Canada",
    publisher = "Association for Computational Linguistics",
}
```

**Resources:**
- Paper: https://arxiv.org/abs/2305.17529
- Dataset: https://huggingface.co/datasets/huuuyeah/meetingbank
- Zenodo: https://zenodo.org/record/7989108

**What we use:**
- 1,366 city council meetings from 6 U.S. cities
- Meeting transcripts and summaries
- Used for: Meeting discovery, transcript analysis, summarization benchmarking

---

## 🗂️ **Other Data Sources**

### **U.S. Census Bureau**
- Geographic boundaries and demographic data
- Source: https://www.census.gov/
- License: Public Domain (U.S. Government)

### **Open States API**
- State and local legislative information
- Source: https://openstates.org/
- License: Various (check per state)
- API Key: Required for access

### **Harvard Dataverse**
- Meeting datasets and civic engagement research
- Source: https://dataverse.harvard.edu/
- License: Varies by dataset

### **Ballotpedia** ⭐
- Ballot measures, referendums, and propositions
- Organization: Lucy Burns Institute
- Source: https://ballotpedia.org/
- API: https://ballotpedia.org/API-documentation
- License: API access is limited at scale (paid tier available)
- Coverage: All 50 states, historical measures back to 1990s
- Used for: Tracking fluoridation votes, school bond measures, health policy propositions

### **MIT Election Data + Science Lab**
- Presidential, Congressional, and gubernatorial election results
- Organization: Massachusetts Institute of Technology
- Source: https://electionlab.mit.edu/data
- Repository: https://github.com/MEDSL/official-returns
- License: Free for research and commercial use
- Coverage: 1976-present, county-level results
- Used for: Political composition analysis, jurisdiction context

### **OpenElections**
- State-by-state certified election results in standardized CSV format
- Source: https://openelections.net/
- GitHub: https://github.com/openelections
- License: Open source (various by state)
- Coverage: All 50 states (various completion levels), precinct-level data
- Used for: Detailed election results, local race outcomes, advocacy targeting

### **Open Civic Data (OCD) Standards**
- Division identifiers and civic data standards
- Specification: https://open-civic-data.readthedocs.io/en/latest/proposals/0002.html
- Repository: https://github.com/opencivicdata/ocd-division-ids
- License: Open source
- Used for: Standardized jurisdiction identifiers, cross-platform compatibility

### **Roper Center for Public Opinion Research**
- Scientifically validated survey questions and public opinion data
- Organization: Cornell University
- Source: https://ropercenter.cornell.edu/
- iPoll Database: https://ropercenter.cornell.edu/ipoll/
- License: Free public search (metadata and question wording), full data requires institutional membership
- Coverage: 500,000+ survey questions from 1930s-present, all major polling organizations
- Used for: Topic definitions, validated question wording, national opinion baselines, messaging optimization
- Citation: "Roper Center for Public Opinion Research, Cornell University. iPoll Databank. https://ropercenter.cornell.edu/ipoll/"

---

## 🙏 **Acknowledgments**

We are grateful to the authors of MeetingBank for making their dataset publicly available for research purposes. Their work on meeting summarization has been instrumental in developing civic engagement tools.

Special thanks to:
- The Association for Computational Linguistics (ACL)
- HuggingFace for hosting datasets
- Open States for legislative data
- All municipal governments providing open access to meeting records

---

## 📖 **How to Cite This Project**

If you use Open Navigator for Engagement in your research, please cite:

```
Open Navigator for Engagement
GitHub: https://github.com/getcommunityone/open-navigator-for-engagement
License: MIT
```

**BibTeX:**
```bibtex
@software{open-navigator-2026,
    title = {Open Navigator for Engagement},
    author = {Community One},
    year = {2026},
    url = {https://github.com/getcommunityone/open-navigator-for-engagement},
    license = {MIT}
}
```

---

## 📝 **License Compliance**

This project respects all dataset licenses and terms of use. See [LICENSE](LICENSE) for this project's MIT license.

For dataset-specific licenses, please refer to the original sources listed above.
