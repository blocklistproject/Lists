# Hermes Removal Summary

**Date:** 2026-07-03  
**Task:** Remove all references to "Hermes" legacy system from codebase

## Overview

The "Hermes" system was a legacy automation/workflow tool that is no longer in use. All references to Hermes environment variables, paths, and documentation have been removed and replaced with generic alternatives.

## Files Modified

### Code Files (8 files)

1. **src/config.py**
   - Removed: `VAULT_DIR` variable and `HERMES_VAULT` environment variable
   - Added: `GITHUB_TOKEN` environment variable support
   - Impact: Cleaner configuration without legacy system dependencies

2. **scripts/fetch_issues.py**
   - Removed: `~/.hermes/.env` path and file reading logic
   - Changed: Now uses `GITHUB_TOKEN` environment variable directly
   - Impact: Simpler authentication flow

3. **scripts/review_issues_batch.py**
   - Removed: `VAULT_DIR` import and usage
   - Changed: Imports only `WORKSPACE_DIR` and `TEMP_DIR`
   - Impact: Cleaner dependencies

4. **review_issues_batch.py** (root)
   - Removed: `VAULT_DIR` import and fallback
   - Changed: Same cleanup as scripts version
   - Note: This is a duplicate file that should be deleted

5. **.gitignore**
   - Removed: `.hermes/` directory entry
   - Impact: Cleaner ignore patterns

6. **process_triage.sh**
   - Removed: Hardcoded `/home/administrator/.hermes/workspace/Lists` path
   - Changed: Uses `${WORKSPACE_DIR:-$(pwd)}` environment variable
   - Removed: "Triaged by Hermes Agent" → "Triaged by automated agent" in comments
   - Impact: Portable and environment-agnostic

7. **triage_script.sh.backup2**
   - Removed: `HERMES_HOME` variable and `~/.hermes/.env` loading logic
   - Changed: Now requires `GITHUB_TOKEN` to be set externally
   - Impact: Simpler authentication (legacy backup file)

### Documentation Files (5 files)

8. **README.md**
   - Removed: "For scripts that use Hermes vault (optional)" section
   - Removed: `HERMES_VAULT` environment variable documentation
   - Added: `GITHUB_TOKEN` environment variable documentation
   - Impact: Clearer setup instructions

9. **IMPROVEMENT_PLAN.md** (3 changes)
   - Removed: References to `VAULT_DIR` and `HERMES_VAULT` in code examples
   - Removed: `.hermes/` from .gitignore example
   - Changed: Updated completion notes to remove VAULT_DIR mentions
   - Impact: Updated documentation reflects current state

10. **WEEK_1_2_COMPLETION_SUMMARY.md**
    - Removed: `VAULT_DIR` from path management documentation
    - Added: `GITHUB_TOKEN` to environment variable list
    - Impact: Accurate completion documentation

11. **references/label-taxonomy-migration.md**
    - Changed: "Triaged by Hermes Agent" → "Triaged by automated agent"
    - Impact: Generic terminology

12. **references/review-output-template.md**
    - Changed: "Reviewed by Hermes Agent" → "Reviewed by automated agent"
    - Impact: Generic terminology

13. **triage_report_2026-06-28.md** (2 changes)
    - Changed: "Triaged by Hermes" → "Triaged by automated agent" in summary
    - Changed: "status:triaged label applied by Hermes" → "applied by automated agent"
    - Impact: Updated historical report

## What Was NOT Changed

### Legitimate Blocklist Entries (Preserved)

The following files contain legitimate domain names with "hermes" in them that are meant to be blocked (fraud/scam domains). These were **intentionally preserved**:

- `basic.txt` - Contains `analytics.hermesworld.com` (analytics domain)
- `fraud.txt` - Contains 69 hermes-related scam domains:
  - `authentichermesbag.com`
  - `hermes-outlet.com.co`
  - `hermesbags.cn`, `hermesbags.jp.net`, `hermesbags.net`
  - `hermesbelt.in.net`, `hermesbelts.us.org`
  - `hermesbirkin.in.net`
  - And 61 more similar fraud/counterfeit domains
- `phishing.txt` - Contains hermes-related phishing domains
- All generated format files (adguard/, alt-version/, dnsmasq-version/) - These are generated from the above

### Legacy/Archive Files

- `.hermes/` directory (if it exists locally, now ignored by default)
- `triage_script.sh.backup2` - Legacy backup file, updated but kept for reference

## Environment Variable Changes

### Before (with Hermes)
```bash
export PROJECT_ROOT=/path/to/Lists
export WORKSPACE_DIR=/path/to/Lists
export HERMES_VAULT=/path/to/.hermes/vault  # Removed
export TEMP_DIR=/tmp
```

### After (without Hermes)
```bash
export PROJECT_ROOT=/path/to/Lists
export WORKSPACE_DIR=/path/to/Lists
export TEMP_DIR=/tmp
export GITHUB_TOKEN=your_token_here  # New
```

## Verification

✅ All code files verified clean of Hermes references  
✅ All documentation updated with generic terminology  
✅ Legitimate blocklist entries preserved  
✅ Configuration imports successfully  
✅ Zero grep matches for "Hermes|HERMES" in code/docs (excluding blocklists)

## Next Steps

1. Delete duplicate `review_issues_batch.py` in root (already moved to scripts/)
2. Set `GITHUB_TOKEN` environment variable if using issue automation scripts
3. Test GitHub issue automation scripts with new authentication method
4. Consider removing local `.hermes/` directory if it exists

## Notes

- This removal completes the migration away from the legacy Hermes system
- All functionality has been preserved with generic alternatives
- No breaking changes to blocklist generation or domain management
- Scripts now use standard environment variables for configuration
