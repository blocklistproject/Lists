#!/usr/bin/env python3
"""Monitor upstream blocklist sources and create PRs for updates.

This script:
1. Reads upstream source configuration from config/lists.yml
2. Fetches each upstream source
3. Compares with current list
4. Creates a PR if new domains are found
5. Respects auto-merge thresholds

Usage:
    python scripts/monitor_upstream.py --list ads
    python scripts/monitor_upstream.py --all
    python scripts/monitor_upstream.py --dry-run
"""

import argparse
import hashlib
import json
import sys
import time
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import requests
import yaml

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import CONFIG_DIR, PROJECT_ROOT, TEMP_DIR
from src.normalize import normalize_line, parse_file_to_set


@dataclass
class UpstreamSource:
    """Configuration for an upstream blocklist source."""

    url: str
    format: str
    trusted: bool
    update_frequency: str
    filter_comments: bool = True
    filter_category: str | None = None
    max_domains: int | None = None


@dataclass
class UpdateResult:
    """Result of checking an upstream source."""

    list_name: str
    source_url: str
    new_domains: set[str]
    removed_domains: set[str]
    total_upstream: int
    total_local: int
    cache_hit: bool = False
    error: str | None = None


def load_config() -> dict[str, Any]:
    """Load configuration from lists.yml."""
    config_path = CONFIG_DIR / "lists.yml"
    with config_path.open() as f:
        return yaml.safe_load(f)


def get_cache_path(url: str) -> Path:
    """Generate cache file path for a URL."""
    url_hash = hashlib.md5(url.encode()).hexdigest()
    return TEMP_DIR / f"upstream_cache_{url_hash}.txt"


def is_cache_valid(cache_path: Path, ttl: int) -> bool:
    """Check if cache file is still valid."""
    if not cache_path.exists():
        return False

    age = time.time() - cache_path.stat().st_mtime
    return age < ttl


def fetch_upstream_domains(
    source: UpstreamSource, cache_ttl: int = 86400
) -> set[str]:
    """Fetch domains from an upstream source.

    Args:
        source: Upstream source configuration
        cache_ttl: Cache time-to-live in seconds

    Returns:
        Set of normalized domain names
    """
    cache_path = get_cache_path(source.url)

    # Check cache first
    if is_cache_valid(cache_path, cache_ttl):
        print(f"  Using cached data for {source.url}")
        return parse_file_to_set(cache_path)

    # Fetch from upstream
    print(f"  Fetching {source.url}...")
    try:
        response = requests.get(
            source.url,
            timeout=30,
            headers={"User-Agent": "BlockListProject-Upstream-Monitor/1.0"},
        )
        response.raise_for_status()
        content = response.text

        # Save to cache
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        cache_path.write_text(content)

        # Parse domains based on format
        domains = set()
        for line in content.splitlines():
            line = line.strip()

            # Skip comments if configured
            if source.filter_comments and line.startswith("#"):
                continue

            # Skip empty lines
            if not line:
                continue

            # Normalize based on format
            domain = normalize_line(line)
            if domain:
                domains.add(domain)

        # Apply max_domains limit if set
        if source.max_domains and len(domains) > source.max_domains:
            print(
                f"  ⚠️  Limiting to {source.max_domains} domains "
                f"(upstream has {len(domains)})"
            )
            # Take first N domains (sorted for consistency)
            domains = set(sorted(domains)[: source.max_domains])

        print(f"  ✓ Fetched {len(domains)} domains")
        return domains

    except requests.RequestException as e:
        print(f"  ✗ Error fetching {source.url}: {e}")
        return set()


def load_exclusions(list_name: str) -> set[str]:
    """Load excluded domains for a list.
    
    Exclusions are domains that should never be added from upstream sources,
    typically false positives or user-requested removals.
    
    Args:
        list_name: Name of the list (e.g., 'ads', 'malware')
        
    Returns:
        Set of excluded domain names
    """
    exclusion_file = CONFIG_DIR / "exclusions" / f"{list_name}.txt"
    
    if not exclusion_file.exists():
        return set()
    
    exclusions = set()
    with exclusion_file.open('r', encoding='utf-8') as f:
        for line in f:
            line = line.strip().lower()
            # Skip empty lines and comments
            if line and not line.startswith('#'):
                exclusions.add(line)
    
    if exclusions:
        print(f"  ℹ️  Loaded {len(exclusions)} exclusion(s) from exclusions/{exclusion_file.name}")
    
    return exclusions


