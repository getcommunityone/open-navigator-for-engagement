#!/usr/bin/env python3
"""Simple aggregation regeneration script"""
import os
import sys

# Set environment to avoid pager issues
os.environ['PAGER'] = 'cat'
os.environ['PYTHONUNBUFFERED'] = '1'

# Change to project directory
os.chdir('/home/developer/projects/oral-health-policy-pulse')
sys.path.insert(0, '/home/developer/projects/oral-health-policy-pulse')

# Suppress warnings
import warnings
warnings.filterwarnings('ignore')

# Import and run
print("Starting aggregation...", flush=True)
from scripts.aggregate_bills_from_postgres import main
main()
print("\n✅ Complete!", flush=True)
