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
LIST_DIR = REPO_DIR  # where the .txt files are
DEAD_DOMAINS_FILE = os.path.join(REPO_DIR, 'dead-domains.txt')

def load_issues():
    # Use gh to get open issues (excluding PRs)
    cmd = ["gh", "issue", "list", "--repo", "blocklistproject/Lists", "--state", "open", "--limit", "100", "--json", "number,title,author,createdAt,updatedAt,body,labels"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Failed to fetch issues: {result.stderr}")
    return json.loads(result.stdout)

def sort_issues_by_date(issues):
    return sorted(issues, key=lambda x: x['createdAt'])

def split_fields(body: str) -> dict[str, str]:
    # From review_issues_batch.py
    matches = list(re.finditer(r'^###\s+(.+?)\s*$', body or '', re.M))
    fields: dict[str, str] = {}
    for i, m in enumerate(matches):
        key = m.group(1).strip().lower()
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(body)
        fields[key] = body[start:end].strip()
    return fields

def normalize_domain(text: str) -> str | None:
    text = text.strip().strip('`<>[]{}.,;\\\'"')
    if not text or text.lower() in {'_no response_', 'no response'}:
        return None
    if '://' in text:
        from urllib.parse import urlparse
        host = urlparse(text).hostname
    else:
        # Simple domain regex
        m = re.search(r'(?i)\\b((?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\\.)+[a-z]{2,})', text)
        host = m.group(1) if m else text.split()[0] if text.split() else None
    if not host:
        return None
    host = host.lower().strip('.')
    if not re.match(r'^[a-z0-9_.-]+\\.[a-z]{2,}$', host):
        return None
    return host

def extract_domain_from_field(field_value: str) -> str | None:
    # Extract the first domain-like string from the field value
    if not field_value:
        return None
    # Look for a domain in the first line or first token
    lines = [line.strip() for line in field_value.split('\\n') if line.strip()]
    if not lines:
        return None
    first_line = lines[0]
    # Try to find a domain pattern
    domain = normalize_domain(first_line)
    if domain:
        return domain
    # Fallback: split by whitespace and take the first token
    parts = first_line.split()
    if parts:
        candidate = parts[0].strip('<>[]{}(),;:\\\"\'')
        if candidate:
            return normalize_domain(candidate)
    return None

def check_domain_alive(domain: str) -> bool:
    """Return True if domain appears alive (DNS or HTTP responds), False otherwise."""
    # DNS check
    try:
        socket.getaddrinfo(domain, 80, timeout=5)
        return True
    except socket.gaierror:
        pass
    except Exception:
        pass

    # HTTP check
    for protocol in ['http', 'https']:
        url = f'{protocol}://{domain}'
        try:
            resp = requests.head(url, timeout=10, allow_redirects=True)
            # Consider any HTTP response as alive
            return True
        except requests.exceptions.RequestException:
            continue
        except Exception:
            continue
    return False

def find_lists_containing_domain(domain: str) -> list[str]:
    """Return list of list filenames (without .txt) that contain the domain."""
    lists = []
    for filename in os.listdir(LIST_DIR):
        if filename.endswith('.txt') and filename != 'dead-domains.txt':
            path = os.path.join(LIST_DIR, filename)
            try:
                with open(path, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith('#') or not line:
                            continue
                        parts = line.split()
                        if parts and parts[0] == domain:
                            lists.append(filename[:-4])  # remove .txt
                            break
            except Exception:
                pass
    return lists

def update_lists(domain: str, lists_to_remove_from: list[str], lists_to_add_to: list[str], commit_message: str):
    """Remove domain from the given lists, add to the given lists, and update generated formats."""
    # Remove from each list
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
                # Skip this line (remove domain)
                continue
            new_lines.append(line)
        with open(list_file, 'w') as f:
            f.writelines(new_lines)
    
    # Add to each list (if not already present)
    for list_name in lists_to_add_to:
        list_file = os.path.join(LIST_DIR, f'{list_name}.txt')
        if not os.path.exists(list_file):
            continue
        # Check if domain already exists (case-insensitive)
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
                f.write(f'{domain}\\n')
    
    # Update generated formats by running build.py
    subprocess.run(['python3', 'build.py'], cwd=REPO_DIR, check=True)
    
    # Commit changes
    subprocess.run(['git', 'add', '.'], cwd=REPO_DIR, check=True)
    subprocess.run(['git', 'commit', '-m', commit_message], cwd=REPO_DIR, check=True)
    subprocess.run(['git', 'push', 'origin', 'master'], cwd=REPO_DIR, check=True)

def process_dead_domain_report(issue):
    """Process a maintenance/dead domain report issue."""
    issue_num = issue['number']
    print(f'Processing issue #{issue_num}: {issue["title"]}')
    
    # Extract dead domains from the issue body (from the sample in <details>)
    body = issue['body']
    # We'll extract the first 10 domains that look like domains from the body
    # Look for lines that are not comments and look like a domain
    potential_domains = []
    for line in body.split('\\n'):
        line = line.strip()
        if line.startswith('#') or not line:
            continue
        # Simple domain pattern: contains a dot, and only allowed characters
        if re.match(r'^[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$', line):
            potential_domains.append(line)
    # Take first 10
    domains_to_check = potential_domains[:10]
    print(f'  Found {len(domains_to_check)} domains to check from sample')
    
    # Verify each domain is dead
    dead_domains = []
    for domain in domains_to_check:
        alive = check_domain_alive(domain)
        if not alive:
            dead_domains.append(domain)
            print(f'  {domain}: dead')
        else:
            print(f'  {domain}: alive (skipping removal)')
    
    if not dead_domains:
        print('  No dead domains found in sample; skipping')
        comment = f'Checked {len(domains_to_check)} domains from the sample; all appear alive. No action taken.'
        subprocess.run(['gh', 'issue', 'comment', str(issue_num), '--body', comment], cwd=REPO_DIR, check=True)
        # Keep label as status:needs-triage
        return
    
    # For each dead domain, find which lists it belongs to and remove
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
    
    # Prepare commit message
    commit_lines = [f'Remove dead domains from issue #{issue_num}']
    for domain, lists in removed_from.items():
        comment_lines.append(f'  - {domain} (from: {", ".join(lists)})')
    commit_message = '\\n'.join(commit_lines)
    
    # Update lists and commit
    try:
        # We'll remove all dead domains at once
        all_lists_to_update = set()
        for lists in removed_from.values():
            all_lists_to_update.update(lists)
        
        # Remove each domain from its lists
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
        
        # Update generated formats
        subprocess.run(['python3', 'build.py'], cwd=REPO_DIR, check=True)
        
        # Commit
        subprocess.run(['git', 'add', '.'], cwd=REPO_DIR, check=True)
        subprocess.run(['git', 'commit', '-m', commit_message], cwd=REPO_DIR, check=True)
        subprocess.run(['git', 'push', 'origin', 'master'], cwd=REPO_DIR, check=True)
        
        # Comment on issue
        result = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=REPO_DIR, capture_output=True, text=True, check=True)
        commit_sha = result.stdout.strip()
        comment = f'Removed {len(dead_domains)} dead domains from the sample (see commit).\\n\\n' + \
                  '\\n'.join([f'- {domain} (from: {", ".join(lists)})' for domain, lists in removed_from.items()]) + \
                  f'\\n\\nCommit: {commit_sha}'
        subprocess.run(['gh', 'issue', 'comment', str(issue_num), '--body', comment], cwd=REPO_DIR, check=True)
        
        # Update labels: remove status:needs-info, add status:verified-exists? Actually, we removed them, so we can add status:verified-removed? 
        # We'll remove status:needs-info and add status:completed
        subprocess.run(['gh', 'issue', 'edit', str(issue_num), '--remove-label', 'status:needs-info'], cwd=REPO_DIR, check=True)
        subprocess.run(['gh', 'issue', 'edit', str(issue_num), '--add-label', 'status:completed'], cwd=REPO_DIR, check=True)
        # Close the issue
        subprocess.run(['gh', 'issue', 'close', str(issue_num)], cwd=REPO_DIR, check=True)
        
        print(f'  Processed issue #{issue_num}')
    except subprocess.CalledProcessError as e:
        print(f'  Error processing issue #{issue_num}: {e}')
        comment = f'Failed to process dead domains: {e}'
        subprocess.run(['gh', 'issue', 'comment', str(issue_num), '--body', comment], cwd=REPO_DIR, check=True)

def process_add_remove_request(issue):
    """Process an add or remove request issue."""
    issue_num = issue['number']
    print(f'Processing issue #{issue_num}: {issue["title"]}')
    
    body = issue['body']
    fields = split_fields(body)
    
    # Determine request type from labels or fields
    labels = [label['name'] for label in issue['labels']]
    if 'request:add' in labels:
        action = 'add'
    elif 'request:remove' in labels:
        action = 'remove'
    else:
        # Fallback to field names
        if 'domain to add' in fields:
            action = 'add'
        elif 'domain to remove' in fields:
            action = 'remove'
        else:
            # No clear request
            comment = 'No actionable request found; please use the appropriate template for add/remove requests.'
            subprocess.run(['gh', 'issue', 'comment', str(issue_num), '--body', comment], cwd=REPO_DIR, check=True)
            subprocess.run(['gh', 'issue', 'edit', str(issue_num), '--add-label', 'status:needs-triage'], cwd=REPO_DIR, check=True)
            return
    
    # Extract domain
    domain_field = fields.get('domain to add') if action == 'add' else fields.get('domain to remove')
    domain = extract_domain_from_field(domain_field)
    if not domain:
        # Try to find any domain in the body
        domain = extract_domain_from_field(body)
    if not domain:
        comment = f'Could not extract domain from the issue. Please provide a clear domain to {action}.'
        subprocess.run(['gh', 'issue', 'comment', str(issue_num), '--body', comment], cwd=REPO_DIR, check=True)
        subprocess.run(['gh', 'issue', 'edit', str(issue_num), '--add-label', 'status:needs-info'], cwd=REPO_DIR, check=True)
        return
    
    # Extract target list
    target_field = fields.get('target blocklist') or fields.get('current blocklist')
    target_list = target_field.strip().lower() if target_field else ''
    if not target_list:
        # Try to infer from labels or context
        # For now, we'll try to find a list file that matches common names
        # We'll leave it empty and try to find the domain in existing lists
        pass
    
    # Normalize target list name (remove .txt if present)
    if target_list.endswith('.txt'):
        target_list = target_list[:-4]
    
    # Verify domain if adding
    if action == 'add':
        if not check_domain_alive(domain):
            comment = f'Domain {domain} failed verification (DNS or HTTP check). Please provide evidence that the domain is active and should be blocked.'
            subprocess.run(['gh', 'issue', 'comment', str(issue_num), '--body', comment], cwd=REPO_DIR, check=True)
            subprocess.run(['gh', 'issue', 'edit', str(issue_num), '--add-label', 'status:needs-info'], cwd=REPO_DIR, check=True)
            return
    
    # Determine which lists to modify
    lists_to_remove_from = []
    lists_to_add_to = []
    if action == 'remove':
        # Find which lists contain the domain
        lists_to_remove_from = find_lists_containing_domain(domain)
        if not lists_to_remove_from:
            comment = f'Domain {domain} not found in any blocklist. Nothing to remove.'
            subprocess.run(['gh', 'issue', 'comment', str(issue_num), '--body', comment], cwd=REPO_DIR, check=True)
            # Label as status:not-found? We'll use status:needs-triage
            subprocess.run(['gh', 'issue', 'edit', str(issue_num), '--add-label', 'status:needs-triage'], cwd=REPO_DIR, check=True)
            return
    else:  # add
        # If target_list is specified, use it; otherwise, we need to decide where to add.
        # For simplicity, we'll add to a default list? But we don't know.
        # We'll look at the issue for hints: maybe the target is in the body.
        # If target_list is empty, we'll try to see if the domain is already in any list (should not be for add)
        # We'll default to 'basic' or something? Not safe.
        # Instead, we'll ask for clarification.
        if not target_list:
            comment = f'Please specify the target blocklist for adding {domain}.'
            subprocess.run(['gh', 'issue', 'comment', str(issue_num), '--body', comment], cwd=REPO_DIR, check=True)
            subprocess.run(['gh', 'issue', 'edit', str(issue_num), '--add-label', 'status:needs-info'], cwd=REPO_DIR, check=True)
            return
        lists_to_add_to = [target_list]
    
    # Prepare commit message
    if action == 'add':
        action_word = 'Add'
    else:
        action_word = 'Remove'
    commit_lines = [f'{action_word} domain {domain} from issue #{issue_num}']
    if lists_to_remove_from:
        commit_lines.append(f'  Removed from: {", ".join(lists_to_remove_from)}')
    if lists_to_add_to:
        commit_lines.append(f'  Added to: {", ".join(lists_to_add_to)}')
    commit_message = '\\n'.join(commit_lines)
    
    # Update lists and commit
    try:
        update_lists(domain, lists_to_remove_from, lists_to_add_to, commit_message)
        
        # Comment on issue
        if action == 'add':
            comment = f'✅ Added {domain} to {", ".join(lists_to_add_to)}.\\n\\n'
        else:
            comment = f'✅ Removed {domain} from {", ".join(lists_to_remove_from)}.\\n\\n'
        comment += f'Domain: {domain}\\n'
        if action == 'add':
            comment += f'Added to: {", ".join(lists_to_add_to)}\\n'
        else:
            comment += f'Removed from: {", ".join(lists_to_remove_from)}\\n'
        # Get commit SHA
        result = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=REPO_DIR, capture_output=True, text=True, check=True)
        commit_sha = result.stdout.strip()
        comment += f'\\nCommit: {commit_sha}'
        subprocess.run(['gh', 'issue', 'comment', str(issue_num), '--body', comment], cwd=REPO_DIR, check=True)
        
        # Update labels: remove status:needs-info, add status:completed
        if 'status:needs-info' in labels:
            subprocess.run(['gh', 'issue', 'edit', str(issue_num), '--remove-label', 'status:needs-info'], cwd=REPO_DIR, check=True)
        subprocess.run(['gh', 'issue', 'edit', str(issue_num), '--add-label', 'status:completed'], cwd=REPO_DIR, check=True)
        # Close the issue
        subprocess.run(['gh', 'issue', 'close', str(issue_num)], cwd=REPO_DIR, check=True)
        
        print(f'  Processed issue #{issue_num}')
    except subprocess.CalledProcessError as e:
        print(f'  Error processing issue #{issue_num}: {e}')
        comment = f'Failed to process request: {e}'
        subprocess.run(['gh', 'issue', 'comment', str(issue_num), '--body', comment], cwd=REPO_DIR, check=True)

def main():
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
            # No recognizable request label
            issue_num = issue['number']
            comment = 'No actionable request found; please use the appropriate template for add/remove requests or maintenance reports.'
            subprocess.run(['gh', 'issue', 'comment', str(issue_num), '--body', comment], cwd=REPO_DIR, check=True)
            subprocess.run(['gh', 'issue', 'edit', str(issue_num), '--add-label', 'status:needs-triage'], cwd=REPO_DIR, check=True)
    
    print('Batch processing complete')

if __name__ == '__main__':
    main()
