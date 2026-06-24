#!/bin/bash
set -euo pipefail

cd /home/administrator/.hermes/workspace/Lists

PERSISTENT_STATE_FILE="/tmp/triate_state_blocklistproject"
PROCESSED_FILE="/tmp/processed_items_$$"  # we might not need this now
ITEMS_FILE="/tmp/items_$$"

# Ensure labels exist
ensure_label() {
  local name="$1"
  local color="$2"
  local description="$3"
  # Check if label exists by listing and matching the name exactly
  if ! gh label list --limit 100 | awk -F'\t' '{print $1}' | grep -qx "$name"; then
    echo "Creating label: $name"
    gh label create "$name" --color "$color" --description "$description"
  fi
}

# Labels we will use
ensure_label "status:triaged" "0052cc" "Triaged by Hermes Agent"
ensure_label "status:mergeable" "0e8a16" "Merges cleanly with base branch"
ensure_label "status:conflicts" "b60205" "Has merge conflicts with base branch"

init_processed() {
  > "$PROCESSED_FILE"
}

mark_processed() {
  echo "$1:$2" >> "$PROCESSED_FILE"
}

is_processed() {
  grep -q "^$1:$2$" "$PROCESSED_FILE"
}

get_items_json() {
  local pr_json issue_json
  local last_pr last_issue
  # Read persistent state
  if [ -f "$PERSISTENT_STATE_FILE" ]; then
    last_pr=$(jq -r '.last_pr // 0' "$PERSISTENT_STATE_FILE")
    last_issue=$(jq -r '.last_issue // 0' "$PERSISTENT_STATE_FILE")
  else
    last_pr=0
    last_issue=0
  fi
  # Get PRs
  pr_output=$(gh pr list --state open --json number,title,author,createdAt --limit 100 2>/dev/null)
  if [ -z "$pr_output" ]; then
    pr_json='[]'
  else
    pr_json=$(echo "$pr_output" | jq -c '[.[] | . + {type:"PR"}]' 2>/dev/null) || pr_json='[]'
  fi
  # Get issues
  issue_output=$(gh issue list --state open --json number,title,author,createdAt,labels --limit 100 2>/dev/null)
  if [ -z "$issue_output" ]; then
    issue_json='[]'
  else
    issue_json=$(echo "$issue_output" | jq -c '[.[] | . + {type:"ISSUE"}]' 2>/dev/null) || issue_json='[]'
  fi
  # Combine, filter by last processed numbers, and sort by createdAt
  jq -n --argjson p "$pr_json" --argjson i "$issue_json" --argjson last_pr "$last_pr" --argjson last_issue "$last_issue" '
    ($p + $i)
    | map(
        if .type == "PR" then .number > $last_pr else .number > $last_issue end
      )
    | sort_by(.createdAt)
  '
}

process_item() {
  local type="$1"
  local number="$2"
  local item_json="$3"
  
  echo "Processing $type #$number"
  
  if [ "$type" = "PR" ]; then
    # PR triage
    git fetch origin pull/$number/head:pr-$number 2>/dev/null || true
    git checkout pr-$number 2>/dev/null || true
    git checkout master 2>/dev/null || true
    if git merge --no-commit --no-ff pr-$number 2>/dev/null; then
      echo "Merge successful"
      gh pr comment $number --body "Triaged by Hermes Agent: Merges cleanly with base branch."
      gh pr edit $number --add-label "status:mergeable" 2>/dev/null || true || true
      git merge --abort 2>/dev/null || true
    else
      echo "Merge conflicts or failed to fetch"
      gh pr comment $number --body "Triaged by Hermes Agent: Merge conflicts or could not test merge."
      gh pr edit $number --add-label "status:conflicts" 2>/dev/null || true
    fi
    git checkout master 2>/dev/null || true
    git branch -D pr-$number 2>/dev/null || true
    mark_processed "$type" "$number"
  else
    # Issue triage
    gh issue edit $number --add-label "status:triaged" 2>/dev/null || true
    gh issue comment $number --body "Triaged by Hermes Agent." 2>/dev/null || true
    mark_processed "$type" "$number"
  fi
}

init_processed

# Get items and save to file
get_items_json > "$ITEMS_FILE"

total_processed=0
batch_num=1
while [ $(jq length "$ITEMS_FILE") -gt 0 ]; do
  echo "Starting batch $batch_num"
  processed=0
  while [ $processed -lt 10 ] && [ $(jq length "$ITEMS_FILE") -gt 0 ]; do
    # Get the first item
    item=$(jq -r '.[0]' "$ITEMS_FILE")
    # Remove the first item from the file
    jq 'del(.[0])' "$ITEMS_FILE" > "${ITEMS_FILE}.tmp" && mv "${ITEMS_FILE}.tmp" "$ITEMS_FILE"
    
    type=$(echo "$item" | jq -r '.type')
    number=$(echo "$item" | jq -r '.number')
    
    if is_processed "$type" "$number"; then
      continue
    fi
    
    process_item "$type" "$number" "$item"
    processed=$((processed+1))
    
    # Update persistent state for this type
    if [ "$type" = "PR" ]; then
      if [ "$number" -gt "$last_pr" ]; then
        last_pr="$number"
      fi
    else
      if [ "$number" -gt "$last_issue" ]; then
        last_issue="$number"
      fi
    fi
  done
  
  echo "Batch $batch_num: Processed $processed items."
  total_processed=$((total_processed + processed))
  
  # Update persistent state file
  jq -n --argjson lp "$last_pr" --argjson li "$last_issue" '{last_pr: $lp, last_issue: $li}' > "$PERSISTENT_STATE_FILE"
  
  if [ $processed -eq 0 ]; then
    echo "No items processed in this batch, breaking."
    break
  fi
  
  batch_num=$((batch_num+1))
done

echo "Total processed: $total_processed items."

# Cleanup
rm -f "$ITEMS_FILE" "$PROCESSED_FILE"
# Note: we leave the persistent state file for the next run