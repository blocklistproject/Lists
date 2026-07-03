#!/usr/bin/env python3
"""Batch issue triage for blocklistproject/Lists.

Processes GitHub issues in batches of 10, verifying domains and applying updates.
"""

import json
import os
import re
import socket
import subprocess
import sys
import time
import urllib.request
from pathlib import Path
from urllib.error import HTTPError, URLError

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

try:
    from src.config import VAULT_DIR, WORKSPACE_DIR, TEMP_DIR
except ImportError:
    # Fallback to environment variables if src.config not available
    VAULT_DIR = Path(os.environ.get("HERMES_VAULT", Path.home() / ".hermes" / "vault"))
    WORKSPACE_DIR = Path(os.environ.get("WORKSPACE_DIR", Path.cwd()))
    TEMP_DIR = Path(os.environ.get("TEMP_DIR", "/tmp"))

WORKSPACE = WORKSPACE_DIR
LOCK_DIR = TEMP_DIR / "blocklistproject-triage-cron.lock"
ISSUES_FILE = TEMP_DIR / "issues.json"
RESULTS_FILE = TEMP_DIR / "batch_results.json"

# Longer timeout to avoid conflicts with other runs
LOCK_TIMEOUT_SECONDS = 7200  # 2 hours

# Blocklist files (source files, not generated)
SOURCE_LISTS = {
    "abuse": "abuse.txt",
    "ads": "ads.txt",
    "crypto": "crypto.txt",
    "drugs": "drugs.txt",
    "facebook": "facebook.txt",
    "fraud": "fraud.txt",
    "gambling": "gambling.txt",
    "malware": None,  # No single source file
    "phishing": None,
    "piracy": None,
    "porn": "porn.txt",
    "ransomware": None,
    "redirect": None,
    "scam": None,
    "smart-tv": None,
    "tiktok": None,
    "torrent": None,
    "tracking": None,
    "twitter": None,
    "vaping": None,
    "whatsapp": None,
    "youtube": None,
}


def is_domain_active(domain: str) -> dict:
    """Check if domain is active via DNS and HTTP probes."""
    result = {"domain": domain, "dns": False, "http": None, "http_code": None, "error": None}

    # DNS probe
    try:
        socket.getaddrinfo(domain, 443, socket.AF_INET)
        result["dns"] = True
    except (socket.gaierror, OSError) as e:
        result["error"] = f"DNS error: {e}"

    # HTTP probe
    if result["dns"]:
        for scheme in ["https", "http"]:
            try:
                url = f"{scheme}://{domain}"
                req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req, timeout=5) as resp:
                    result["http"] = scheme
                    result["http_code"] = resp.status
                    break
            except HTTPError as e:
                result["http"] = scheme
                result["http_code"] = e.code
                break
            except (URLError, TimeoutError) as e:
                result["error"] = f"HTTP error ({scheme}): {e}"

    return result


def read_file(path: Path) -> str:
    """Read file content, return empty string if not found."""
    try:
        return path.read_text(encoding="utf-8").strip()
    except FileNotFoundError:
        return ""


def write_file(path: Path, content: str) -> None:
    """Write content to file."""
    path.write_text(content, encoding="utf-8")


def domain_in_list(domain: str, list_name: str) -> bool:
    """Check if domain is in a source list."""
    source_file = SOURCE_LISTS.get(list_name)
    if not source_file:
        return False

    list_path = WORKSPACE / source_file
    content = read_file(list_path)

    # Check for domain as standalone or at end of line
    pattern = rf"^\s*{re.escape(domain)}\s*$"
    return bool(re.search(pattern, content, re.MULTILINE))


def add_to_list(domain: str, list_name: str) -> bool:
    """Add domain to source list."""
    source_file = SOURCE_LISTS.get(list_name)
    if not source_file:
        return False

    list_path = WORKSPACE / source_file
    current = read_file(list_path)

    if domain in current:
        return True  # Already present

    # Add domain at end of file
    if current:
        new_content = f"{current}\n{domain}"
    else:
        new_content = domain

    write_file(list_path, new_content)
    return True