def compare_with_local(
    list_name: str, upstream_domains: set[str]
) -> tuple[set[str], set[str]]:
    """Compare upstream domains with local list.

    Args:
        list_name: Name of the list (e.g., 'ads', 'malware')
        upstream_domains: Set of domains from upstream

    Returns:
        Tuple of (new_domains, removed_domains)
        Note: removed_domains is always empty - we never remove domains based on upstream sources
              as local lists may contain domains from multiple sources or manual additions
    """
    local_file = PROJECT_ROOT / f"{list_name}.txt"

    if not local_file.exists():
        print(f"  ℹ️  Local file {local_file} does not exist, treating as empty")
        # Still apply exclusions even for new lists
        exclusions = load_exclusions(list_name)
        upstream_domains = upstream_domains - exclusions
        return upstream_domains, set()

    local_domains = parse_file_to_set(local_file)
    
    # Load and apply exclusions
    exclusions = load_exclusions(list_name)
    if exclusions:
        # Remove excluded domains from upstream before comparison
        upstream_domains = upstream_domains - exclusions
        
        # Check if any excluded domains are in new_domains that would be added
        excluded_from_new = (upstream_domains | exclusions) & exclusions
        if excluded_from_new:
            print(f"  ✓ Filtered {len(excluded_from_new)} excluded domain(s)")

    new_domains = upstream_domains - local_domains
    
    # IMPORTANT: Never suggest removing domains based on upstream sources
    # Local lists may contain domains from:
    # - Multiple upstream sources
    # - Manual additions
    # - User contributions
    # - Other sources not currently monitored
    removed_domains = set()

    return new_domains, removed_domains


def check_upstream_updates(list_name: str, config: dict[str, Any]) -> list[UpdateResult]:
    """Check all upstream sources for a list.

    Args:
        list_name: Name of the list to check
        config: Configuration dictionary

    Returns:
        List of UpdateResult objects
    """
    list_config = config["lists"].get(list_name)
    if not list_config:
        print(f"✗ List '{list_name}' not found in configuration")
        return []

    upstream_sources = list_config.get("upstream_sources", [])
    if not upstream_sources:
        print(f"ℹ️  List '{list_name}' has no upstream sources configured")
        return []

    print(f"\n📡 Checking upstream sources for '{list_name}'...")
    print(f"   Found {len(upstream_sources)} source(s)")

    results = []
    cache_ttl = config.get("settings", {}).get("upstream", {}).get("cache_ttl", 86400)

    for idx, source_dict in enumerate(upstream_sources, 1):
        print(f"\n[{idx}/{len(upstream_sources)}] Processing source...")

        source = UpstreamSource(
            url=source_dict["url"],
            format=source_dict.get("format", "domains"),
            trusted=source_dict.get("trusted", False),
            update_frequency=source_dict.get("update_frequency", "daily"),
            filter_comments=source_dict.get("filter_comments", True),
            filter_category=source_dict.get("filter_category"),
            max_domains=source_dict.get("max_domains"),
        )

        # Fetch upstream domains
        upstream_domains = fetch_upstream_domains(source, cache_ttl)
        if not upstream_domains:
            results.append(
                UpdateResult(
                    list_name=list_name,
                    source_url=source.url,
                    new_domains=set(),
                    removed_domains=set(),
                    total_upstream=0,
                    total_local=0,
                    error="Failed to fetch upstream domains",
                )
            )
            continue

        # Compare with local
        new_domains, removed_domains = compare_with_local(list_name, upstream_domains)

        # Get local count
        local_file = PROJECT_ROOT / f"{list_name}.txt"
        local_count = len(parse_file_to_set(local_file)) if local_file.exists() else 0

        result = UpdateResult(
            list_name=list_name,
            source_url=source.url,
            new_domains=new_domains,
            removed_domains=removed_domains,
            total_upstream=len(upstream_domains),
            total_local=local_count,
        )
        results.append(result)

        # Print summary
        print(f"  📊 Summary:")
        print(f"     Upstream: {result.total_upstream} domains")
        print(f"     Local: {result.total_local} domains")
        print(f"     New: {len(result.new_domains)} domains")
        if result.removed_domains:
            print(f"     Removed: {len(result.removed_domains)} domains")

    return results


