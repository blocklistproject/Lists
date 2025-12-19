#!/usr/bin/env python3
"""Generate changelog showing domains added/removed since last release."""

import argparse
import subprocess
from pathlib import Path


def get_changed_files(since_tag: str | None) -> list[str]:
    """Get list of .txt files changed since the given tag."""
    if since_tag:
        cmd = ["git", "diff", "--name-only", since_tag, "HEAD", "--", "*.txt"]
    else:
        # No previous tag, consider all files as new
        cmd = ["git", "ls-files", "*.txt"]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    return [f for f in result.stdout.strip().split("\n") if f and f.endswith(".txt")]


def get_file_at_revision(filepath: str, revision: str) -> set[str]:
    """Get domains from a file at a specific git revision."""
    cmd = ["git", "show", f"{revision}:{filepath}"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        return set()
    
    domains = set()
    for line in result.stdout.split("\n"):
        line = line.strip()
        if not line or line.startswith("#") or line.startswith("!"):
            continue
        
        # Handle hosts format
        if line.startswith("0.0.0.0 ") or line.startswith("127.0.0.1 "):
            parts = line.split()
            if len(parts) >= 2:
                domains.add(parts[1].lower())
        # Handle domain-only format
        elif "." in line and not line.startswith("server="):
            domains.add(line.lower())
    
    return domains


def get_current_domains(filepath: str) -> set[str]:
    """Get domains from a file in the working directory."""
    path = Path(filepath)
    if not path.exists():
        return set()
    
    domains = set()
    for line in path.read_text(encoding="utf-8").split("\n"):
        line = line.strip()
        if not line or line.startswith("#") or line.startswith("!"):
            continue
        
        if line.startswith("0.0.0.0 ") or line.startswith("127.0.0.1 "):
            parts = line.split()
            if len(parts) >= 2:
                domains.add(parts[1].lower())
        elif "." in line and not line.startswith("server="):
            domains.add(line.lower())
    
    return domains


def generate_changelog(since_tag: str | None, output_path: str) -> None:
    """Generate a changelog showing domains added/removed."""
    # Only look at root .txt files (the canonical source)
    root_txt_files = [
        f for f in Path(".").glob("*.txt")
        if f.name not in ["README.md", "LICENSE"] and not f.name.startswith(".")
    ]
    
    total_added = 0
    total_removed = 0
    changes_by_list: dict[str, dict] = {}
    
    for txt_file in sorted(root_txt_files):
        list_name = txt_file.stem
        filepath = str(txt_file)
        
        current = get_current_domains(filepath)
        
        if since_tag:
            previous = get_file_at_revision(filepath, since_tag)
        else:
            previous = set()
        
        added = current - previous
        removed = previous - current
        
        if added or removed:
            changes_by_list[list_name] = {
                "added": len(added),
                "removed": len(removed),
                "total": len(current),
                "added_examples": sorted(added)[:5],
                "removed_examples": sorted(removed)[:5],
            }
            total_added += len(added)
            total_removed += len(removed)
    
    # Write changelog
    with open(output_path, "w", encoding="utf-8") as f:
        if since_tag:
            f.write(f"Changes since {since_tag}\n\n")
        else:
            f.write("Initial release\n\n")
        
        f.write(f"**Summary:** +{total_added:,} added, -{total_removed:,} removed\n\n")
        
        if changes_by_list:
            f.write("### Changes by List\n\n")
            f.write("| List | Added | Removed | Total |\n")
            f.write("|------|------:|--------:|------:|\n")
            
            for name, data in sorted(changes_by_list.items()):
                f.write(f"| {name} | +{data['added']:,} | -{data['removed']:,} | {data['total']:,} |\n")
            
            f.write("\n")
            
            # Show example domains for significant changes
            f.write("### Notable Changes\n\n")
            for name, data in sorted(changes_by_list.items(), key=lambda x: x[1]["added"], reverse=True)[:5]:
                if data["added"] > 0:
                    examples = ", ".join(f"`{d}`" for d in data["added_examples"][:3])
                    f.write(f"**{name}**: +{data['added']:,} domains (e.g., {examples})\n\n")
        else:
            f.write("No changes to blocklists.\n")
    
    print(f"Changelog written to {output_path}")
    print(f"Total: +{total_added:,} added, -{total_removed:,} removed")


def main():
    parser = argparse.ArgumentParser(description="Generate release changelog")
    parser.add_argument("--since", help="Previous git tag to compare against")
    parser.add_argument("--output", default="changelog.md", help="Output file path")
    
    args = parser.parse_args()
    
    generate_changelog(args.since, args.output)


if __name__ == "__main__":
    main()
