from src.issue_reply import build_llm_prompt, format_preview


def test_build_llm_prompt_includes_issue_context():
    prompt = build_llm_prompt(
        issue_number=42,
        title="[add] example.com",
        body="Please add example.com to the malware list.",
        latest_comment="Thanks for the report.",
        suggested_action="comment",
        close_issue=False,
    )

    assert "Issue #42" in prompt
    assert "[add] example.com" in prompt
    assert "Please add example.com to the malware list." in prompt
    assert "Thanks for the report." in prompt
    assert "comment" in prompt.lower()


def test_format_preview_mentions_closure_when_requested():
    preview = format_preview(
        reply_text="Thanks for the report. We have reviewed this and will keep it under watch.",
        action="comment",
        close_issue=True,
    )

    assert "Reply preview" in preview
    assert "Thanks for the report." in preview
    assert "close the issue" in preview.lower()