def generate_pr_body(results: list[UpdateResult], list_name: str) -> str:
    """Generate PR description body."""
    total_new = sum(len(r.new_domains) for r in results)
    total_removed = sum(len(r.removed_domains) for r in results)

    body = f"""## 🤖 Automated Upstream Update: {list_name}

This PR was automatically generated by the upstream monitoring system.

### 📊 Summary

- **List:** `{list_name}.txt`
- **New domains:** {total_new}
- **Removed domains:** {total_removed}
- **Sources checked:** {len(results)}

### 📡 Source Details

"""

    for idx, result in enumerate(results, 1):
        body += f"""
#### Source {idx}: {result.source_url.split('/')[-1]}

- **URL:** {result.source_url}
- **Upstream total:** {result.total_upstream} domains
- **New domains:** {len(result.new_domains)}
"""
        if result.removed_domains:
            body += f"- **Removed domains:** {len(result.removed_domains)}\n"

        if result.error:
            body += f"- ⚠️ **Error:** {result.error}\n"

        # Show sample of new domains (first 10)
        if result.new_domains and len(result.new_domains) <= 20:
            body += "\n**New domains:**\n```\n"
            for domain in sorted(result.new_domains)[:20]:
                body += f"{domain}\n"
            body += "```\n"
        elif result.new_domains:
            body += f"\n**Sample of new domains** (showing 10 of {len(result.new_domains)}):\n```\n"
            for domain in sorted(result.new_domains)[:10]:
                body += f"{domain}\n"
            body += "```\n"

    body += """
### ✅ Validation

- [ ] New domains are relevant to the `{list_name}` category
- [ ] No false positives identified
- [ ] Domains pass validation checks
- [ ] Build succeeds

### 🔄 Merge Policy

"""

    if total_new <= 10:
        body += "✅ **Auto-merge eligible** - Changes are below threshold (≤10 domains)\n"
    elif total_new <= 100:
        body += "⚠️ **Manual review recommended** - Changes are moderate (11-100 domains)\n"
    else:
        body += "🔴 **Manual review required** - Changes exceed threshold (>100 domains)\n"

    body += """
---

_This PR was created by the [upstream monitoring workflow](.github/workflows/upstream-monitor.yml)._  
_To disable upstream monitoring for this list, remove the `upstream_sources` section from `config/lists.yml`._
"""

    return body


