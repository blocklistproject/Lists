# Label Taxonomy Migration Guide

## Current State (as of 2026-06-27)

### Labels Used on Open Issues
- `status:needs-info` - Needs more information from reporter
- `bot` - Applied automatically by bot/cron
- `status:needs-review` - Issue needs human review
- `request:add` - Request to add a domain to a blocklist
- `request:remove` - False-positive/removal request
- `status:triaged` - Triaged by automated agent
- `status:unverified` - Domain verification failed (DNS/HTTP)
- `status:not-found` - Requested removal target was not found
- `status:needs-triage` - Needs maintainer review

### Issue Statistics
- **Total open issues:** ~70+
- **Open PRs:** 0

## Recommended Taxonomy

### Status Labels (state tracking)
- `status:needs-triage` - Needs maintainer review
- `status:needs-info` - Needs more information from reporter
- `status:verified-new` - Domain verified and added
- `status:verified-exists` - Domain verified and already present
- `status:not-found` - Domain not found/verified removal target
- `status:blocked` - Blocked by external dependency
- `status:duplicate` - Duplicate of another issue

### Request Labels (issue type)
- `request:add` - Add a domain to a blocklist
- `request:remove` - Remove a domain from a blocklist
- `request:maintenance` - Dead domain/legitimate cleanup request
- `question` - Question about the project

### Source Labels (origin tracking)
- `source:automation` - Created by bot/cron
- `source:human` - Created by user/reporter

## Migration Strategy

### Phase 1: Label Audit
1. List all repo labels and usage counts
2. Identify duplicate/conflicting labels
3. Identify labels referenced by templates that don't exist

### Phase 2: Label Updates
1. Create canonical label definitions
2. Update issue templates
3. Update workflow files

### Phase 3: Issue Migration
1. Process issues in batches of 10
2. Add canonical labels while preserving old ones
3. Remove old labels only after migration is complete

## Current Workflow

1. **Triage new issues** - Check for structured fields
2. **Verify domains** - DNS and HTTP checks
3. **Apply appropriate labels** - Based on findings
4. **Comment with evidence** - Include commit SHA when applicable
5. **Close completed issues** - Use reason `completed`

## Notes

- Avoid bulk label removals that could notify subscribers
- Keep old labels during migration for compatibility
- Update automation/templates before deleting obsolete labels
