#!/usr/bin/env python3
"""Process first batch of 10 issues for triage."""
import json
import subprocess

# Issue numbers to process (first 10 in the list)
ISSUES = [1567, 1554, 1535, 1523, 1522, 1487, 1486, 1485, 1467, 1466]

def get_issue_details(num):
    """Get issue details as JSON."""
    result = subprocess.run(
        ["gh", "issue", "view", str(num), "--json", "title,state,labels,author,createdAt,updatedAt,body,number"],
        capture_output=True, text=True
    )
    return result.stdout, result.stderr, result.returncode

for num in ISSUES:
    print(f"=== Issue #{num} ===")
    stdout, stderr, rc = get_issue_details(num)
    if rc == 0:
        try:
            data = json.loads(stdout)
            print(f"Title: {data.get('title', 'N/A')}")
            print(f"State: {data.get('state', 'N/A')}")
            print(f"Labels: {[l['name'] for l in data.get('labels', [])]}")
            print(f"Author: {data.get('author', {}).get('login', 'N/A')}")
            print(f"Body preview: {data.get('body', '')[:500]}...")
        except json.JSONDecodeError:
            print(f"JSON parse error: {stdout[:200]}")
    else:
        print(f"Error: {stderr}")
    print()
