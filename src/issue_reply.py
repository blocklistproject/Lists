"""Helpers for generating and previewing GitHub issue replies."""

from __future__ import annotations

import json
import os
import urllib.request
from typing import Any


class IssueReplyError(RuntimeError):
    """Raised when an issue-reply flow cannot complete."""


def build_llm_prompt(
    *,
    issue_number: int,
    title: str,
    body: str,
    latest_comment: str | None = None,
    suggested_action: str = "comment",
    close_issue: bool = False,
) -> str:
    """Construct a prompt for a language model to draft a helpful issue reply."""
    latest = latest_comment or "No previous maintainer comment."
    close_note = "The issue should be closed after the reply." if close_issue else "The issue should remain open."
    return (
        f"You are helping maintain a DNS blocklist project.\n"
        f"Draft a concise, professional GitHub issue reply for Issue #{issue_number}.\n"
        f"Title: {title}\n"
        f"Issue body: {body}\n"
        f"Latest maintainer comment: {latest}\n"
        f"Suggested action: {suggested_action}\n"
        f"{close_note}\n"
        f"Return only the reply text, no markdown fences, and keep it friendly and short."
    )


def format_preview(reply_text: str, *, action: str, close_issue: bool) -> str:
    """Format a human-readable preview of the planned issue action."""
    close_phrase = "and close the issue" if close_issue else "without closing the issue"
    return (
        "Reply preview\n"
        f"Action: {action}\n"
        f"Outcome: {close_phrase}\n\n"
        f"{reply_text}"
    )


def call_llm_provider(
    prompt: str,
    *,
    api_key: str,
    provider: str = "openai",
    model: str | None = None,
    base_url: str | None = None,
) -> str:
    """Call an LLM provider using a lightweight JSON POST request."""
    if provider != "openai":
        raise IssueReplyError(f"Unsupported provider: {provider}")

    if not api_key:
        raise IssueReplyError("An API key is required for the LLM provider.")

    endpoint = base_url or os.environ.get("OPENAI_API_BASE", "https://api.openai.com/v1/chat/completions")
    payload: dict[str, Any] = {
        "model": model or os.environ.get("OPENAI_MODEL", "gpt-4o-mini"),
        "messages": [
            {"role": "system", "content": "You write concise maintainer replies."},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.2,
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    req = urllib.request.Request(
        endpoint,
        data=json.dumps(payload).encode("utf-8"),
        headers=headers,
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as response:
            data = json.loads(response.read().decode("utf-8"))
    except Exception as exc:  # pragma: no cover - network path
        raise IssueReplyError(f"LLM request failed: {exc}") from exc

    choices = data.get("choices", [])
    if not choices:
        raise IssueReplyError("LLM response did not contain any choices.")
    message = choices[0].get("message", {})
    content = message.get("content", "")
    if isinstance(content, list):
        return "".join(part.get("text", "") for part in content if isinstance(part, dict))
    return str(content).strip()
