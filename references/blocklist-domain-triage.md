# Blocklist Domain Triage Workflow

## Objective

Process add/remove requests for the blocklistproject/Lists repository systematically.

## Process

1. **Batch processing**: Handle ~10 issues per batch to keep commits small and auditable.
2. **Research each URL/domain**:
   - Check current presence across all list formats (.txt, adguard, dnsmasq, alt)
   - DNS probe with `socket.getaddrinfo`
   - HTTP/HTTPS HEAD/GET probe (record status, final URL, server, content-type)
   - Validate against issue evidence and public documentation
3. **Apply changes**:
   - Add only active/verifiable domains to the correct list
   - Remove false positives from the source list only (don't move to other lists)
   - Update all generated formats when changing list data
4. **Commit/push**: Use clear commit messages with issue reference
5. **Comment/close**: Leave evidence-backed explanation and commit SHA

## Verification

Run after changes:
- `git diff --check`
- `pytest -q`
- `ruff check src/ tests/ build.py`
- `python build.py --dry-run --validate --verbose`

## Labels

- `status:needs-triage` → `status:verified-new` / `status:verified-exists` / `status:not-found`
- `status:needs-info` → `status:verified-*` after research, or leave open if unverifiable
- `request:add` / `request:remove` - preserve these as request type

## Notes

- Do not bulk-delete from large reports without verification
- If evidence contradictory, prefer `status:needs-triage` over both statuses
- For maintenance/dead-domain reports, comment and label unless doing dedicated cleanup
