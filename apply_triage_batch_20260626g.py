#!/usr/bin/env python3
"""
Apply triage batch 20260626g.
Processes issues from .triage-batch-20260626g.json and applies actions.
"""
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path('/home/administrator/.hermes/workspace/Lists')
BATCH_FILE = ROOT / ".triage-batch-20260626g.json"

def load_batch():
    with open(BATCH_FILE, 'r') as f:
        return json.load(f)

def run_gh(args):
    """Run gh CLI command and return result."""
    cmd = ["gh"] + args
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT)
    return result

def close_issue(number, reason, comment):
    """Close an issue with a reason and comment."""
    print(f"Closing issue #{number}: {reason}")
    result = run_gh([
        "issue", "close", str(number),
        "--reason", reason,
        "--comment", comment
    ])
    if result.returncode != 0:
        print(f"  ERROR: {result.stderr}")
        return False
    print(f"  OK: Issue #{number} closed")
    return True

def leave_open_add_comment(number, comment):
    """Leave issue open but add a comment."""
    print(f"Leaving issue #{number} open with comment")
    result = run_gh([
        "issue", "comment", str(number),
        "--body", comment
    ])
    if result.returncode != 0:
        print(f"  ERROR: {result.stderr}")
        return False
    print(f"  OK: Comment added to issue #{number}")
    return True

def add_domain_to_list(domain, target_list, comment):
    """Add domain to a list file."""
    print(f"Adding domain {domain} to list {target_list}")
    list_file = ROOT / f"{target_list.lower()}.txt"
    with open(list_file, 'a') as f:
        f.write(f"\n{domain}")
    print(f"  OK: Domain {domain} added to {list_file}")
    return True

def main():
    batch = load_batch()
    processed = []
    failed = []

    for result in batch["results"]:
        issue_num = result["issue"]
        action = result["action"]
        domain = result.get("domain", "")
        target_list = result.get("target_list", "")
        reason = result.get("reason", "")
        evidence = result.get("evidence", "")

        success = False
        comment_text = ""

        if action == "not_found":
            comment_text = (
                f"I reviewed issue #{issue_num} and could not find the domain "
                f"in any of the blocklists. The domain `{domain}` is not present. "
                f"Closing as **not planned**."
            )
            success = close_issue(issue_num, "not planned", comment_text)

        elif action == "unverified":
            comment_text = (
                f"I reviewed issue #{issue_num} and was unable to verify the domain. "
                f"DNS check: {result.get('dns_ok', 'unknown')}, HTTP status: {result.get('http_status', 'unknown')}. "
                f"Please provide verifiable evidence that this domain should be added/removed. "
                f"Closing as **not planned**."
            )
            success = close_issue(issue_num, "not planned", comment_text)

        elif action == "needs_review":
            comment_text = (
                f"I reviewed issue #{issue_num} and need more information. "
                f"Could you please provide more details or clarify your request? "
                f"This issue will be left open for further discussion."
            )
            success = leave_open_add_comment(issue_num, comment_text)

        elif action == "add":
            if domain:
                list_name = target_list if target_list else "ads"
                list_file = ROOT / f"{list_name.lower()}.txt"
                comment_text = (
                    f"I verified the domain `{domain}` and it appears to be valid. "
                    f"Adding to the {list_name} list. "
                    f"See commit for details."
                )
                if add_domain_to_list(domain, list_name, comment_text):
                    success = leave_open_add_comment(issue_num, comment_text)
                else:
                    success = False
            else:
                comment_text = (
                    f"I reviewed issue #{issue_num} and the domain was not provided. "
                    f"Please provide the domain to add. Closing as **not planned**."
                )
                success = close_issue(issue_num, "not planned", comment_text)
        else:
            print(f"Unknown action: {action} for issue #{issue_num}")
            failed.append({"issue": issue_num, "reason": f"Unknown action: {action}"})
            continue

        if success:
            processed.append({
                "issue": issue_num,
                "action": action,
                "status": "success"
            })
        else:
            failed.append({"issue": issue_num, "action": action})

    batch["applied_at"] = datetime.utcnow().isoformat() + "Z"
    batch["status"] = "applied"
    batch["results_summary"] = {
        "processed": len(processed),
        "failed": len(failed),
        "processed_list": processed,
        "failed_list": failed
    }

    with open(BATCH_FILE, 'w') as f:
        json.dump(batch, f, indent=2)

    print(f"\n=== Summary ===")
    print(f"Processed: {len(processed)}")
    print(f"Failed: {len(failed)}")
    for f_item in failed:
        print(f"  FAILED: {f_item}")
    return 0 if len(failed) == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
