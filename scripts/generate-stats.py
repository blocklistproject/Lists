#!/usr/bin/env python3
"""Generate statistics dashboard for the blocklist project.

Creates a markdown stats page with:
- Domain count per list and total
- TLD distribution
- Category breakdown
- Historical trends (if git history available)
"""

import json
import subprocess
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

# Try relative imports first (when run as module), fall back to direct
try:
    from src.normalize import parse_file_to_set
except ImportError:
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from src.normalize import parse_file_to_set


def get_all_domains() -> dict[str, set[str]]:
    """Load all domains from root .txt files."""
    domains_by_list: dict[str, set[str]] = {}
    
    root = Path(".")
    for txt_file in sorted(root.glob("*.txt")):
        if txt_file.name in ["README.md", "LICENSE", "everything.txt"]:
            continue
        if txt_file.name.startswith("."):
            continue
        
        list_name = txt_file.stem
        domains = parse_file_to_set(txt_file)
        if domains:
            domains_by_list[list_name] = domains
    
    return domains_by_list


def extract_tld(domain: str) -> str:
    """Extract the TLD from a domain."""
    parts = domain.rsplit(".", 1)
    return parts[-1] if len(parts) > 1 else domain


def extract_sld(domain: str) -> str:
    """Extract the second-level domain (e.g., 'example' from 'sub.example.com')."""
    parts = domain.split(".")
    if len(parts) >= 2:
        return parts[-2]
    return domain


def count_tlds(all_domains: set[str]) -> Counter:
    """Count TLD distribution across all domains."""
    return Counter(extract_tld(d) for d in all_domains)


def get_category_mapping() -> dict[str, list[str]]:
    """Map categories to list names based on config."""
    config_path = Path("config/lists.yml")
    if not config_path.exists():
        return {}
    
    import yaml
    with open(config_path) as f:
        config = yaml.safe_load(f)
    
    category_map: dict[str, list[str]] = defaultdict(list)
    for name, info in config.get("lists", {}).items():
        for cat in info.get("categories", []):
            category_map[cat].append(name)
    
    return dict(category_map)


