# GitHub Workflows Quick Reference

## Normalize and Sync Formats

**Location**: `.github/workflows/normalize-sync.yml`

**Purpose**: Clean invalid entries and regenerate all format files to ensure synchronization

**Trigger**: Manual (workflow_dispatch)

**Quick Start**:
```bash
# Via GitHub CLI
gh workflow run normalize-sync.yml

# Dry run (preview only)
gh workflow run normalize-sync.yml -f dry_run=true
```

**Via GitHub UI**:
1. Go to Actions tab
2. Select "Normalize and Sync Formats"
3. Click "Run workflow"
4. Configure options and run

**What it fixes**:
- Invalid domain entries (paths, fragments, non-ASCII)
- Format sync issues between .txt, adguard, dnsmasq, alt-version
- Test failures in `test_all_formats_produce_same_domains`

**When to use**:
- ✅ After manual edits to list files
- ✅ When format sync tests fail
- ✅ After bulk domain changes
- ✅ As periodic maintenance (monthly)

**Related Documentation**: [docs/NORMALIZE_SYNC.md](NORMALIZE_SYNC.md)

---

## Other Available Workflows

### Build Blocklists
- **File**: `build.yml`
- **Trigger**: Push, PR, Manual
- **Purpose**: Build and validate blocklists

### Upstream Monitor
- **File**: `upstream-monitor.yml`
- **Trigger**: Scheduled, Manual
- **Purpose**: Check for updates from upstream sources

### Dead Domains Check
- **File**: `dead-domains.yml`
- **Trigger**: Scheduled, Manual
- **Purpose**: Identify and remove inactive domains

### Weekly Report
- **File**: `weekly-report.yml`
- **Trigger**: Scheduled (weekly)
- **Purpose**: Generate statistics and changelog

---

## Useful Commands

```bash
# List all workflows
gh workflow list

# Run a specific workflow
gh workflow run <workflow-name>

# View workflow runs
gh run list --workflow=<workflow-name>

# Watch a workflow run
gh run watch

# View run logs
gh run view <run-id> --log
```
