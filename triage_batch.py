#!/usr/bin/env python3
"""Batch triage script for blocklistproject/Lists issues."""

import json
import subprocess
import sys
import os
import re
from datetime import datetime

REPO = "blocklistproject/Lists"

def gh_cli(args):
    """Run gh CLI command and return output."""
    cmd = ["gh", "-R", REPO] + args
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode, result.stdout, result.stderr

def main():
    print("Starting triage batch...")
    
    # Get open issues list
    rc, out, err = gh_cli(["issue", "list", "--state", "open", "--limit", "100"])
    if rc != 0:
        print(f"Error getting issue list: {err}")
        return
    
    issues = []
    for line in out.strip().split('\n'):
        parts = line.split('\t')
        if len(parts) >= 4:
            try:
                num = int(parts[0])
                state = parts[1]
                labels = parts[2]
                title = parts[3]
                if state == "OPEN":
                    issues.append({
                        "number": num,
                        "state": state,
                        "labels": labels,
                        "title": title
                    })
            except:
                pass
    
    print(f"Found {len(issues)} open issues")
    
    # Process first 10
    batch = issues[:10]
    print(f"Processing batch of {len(batch)} issues")
    
    # Create fresh batch data
    batch_data = {
        "batch": 1,
        "start_time": datetime.utcnow().isoformat() + "Z",
        "issues_processed": [],
        "status": "in-progress"
    }
    
    for issue in batch:
        num = issue["number"]
        print(f"\n--- Issue #{num} ---")
        print(f"Title: {issue['title']}")
        print(f"Labels: {issue['labels']}")
        
        # Get full details via gh issue view
        rc, out, err = gh_cli(["issue", "view", str(num), "--json", "title,state,labels,author,createdAt,body"])
        
        if rc == 0:
            try:
                details = json.loads(out)
                title = details.get('title', 'N/A')
                labels = [l['name'] for l in details.get('labels', [])]
                author = details.get('author', {}).get('login', 'N/A')
                body = details.get('body', '')[:500]
                
                # Check for add/remove request patterns
                is_add = "request:add" in labels
                is_remove = "request:remove" in labels
                
                domain = None
                if is_add or is_remove:
                    url_match = re.search(r'https?://([^\s/]+)', body)
                    if url_match:
                        domain = url_match.group(1)
                
                batch_data["issues_processed"].append({
                    "issue": num,
                    "title": title,
                    "labels": labels,
                    "author": author,
                    "status": "needs-triage",
                    "domain": domain,
                    "body_preview": body[:500]
                })
            except Exception as e:
                print(f"Error parsing JSON: {e}")
                batch_data["issues_processed"].append({
                    "issue": num,
                    "title": issue["title"],
                    "labels": issue["labels"].split(',') if issue["labels"] else [],
                    "status": "error-fetching"
                })
        else:
            print(f"Error getting issue details: {err}")
            batch_data["issues_processed"].append({
                "issue": num,
                "title": issue["title"],
                "labels": issue["labels"].split(',') if issue["labels"] else [],
                "status": "error-fetching"
            })
    
    batch_data["status"] = "complete"
    
    # Write fresh file
    with open('.triage-batch-20260625.json', 'w') as f:
        json.dump(batch_data, f, indent=2)
    
    print("\nBatch processing complete.")
    print(f"Results saved to .triage-batch-20260625.json")

if __name__ == "__main__":
    main()