def create_pr_branch(list_name: str, results: list[UpdateResult]) -> str | None:
    """Create a git branch with upstream updates.

    Args:
        list_name: Name of the list
        results: Update results

    Returns:
        Branch name if successful, None otherwise
    """
    import subprocess

    # Check for existing upstream-update branches for this list
    try:
        result = subprocess.run(
            ["git", "branch", "-r"],
            cwd=PROJECT_ROOT,
            check=True,
            capture_output=True,
            text=True
        )
        existing_branches = [
            line.strip().replace("origin/", "")
            for line in result.stdout.splitlines()
            if f"upstream-update/{list_name}/" in line
        ]
        
        # Delete old upstream-update branches for this list
        if existing_branches:
            print(f"  🧹 Cleaning up {len(existing_branches)} old branch(es)...")
            for branch in existing_branches:
                try:
                    subprocess.run(
                        ["git", "push", "origin", "--delete", branch],
                        cwd=PROJECT_ROOT,
                        check=True,
                        capture_output=True
                    )
                    print(f"     Deleted {branch}")
                except subprocess.CalledProcessError:
                    print(f"     Warning: Could not delete {branch}")
    except subprocess.CalledProcessError as e:
        print(f"  ⚠️  Warning: Could not check for existing branches: {e}")

    # Create branch name
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    branch_name = f"upstream-update/{list_name}/{timestamp}"

    try:
        # Create and checkout new branch
        subprocess.run(
            ["git", "checkout", "-b", branch_name], cwd=PROJECT_ROOT, check=True
        )

        # Merge all new domains
        all_new_domains = set()
        for result in results:
            all_new_domains.update(result.new_domains)

        if not all_new_domains:
            print("  ℹ️  No new domains to add")
            subprocess.run(["git", "checkout", "main"], cwd=PROJECT_ROOT, check=True)
            subprocess.run(
                ["git", "branch", "-D", branch_name], cwd=PROJECT_ROOT, check=True
            )
            return None

        # Read existing file
        list_file = PROJECT_ROOT / f"{list_name}.txt"
        existing_domains = parse_file_to_set(list_file) if list_file.exists() else set()

        # Combine and sort
        all_domains = sorted(existing_domains | all_new_domains)

        # Write updated file
        with list_file.open("w") as f:
            f.write(f"# {list_name.title()} Blocklist\n")
            f.write("# Updated by upstream monitoring\n")
            f.write(f"# Date: {datetime.now().isoformat()}\n\n")
            for domain in all_domains:
                f.write(f"0.0.0.0 {domain}\n")

        # Regenerate all output formats to keep them in sync
        print(f"  🔄 Regenerating output formats...")
        
        try:
            result = subprocess.run(
                ["python3", "build.py", "--list", list_name],
                cwd=PROJECT_ROOT,
                check=True,
                capture_output=True,
                text=True
            )
            print(f"  ✓ Generated all output formats")
        except subprocess.CalledProcessError as e:
            print(f"  ⚠️  Warning: Failed to generate formats: {e}")
            print(f"      Output: {e.stderr if e.stderr else 'none'}")
            # Continue anyway - formats can be regenerated by CI
        
        # Add all generated files
        subprocess.run(["git", "add", "-A"], cwd=PROJECT_ROOT, check=True)
        
        # Commit changes
        commit_msg = f"chore: update {list_name} from upstream sources\n\nAdded {len(all_new_domains)} new domains from upstream sources."
        subprocess.run(
            ["git", "commit", "-m", commit_msg], cwd=PROJECT_ROOT, check=True
        )
        
        # Push branch to remote
        subprocess.run(
            ["git", "push", "-u", "origin", branch_name], 
            cwd=PROJECT_ROOT, 
            check=True
        )

        print(f"  ✓ Created branch: {branch_name}")
        print(f"  ✓ Pushed branch to origin")
        print(f"  ✓ Added {len(all_new_domains)} domains")

        return branch_name

    except subprocess.CalledProcessError as e:
        print(f"  ✗ Error creating branch: {e}")
        return None


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Monitor upstream blocklist sources",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--list",
        "-l",
        help="Specific list to check (e.g., ads, malware)",
    )
    parser.add_argument(
        "--all",
        "-a",
        action="store_true",
        help="Check all lists with upstream sources",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Check for updates but don't create PRs",
    )
    parser.add_argument(
        "--no-cache",
        action="store_true",
        help="Ignore cache and fetch fresh data",
    )

    args = parser.parse_args()

    if not args.list and not args.all:
        parser.error("Either --list or --all must be specified")

    # Load configuration
    print("📋 Loading configuration...")
    config = load_config()

    # Determine which lists to check
    if args.all:
        lists_to_check = [
            name
            for name, cfg in config["lists"].items()
            if cfg.get("upstream_sources")
        ]
        print(f"   Found {len(lists_to_check)} lists with upstream sources")
    else:
        lists_to_check = [args.list]

    if not lists_to_check:
        print("✗ No lists to check")
        return 1

    # Check each list
    all_results = defaultdict(list)
    for list_name in lists_to_check:
        results = check_upstream_updates(list_name, config)
        if results:
            all_results[list_name] = results

    # Print overall summary
    print("\n" + "=" * 60)
    print("📊 OVERALL SUMMARY")
    print("=" * 60)

    total_new = 0
    total_removed = 0

    for list_name, results in all_results.items():
        new_count = sum(len(r.new_domains) for r in results)
        removed_count = sum(len(r.removed_domains) for r in results)
        total_new += new_count
        total_removed += removed_count

        print(f"\n{list_name}:")
        print(f"  New: {new_count} domains")
        if removed_count:
            print(f"  Removed: {removed_count} domains")

    print(f"\nTotal new domains: {total_new}")
    if total_removed:
        print(f"Total removed domains: {total_removed}")

    # Create PRs if not dry-run
    if not args.dry_run and total_new > 0:
        print("\n" + "=" * 60)
        print("🔧 CREATING PULL REQUESTS")
        print("=" * 60)

        for list_name, results in all_results.items():
            new_count = sum(len(r.new_domains) for r in results)
            if new_count == 0:
                continue

            print(f"\nCreating PR for {list_name}...")

            # Create branch and commit
            branch_name = create_pr_branch(list_name, results)
            if branch_name:
                pr_body = generate_pr_body(results, list_name)
                pr_title = f"chore: update {list_name} from upstream sources"

                # Save PR info for GitHub Actions to create
                pr_info = {
                    "list_name": list_name,
                    "title": pr_title,
                    "branch": branch_name,
                    "new_domains": new_count,
                    "body": pr_body,
                }

                pr_file = TEMP_DIR / f"pr_{list_name}.json"
                pr_file.write_text(json.dumps(pr_info, indent=2))

                print(f"  ✓ PR info saved to {pr_file}")
            else:
                print(f"  ✗ Failed to create branch for {list_name}")

    elif args.dry_run:
        print("\n💡 Dry-run mode: No PRs created")
        print("   Run without --dry-run to create pull requests")

    return 0


if __name__ == "__main__":
    sys.exit(main())
