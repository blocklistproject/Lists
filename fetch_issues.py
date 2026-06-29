#!/usr/bin/env python3
import os, json, urllib.request, urllib.error

hermes_env = os.path.expanduser('~/.hermes/.env')
GITHUB_TOKEN = None
if os.path.exists(hermes_env):
    with open(hermes_env) as f:
        for line in f:
            if line.startswith('GITHUB_TOKEN='):
                GITHUB_TOKEN = line.strip().split('=', 1)[1].strip()
                break

owner_repo = 'blocklistproject/Lists'
url = f'https://api.github.com/repos/{owner_repo}/issues?state=open&per_page=100&direction=asc'

req = urllib.request.Request(url)
req.add_header('Authorization', f'token {GITHUB_TOKEN}')
req.add_header('Accept', 'application/vnd.github.v3+json')

try:
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode())
        issues = [i for i in data if 'pull_request' not in i]
        print(f'Found {len(issues)} open issues')
        for issue in issues:
            labels = ', '.join(l['name'] for l in issue.get('labels', []))
            print(f"Issue #{issue['number']:5}  {issue['state']:6}  {labels:40}  {issue['title']}")
except urllib.error.HTTPError as e:
    print(f'HTTP Error {e.code}: {e.reason}')
