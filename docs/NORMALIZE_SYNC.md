# Normalize and Sync Workflow

This workflow helps maintain consistency across all blocklist formats by detecting and removing invalid entries, then regenerating all format variations.

## What It Does

1. **Detects Invalid Entries**: Scans all `.txt` list files for invalid domain entries:
   - Domains starting with `#` (comment character)
   - Domains containing `/` (paths like `example.com/api`)
   - Domains ending with `.` (trailing dots like `example.com.`)
   - Domains with non-ASCII characters (like `sportfogadás.com`)
   - Domains with URL fragments (like `example.html#section`)
   - Domains with query parameters (like `example.com?param=value`)
   - Domains with protocols (like `http://example.com`)

2. **Removes Invalid Entries**: Automatically removes any invalid entries found

3. **Regenerates Formats**: Rebuilds all format variations (hosts, adguard, dnsmasq, alt-version) to ensure synchronization

4. **Updates Everything List**: Regenerates the special "everything" combined list

## How to Run

### Via GitHub UI (Recommended)

1. Go to the **Actions** tab in the repository
2. Select **"Normalize and Sync Formats"** from the workflow list
3. Click **"Run workflow"** button
4. Configure options:
   - **Commit and push changes**: Whether to commit changes (default: true)
   - **Dry run**: Preview changes without committing (default: false)
5. Click **"Run workflow"** to start

### Via GitHub CLI

```bash
# Run with default settings (commit changes)
gh workflow run normalize-sync.yml

# Dry run (preview changes only)
gh workflow run normalize-sync.yml -f dry_run=true

# Run but don't commit
gh workflow run normalize-sync.yml -f commit_changes=false
```

### Locally

You can also run the script locally:

```bash
# From repository root
python3 scripts/normalize_and_sync.py
```

## Workflow Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `commit_changes` | boolean | `true` | Whether to commit and push changes |
| `dry_run` | boolean | `false` | Show changes without committing |

## When to Use

Run this workflow when:

- ✅ Format sync tests are failing (`test_all_formats_produce_same_domains`)
- ✅ Manual edits were made to `.txt` files without regenerating formats
- ✅ You suspect invalid entries have been added
- ✅ Automated upstream sync created inconsistencies
- ✅ After bulk domain removals
- ✅ As periodic maintenance (monthly recommended)

## Output

The workflow provides detailed output including:

- Number of invalid entries removed per list
- Examples of removed entries with reasons
- Summary of regenerated lists
- Git diff showing all changes
- Commit status

## Example Output

```
======================================================================
Normalizing and Syncing Blocklists
======================================================================

📋 Phase 1: Cleaning invalid entries from source files
----------------------------------------------------------------------

✓ adobe: Removed 13 invalid entries
    - #cdn-ffc.oobesaas.adobe.com/* (starts with # (comment))
    - adobeexchange.com/api (contains / (path))
    - crl.verisign.net. (ends with . (trailing dot))
    ... and 10 more

✓ gambling: Removed 1 invalid entries
    - sportfogadás.com (contains non-ASCII characters)

✅ Cleaned 14 invalid entries from 2 list(s)

📋 Phase 2: Regenerating format files
----------------------------------------------------------------------

🔄 Regenerating 2 list(s)...
✓ 2 lists built successfully
Total domains: 279,240

📋 Phase 3: Regenerating 'everything' combined list
----------------------------------------------------------------------

🔄 Regenerating 'everything' list...
✅ Successfully regenerated 'everything' list with 4,752,437 domains

======================================================================
✅ Normalization and sync complete!
======================================================================

Modified lists: adobe, gambling
Total invalid entries removed: 14
```

## Related Scripts

- **`scripts/normalize_and_sync.py`**: The main script (can be run locally)
- **`scripts/verify_format_sync.py`**: Checks if formats are in sync (read-only)
- **`scripts/regenerate_everything.py`**: Regenerates only the "everything" list
- **`build.py`**: Core build script for individual lists

## Troubleshooting

### Workflow fails with "Config file not found"

Ensure `config/lists.yml` exists in the repository.

### Changes aren't committed

Check that `commit_changes` is set to `true` and `dry_run` is set to `false`.

### Script reports no changes but tests still fail

Run `scripts/verify_format_sync.py --fix` locally to diagnose specific format issues.

## Automation

Consider setting up:

- **Pre-commit hook**: Run verification before commits
- **Scheduled workflow**: Run monthly as maintenance
- **Post-upstream-sync**: Run after upstream monitoring creates PRs

## Related Documentation

- [Exclusion Lists System](../config/exclusions/README.md)
- [Remove Domain Script](remove_domain.py)
- [Format Sync Verification](verify_format_sync.py)
