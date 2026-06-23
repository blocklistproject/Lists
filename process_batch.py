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
    # We'll extract the sample domains from the <details> section
    # Look for the code block after "<details>" and before "</details>"
    # We'll extract lines that look like domains (not starting with #)
    domains = []
    in_details = False
    for line in body.split('\\n'):
        if '<details>' in line:
            in_details = True
            continue
        if '</details>' in line:
            in_details = False
            break
        if in_details:
            line = line.strip()
            if line.startswith('#') or not line:
                continue
            # Assume the line is a domain (first token)
            parts = line.split()
            if parts:
                domain = parts[0]
                if domain.endswith('.'):
                    domain = domain[:-1]
                domains.append(domain)
    
    # Limit to first 50 domains to avoid too much processing
    domains_to_check = domains[:50]
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
        
        # Get commit SHA
        result = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=REPO_DIR, capture_output=True, text=True, check=True)
        commit_sha = result.stdout.strip()
        
        # Comment on issue
        comment = f'Removed {len(dead_domains)} dead domains from the sample (see commit).\\n\\n' + \
                  '\\n'.join([f'- {domain} (from: {", ".join(lists)})' for domain, lists in removed_from.items()]) + \
                  f'\\n\\nCommit: {commit_sha}'
        subprocess.run(['gh', 'issue', 'comment', str(issue_num), '--body', comment], cwd=REPO_DIR, check=True)
        
        # Update labels: remove status:needs-triage, add status:verified-removed
        subprocess.run(['gh', 'issue', 'edit', str(issue_num), '--remove-label', 'status:needs-triage'], cwd=REPO_DIR, check=True)
        subprocess.run(['gh', 'issue', 'edit', str(issue_num), '--add-label', 'status:verified-removed'], cwd=REPO_DIR, check=True)
        
        print(f'  Processed issue #{issue_num}')
    except subprocess.CalledProcessError as e:
        print(f'  Error processing issue #{issue_num}: {e}')
        comment = f'Failed to process dead domains: {e}'
        subprocess.run(['gh', 'issue', 'comment', str(issue_num), '--body', comment], cwd=REPO_DIR, check=True)

