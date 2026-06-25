#!/usr/bin/env python3
"""Process GitHub issues in batches for triage."""
import json
import os
import re
import socket
import subprocess
import sys
from datetime import datetime

import requests

# Configuration
REPO_DIR = '/home/administrator/.hermes/workspace/Lists'
LIST_DIR = REPO_DIR
LOCK_FILE = '/tmp/blocklistproject-triage-cron.lock'
STARTED_FILE = os.path.join(LOCK_FILE, 'started')

def load_issues():
    """Fetch open issues from GitHub."""
    cmd = ["gh", "issue", "list", "--repo", "blocklistproject/Lists", "--state", "open", "--limit", "100", "--json", "number,title,author,createdAt,updatedAt,body,labels"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Failed to fetch issues: {result.stderr}")
    return json.loads(result.stdout)

def sort_issues_by_date(issues):
    return sorted(issues, key=lambda x: x['createdAt'])

def split_fields(body: str) -> dict[str, str]:
    """Parse markdown fields from issue body."""
    matches = list(re.finditer(r'^###\s+(.+?)\s*$', body or '', re.M))
    fields: dict[str, str] = {}
    for i, m in enumerate(matches):
        key = m.group(1).strip().lower()
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(body)
        fields[key] = body[start:end].strip()
    return fields

def normalize_domain(text: str | None) -> str | None:
    """Normalize a domain string."""
    if not text:
        return None
    text = text.strip().strip('`<>[]{}.,;\'"')
    if not text or text.lower() in {'_no response_', 'no response'}:
        return None
    if '://' in text:
        from urllib.parse import urlparse
        host = urlparse(text).hostname
    else:
        m = re.search(r'(?i)\b((?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,})', text)
        host = m.group(1) if m else text.split()[0] if text.split() else None
    if not host:
        return None
    host = host.lower().strip('.')
    if not re.match(r'^[a-z0-9_.-]+\.[a-z]{2,}$', host):
        return None
    return host

def check_domain_alive(domain: str) -> bool:
    """Return True if domain appears alive."""
    try:
        socket.getaddrinfo(domain, 80, timeout=5)
        return True
    except (socket.gaierror, Exception):
        pass
    for protocol in ['http', 'https']:
        url = f'{protocol}://{domain}'
        try:
            resp = requests.head(url, timeout=10, allow_redirects=True)
            return True
        except requests.exceptions.RequestException:
            continue
        except Exception:
            continue
    return False

def find_lists_containing_domain(domain: str) -> list[str]:
    """Return list filenames containing the domain."""
    lists = []
    for filename in os.listdir(LIST_DIR):
        if filename.endswith('.txt') and filename != 'dead-domains.txt':
            path = os.path.join(LIST_DIR, filename)
            try:
                with open(path, 'r') as f:
                    for line in f:
                        stripped = line.strip()
                        if stripped.startswith('#') or not stripped:
                            continue
                        parts = stripped.split()
                        if parts and parts[0] == domain:
                            lists.append(filename[:-4])
                            break
            except Exception:
                pass
    return lists

def update_lists(domain: str, lists_to_remove_from: list[str], lists_to_add_to: list[str], commit_message: str):
    """Update list files and push changes."""
    for list_name in lists_to_remove_from:
        list_file = os.path.join(LIST_DIR, f'{list_name}.txt')
        if not os.path.exists(list_file):
            continue
        with open(list_file, 'r') as f:
            lines = f.readlines()
        new_lines = []
        for line in lines:
            stripped = line.strip()
            if stripped.startswith('#') or not stripped:
                new_lines.append(line)
                continue
            parts = stripped.split()
            if parts and parts[0] == domain:
                continue
            new_lines.append(line)
        with open(list_file, 'w') as f:
            f.writelines(new_lines)

    for list_name in lists_to_add_to:
        list_file = os.path.join(LIST_DIR, f'{list_name}.txt')
        if not os.path.exists(list_file):
            continue
        exists = False
        with open(list_file, 'r') as f:
            for line in f:
                stripped = line.strip()
                if stripped.startswith('#') or not stripped:
                    continue
                parts = line.split()
                if parts and parts[0].lower() == domain.lower():
                    exists = True
                    break
        if not exists:
            with open(list_file, 'a') as f:
                f.write(f'{domain}\n')

    subprocess.run(['python3', 'build.py'], cwd=REPO_DIR, check=True)
    subprocess.run(['git', 'add', '.'], cwd=REPO_DIR, check=True)
    subprocess.run(['git', 'commit', '-m', commit_message], cwd=REPO_DIR, check=True)
    subprocess.run(['git', 'push', 'origin', 'master'], cwd=REPO_DIR, check=True)

def process_dead_domain_report(issue):
    """Process a maintenance/dead domain report."""
    issue_num = issue['number']
    print(f'Processing issue #{issue_num}: {issue["title"]}')
    body = issue['body']
    potential_domains = []
    for line in body.split('\n'):
        line = line.strip()
        if line.startswith('#') or not line:
            continue
        if re.match(r'^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', line):
            potential_domains.append(line)
    domains_to_check = potential_domains[:10]
    print(f'  Found {len(domains_to_check)} domains to check from sample')

    dead_domains = []
    for domain in domains_to_check:
        if not check_domain_alive(domain):
            dead_domains.append(domain)
            print(f'  {domain}: dead')
        else:
            print(f'  {domain}: alive (skipping removal)')

    if not dead_domains:
        print('  No dead domains found in sample; skipping')
        comment = f'Checked {len(domains_to_check)} domains from the sample; all appear alive. No action taken.'
        subprocess.run(['gh', 'issue', 'comment', str(issue_num), '--body', comment], cwd=REPO_DIR, check=True)
        return

    removed_from = {}
    for domain in dead_domains:
        lists = find_lists_containing_domain(domain)
        if lists:
            removed_from[domain] = lists
        else:
            print(f'  Warning: {domain} not found in any list')

    if not removed_from:
        print('  No domains found in any list; skipping')
        comment = f'Checked {len(dead_domains)} dead domains from sample; none found in current lists. No action taken.'
        subprocess.run(['gh', 'issue', 'comment', str(issue_num), '--body', comment], cwd=REPO_DIR, check=True)
        return

    commit_lines = [f'Remove dead domains from issue #{issue_num}']
    for domain, lists in removed_from.items():
        commit_lines.append(f'  - {domain} (from: {", ".join(lists)})')
    commit_message = '\n'.join(commit_lines)

    try:
        all_lists_to_update = set()
        for lists in removed_from.values():
            all_lists_to_update.update(lists)

        for domain, lists in removed_from.items():
            for list_name in lists:
                list_file = os.path.join(LIST_DIR, f'{list_name}.txt')
                if not os.path.exists(list_file):
                    continue
                with open(list_file, 'r') as f:
                    lines = f.readlines()
                new_lines = []
                for line in lines:
                    stripped = line.strip()
                    if stripped.startswith('#') or not stripped:
                        new_lines.append(line)
                        continue
                    parts = stripped.split()
                    if parts and parts[0] == domain:
                        continue
                    new_lines.append(line)
                with open(list_file, 'w') as f:
                    f.writelines(new_lines)

        subprocess.run(['python3', 'build.py'], cwd=REPO_DIR, check=True)
        subprocess.run(['git', 'add', '.'], cwd=REPO_DIR, check=True)
        result = subprocess.run(['git', 'commit', '-m', commit_message], cwd=REPO_DIR, capture_output=True, text=True)
        if result.returncode != 0 and 'nothing to commit' not in result.stderr:
            raise RuntimeError(result.stderr)
        subprocess.run(['git', 'push', 'origin', 'master'], cwd=REPO_DIR, check=True)

        result = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=REPO_DIR, capture_output=True, text=True, check=True)
        commit_sha = result.stdout.strip()
        comment = f'Removed {len(dead_domains)} dead domains from the sample (see commit).\n\n' + \
                  '\n'.join([f'- {domain} (from: {", ".join(lists)})' for domain, lists in removed_from.items()]) + \
                  f'\n\nCommit: {commit_sha}'
        subprocess.run(['gh', 'issue', 'comment', str(issue_num), '--body', comment], cwd=REPO_DIR, check=True)
        subprocess.run(['gh', 'issue', 'edit', str(issue_num), '--remove-label', 'status:needs-info'], cwd=REPO_DIR, check=True)
        subprocess.run(['gh', 'issue', 'edit', str(issue_num), '--add-label', 'status:completed'], cwd=REPO_DIR, check=True)
        subprocess.run(['gh', 'issue', 'close', str(issue_num)], cwd=REPO_DIR, check=True)
        print(f'  Processed issue #{issue_num}')
    except subprocess.CalledProcessError as e:
        print(f'  Error processing issue #{issue_num}: {e}')
        comment = f'Failed to process dead domains: {e}'
        subprocess.run(['gh', 'issue', 'comment', str(issue_num), '--body', comment], cwd=REPO_DIR, check=True)

