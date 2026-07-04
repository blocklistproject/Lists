#!/usr/bin/env python3
import json
import os
import sys
import urllib.error
import urllib.request

# Get GitHub token from environment variable
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')

if not GITHUB_TOKEN:
    print('GITHUB_TOKEN environment variable not set', file=sys.stderr)
    print('Please set: export GITHUB_TOKEN=your_token_here', file=sys.stderr)
    sys.exit(1)

owner_repo = 'blocklistproject/Lists'
all_issues = []
page = 1

while True:
    url = f'https://api.github.com/repos/{owner_repo}/issues?state=open&per_page=100&page={page}&direction=asc'
    req = urllib.request.Request(url)
    req.add_header('Authorization', f'token {GITHUB_TOKEN}')
    req.add_header('Accept', 'application/vnd.github.v3+json')

    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode())
            if not data:
                break
            for issue in data:
                if 'pull_request' not in issue:
                    all_issues.append(issue)
            page += 1
    except urllib.error.HTTPError as e:
        print(f'HTTP Error {e.code}: {e.reason}', file=sys.stderr)
        break
    except Exception as e:
        print(f'Error: {e}', file=sys.stderr)
        break

# Save to file
with open('/tmp/issues.json', 'w') as f:
    json.dump(all_issues, f, indent=2)

print(f'Found {len(all_issues)} open issues')
print('Saved to /tmp/issues.json')

# Print summary
add_count = sum(1 for i in all_issues if any('request:add' in l['name'] for l in i.get('labels', [])))
remove_count = sum(1 for i in all_issues if any('request:remove' in l['name'] for l in i.get('labels', [])))
triaged_count = sum(1 for i in all_issues if any('status:triaged' in l['name'] for l in i.get('labels', [])))

print(f'Add requests: {add_count}')
print(f'Remove requests: {remove_count}')
print(f'Triaged: {triaged_count}')
