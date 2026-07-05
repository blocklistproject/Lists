#!/usr/bin/env python3
"""Remove domain(s) from blocklist(s) and regenerate all formats.

This script:
1. Accepts domain(s) via CLI or file
2. Normalizes and validates domains
3. Searches for domain across specified lists (or all lists)
4. Removes from all formats (.txt, adguard, dnsmasq, alt-version)
5. Regenerates affected output formats
6. Optionally commits changes with git

Usage:
    # Remove a single domain from a specific list
    python scripts/remove_domain.py --list ads --domain example.com
    
    # Remove from all lists where it appears
    python scripts/remove_domain.py --domain example.com --all-lists
    
    # Remove multiple domains from file
    python scripts/remove_domain.py --list malware --file domains.txt
    
    # Remove and commit changes
    python scripts/remove_domain.py --list ads --domain example.com --commit --reason "False positive" --issue 123
    
    # Remove without regenerating formats (faster, but formats will be out of sync)
    python scripts/remove_domain.py --list ads --domain example.com --no-regenerate
"""

import argparse
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import CONFIG_DIR, PROJECT_ROOT
from src.normalize import normalize_line, parse_file_to_set


class DomainRemover:
    """Handles removing domains from blocklists."""

    def __init__(
        self,
        list_name: str | None = None,
        all_lists: bool = False,
        reason: str | None = None,
        issue: int | None = None,
        commit: bool = False,
        regenerate: bool = True,
    ):
        """Initialize the domain remover.

        Args:
            list_name: Name of the list (e.g., 'ads', 'malware'), or None for all lists
            all_lists: If True, search and remove from all lists
            reason: Optional reason for removal
            issue: Optional GitHub issue number
            commit: Whether to commit changes
            regenerate: Whether to regenerate all formats
        """
        self.list_name = list_name
        self.all_lists = all_lists
        self.reason = reason
        self.issue = issue
        self.commit = commit
        self.regenerate = regenerate
        self.removed_count = 0
        self.not_found_count = 0
        self.domains_removed = []
        self.affected_lists = set()

    def normalize_domain(self, domain: str) -> str | None:
        """Normalize a domain to its base form.

        Args:
            domain: Domain to normalize

        Returns:
            Normalized domain or None if invalid
        """
        # Strip whitespace
        domain = domain.strip()

        # Remove protocol if present
        domain = re.sub(r"^https?://", "", domain)

        # Remove www. prefix
        domain = re.sub(r"^www\.", "", domain)

        # Remove port if present
        domain = re.sub(r":\d+$", "", domain)

        # Remove trailing slash and path
        domain = domain.split("/")[0]

        # Basic validation: must have at least one dot and valid characters
        if not re.match(r"^[a-z0-9]([a-z0-9\-]{0,61}[a-z0-9])?(\.[a-z0-9]([a-z0-9\-]{0,61}[a-z0-9])?)*$", domain.lower()):
            return None

        return domain.lower()

    def get_list_files(self) -> list[Path]:
        """Get list of .txt files to process.

        Returns:
            List of Path objects for main list files
        """
        if self.all_lists:
            # Find all .txt files in root (except special ones)
            txt_files = sorted(PROJECT_ROOT.glob("*.txt"))
            # Exclude non-list files
            exclude = {"README.txt", "LICENSE.txt", "CHANGELOG.txt"}
            return [f for f in txt_files if f.name not in exclude]
        elif self.list_name:
            list_file = PROJECT_ROOT / f"{self.list_name}.txt"
            if not list_file.exists():
                print(f"✗ List file not found: {list_file}")
                print(f"  Available lists: ads, malware, phishing, tracking, gambling, etc.")
                return []
            return [list_file]
        else:
            return []

    def check_hosts_line(self, line: str, domain: str) -> bool:
        """Check if a hosts format line contains the domain.

        Args:
            line: Line to check
            domain: Domain to find

        Returns:
            True if line contains the domain
        """
        parts = line.strip().split()
        return len(parts) >= 2 and parts[1] == domain

    def check_adguard_line(self, line: str, domain: str) -> bool:
        """Check if an AdGuard format line contains the domain.

        Args:
            line: Line to check
            domain: Domain to find

        Returns:
            True if line contains the domain
        """
        stripped = line.strip()
        return stripped == f"||{domain}^"

    def check_dnsmasq_line(self, line: str, domain: str) -> bool:
        """Check if a dnsmasq format line contains the domain.

        Args:
            line: Line to check
            domain: Domain to find

        Returns:
            True if line contains the domain
        """
        stripped = line.strip()
        return stripped == f"server=/{domain}/"

    def remove_from_file(self, filepath: Path, domain: str, check_func) -> int:
        """Remove domain from a specific file.

        Args:
            filepath: Path to file
            domain: Domain to remove
            check_func: Function to check if line matches domain

        Returns:
            Number of lines removed
        """
        if not filepath.exists():
            return 0

        with filepath.open() as f:
            lines = f.readlines()

        new_lines = []
        removed = 0
        for line in lines:
            if check_func(line, domain):
                removed += 1
            else:
                new_lines.append(line)

        if removed > 0:
            with filepath.open("w") as f:
                f.writelines(new_lines)

        return removed

    def remove_domain(self, domain: str) -> bool:
        """Remove a single domain from the list(s).

        Args:
            domain: Domain to remove

        Returns:
            True if domain was removed from at least one file, False otherwise
        """
        # Normalize domain
        normalized = self.normalize_domain(domain)
        if not normalized:
            print(f"  ⚠️  Skipped invalid domain: {domain}")
            self.not_found_count += 1
            return False

        # Get list files to check
        list_files = self.get_list_files()
        if not list_files:
            print(f"  ✗ No valid list files to process")
            return False

        found_in_any = False

        for list_file in list_files:
            list_name = list_file.stem
            total_removed = 0

            # Remove from main .txt file
            removed = self.remove_from_file(list_file, normalized, self.check_hosts_line)
            if removed > 0:
                print(f"  ✓ Removed from {list_file.name}: {removed} occurrence(s)")
                total_removed += removed
                self.affected_lists.add(list_name)

            # Remove from adguard format
            adguard_file = PROJECT_ROOT / "adguard" / f"{list_name}-ags.txt"
            removed = self.remove_from_file(adguard_file, normalized, self.check_adguard_line)
            if removed > 0:
                print(f"  ✓ Removed from adguard/{adguard_file.name}: {removed} occurrence(s)")
                total_removed += removed

            # Remove from dnsmasq format
            dnsmasq_file = PROJECT_ROOT / "dnsmasq-version" / f"{list_name}-dnsmasq.txt"
            removed = self.remove_from_file(dnsmasq_file, normalized, self.check_dnsmasq_line)
            if removed > 0:
                print(f"  ✓ Removed from dnsmasq-version/{dnsmasq_file.name}: {removed} occurrence(s)")
                total_removed += removed

            # Remove from alt-version format
            alt_file = PROJECT_ROOT / "alt-version" / f"{list_name}-nl.txt"
            removed = self.remove_from_file(alt_file, normalized, self.check_hosts_line)
            if removed > 0:
                print(f"  ✓ Removed from alt-version/{alt_file.name}: {removed} occurrence(s)")
                total_removed += removed

            if total_removed > 0:
                found_in_any = True

        if found_in_any:
            print(f"  ✓ Removed: {normalized}")
            self.domains_removed.append(normalized)
            self.removed_count += 1
        else:
            print(f"  ℹ️  Not found: {normalized}")
            self.not_found_count += 1

        return found_in_any

    def remove_from_file_input(self, filepath: Path) -> int:
        """Remove domains from a file (one per line).

        Args:
            filepath: Path to file containing domains

        Returns:
            Number of domains removed
        """
        if not filepath.exists():
            print(f"✗ File not found: {filepath}")
            return 0

        print(f"📄 Reading domains from: {filepath}")

        with filepath.open() as f:
            domains = [line.strip() for line in f if line.strip() and not line.startswith("#")]

        print(f"   Found {len(domains)} domain(s) in file")

        for domain in domains:
            self.remove_domain(domain)

        return self.removed_count

    def regenerate_formats(self) -> bool:
        """Regenerate all output formats using build.py.

        Returns:
            True if successful
        """
        if not self.regenerate:
            print("  ⚠️  Skipping format regeneration (--no-regenerate)")
            return True

        if not self.affected_lists:
            return True

        print("🔄 Regenerating output formats for affected lists...")

        success = True
        for list_name in sorted(self.affected_lists):
            try:
                result = subprocess.run(
                    ["python3", "build.py", "--list", list_name],
                    cwd=PROJECT_ROOT,
                    check=True,
                    capture_output=True,
                    text=True,
                )
                print(f"  ✓ Regenerated formats for {list_name}")
            except subprocess.CalledProcessError as e:
                print(f"  ✗ Failed to regenerate {list_name}")
                print(f"     Error: {e.stderr if e.stderr else 'unknown'}")
                success = False
            except FileNotFoundError:
                print(f"  ✗ Python not found. Cannot regenerate formats.")
                success = False
                break

        return success

    def commit_changes(self) -> bool:
        """Commit changes to git.

        Returns:
            True if successful
        """
        if not self.commit:
            print("\n💡 Changes not committed. Use --commit to commit automatically.")
            print("   Or commit manually with:")
            if self.affected_lists:
                lists_str = ", ".join(sorted(self.affected_lists))
                print(f"   git add . && git commit -m 'Remove domains from {lists_str}'")
            else:
                print(f"   git add . && git commit -m 'Remove domains from blocklists'")
            return True

        print("📝 Committing changes...")

        try:
            # Stage all changes
            subprocess.run(["git", "add", "-A"], cwd=PROJECT_ROOT, check=True)

            # Build commit message
            if self.removed_count == 1:
                if len(self.affected_lists) == 1:
                    subject = f"Remove domain from {list(self.affected_lists)[0]} list"
                else:
                    subject = f"Remove domain from {len(self.affected_lists)} lists"
            else:
                if len(self.affected_lists) == 1:
                    subject = f"Remove {self.removed_count} domains from {list(self.affected_lists)[0]} list"
                else:
                    subject = f"Remove {self.removed_count} domains from {len(self.affected_lists)} lists"

            body_parts = []
            if self.reason:
                body_parts.append(f"Reason: {self.reason}")
            if self.issue:
                body_parts.append(f"Closes #{self.issue}")

            # Show domains removed (limit to 10 for readability)
            if self.domains_removed:
                domains_to_show = self.domains_removed[:10]
                body_parts.append("\nDomains removed:")
                for d in domains_to_show:
                    body_parts.append(f"- {d}")
                if len(self.domains_removed) > 10:
                    body_parts.append(f"... and {len(self.domains_removed) - 10} more")

            # Show affected lists
            if self.affected_lists:
                body_parts.append(f"\nAffected lists: {', '.join(sorted(self.affected_lists))}")

            commit_msg = subject
            if body_parts:
                commit_msg += "\n\n" + "\n".join(body_parts)

            # Commit
            subprocess.run(
                ["git", "commit", "-m", commit_msg],
                cwd=PROJECT_ROOT,
                check=True,
            )

            print(f"  ✓ Committed changes")
            print("\n💡 Push changes with: git push origin main")
            return True

        except subprocess.CalledProcessError as e:
            print(f"  ✗ Failed to commit: {e}")
            return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Remove domain(s) from blocklist(s)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Remove single domain from specific list
  python scripts/remove_domain.py --list ads --domain example.com
  
  # Remove domain from all lists where it appears
  python scripts/remove_domain.py --domain example.com --all-lists
  
  # Remove from file
  python scripts/remove_domain.py --list malware --file domains.txt
  
  # Remove and commit
  python scripts/remove_domain.py --list ads --domain example.com --commit --reason "False positive"
  
  # Remove without regenerating formats (faster)
  python scripts/remove_domain.py --list ads --domain example.com --no-regenerate
        """,
    )

    parser.add_argument(
        "--list",
        "-l",
        help="List name (e.g., ads, malware, phishing). Omit to use --all-lists",
    )
    parser.add_argument(
        "--all-lists",
        "-a",
        action="store_true",
        help="Search and remove from all lists",
    )
    parser.add_argument(
        "--domain",
        "-d",
        help="Single domain to remove",
    )
    parser.add_argument(
        "--file",
        "-f",
        type=Path,
        help="File containing domains (one per line)",
    )
    parser.add_argument(
        "--reason",
        "-r",
        help="Reason for removal (included in commit message)",
    )
    parser.add_argument(
        "--issue",
        "-i",
        type=int,
        help="GitHub issue number (e.g., 123)",
    )
    parser.add_argument(
        "--commit",
        "-c",
        action="store_true",
        help="Commit changes to git",
    )
    parser.add_argument(
        "--no-regenerate",
        action="store_true",
        help="Skip regenerating output formats (faster, but formats will be out of sync)",
    )

    args = parser.parse_args()

    # Validate arguments
    if not args.domain and not args.file:
        parser.error("Either --domain or --file must be specified")

    if args.domain and args.file:
        parser.error("Cannot specify both --domain and --file")

    if not args.list and not args.all_lists:
        parser.error("Either --list or --all-lists must be specified")

    if args.list and args.all_lists:
        parser.error("Cannot specify both --list and --all-lists")

    # Initialize remover
    remover = DomainRemover(
        list_name=args.list,
        all_lists=args.all_lists,
        reason=args.reason,
        issue=args.issue,
        commit=args.commit,
        regenerate=not args.no_regenerate,
    )

    if args.all_lists:
        print(f"\n🔍 Removing domain(s) from all lists where found...")
    else:
        print(f"\n🔍 Removing domain(s) from {args.list} list...")

    # Remove domain(s)
    if args.domain:
        remover.remove_domain(args.domain)
    elif args.file:
        remover.remove_from_file_input(args.file)

    # Summary
    print(f"\n📊 Summary:")
    print(f"   Removed: {remover.removed_count}")
    print(f"   Not found: {remover.not_found_count}")
    if remover.affected_lists:
        print(f"   Affected lists: {', '.join(sorted(remover.affected_lists))}")

    if remover.removed_count == 0:
        print("\n✓ No changes needed")
        return 0

    # Regenerate formats
    if not remover.regenerate_formats():
        print("\n⚠️  Warning: Some formats failed to regenerate")
        print("   Run build.py or the generate scripts manually")

    # Commit if requested
    remover.commit_changes()

    print(f"\n✓ Done! Removed {remover.removed_count} domain(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