def process_add_remove_request(issue):
    """Process an add or remove request."""
    issue_num = issue['number']
    print(f'Processing issue #{issue_num}: {issue["title"]}')
    body = issue['body']
    fields = split_fields(body)
    labels = [label['name'] for label in issue['labels']]
    if 'request:add' in labels:
        action = 'add'
    elif 'request:remove' in labels:
        action = 'remove'
    else:
        if 'domain to add' in fields:
            action = 'add'
        elif 'domain to remove' in fields:
            action = 'remove'
        else:
            comment = 'No actionable request found; please use the appropriate template for add/remove requests.'
            subprocess.run(['gh', 'issue', 'comment', str(issue_num), '--body', comment], cwd=REPO_DIR, check=True)
            subprocess.run(['gh', 'issue', 'edit', str(issue_num), '--add-label', 'status:needs-triage'], cwd=REPO_DIR, check=True)
            return

    domain_field = fields.get('domain to add') if action == 'add' else fields.get('domain to remove')
    domain = normalize_domain(domain_field)
    if not domain:
        domain = normalize_domain(body)
    if not domain:
        comment = f'Could not extract domain from the issue. Please provide a clear domain to {action}.'
        subprocess.run(['gh', 'issue', 'comment', str(issue_num), '--body', comment], cwd=REPO_DIR, check=True)
        subprocess.run(['gh', 'issue', 'edit', str(issue_num), '--add-label', 'status:needs-info'], cwd=REPO_DIR, check=True)
        return

    target_field = fields.get('target blocklist') or fields.get('current blocklist')
    target_list = target_field.strip().lower() if target_field else ''
    if target_list.endswith('.txt'):
        target_list = target_list[:-4]

    if action == 'add':
        if not check_domain_alive(domain):
            comment = f'Domain {domain} failed verification (DNS or HTTP check). Please provide evidence that the domain is active and should be blocked.'
            subprocess.run(['gh', 'issue', 'comment', str(issue_num), '--body', comment], cwd=REPO_DIR, check=True)
            subprocess.run(['gh', 'issue', 'edit', str(issue_num), '--add-label', 'status:needs-info'], cwd=REPO_DIR, check=True)
            return

    lists_to_remove_from = []
    lists_to_add_to = []
    if action == 'remove':
        lists_to_remove_from = find_lists_containing_domain(domain)
        if not lists_to_remove_from:
            comment = f'Domain {domain} not found in any blocklist. Nothing to remove.'
            subprocess.run(['gh', 'issue', 'comment', str(issue_num), '--body', comment], cwd=REPO_DIR, check=True)
            subprocess.run(['gh', 'issue', 'edit', str(issue_num), '--add-label', 'status:needs-triage'], cwd=REPO_DIR, check=True)
            return
    else:
        if not target_list:
            comment = f'Please specify the target blocklist for adding {domain}.'
            subprocess.run(['gh', 'issue', 'comment', str(issue_num), '--body', comment], cwd=REPO_DIR, check=True)
            subprocess.run(['gh', 'issue', 'edit', str(issue_num), '--add-label', 'status:needs-info'], cwd=REPO_DIR, check=True)
            return
        lists_to_add_to = [target_list]

    action_word = 'Add' if action == 'add' else 'Remove'
    commit_lines = [f'{action_word} domain {domain} from issue #{issue_num}']
    if lists_to_remove_from:
        commit_lines.append(f'  Removed from: {", ".join(lists_to_remove_from)}')
    if lists_to_add_to:
        commit_lines.append(f'  Added to: {", ".join(lists_to_add_to)}')
    commit_message = '\n'.join(commit_lines)

    try:
        update_lists(domain, lists_to_remove_from, lists_to_add_to, commit_message)
        result = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=REPO_DIR, capture_output=True, text=True, check=True)
        commit_sha = result.stdout.strip()
        if action == 'add':
            comment = f'✅ Added {domain} to {", ".join(lists_to_add_to)}.\n\nDomain: {domain}\nAdded to: {", ".join(lists_to_add_to)}\n\nCommit: {commit_sha}'
        else:
            comment = f'✅ Removed {domain} from {", ".join(lists_to_remove_from)}.\n\nDomain: {domain}\nRemoved from: {", ".join(lists_to_remove_from)}\n\nCommit: {commit_sha}'
        subprocess.run(['gh', 'issue', 'comment', str(issue_num), '--body', comment], cwd=REPO_DIR, check=True)
        if 'status:needs-info' in labels:
            subprocess.run(['gh', 'issue', 'edit', str(issue_num), '--remove-label', 'status:needs-info'], cwd=REPO_DIR, check=True)
        subprocess.run(['gh', 'issue', 'edit', str(issue_num), '--add-label', 'status:completed'], cwd=REPO_DIR, check=True)
        subprocess.run(['gh', 'issue', 'close', str(issue_num)], cwd=REPO_DIR, check=True)
        print(f'  Processed issue #{issue_num}')
    except subprocess.CalledProcessError as e:
        print(f'  Error processing issue #{issue_num}: {e}')
        comment = f'Failed to process request: {e}'
        subprocess.run(['gh', 'issue', 'comment', str(issue_num), '--body', comment], cwd=REPO_DIR, check=True)

