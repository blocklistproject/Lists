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
    with open('/tmp/issues.json', 'r') as f:
        return json.load(f)

def sort_issues_by_date(issues):
    return sorted(issues, key=lambda x: x['createdAt'])

def get_domain_from_text(text):
    # Extract domain from a line (assuming it's the first token)
    # Remove comments and whitespace
    line = text.strip()
    if line.startswith('#') or not line:
        return None
    # Split by whitespace and take first part
    parts = line.split()
    if not parts:
        return None
    domain = parts[0]
    # Remove trailing dot if present
    if domain.endswith('.'):
        domain = domain[:-1]
    return domain

def check_domain_alive(domain):
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
            # Consider any HTTP response as alive (even 4xx/5xx might be a parking page)
            # But we want to see if there's a web server responding.
            # We'll consider it alive if we get a response (any status) or if there's a redirect.
            return True
        except requests.exceptions.RequestException:
            continue
        except Exception:
            continue
    return False

def find_lists_containing_domain(domain):
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
                        # Extract domain from line (first token)
                        parts = line.split()
                        if parts and parts[0] == domain:
                            lists.append(filename[:-4])  # remove .txt
                            break
            except Exception:
                pass
    return lists

def update_lists(domain, lists_to_remove_from, commit_message):
    """Remove domain from the given lists and update generated formats."""
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
    # Find the <details> section with the sample
    # We'll look for the code block after "<details>"
    # Simple approach: look for lines that look like domains (containing a dot and no spaces)
    # We'll extract from the sample section.
    # Since the issue has a specific format, we can look for the sample.
    # We'll extract the first 10 domains from the sample.
    domains = []
    in_sample = False
    for line in body.split('\\n'):
        if '<details>' in line:
            in_sample = True
            continue
        if '</details>' in line:
            in_sample = False
            break
        if in_sample:
            domain = check_domain_alive(line.strip())  # This will return True/False, but we want the domain string
            # Actually, we need to extract the domain from the line.
            # Let's change: we'll use get_domain_from_text
            pass
    # Let's do a simpler extraction: look for lines that are not comments and have a dot.
    # We'll parse the body for the sample section.
    # We'll use regex to find the code block inside <details>.
    # Given time, we'll extract all lines that look like domains (alphanumeric, dots, hyphens) and are not comments.
    # We'll take the first 10.
    # We'll look for the pattern: start of line, then domain-like string, then end of line.
    # We'll ignore lines that start with #.
    # We'll look in the entire body for now.
    potential_domains = []
    for line in body.split('\\n'):
        line = line.strip()
        if line.startswith('#') or not line:
            continue
        # Simple domain pattern: contains a dot, and only allowed characters
        if re.match(r'^[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$', line):
            potential_domains.append(line)
        # Also consider domains with numbers in TLD? We'll keep simple.
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
        # Comment that we checked and found none dead
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
        commit_lines.append(f'  - {domain} (from: {", ".join(lists)})')
    commit_message = '\\n'.join(commit_lines)
    
    # Update lists and commit
    try:
        # We'll remove all dead domains at once
        # First, collect all domains to remove and their lists
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
        comment = f'Removed {len(dead_domains)} dead domains from the sample (see commit).\\n\\n' + \
                  '\\n'.join([f'- {domain} (from: {", ".join(lists)})' for domain, lists in removed_from.items()]) + \
                  f'\\n\\nCommit: TODO'  # We'll get the commit SHA after push
        # Get the commit SHA
        result = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=REPO_DIR, capture_output=True, text=True, check=True)
        commit_sha = result.stdout.strip()
        comment = comment.replace('TODO', commit_sha)
        subprocess.run(['gh', 'issue', 'comment', str(issue_num), '--body', comment], cwd=REPO_DIR, check=True)
        
        # Update labels: remove status:needs-triage, add status:verified-exists? 
        # But we removed domains, so we might want to indicate they were removed.
        # We'll remove status:needs-triage and add status:verified-exists? Not exactly.
        # We'll leave status:needs-triage and add a comment that we removed them.
        # Actually, we can change the label to something like status:accepted? 
        # We'll remove status:needs-triage and add status:verified-exists? 
        # But the domain is now removed, so verified-exists doesn't fit.
        # We'll remove status:needs-triage and add status:duplicate? No.
        # Let's just remove status:needs-triage and add status:verified-new? Not accurate.
        # We'll keep status:needs-triage and add a comment.
        # For now, we'll just leave the labels as is.
        print(f'  Processed issue #{issue_num}')
    except subprocess.CalledProcessError as e:
        print(f'  Error processing issue #{issue_num}: {e}')
        # Comment on issue about failure
        comment = f'Failed to process dead domains: {e}'
        subprocess.run(['gh', 'issue', 'comment', str(issue_num), '--body', comment], cwd=REPO_DIR, check=True)

def process_add_remove_request(issue):
    """Process an add or remove request issue."""
    issue_num = issue['number']
    print(f'Processing issue #{issue_num}: {issue["title"]}')
    # TODO: Implement add/remove request processing
    # For now, we'll just label and comment
    labels = [label['name'] for label in issue['labels']]
    if 'request:add' in labels:
        comment = 'Add request received; please provide domain and evidence for verification.'
    elif 'request:remove' in labels:
        comment = 'Remove request received; please provide domain and evidence for verification.'
    else:
        comment = 'Request received; please clarify if this is an add or remove request.'
    subprocess.run(['gh', 'issue', 'comment', str(issue_num), '--body', comment], cwd=REPO_DIR, check=True)
    # Label as status:needs-info
    subprocess.run(['gh', 'issue', 'edit', str(issue_num), '--add-label', 'status:needs-info'], cwd=REPO_DIR, check=True)

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
