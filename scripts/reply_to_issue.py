#!/usr/bin/env python3
"""Draft, preview, and optionally post a maintainer reply to a GitHub issue.

Examples:
    python3 scripts/reply_to_issue.py --issue 123 --dry-run
    python3 scripts/reply_to_issue.py --issue 123 --approve --label status:triaged
    python3 scripts/reply_to_issue.py --issue-url https://github.com/blocklistproject/Lists/issues/123 --close
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.issue_reply import IssueReplyError, build_llm_prompt, call_llm_provider, format_preview


class GitHubClient:
    """Small GitHub REST client for issue comments and labels."""

    def __init__(self, token: str, repository: str):
        self.token = token
        self.repository = repository

    def _request(self, path: str, *, method: str = "GET", payload: dict[str, Any] | None = None) -> Any:
        url = f"https://api.github.com/{path.lstrip('/')}"
        data = None
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github+json",
            "User-Agent": "blocklist-project-automation",
        }
        if payload is not None:
            data = json.dumps(payload).encode("utf-8")
            headers["Content-Type"] = "application/json"

        req = urllib.request.Request(url, data=data, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=60) as response:
                body = response.read().decode("utf-8")
                return json.loads(body) if body else None
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="ignore")
            raise IssueReplyError(f"GitHub API error {exc.code}: {detail}") from exc

    def get_issue(self, issue_number: int) -> dict[str, Any]:
        return self._request(f"repos/{self.repository}/issues/{issue_number}")

    def get_issue_comments(self, issue_number: int) -> list[dict[str, Any]]:
        return self._request(f"repos/{self.repository}/issues/{issue_number}/comments")

    def create_comment(self, issue_number: int, body: str) -> dict[str, Any]:
        return self._request(
            f"repos/{self.repository}/issues/{issue_number}/comments",
            method="POST",
            payload={"body": body},
        )

    def add_labels(self, issue_number: int, labels: list[str]) -> list[dict[str, Any]]:
        return self._request(
            f"repos/{self.repository}/issues/{issue_number}/labels",
            method="POST",
            payload={"labels": labels},
        )

    def close_issue(self, issue_number: int) -> dict[str, Any]:
        return self._request(
            f"repos/{self.repository}/issues/{issue_number}",
            method="PATCH",
            payload={"state": "closed"},
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Draft and optionally post a GitHub issue reply")
    parser.add_argument("--issue", type=int, help="GitHub issue number")
    parser.add_argument("--issue-url", help="Full GitHub issue URL")
    parser.add_argument("--repo", default=os.environ.get("GITHUB_REPOSITORY", "blocklistproject/Lists"))
    parser.add_argument("--token", default=os.environ.get("GITHUB_TOKEN", ""), help="GitHub token")
    parser.add_argument("--provider", default="openai", choices=["openai"], help="LLM provider")
    parser.add_argument("--api-key", default=os.environ.get("OPENAI_API_KEY", ""), help="LLM API key")
    parser.add_argument("--model", default=os.environ.get("OPENAI_MODEL", "gpt-4o-mini"))
    parser.add_argument("--base-url", default=os.environ.get("OPENAI_API_BASE", ""))
    parser.add_argument("--label", action="append", default=[], help="Label to add after replying")
    parser.add_argument("--close", action="store_true", help="Close the issue after posting the reply")
    parser.add_argument("--approve", action="store_true", help="Skip the approval prompt and post immediately")
    parser.add_argument("--dry-run", action="store_true", help="Show the preview without posting")
    return parser.parse_args()


def resolve_issue_number(args: argparse.Namespace) -> int:
    if args.issue is not None:
        return args.issue

    if args.issue_url:
        match = re.search(r"/issues/(\d+)(?:/|$)", args.issue_url)
        if match:
            return int(match.group(1))

    raise SystemExit("Please provide --issue or --issue-url")


def build_issue_context(issue: dict[str, Any], comments: list[dict[str, Any]]) -> tuple[str, str | None]:
    title = issue.get("title", "") or ""
    body = (issue.get("body") or "").strip()

    if not body and comments:
        body = ""

    comment_texts: list[str] = []
    for comment in comments:
        commenter = comment.get("user", {}).get("login", "unknown")
        text = (comment.get("body") or "").strip()
        if text:
            comment_texts.append(f"Comment from {commenter}: {text}")

    latest_comment = comment_texts[-1] if comment_texts else None
    combined_body = "\n\n".join([part for part in [body, *comment_texts] if part])
    return title, combined_body if combined_body else latest_comment


def maybe_prompt_for_approval(preview: str) -> bool:
    response = input("Apply this reply to GitHub? [y/N]: ").strip().lower()
    return response in {"y", "yes"}


def main() -> int:
    args = parse_args()
    issue_number = resolve_issue_number(args)

    if not args.token:
        raise SystemExit("Set GITHUB_TOKEN to use the GitHub API")

    client = GitHubClient(args.token, args.repo)

    try:
        issue = client.get_issue(issue_number)
        comments = client.get_issue_comments(issue_number)
    except IssueReplyError as exc:
        print(f"Failed to load issue: {exc}", file=sys.stderr)
        return 1

    title, context_body = build_issue_context(issue, comments)
    latest_comment = comments[-1].get("body", "") if comments else None

    prompt = build_llm_prompt(
        issue_number=issue_number,
        title=title,
        body=context_body or "",
        latest_comment=latest_comment,
        suggested_action="comment",
        close_issue=args.close,
    )

    api_key = args.api_key or os.environ.get("OPENAI_API_KEY", "")
    if not api_key:
        print("OPENAI_API_KEY is not set; unable to generate a reply automatically.", file=sys.stderr)
        return 1

    try:
        reply_text = call_llm_provider(
            prompt,
            api_key=api_key,
            provider=args.provider,
            model=args.model,
            base_url=args.base_url or None,
        )
    except IssueReplyError as exc:
        print(f"LLM request failed: {exc}", file=sys.stderr)
        return 1

    action = "comment"
    if args.label:
        action = f"comment + add label(s): {', '.join(args.label)}"
    if args.close:
        action = f"{action} + close"

    preview = format_preview(reply_text, action=action, close_issue=args.close)
    print(preview)

    if args.dry_run:
        print("Dry run only; nothing was posted.")
        return 0

    if not args.approve and not maybe_prompt_for_approval(preview):
        print("Reply not posted.")
        return 0

    try:
        client.create_comment(issue_number, reply_text)
        if args.label:
            client.add_labels(issue_number, args.label)
        if args.close:
            client.close_issue(issue_number)
    except IssueReplyError as exc:
        print(f"Failed to apply reply: {exc}", file=sys.stderr)
        return 1

    print("Reply posted successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