def process_unlabeled_issue(issue):
    """Handle unlabeled issues."""
    issue_num = issue['number']
    comment = 'No actionable request found; please use the appropriate template for add/remove requests or maintenance reports.'
    subprocess.run(['gh', 'issue', 'comment', str(issue_num), '--body', comment], cwd=REPO_DIR, check=True)
    subprocess.run(['gh', 'issue', 'edit', str(issue_num), '--add-label', 'status:needs-triage'], cwd=REPO_DIR, check=True)

def main():
    # Check lock file
    if os.path.exists(LOCK_FILE):
        if os.path.isfile(LOCK_FILE) or os.path.isdir(LOCK_FILE):
            if os.path.exists(STARTED_FILE):
                try:
                    with open(STARTED_FILE, 'r') as f:
                        created_at = f.read().strip()
                    # Parse timestamp and check age
                    # Format: 'Lock created at 2026-06-24T11:16:33-05:00'
                    match = re.search(r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}-\d{2}:\d{2})', created_at)
                    if match:
                        ts_str = match.group(1)
                        from datetime import timezone, timedelta
                        # Parse ISO format with timezone
                        dt = datetime.fromisoformat(ts_str)
                        now = datetime.now(dt.tzinfo)
                        age_seconds = (now - dt).total_seconds()
                        if age_seconds < 7200:  # 2 hours
                            print(f'Skipping: lock file is {age_seconds/60:.1f} minutes old (< 2 hours)')
                            sys.exit(0)
                except Exception as e:
                    print(f'Error checking lock file: {e}')
                    sys.exit(1)

    issues = load_issues()
    sorted_issues = sort_issues_by_date(issues)
    batch = sorted_issues[:10]
    print(f'Processing batch of {len(batch)} issues')

    for issue in batch:
        labels = [label['name'] for label in issue['labels']]
        if 'request:maintenance' in labels:
            process_dead_domain_report(issue)
        elif 'request:add' in labels or 'request:remove' in labels:
            process_add_remove_request(issue)
        else:
            process_unlabeled_issue(issue)

    print('Batch processing complete')

if __name__ == '__main__':
    main()
