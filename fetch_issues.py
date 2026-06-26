import json
import subprocess
import sys

def main():
    result = subprocess.run(
        ['gh', 'issue', 'list', '--repo', 'blocklistproject/Lists', '--state', 'open', '--json', 'number,title,state,labels,author,createdAt,updatedAt,comments'],
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        print(f"Error: {result.stderr}", file=sys.stderr)
        sys.exit(1)
    
    issues = json.loads(result.stdout)
    print(f"Found {len(issues)} open issues (excluding PRs)")
    
    for i in issues:
        labels = ', '.join(l['name'] for l in i.get('labels', []))
        print(f"#{i['number']:5}  {i['state']:6}  {labels:30}  {i['title']}")

if __name__ == "__main__":
    main()
