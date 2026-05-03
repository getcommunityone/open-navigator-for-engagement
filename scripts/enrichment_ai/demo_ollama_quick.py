#!/usr/bin/env python3
"""
Quick Bill Analysis Demo using Ollama (while waiting for HF access)

Shows 1 bill analysis with Ollama to demonstrate the workflow.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scripts.enrichment_ai.legislative_analysis_intel import DuckDBLegislativeAnalyzer
import subprocess
import json
from datetime import datetime

print("🚀 Quick Llama 3.2 Bill Analysis Demo (via Ollama)")
print("=" * 70)
print()

# Connect and get one bill
with DuckDBLegislativeAnalyzer() as analyzer:
    analyzer.create_bills_table()
    
    bills = analyzer.get_bills_to_analyze(
        state="GA",
        topic_filter="fluorid",
        limit=1,
        skip_analyzed=False  # Get any bill for demo
    )
    
    if not bills:
        print("❌ No bills found")
        sys.exit(1)
    
    bill = bills[0]
    print(f"📋 Bill: {bill['bill_number']}")
    print(f"📝 Title: {bill['title']}")
    print()

# Create simple prompt
prompt = f"""Analyze this water fluoridation bill and identify 2-3 interest groups who would support or oppose it.

Bill: {bill['title']}

Return ONLY valid JSON (no explanation):
{{
  "groups": [
    {{"name": "Group Name", "stance": "support/oppose", "reasoning": "Why they care"}}
  ]
}}"""

print("🤖 Asking Llama 3.2 via Ollama...")
print()

# Call Ollama
result = subprocess.run(
    ['ollama', 'run', 'llama3.2:latest', prompt],
    capture_output=True,
    text=True,
    timeout=60
)

response = result.stdout.strip()

# Extract and display JSON
try:
    if '{' in response:
        json_start = response.index('{')
        json_end = response.rindex('}') + 1
        json_str = response[json_start:json_end]
        data = json.loads(json_str)
        
        print("✅ Analysis Results:")
        print()
        for group in data.get('groups', []):
            print(f"  • {group['name']}")
            print(f"    Stance: {group['stance']}")
            print(f"    Reasoning: {group['reasoning']}")
            print()
        
        print("=" * 70)
        print("💡 This demonstrates the analysis workflow.")
        print("   For production, use HuggingFace version (much faster!)")
        print()
        print("   Once HF access is granted, run:")
        print("   python scripts/enrichment_ai/batch_analyze_bills.py --state GA --limit 10")
        
    else:
        print("❌ No JSON in response")
        print(response[:200])
        
except Exception as e:
    print(f"❌ Error: {e}")
    print("Response:", response[:200])
