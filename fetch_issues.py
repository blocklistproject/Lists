#!/usr/bin/env python3
"""Fetch open issues from GitHub and save to a file for batch processing."""

import json
import os
import subprocess
import sys
from pathlib import Path

ISSUES_FILE = Path("/tmp/issues.json")


def fetch_issues():
    """Fetch open issues from GitHub using gh CLI."""
    try:
        result = subprocess.run(
            [
                "gh", "issue", "list",
                "--repo", "blocklistproject/Lists",
                "--state", "open",
                "--limit", "100",
                "--json", "number,title,labels,author,createdAt,updatedAt,state,url,body"
            ],
            capture_output=True,
            text=True,
            check=True
        )
        
        # Parse JSON
        all_issues = json.loads(result.stdout)
        
        # Filter out pull requests
        issues = [i for i in all_issues if 'pull_request' not in i]
        
        # Save to file
        with open(ISSUES_FILE, "w") as f:
            json.dump(issues, f, indent=2)
        
        print(f"Saved {len(issues)} issues to {ISSUES_FILE}")
        return 0
        
    except subprocess.CalledProcessError as e:
        print(f"Error fetching issues: {e}")
        print(f"stdout: {e.stdout}")
        print(f"stderr: {e.stderr}")
        return 1
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(fetch_issues())
