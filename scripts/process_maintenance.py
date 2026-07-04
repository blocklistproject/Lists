import json
import os
import socket
import subprocess
import sys
from pathlib import Path

import requests

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

try:
    from src.config import WORKSPACE_DIR
except ImportError:
    # Fallback to environment variables if src.config not available
    WORKSPACE_DIR = Path(os.environ.get("WORKSPACE_DIR", Path.cwd()))

# Configuration
REPO_DIR = WORKSPACE_DIR
LIST_DIR = REPO_DIR  # where the .txt files are
DEAD_DOMAINS_FILE = REPO_DIR / 'dead-domains.txt'

def check_domain_alive(domain):
    """Return True if domain appears alive (DNS or HTTP responds), False otherwise."""
    # DNS check
    try:
        socket.getaddrinfo(domain, 80, timeout=2)
        return True
    except socket.gaierror:
        pass
    except Exception:
        pass

    # HTTP check
    for protocol in ['http', 'https']:
        url = f'{protocol}://{domain}'
        try:
            requests.head(url, timeout=2, allow_redirects=True)
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
                with open(path) as f:
                    for line in f:
                        line = line.strip()
                        if not line or line.startswith('#'):
                            continue
                        # Extract potential domain from line
                        if line.startswith('0.0.0.0 '):
                            # Format: 0.0.0.0 domain [comment]
                            potential = line[8:].split()[0] if len(line) > 8 else ''
                        elif line.startswith('||') and '^' in line:
                            # Format: ||domain^
                            potential = line[2:].split('^')[0]
                        else:
                            # Assume the line is just the domain (maybe with a comment)
                            potential = line.split()[0] if line.split() else ''
                        if potential.lower() == domain.lower():
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
        with open(list_file) as f:
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
    subprocess.run(['git', 'push', 'origin', 'main'], cwd=REPO_DIR, check=True)

def extract_domains_from_issue_body(body):
    """Extract domains from the <details> section of the issue body."""
    lines = body.split('\n')
    in_details = False
    in_code_block = False
    domains = []
    for line in lines:
        if '<details>' in line:
            in_details = True
            continue
        if '</details>' in line:
            in_details = False
            in_code_block = False
            break
        if not in_details:
            continue
        if line.strip() == '```':
            in_code_block = not in_code_block
            continue
        if not in_code_block:
            continue
        line = line.strip()
        if line.startswith('#') or not line:
            continue
        parts = line.split()
        if parts:
            domain = parts[0]
            if domain.endswith('.'):
                domain = domain[:-1]
            domains.append(domain)
    return domains

def process_maintenance_issue(issue):
    """Process a maintenance/dead domain report issue."""
    issue_num = issue['number']
    print(f'Processing issue #{issue_num}: {issue["title"]}')

    # Extract dead domains from the issue body (from the sample in <details>)
    body = issue['body']
    domains_to_check = extract_domains_from_issue_body(body)
    print(f'  Found {len(domains_to_check)} domains to check from sample')

    # Limit to first 50 domains to avoid too much processing
    domains_to_check = domains_to_check[:50]

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

        subprocess.run(['gh', 'issue', 'close', str(issue_num), '--reason', 'completed'], cwd=REPO_DIR, check=True)
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

        subprocess.run(['gh', 'issue', 'close', str(issue_num), '--reason', 'completed'], cwd=REPO_DIR, check=True)
        return

    # Prepare commit message
    commit_lines = [f'Remove dead domains from issue #{issue_num}']
    for domain, lists in removed_from.items():
        commit_lines.append(f'  - {domain} (from: {", ".join(lists)})')
    commit_message = '\n'.join(commit_lines)

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
                with open(list_file) as f:
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
        subprocess.run(['git', 'commit', '-m', commit_message], cwd=REPO_DIR, check=True)
        subprocess.run(['git', 'push', 'origin', 'main'], cwd=REPO_DIR, check=True)

        # Get commit SHA
        result = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=REPO_DIR, capture_output=True, text=True, check=True)
        commit_sha = result.stdout.strip()

        # Comment on issue
        comment = f'Removed {len(dead_domains)} dead domains from the sample (see commit).\n\n' + \
                  '\n'.join([f'- {domain} (from: {", ".join(lists)})' for domain, lists in removed_from.items()]) + \
                  f'\n\nCommit: {commit_sha}'
        subprocess.run(['gh', 'issue', 'comment', str(issue_num), '--body', comment], cwd=REPO_DIR, check=True)

        subprocess.run(['gh', 'issue', 'close', str(issue_num), '--reason', 'completed'], cwd=REPO_DIR, check=True)

        # Update labels: remove status:needs-triage, add status:verified-removed
        subprocess.run(['gh', 'issue', 'edit', str(issue_num), '--remove-label', 'status:needs-triage'], cwd=REPO_DIR, check=True)

        print(f'  Processed issue #{issue_num}')
    except subprocess.CalledProcessError as e:
        print(f'  Error processing issue #{issue_num}: {e}')
        comment = f'Failed to process dead domains: {e}'
        subprocess.run(['gh', 'issue', 'comment', str(issue_num), '--body', comment], cwd=REPO_DIR, check=True)

        subprocess.run(['gh', 'issue', 'close', str(issue_num), '--reason', 'completed'], cwd=REPO_DIR, check=True)

def main():
    # Get all open maintenance issues
    # We'll use gh to get the issues in JSON format
    result = subprocess.run(['gh', 'issue', 'list', '--state', 'open', '--label', 'request:maintenance', '--json', 'number,title,body,labels,createdAt'],
                            capture_output=True, text=True, cwd=REPO_DIR)
    if result.returncode != 0:
        print(f'Failed to fetch issues: {result.stderr}')
        sys.exit(1)

    issues = json.loads(result.stdout)
    print(f'Found {len(issues)} maintenance issues')

    for issue in issues:
        process_maintenance_issue(issue)

if __name__ == '__main__':
    main()