def get_historical_counts() -> list[dict]:
    """Get domain counts from git history (last 10 commits that touched lists)."""
    history = []
    
    # Get commits that modified .txt files
    cmd = [
        "git", "log", "--format=%H %aI", "--diff-filter=M",
        "-n", "20", "--", "*.txt"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        return history
    
    commits = result.stdout.strip().split("\n")[:10]
    
    for line in commits:
        if not line.strip():
            continue
        
        parts = line.split(" ", 1)
        if len(parts) != 2:
            continue
        
        commit_hash, date_str = parts
        
        # Count total domains at this commit (just ads.txt as proxy for speed)
        cmd = ["git", "show", f"{commit_hash}:ads.txt"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            count = sum(1 for line in result.stdout.split("\n") 
                       if line.strip() and line.startswith("0.0.0.0 "))
            history.append({
                "date": date_str[:10],
                "commit": commit_hash[:7],
                "ads_count": count,
            })
    
    return history


def generate_stats_markdown(output_path: str = "STATS.md") -> None:
    """Generate the statistics dashboard markdown file."""
    print("Loading domains...")
    domains_by_list = get_all_domains()
    
    # Calculate totals
    all_domains: set[str] = set()
    for domains in domains_by_list.values():
        all_domains.update(domains)
    
    total_unique = len(all_domains)
    total_entries = sum(len(d) for d in domains_by_list.values())
    
    print(f"Analyzing {total_unique:,} unique domains...")
    
    # TLD analysis
    tld_counts = count_tlds(all_domains)
    top_tlds = tld_counts.most_common(20)
    
    # Category mapping
    category_map = get_category_mapping()
    
    # Historical data
    print("Fetching historical data...")
    history = get_historical_counts()
    
    # Generate markdown
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("# Block List Project Statistics\n\n")
        f.write(f"*Last updated: {now}*\n\n")
        
        # Summary
        f.write("## Summary\n\n")
        f.write("| Metric | Value |\n")
        f.write("|--------|------:|\n")
        f.write(f"| Total Lists | {len(domains_by_list)} |\n")
        f.write(f"| Unique Domains | {total_unique:,} |\n")
        f.write(f"| Total Entries (with overlap) | {total_entries:,} |\n")
        f.write(f"| Unique TLDs | {len(tld_counts):,} |\n")
        f.write("\n")
        
        # Domain counts by list
        f.write("## Domains by List\n\n")
        f.write("| List | Domains | % of Total |\n")
        f.write("|------|--------:|-----------:|\n")
        
        sorted_lists = sorted(domains_by_list.items(), key=lambda x: len(x[1]), reverse=True)
        for name, domains in sorted_lists:
            pct = (len(domains) / total_unique * 100) if total_unique > 0 else 0
            f.write(f"| {name} | {len(domains):,} | {pct:.1f}% |\n")
        f.write("\n")
        
        # TLD distribution
        f.write("## Top TLDs Blocked\n\n")
        f.write("| TLD | Count | % |\n")
        f.write("|-----|------:|--:|\n")
        
        for tld, count in top_tlds:
            pct = (count / total_unique * 100) if total_unique > 0 else 0
            f.write(f"| .{tld} | {count:,} | {pct:.1f}% |\n")
        f.write("\n")
        
        # Category breakdown
        if category_map:
            f.write("## Categories\n\n")
            f.write("| Category | Lists | Total Domains |\n")
            f.write("|----------|------:|--------------:|\n")
            
            category_totals = []
            for cat, lists in category_map.items():
                cat_domains: set[str] = set()
                for lst in lists:
                    if lst in domains_by_list:
                        cat_domains.update(domains_by_list[lst])
                category_totals.append((cat, len(lists), len(cat_domains)))
            
            for cat, num_lists, num_domains in sorted(category_totals, key=lambda x: x[2], reverse=True):
                f.write(f"| {cat} | {num_lists} | {num_domains:,} |\n")
            f.write("\n")
        
        # Historical trends
        if history:
            f.write("## Recent History (ads.txt as sample)\n\n")
            f.write("| Date | Commit | Domains |\n")
            f.write("|------|--------|--------:|\n")
            
            for entry in history:
                f.write(f"| {entry['date']} | {entry['commit']} | {entry['ads_count']:,} |\n")
            f.write("\n")
        
        # Overlap analysis
        f.write("## List Overlap\n\n")
        f.write("Many domains appear in multiple lists. Here are the most common overlaps:\n\n")
        
        # Count how many lists each domain appears in
        domain_list_count: Counter = Counter()
        for domains in domains_by_list.values():
            for d in domains:
                domain_list_count[d] += 1
        
        overlap_dist = Counter(domain_list_count.values())
        f.write("| Appears in N Lists | Domains |\n")
        f.write("|-------------------:|--------:|\n")
        for n in sorted(overlap_dist.keys()):
            f.write(f"| {n} | {overlap_dist[n]:,} |\n")
        f.write("\n")
        
        # Footer
        f.write("---\n\n")
        f.write("*Generated by `scripts/generate-stats.py`*\n")
    
    print(f"Statistics written to {output_path}")


def generate_stats_json(output_path: str = "stats.json") -> None:
    """Generate statistics as JSON for programmatic access."""
    domains_by_list = get_all_domains()
    
    all_domains: set[str] = set()
    for domains in domains_by_list.values():
        all_domains.update(domains)
    
    tld_counts = count_tlds(all_domains)
    
    stats = {
        "generated": datetime.now(timezone.utc).isoformat(),
        "total_unique_domains": len(all_domains),
        "lists": {
            name: len(domains) for name, domains in domains_by_list.items()
        },
        "top_tlds": dict(tld_counts.most_common(50)),
    }
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2)
    
    print(f"JSON stats written to {output_path}")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate statistics dashboard")
    parser.add_argument("--output", default="STATS.md", help="Output markdown file")
    parser.add_argument("--json", help="Also output JSON stats to this file")
    
    args = parser.parse_args()
    
    generate_stats_markdown(args.output)
    
    if args.json:
        generate_stats_json(args.json)


if __name__ == "__main__":
    main()
