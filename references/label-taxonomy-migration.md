# Label Taxonomy Migration Guide

## Target Taxonomy

```
request:add     - Add domain to list
request:remove  - Remove domain from list

status:needs-triage    - Awaiting initial review
status:needs-info      - Missing evidence required
status:verified-new    - Domain is active, add recommended
status:verified-exists - Domain is active, removal recommended
status:not-found       - Domain not found/active
status:blocked         - Cannot process (policy/legal)
status:completed       - Action taken

area:adguard          - AdGuard Home format
area:dnsmasq          - Dnsmasq format
area:alt              - Alternative formats
area:everything       - Everything combined list
```

## Migration Steps

1. **Audit current labels and issue counts** (read-only)
2. **Create/update canonical labels** first (low-risk, no notifications)
3. **Update issue templates and workflows** to emit canonical labels
4. **Migrate issues in batches** (add canonical, preserve old if user hasn't approved removal)
5. **Verify no open issues carry legacy labels**
6. **Delete obsolete labels** only after verification
7. **Update templates/workflows** to prevent reintroduction

## Pitfalls

- Bulk label changes notify subscribers → get approval before large migrations
- Do not delete old labels before automation is updated
- `gh issue edit` exhausts GraphQL rate limit on large batches → switch to REST if needed
- Contradictory bot statuses → prefer `status:needs-triage`

## REST Fallback for Bulk Migrations

If GraphQL quota exhausted:

```bash
# Get issue numbers with label
curl -s \
  -H "Authorization: token $GITHUB_TOKEN" \
  "https://api.github.com/repos/$OWNER/$REPO/issues?labels=needs-triage&state=open" \
  | python3 -c "import sys,json; [print(i['number']) for i in json.load(sys.stdin)]"

# Set complete label set via REST
curl -s -X PATCH \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/issues/N \
  -d '{"labels": ["canonical:label1", "canonical:label2"]}'
```