def process_add_remove_request(issue):
    """Process an add or remove request issue."""
    issue_num = issue['number']
    print(f'Processing issue #{issue_num}: {issue["title"]}')
    
    labels = [label['name'] for label in issue['labels']]
    body = issue['body']
    
    # Extract the domain from the issue body (look for the first line after "### Domain to add" or "### Domain to remove")
    # We'll look for a line that contains a domain (simplified)
    domain = None
    target_list = None
    operation = None  # 'add' or 'remove'
    
    lines = body.split('\\n')
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.lower().startswith('### domain to add') or stripped.lower().startswith('**url you wish to be added'):
            operation = 'add'
            # Look for the domain in the next few lines
            for j in range(i+1, min(i+5, len(lines))):
                candidate = lines[j].strip()
                if candidate and not candidate.startswith('#') and not candidate.startswith('###') and not candidate.startswith('**'):
                    candidate = candidate.split()[0] if candidate.split() else ''
                    candidate = candidate.replace('https://', '').replace('http://', '').split('/')[0]
                    if '.' in candidate:
                        domain = candidate
                        break
            # Also look for target list
            for j in range(i+1, min(i+10, len(lines))):
                if lines[j].strip().startswith('### Target blocklist'):
                    target_list = lines[j+1].strip()
                    break
            break
        elif stripped.lower().startswith('### domain to remove') or stripped.lower().startswith('**url you wish to be removed'):
            operation = 'remove'
            for j in range(i+1, min(i+5, len(lines))):
                candidate = lines[j].strip()
                if candidate and not candidate.startswith('#') and not candidate.startswith('###') and not candidate.startswith('**'):
                    candidate = candidate.split()[0] if candidate.split() else ''
                    candidate = candidate.replace('https://', '').replace('http://', '').split('/')[0]
                    if '.' in candidate:
                        domain = candidate
                        break
            for j in range(i+1, min(i+10, len(lines))):
                if lines[j].strip().startswith('### Current blocklist'):
                    target_list = lines[j+1].strip()
                    break
            break
    
    if not domain or not target_list or not operation:
        # Fallback: just ask for more information
        comment = 'Could not extract domain and target list from the issue. Please provide the domain and target blocklist in the specified format.'
        subprocess.run(['gh', 'issue', 'comment', str(issue_num), '--body', comment], cwd=REPO_DIR, check=True)
        subprocess.run(['gh', 'issue', 'edit', str(issue_num), '--add-label', 'status:needs-info'], cwd=REPO_DIR, check=True)
        return
    
    # Normalize target list name (remove .txt if present, and match to our list files)
    target_list = target_list.lower().replace('.txt', '')
    
    # Check if the domain is already in the target list (for add) or not in the list (for remove)
    lists_containing = find_lists_containing_domain(domain)
    currently_listed = target_list in lists_containing
    
    if operation == 'add':
        if currently_listed:
            comment = f'The domain `{domain}` is already present in the `{target_list}` list. No action needed.'
            subprocess.run(['gh', 'issue', 'comment', str(issue_num), '--body', comment], cwd=REPO_DIR, check=True)
            subprocess.run(['gh', 'issue', 'edit', str(issue_num), '--add-label', 'status:duplicate'], cwd=REPO_DIR, check=True)
            return
        else:
            # Verify the domain is active
            alive = check_domain_alive(domain)
            if not alive:
                comment = f'The domain `{domain}` does not appear to be active. Please verify the domain is correct and active.'
                subprocess.run(['gh', 'issue', 'comment', str(issue_num), '--body', comment], cwd=REPO_DIR, check=True)
                subprocess.run(['gh', 'issue', 'edit', str(issue_num), '--add-label', 'status:needs-info'], cwd=REPO_DIR, check=True)
                return
            # Add the domain to the list
            list_file = os.path.join(LIST_DIR, f'{target_list}.txt')
            if not os.path.exists(list_file):
                comment = f'The target list `{target_list}` does not exist. Please verify the list name.'
                subprocess.run(['gh', 'issue', 'comment', str(issue_num), '--body', comment], cwd=REPO_DIR, check=True)
                return
            with open(list_file, 'r') as f:
                lines = f.readlines()
            # Check if domain already exists (should not, but double-check)
            for line in lines:
                stripped = line.strip()
                if stripped.startswith('#') or not stripped:
                    continue
                parts = stripped.split()
                if parts and parts[0] == domain:
                    comment = f'The domain `{domain}` is already present in the `{target_list}` list. No action needed.'
                    subprocess.run(['gh', 'issue', 'comment', str(issue_num), '--body', comment], cwd=REPO_DIR, check=True)
                    return
            # Add the domain
            lines.append(f'{domain}\\n')
            with open(list_file, 'w') as f:
                f.writelines(lines)
            # Update generated formats
            subprocess.run(['python3', 'build.py'], cwd=REPO_DIR, check=True)
            # Commit
            subprocess.run(['git', 'add', '.'], cwd=REPO_DIR, check=True)
            commit_msg = f'Add {domain} to {target_list} list from issue #{issue_num}'
            subprocess.run(['git', 'commit', '-m', commit_msg], cwd=REPO_DIR, check=True)
            subprocess.run(['git', 'push', 'origin', 'master'], cwd=REPO_DIR, check=True)
            # Get commit SHA
            result = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=REPO_DIR, capture_output=True, text=True, check=True)
            commit_sha = result.stdout.strip()
            comment = f'Added `{domain}` to the `{target_list}` list.\\n\\nCommit: {commit_sha}'
            subprocess.run(['gh', 'issue', 'comment', str(issue_num), '--body', comment], cwd=REPO_DIR, check=True)
            # Update labels
            subprocess.run(['gh', 'issue', 'edit', str(issue_num), '--remove-label', 'status:needs-info'], cwd=REPO_DIR, check=True)
            subprocess.run(['gh', 'issue', 'edit', str(issue_num), '--remove-label', 'request:add'], cwd=REPO_DIR, check=True)
            subprocess.run(['gh', 'issue', 'edit', str(issue_num), '--add-label', 'status:verified-new'], cwd=REPO_DIR, check=True)
            print(f'  Added {domain} to {target_list} list')
    else:  # remove
        if not currently_listed:
            comment = f'The domain `{domain}` is not present in the `{target_list}` list. No action needed.'
            subprocess.run(['gh', 'issue', 'comment', str(issue_num), '--body', comment], cwd=REPO_DIR, check=True)
            subprocess.run(['gh', 'issue', 'edit', str(issue_num), '--add-label', 'status:not-found'], cwd=REPO_DIR, check=True)
            return
        else:
            # Verify the domain is currently blocked (we already know it is in the list)
            # Remove the domain from the list
            list_file = os.path.join(LIST_DIR, f'{target_list}.txt')
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
            # Update generated formats
            subprocess.run(['python3', 'build.py'], cwd=REPO_DIR, check=True)
            # Commit
            subprocess.run(['git', 'add', '.'], cwd=REPO_DIR, check=True)
            commit_msg = f'Remove {domain} from {target_list} list from issue #{issue_num}'
            subprocess.run(['git', 'commit', '-m', commit_msg], cwd=REPO_DIR, check=True)
            subprocess.run(['git', 'push', 'origin', 'master'], cwd=REPO_DIR, check=True)
            # Get commit SHA
            result = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=REPO_DIR, capture_output=True, text=True, check=True)
            commit_sha = result.stdout.strip()
            comment = f'Removed `{domain}` from the `{target_list}` list.\\n\\nCommit: {commit_sha}'
            subprocess.run(['gh', 'issue', 'comment', str(issue_num), '--body', comment], cwd=REPO_DIR, check=True)
            # Update labels
            subprocess.run(['gh', 'issue', 'edit', str(issue_num), '--remove-label', 'status:needs-info'], cwd=REPO_DIR, check=True)
            subprocess.run(['gh', 'issue', 'edit', str(issue_num), '--remove-label', 'request:remove'], cwd=REPO_DIR, check=True)
            subprocess.run(['gh', 'issue', 'edit', str(issue_num), '--add-label', 'status:verified-removed'], cwd=REPO_DIR, check=True)
            print(f'  Removed {domain} from {target_list} list')

def process_other_issue(issue):
    """Process an issue that doesn't match known request types."""
    issue_num = issue['number']
    comment = 'No actionable request found; please use the appropriate template for add/remove requests or maintenance reports.'
    subprocess.run(['gh', 'issue', 'comment', str(issue_num), '--body', comment], cwd=REPO_DIR, check=True)
    subprocess.run(['gh', 'issue', 'edit', str(issue_num), '--add-label', 'status:needs-triage'], cwd=REPO_DIR, check=True)

def main():
    # Read issues from stdin (as JSON array)
    data = sys.stdin.read()
    issues = json.loads(data)
    
    print(f'Processing {len(issues)} issues')
    
    for issue in issues:
        labels = [label['name'] for label in issue['labels']]
        if 'request:maintenance' in labels:
            process_dead_domain_report(issue)
        elif 'request:add' in labels or 'request:remove' in labels:
            process_add_remove_request(issue)
        else:
            process_other_issue(issue)

if __name__ == '__main__':
    main()