def remove_from_list(domain: str, list_name: str) -> bool:
    """Remove domain from source list."""
    source_file = SOURCE_LISTS.get(list_name)
    if not source_file:
        return False

    list_path = WORKSPACE / source_file
    content = read_file(list_path)

    if domain not in content:
        return True  # Not present, nothing to remove

    # Remove domain from content
    pattern = rf"(?m)^\s*{re.escape(domain)}\s*$\n?"
    new_content = re.sub(pattern, "", content).strip()
    write_file(list_path, new_content)
    return True


def run_git_command(cmd: list) -> str:
    """Run a git command in the workspace directory."""
    result = subprocess.run(
        cmd,
        cwd=WORKSPACE,
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()


def build_and_validate() -> bool:
    """Run build.py validation and return success status."""
    try:
        subprocess.run(
            ["python3", "build.py", "--dry-run", "--validate", "--verbose"],
            cwd=WORKSPACE,
            check=True,
            capture_output=True,
            text=True,
        )
        return True
    except subprocess.CalledProcessError as e:
        print(f"Build validation failed: {e.stderr}")
        return False


def commit_changes(issue_numbers: list, action: str, domains: list) -> str:
    """Commit changes and return commit SHA."""
    run_git_command(["git", "add", "."])

    domains_str = ", ".join(domains[:3]) + ("..." if len(domains) > 3 else "")
    issue_str = ", ".join(f"#{n}" for n in issue_numbers)

    message = f"Triage {issue_str}: {action} {domains_str}"

    run_git_command(["git", "commit", "-m", message])
    sha = run_git_command(["git", "rev-parse", "HEAD"])

    return sha


def push_changes() -> bool:
    """Push changes to origin master."""
    try:
        run_git_command(["git", "push", "origin", "master"])
        return True
    except subprocess.CalledProcessError as e:
        print(f"Push failed: {e}")
        return False


def issue_has_required_fields(issue: dict, field: str) -> bool:
    """Check if issue has required fields in body."""
    body = issue.get("body", "")
    return field.lower() in body.lower()


def parse_issue(issue: dict) -> dict:
    """Parse an issue and extract domain/list information."""
    body = issue.get("body", "")
    title = issue.get("title", "")
    issue_num = issue.get("number")

    result = {
        "issue": issue_num,
        "title": title,
        "type": "unknown",
        "domain": None,
        "list": None,
        "action": None,
        "evidence": None,
        "status": "incomplete",
    }

    # Normalize line endings
    body = body.replace("\r\n", "\n")

    # Check for add/remove request patterns in title
    if "[add" in title.lower():
        result["type"] = "add"

        # Extract domain from title first
        domain_match = re.search(r"\[add\s+(?:request\])?\s*(.+?)(?:\s*\])?$", title, re.IGNORECASE)
        if domain_match:
            result["domain"] = domain_match.group(1).strip()

        # Fallback: look in body for "URL you wish to be added:"
        if not result["domain"]:
            domain_match = re.search(r"URL\s+you\s+wish\s+to\s+be\s+added:\s*([^\s\n,]+)", body, re.IGNORECASE)
            if domain_match:
                result["domain"] = domain_match.group(1).strip()

        # Extract list from title or body - handle URLs, code blocks, and plain names
        list_match = re.search(r"Add\s+to\s+list:\s*(.+?)(?:\n|$)", body, re.IGNORECASE)
        if list_match:
            list_name = list_match.group(1).strip()
            # Clean up: remove URLs, markdown, trailing punctuation
            # Extract basename from URLs like https://blocklistproject.github.io/Lists/abuse.txt
            url_match = re.search(r"[/\\]([^/\\]+)\.txt\b", list_name)
            if url_match:
                list_name = url_match.group(1)
            # Remove markdown code blocks
            list_name = re.sub(r"^\s*`\s*|\s*`\s*$", "", list_name)
            list_name = list_name.lower().replace(".txt", "").strip()
            result["list"] = list_name

            # If result is still invalid, try to extract a single list name from comma-separated list
            if not result["list"] or result["list"] not in SOURCE_LISTS:
                # Try to extract first valid list from comma-separated list like "abuse, ads, possibly more"
                first_match = re.search(r"([a-zA-Z][a-zA-Z0-9\-_]*)", list_match.group(1))
                if first_match:
                    list_name = first_match.group(1).lower()
                    result["list"] = list_name

    elif "[remove" in title.lower() or "[remove" in body.lower():
        result["type"] = "remove"

        # Extract domain from title first
        domain_match = re.search(r"\[remove\s+(?:request\])?\s*(.+?)(?:\s*\\])?$", title, re.IGNORECASE)
        if domain_match:
            result["domain"] = domain_match.group(1).strip()

        # Fallback: look in body for "URL you wish to be removed:"
        if not result["domain"]:
            domain_match = re.search(r"URL\s+you\s+wish\s+to\s+be\s+removed:\s*([^\s\n,]+)", body, re.IGNORECASE)
            if domain_match:
                result["domain"] = domain_match.group(1).strip()

        # Extract list - handle URLs, code blocks, and plain names
        list_match = re.search(r"List\s+it\s+is\s+on:\s*(.+?)(?:\n|$)", body, re.IGNORECASE)
        if list_match:
            list_name = list_match.group(1).strip()
            # Clean up: remove URLs, markdown, trailing punctuation
            # Extract basename from URLs like https://blocklistproject.github.io/Lists/abuse.txt
            url_match = re.search(r"[/\\]([^/\\]+)\.txt\b", list_name)
            if url_match:
                list_name = url_match.group(1)
            # Remove markdown code blocks
            list_name = re.sub(r"^\s*`\s*|\s*`\s*$", "", list_name)
            list_name = re.sub(r"^\s*\*\s*$", "", list_name)
            list_name = list_name.lower().replace(".txt", "").strip()
            # If still empty after cleanup, try alternate patterns
            if not list_name:
                result["list"] = None
                alt_match = re.search(r"List it is on:\s*(.+?)(?:\n|$)", body, re.IGNORECASE)
                if alt_match:
                    list_name = alt_match.group(1).strip().lower().replace(".txt", "").strip()
            result["list"] = list_name if list_name in SOURCE_LISTS else None
            result["list"] = list_name
    # Extract evidence/reason from body
    if not result["evidence"]:
    if not result["evidence"]:
        evidence_match = re.search(r"Why you believe this should be added[:\s]+(.+?)(?:\n\n|$)", body, re.IGNORECASE | re.DOTALL)
        if evidence_match:
            result["evidence"] = evidence_match.group(1).strip()
        else:
            evidence_match = re.search(r"Why you believe this to be a false positive[:\s]+(.+?)(?:\n\n|$)", body, re.IGNORECASE | re.DOTALL)
            if evidence_match:
                result["evidence"] = evidence_match.group(1).strip()

    # Validate extracted domain
    if result["domain"]:
        # Clean up any trailing punctuation or markdown
        result["domain"] = re.sub(r"[\s\*\`\"]+$", "", result["domain"])

    return result


def process_issue(issue: dict) -> dict:
    """Process a single issue and return results."""
    parsed = parse_issue(issue)
    issue_num = parsed["issue"]
    domain = parsed["domain"]
    list_name = parsed["list"]

    result = {
        "issue": issue_num,
        "domain": domain,
        "list": list_name,
        "type": parsed["type"],
        "status": "incomplete",
        "message": "",
        "action_taken": False,
    }

    # Validate we have required info
    if not domain:
        result["status"] = "incomplete"
        result["message"] = "Could not parse domain from issue"
        return result

    if not list_name:
        result["status"] = "incomplete"
        result["message"] = "Could not determine target list"
        return result

    if list_name not in SOURCE_LISTS:
        result["status"] = "incomplete"
        result["message"] = f"Unknown list: {list_name}"
        return result

    # Verify domain activity
    verification = is_domain_active(domain)

    if parsed["type"] == "add":
        # For add requests, verify domain exists
        if verification["dns"] and verification["http"]:
            if domain_in_list(domain, list_name):
                result["status"] = "skipped"
                result["message"] = f"Domain {domain} is already in {list_name}"
            else:
                # Add domain
                if add_to_list(domain, list_name):
                    result["status"] = "verified-add"
                    result["action_taken"] = True
                    result["message"] = f"Added {domain} to {list_name} (verified: DNS={verification['dns']}, HTTP={verification['http']})"
                else:
                    result["status"] = "error"
                    result["message"] = f"Failed to add {domain} to {list_name}"
        else:
            result["status"] = "incomplete"
            result["message"] = f"Domain {domain} verification failed: {verification.get('error', 'unknown')}"

    elif parsed["type"] == "remove":
        # For remove requests, verify domain exists in list
        if domain_in_list(domain, list_name):
            # Remove domain
            if remove_from_list(domain, list_name):
                result["status"] = "verified-remove"
                result["action_taken"] = True
                result["message"] = f"Removed {domain} from {list_name}"
            else:
                result["status"] = "error"
                result["message"] = f"Failed to remove {domain} from {list_name}"
        else:
            result["status"] = "skipped"
            result["message"] = f"Domain {domain} not found in {list_name}"

    return result


def main():
    """Main entry point."""
    start_time = time.time()

    # Check lock file
    lock_file = LOCK_DIR / "started_at"
    if LOCK_DIR.exists() and lock_file.exists():
        lock_age = time.time() - os.path.getmtime(lock_file)
        if lock_age < LOCK_TIMEOUT_SECONDS:
            print(f"Lock file exists and is less than {LOCK_TIMEOUT_SECONDS}s old ({lock_age:.0f}s). Exiting.")
            return 1
        else:
            print(f"Stale lock file detected ({lock_age:.0f}s old), removing...")
            import shutil
            shutil.rmtree(LOCK_DIR)

    LOCK_DIR.mkdir(parents=True, exist_ok=True)
    lock_file.write_text(str(int(start_time)))
    print(f"Lock acquired at {start_time}")

    # Load issues from file
    if not ISSUES_FILE.exists():
        print("No issues file found. Run fetch_issues first.")
        return 1

    with open(ISSUES_FILE) as f:
        issues = json.load(f)

    print(f"Loaded {len(issues)} issues from file")

    # Take first 10 issues
    batch = issues[:10]
    print(f"Processing batch of {len(batch)} issues")

    results = []
    domains_to_build = []

    for issue in batch:
        result = process_issue(issue)
        results.append(result)

        if result["action_taken"] and result["domain"]:
            domains_to_build.append(result["domain"])

        print(f"Issue #{result['issue']}: {result['status']} - {result['message'][:80]}")

    # Write results
    with open(RESULTS_FILE, "w") as f:
        json.dump(results, f, indent=2)

    # Commit and push if we made changes
    if any(r["action_taken"] for r in results):
        issue_nums = [r["issue"] for r in results if r["action_taken"]]
        action_type = "add/remove" if len(set(r["type"] for r in results)) > 1 else results[0]["type"]

        print("Building and validating...")
        if build_and_validate():
            print("Build validation passed")
            sha = commit_changes(issue_nums, action_type, domains_to_build)
            print(f"Committed changes: {sha}")

            if push_changes():
                print("Pushed to origin/master")

                # Comment on issues
                for result in results:
                    if result["action_taken"]:
                        print(f"Would comment on issue #{result['issue']}: {result['message']}")
                        # In a real implementation, this would use gh issue comment
            else:
                print("Push failed")
        else:
            print("Build validation failed, not committing")

    elapsed = time.time() - start_time
    print(f"Batch processing completed in {elapsed:.0f}s")

    # Clean up lock file on success
    try:
        import shutil
        shutil.rmtree(LOCK_DIR)
        print("Lock file removed")
    except Exception as e:
        print(f"Warning: Could not remove lock file: {e}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
