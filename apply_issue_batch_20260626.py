#!/usr/bin/env python3
"""
Triage script for batch issue processing.
Processes issues from .triage-batch-YYYYMMDD.json and applies actions.
"""

import json
import subprocess
import sys
from datetime import datetime

BATCH_FILE = ".triage-batch-20260626a.json"

def load_batch():
    with open(BATCH_FILE, 'r') as f:
        return json.load(f)

def close_issue(number, reason, comment):
    """Close an issue with a reason and comment."""
    print(f"Closing issue #{number}: {reason}")
    # gh issue close --reason {reason} --comment "{comment}" {number}
    cmd = ["gh", "issue", "close", str(number), "--reason", reason, "--comment", comment]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  ERROR: {result.stderr}")
        return False
    print(f"  OK: Issue #{number} closed")
    return True

def leave_open(number, comment):
    """Leave issue open but add a comment."""
    print(f"Leaving issue #{number} open with comment")
    cmd = ["gh", "issue", "comment", str(number), "--body", comment]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  ERROR: {result.stderr}")
        return False
    print(f"  OK: Comment added to issue #{number}")
    return True

def main():
    batch = load_batch()
    processed = []
    failed = []

    for issue in batch["issues"]:
        if issue["action"] == "close-wontfix":
            success = close_issue(
                issue["number"],
                "not planned",
                issue["comment"]
            )
        elif issue["action"] == "close-needs-info":
            success = close_issue(
                issue["number"],
                "not planned",
                issue["comment"]
            )
        elif issue["action"] == "leave-open":
            success = leave_open(
                issue["number"],
                issue["comment"]
            )
        else:
            print(f"Unknown action: {issue['action']}")
            failed.append(issue["number"])
            continue

        if success:
            processed.append({
                "number": issue["number"],
                "action": issue["action"],
                "status": "success"
            })
        else:
            failed.append(issue["number"])

    batch["processed_at"] = datetime.utcnow().isoformat() + "Z"
    batch["results"] = {
        "processed": processed,
        "failed": failed
    }

    with open(BATCH_FILE, 'w') as f:
        json.dump(batch, f, indent=2)

    print(f"\nProcessed: {len(processed)}, Failed: {len(failed)}")
    return 0 if len(failed) == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
