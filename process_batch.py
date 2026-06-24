#!/usr/bin/env python3
import json
import os
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path('/home/administrator/.hermes/workspace/Lists')
BATCH_REVIEW = REPO_ROOT / 'batch_review.json'

def load_batch():
    with open(BATCH_REVIEW, 'r') as f:
        return json.load(f)

def domain_in_lists(domain):
    """Return list of files (relative to REPO_ROOT) where domain appears as 0.0.0.0 <domain> or similar."""
    found = []
    # Check all .txt files in root (excluding generated ones? we'll check all)
    for txt_file in REPO_ROOT.glob('*.txt'):
        # Skip backup files
        if txt_file.suffix in ['.bak', '.backup'] or '.backup' in str(txt_file):
            continue
        try:
            content = txt_file.read_text(encoding='utf-8')
            # Look for lines that start with 0.0.0.0 followed by the domain (possibly with whitespace)
            pattern = rf'^0\.0\.0\.0\s+{re.escape(domain)}\s*$'
            if re.search(pattern, content, re.MULTILINE):
                found.append(str(txt_file.relative_to(REPO_ROOT)))
        except Exception as e:
            print(f"Error reading {txt_file}: {e}", file=sys.stderr)
    return found

def remove_domain_from_file(domain, filepath):
    """Remove lines containing the domain from the file. Returns True if changed."""
    path = REPO_ROOT / filepath
    try:
        content = path.read_text(encoding='utf-8')
        # Remove lines that define the domain (0.0.0.0 domain) and also comments that mention the domain?
        # We'll just remove lines that start with 0.0.0.0 and the domain.
        lines = content.splitlines()
        new_lines = []
        removed = False
        for line in lines:
            # Match lines like: 0.0.0.0 example.com
            # Also could be with tabs or multiple spaces.
            if re.match(r'^0\.0\.0\.0\s+' + re.escape(domain) + r'\s*$', line):
                removed = True
                continue  # skip this line
            new_lines.append(line)
        if removed:
            new_content = '\n'.join(new_lines)
            if new_content and not new_content.endswith('\n'):
                new_content += '\n'
            path.write_text(new_content, encoding='utf-8')
        return removed
    except Exception as e:
        print(f"Error processing {path}: {e}", file=sys.stderr)
        return False

def run_build():
    """Run the build script to regenerate derived files."""
    try:
        subprocess.run([sys.executable, 'build.py'], check=True, cwd=REPO_ROOT)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Build failed: {e}", file=sys.stderr)
        return False

def git_add_commit(message):
    """Add all changes, commit with message."""
    try:
        subprocess.run(['git', 'add', '-A'], check=True, cwd=REPO_ROOT)
        # Check if there are changes to commit
        result = subprocess.run(['git', 'diff', '--cached', '--quiet'], capture_output=True)
        if result.returncode == 0:
            print("No changes to commit.")
            return False
        subprocess.run(['git', 'commit', '-m', message], check=True, cwd=REPO_ROOT)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Git commit failed: {e}", file=sys.stderr)
        return False

def git_push():
    try:
        subprocess.run(['git', 'push'], check=True, cwd=REPO_ROOT)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Git push failed: {e}", file=sys.stderr)
        return False

def comment_on_issue(issue_number, body):
    """Post a comment on the issue using gh."""
    try:
        subprocess.run([
            'gh', 'issue', 'comment', str(issue_number),
            '--repo', 'blocklistproject/Lists',
            '--body', body
        ], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Failed to comment on issue {issue_number}: {e}", file=sys.stderr)
        return False

def close_issue(issue_number, reason='completed'):
    """Close the issue with a reason."""
    try:
        subprocess.run([
            'gh', 'issue', 'close', str(issue_number),
            '--repo', 'blocklistproject/Lists',
            '--reason', reason
        ], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Failed to close issue {issue_number}: {e}", file=sys.stderr)
        return False

def main():
    data = load_batch()
    processed = []
    for item in data:
        issue = item['issue']
        triage = item['triage']
        domains = item.get('domains', {})
        number = issue['number']
        title = issue['title']
        request_type = triage.get('request_type', '')
        print(f"Processing issue #{number}: {title} (type: {request_type})")
        
        if request_type != 'remove':
            print("  Skipping non-remove request.")
            continue
        
        # For each domain in the issue
        for domain, checks in domains.items():
            print(f"  Checking domain: {domain}")
            dns_info = checks.get('dns', {})
            http_info = checks.get('http', {})
            resolves = dns_info.get('resolves', False)
            # Determine if it's a false positive: if DNS fails, likely not a valid domain to block.
            # Also if HTTP shows a legitimate site (we could check status and content-type, but skip for now)
            is_false_positive = not resolves  # simple heuristic
            
            if not is_false_positive:
                print(f"    Domain resolves ({dns_info.get('ips', [])}), assuming not a false positive. Skipping.")
                continue
            
            # Check where the domain appears
            files = domain_in_lists(domain)
            if not files:
                print(f"    Domain {domain} not found in any list. Marking as already removed.")
                # Comment and close
                comment = f"The domain `{domain}` was not found in any blocklist. It may have already been removed."
                comment_on_issue(number, comment)
                close_issue(number, 'completed')
                continue
            
            print(f"    Found in: {', '.join(files)}")
            # Remove from each file
            any_removed = False
            for f in files:
                if remove_domain_from_file(domain, f):
                    any_removed = True
                    print(f"    Removed from {f}")
            
            if any_removed:
                # Rebuild derived files
                if not run_build():
                    print("    Build failed; aborting further processing.")
                    sys.exit(1)
                # Commit
                commit_msg = f"Remove false positive {domain} (closes #{number})\\n\\nRemoved from: {', '.join(files)}"
                if not git_add_commit(commit_msg):
                    print("    No changes to commit after removal?")
                else:
                    if not git_push():
                        print("    Push failed.")
                    else:
                        print("    Changes pushed.")
                # Get the commit SHA for commenting
                result = subprocess.run(['git', 'rev-parse', 'HEAD'], capture_output=True, text=True, check=True)
                commit_sha = result.stdout.strip()
                # Comment on issue
                comment = f"Removed false positive `{domain}` from the following lists: {', '.join(files)}\\n\\nCommit: {commit_sha}"
                comment_on_issue(number, comment)
                close_issue(number, 'completed')
                processed.append((number, domain, files))
            else:
                print(f"    No removal performed (maybe already absent?).")
                comment_on_issue(number, f"Domain `{domain}` appears to be already absent from the lists.")
                close_issue(number, 'completed')
    
    print(f"Processed {len(processed)} issues.")
    return 0

if __name__ == '__main__':
    sys.exit(main())
