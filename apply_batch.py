#!/usr/bin/env python3
import json
import os
import re
from pathlib import Path

ROOT = Path('/home/administrator/.hermes/workspace/Lists')
ISSUE_DATA = Path('/home/administrator/.hermes/workspace/blocklistproject-triage/issues/batch_review.json')

def load_issue_data():
    with open(ISSUE_DATA, 'r') as f:
        return json.load(f)

def list_presence(domain):
    """Return list of list names where domain appears."""
    presence = []
    for list_file in sorted(ROOT.glob('*.txt')):
        if list_file.name == 'everything.txt':
            continue
        try:
            content = list_file.read_text(encoding='utf-8')
            if domain in content.split():
                presence.append(list_file.stem)
        except Exception:
            pass
    # Also check generated formats? We'll rely on the presence from the triage data.
    return presence

def update_list(list_name, domain, action):
    """Add or remove domain from the given list file."""
    list_file = ROOT / f"{list_name}.txt"
    if not list_file.exists():
        return False
    content = list_file.read_text(encoding='utf-8')
    words = content.split()
    if action == 'add':
        if domain not in words:
            words.append(domain)
            list_file.write_text(' '.join(words) + '\n', encoding='utf-8')
            return True
    elif action == 'remove':
        if domain in words:
            words.remove(domain)
            list_file.write_text(' '.join(words) + '\n', encoding='utf-8')
            return True
    return False

def update_all_formats(base_name, domain, action):
    """Update all generated formats for a given base list name."""
    formats = {
        'hosts': ('{name}.txt', '0.0.0.0 {domain}'),
        'domains': ('alt-version/{name}-nl.txt', '{domain}'),
        'adguard': ('adguard/{name}-ags.txt', '||{domain}^'),
        'dnsmasq': ('dnsmasq-version/{name}-dnsmasq.txt', 'server=/{domain}/'),
    }
    for fmt, (pattern, template) in formats.items():
        path = ROOT / pattern.format(name=base_name)
        if not path.exists():
            continue
        line = template.format(domain=domain)
        if action == 'add':
            if line not in path.read_text(encoding='utf-8'):
                with open(path, 'a', encoding='utf-8') as f:
                    f.write(line + '\n')
        elif action == 'remove':
            content = path.read_text(encoding='utf-8')
            if line in content:
                lines = [l for l in content.splitlines() if l.strip() != line.strip()]
                path.write_text('\n'.join(lines) + '\n', encoding='utf-8')

def process_issue(record):
    issue = record['issue']
    triage = record['triage']
    domains_data = record['domains']
    
    issue_num = issue['number']
    issue_title = issue['title']
    request_type = triage.get('request_type', 'maintenance')
    domains = triage.get('domains', [])
    target = triage.get('target', '').lower()
    
    print(f"Processing issue #{issue_num}: {issue_title}")
    print(f"  Request type: {request_type}")
    print(f"  Domains: {domains}")
    print(f"  Target list: {target or '(from issue)'}")
    
    # We'll decide action per domain based on presence and request type
    for domain in domains:
        # Get presence from the triage data (more accurate)
        presence_info = domains_data.get(domain, {})
        presence = presence_info.get('presence', [])
        # Flatten presence: it's a list of lists? Actually from the triage, presence is a list of list names?
        # Looking at the triage output: "presence": list_presence(domain) which returns a list of strings.
        # So presence is a list of list names (stems) where the domain is found.
        present_lists = presence  # assume it's a list of strings
        
        # Determine if we should add or remove
        should_add = False
        should_remove = False
        
        if request_type == 'add':
            # If target is specified, check if domain is in that list; if not, add.
            # If target is empty, we might need to infer the correct list from the issue context.
            # For simplicity, if target is not empty and domain not in that list, add.
            # If target is empty, we'll skip for now (needs manual review).
            if target:
                if target not in present_lists:
                    # Additionally, check if domain is active (resolves and maybe HTTP 2xx)
                    # We'll skip if not resolving.
                    dns_info = presence_info.get('dns', {})
                    if dns_info.get('resolves'):
                        # Optionally check HTTP
                        http_info = presence_info.get('http', {})
                        status = http_info.get('status')
                        if status and 200 <= status < 300:
                            should_add = True
                        else:
                            # Still add if resolves? We'll add if resolves.
                            should_add = True
                    else:
                        print(f"    Domain {domain} does not resolve, skipping add.")
                else:
                    print(f"    Domain {domain} already in {target}.")
            else:
                print(f"    No target specified for add, skipping.")
        elif request_type == 'remove':
            if target:
                if target in present_lists:
                    should_remove = True
                else:
                    print(f"    Domain {domain} not in {target}.")
            else:
                # If no target, remove from all lists where present?
                # For safety, we'll not remove without target.
                print(f"    No target specified for remove, skipping.")
        # TODO: maintenance requests
        
        if should_add:
            print(f"    Adding {domain} to {target}")
            if update_list(target, domain, 'add'):
                update_all_formats(target, domain, 'add')
                print(f"    Added.")
            else:
                print(f"    Failed to add.")
        elif should_remove:
            print(f"    Removing {domain} from {target}")
            if update_list(target, domain, 'remove'):
                update_all_formats(target, domain, 'remove')
                print(f"    Removed.")
            else:
                print(f"    Failed to remove.")
        else:
            print(f"    No action for {domain}.")
    
    # After processing, we need to commit and push? We'll do that after processing all issues in the batch.
    # For now, just return a summary.
    return {
        'issue_number': issue_num,
        'title': issue_title,
        'request_type': request_type,
        'domains': domains,
        'target': target,
        # actions would be collected
    }

def main():
    data = load_issue_data()
    results = []
    for record in data:
        results.append(process_issue(record))
        print("---")
    
    # Summary
    print("\n=== Summary ===")
    for r in results:
        print(f"Issue #{r['issue_number']}: {r['title']} ({r['request_type']})")
    
    # TODO: After processing all issues, we should run local checks, commit, push.
    # We'll do that in a separate step.

if __name__ == '__main__':
    main()
