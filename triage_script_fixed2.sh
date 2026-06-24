#!/bin/bash
set -euo pipefail

# Setup authentication method
if command -v gh &>/dev/null && gh auth status &>/dev/null; then
    AUTH="gh"
else
    AUTH="git"
    if [ -z "$GITHUB_TOKEN" ]; then
        if [ -f "${HERMES_HOME:-$HOME/.hermes}/.env" ] && grep -q "^GITHUB_TOKEN=" "${HERMES_HOME:-$HOME/.hermes}/.env"; then
            GITHUB_TOKEN=$(grep "^GITHUB_TOKEN=" "${HERMES_HOME:-$HOME/.hermes}/.env" | head -1 | cut -d= -f2 | tr -d '\n\r')
        elif grep -q "github.com" ~/.git-credentials 2>/dev/null; then
            GITHUB_TOKEN=$(grep "github.com" ~/.git-credentials 2>/dev/null | head -1 | sed 's|https://[^:]*:\([^@]*\)@.*|\1|')
        fi
    fi
fi

REMOTE_URL=$(git remote get-url origin)
OWNER_REPO=$(echo "$REMOTE_URL" | sed -E 's|.*github\.com[:/]||; s|\.git$||')
OWNER=$(echo "$OWNER_REPO" | cut -d/ -f1)
REPO=$(echo "$OWNER_REPO" | cut -d/ -f2)

echo "Using $AUTH for authentication. Owner: $OWNER, Repo: $REPO"

# Function to log messages
log() {
    echo "[$(date -u +'%Y-%m-%d %H:%M:%S UTC')] $*"
}

# Function to run a command and log its output
run_cmd() {
    log "Running: $*"
    "$@"
}

# Function to get open issues (excluding PRs) using gh or curl
get_open_issues() {
    if [ "$AUTH" = "gh" ]; then
        gh issue list --repo "$OWNER/$REPO" --state open --limit 100 --json number,title,author,createdAt,updatedAt,body,labels \
            --jq 'map(select(.pull_request == null)) | .[]'
    else
        curl -s -H "Authorization: token $GITHUB_TOKEN" \
            "https://api.github.com/repos/$OWNER/$REPO/issues?state=open&per_page=100" |
        jq -c 'map(select(.pull_request == null))'
    fi
}

# Function to get open PRs using gh or curl
get_open_prs() {
    if [ "$AUTH" = "gh" ]; then
        gh pr list --repo "$OWNER/$REPO" --state open --limit 100 --json number,title,author,createdAt,updatedAt,headRefName,baseRefName,additions,deletions,changedFiles,statusCheckRollup,url \
            --jq '.[]'
    else
        curl -s -H "Authorization: token $GITHUB_TOKEN" \
            "https://api.github.com/repos/$OWNER/$REPO/pulls?state=open&per_page=100" |
        jq -c '.[]'
    fi
}

# Function to parse issue body for add/remove request
