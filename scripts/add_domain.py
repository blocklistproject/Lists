#!/usr/bin/env python3
"""Add domain(s) to a blocklist and regenerate all formats.

This script:
1. Accepts domain(s) via CLI or file
2. Normalizes and validates domains
3. Checks for duplicates
4. Adds to the main .txt file (hosts format)
5. Regenerates all output formats (adguard, dnsmasq, alt-version)
6. Optionally commits changes with git

Usage:
    # Add a single domain
    python scripts/add_domain.py --list ads --domain example.com
    
    # Add multiple domains from file
    python scripts/add_domain.py --list malware --file domains.txt
    
    # Add and commit changes
    python scripts/add_domain.py --list ads --domain example.com --commit --reason "User report" --issue 123
    
    # Add without regenerating formats (faster, but formats will be out of sync)
    python scripts/add_domain.py --list ads --domain example.com --no-regenerate
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


class DomainAdder:
    """Handles adding domains to blocklists."""

    def __init__(
        self,
        list_name: str,
        reason: str | None = None,
        issue: int | None = None,
        commit: bool = False,
        regenerate: bool = True,
    ):
        """Initialize the domain adder.

        Args:
            list_name: Name of the list (e.g., 'ads', 'malware')
            reason: Optional reason for adding
            issue: Optional GitHub issue number
            commit: Whether to commit changes
            regenerate: Whether to regenerate all formats
        """
        self.list_name = list_name
        self.reason = reason
        self.issue = issue
        self.commit = commit
        self.regenerate = regenerate
        self.list_file = PROJECT_ROOT / f"{list_name}.txt"
        self.added_count = 0
        self.skipped_count = 0
        self.domains_added = []

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

    def validate_list(self) -> bool:
        """Check if the list file exists.

        Returns:
            True if valid, False otherwise
        """
        if not self.list_file.exists():
            print(f"✗ List file not found: {self.list_file}")
            print(f"  Available lists: ads, malware, phishing, tracking, gambling, etc.")
            return False
        return True

    def add_domain(self, domain: str) -> bool:
        """Add a single domain to the list.

        Args:
            domain: Domain to add

        Returns:
            True if domain was added, False if skipped
        """
        # Normalize domain
        normalized = self.normalize_domain(domain)
        if not normalized:
            print(f"  ⚠️  Skipped invalid domain: {domain}")
            self.skipped_count += 1
            return False

        # Check if already exists
        existing_domains = parse_file_to_set(self.list_file)
        if normalized in existing_domains:
            print(f"  ℹ️  Already exists: {normalized}")
            self.skipped_count += 1
            return False

        # Add to list
        print(f"  ✓ Adding: {normalized}")
        self.domains_added.append(normalized)
        self.added_count += 1
        return True

    def add_from_file(self, filepath: Path) -> int:
        """Add domains from a file (one per line).

        Args:
            filepath: Path to file containing domains

        Returns:
            Number of domains added
        """
        if not filepath.exists():
            print(f"✗ File not found: {filepath}")
            return 0

        print(f"📄 Reading domains from: {filepath}")
        
        with filepath.open() as f:
            domains = [line.strip() for line in f if line.strip() and not line.startswith("#")]

        print(f"   Found {len(domains)} domain(s) in file")

        for domain in domains:
            self.add_domain(domain)

        return self.added_count

    def write_changes(self) -> bool:
        """Write the updated list to disk.

        Returns:
            True if successful
        """
        if not self.domains_added:
            print("  ℹ️  No domains to add")
            return False

        print(f"💾 Writing changes to {self.list_file.name}...")

        # Read existing file
        existing_domains = parse_file_to_set(self.list_file)

        # Combine and sort
        all_domains = sorted(existing_domains | set(self.domains_added))

        # Preserve original header if it exists
        header_lines = []
        with self.list_file.open() as f:
            for line in f:
                if line.strip().startswith("#"):
                    header_lines.append(line)
                else:
                    break

        # Write updated file
        with self.list_file.open("w") as f:
            # Write header
            if header_lines:
                f.writelines(header_lines)
            else:
                f.write(f"# Title: {self.list_name.title()} Block List\n")
                f.write(f"# Updated: {datetime.now().strftime('%Y-%m-%d')}\n\n")

            # Write domains
            for domain in all_domains:
                f.write(f"0.0.0.0 {domain}\n")

        print(f"  ✓ Wrote {len(all_domains)} total domains ({self.added_count} new)")
        return True

    def regenerate_formats(self) -> bool:
        """Regenerate all output formats using Node.js scripts.

        Returns:
            True if successful
        """
        if not self.regenerate:
            print("  ⚠️  Skipping format regeneration (--no-regenerate)")
            return True

        print("🔄 Regenerating output formats...")
        scripts_dir = PROJECT_ROOT / "scripts"

        scripts = [
            ("generate-noip.js", "alt-version"),
            ("generate-dnsmasq.js", "dnsmasq-version"),
            ("generate-adguard.js", "adguard"),
        ]

        success = True
        for script_name, format_name in scripts:
            try:
                result = subprocess.run(
                    ["node", str(scripts_dir / script_name)],
                    cwd=PROJECT_ROOT,
                    check=True,
                    capture_output=True,
                    text=True,
                )
                print(f"  ✓ Generated {format_name}/")
            except subprocess.CalledProcessError as e:
                print(f"  ✗ Failed to generate {format_name}/")
                print(f"     Error: {e.stderr if e.stderr else 'unknown'}")
                success = False
            except FileNotFoundError:
                print(f"  ✗ Node.js not found. Install Node.js to regenerate formats.")
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
            print(f"   git add . && git commit -m 'Add domains to {self.list_name}'")
            return True

        print("📝 Committing changes...")

        try:
            # Stage all changes
            subprocess.run(["git", "add", "-A"], cwd=PROJECT_ROOT, check=True)

            # Build commit message
            if self.added_count == 1:
                subject = f"Add domain to {self.list_name} list"
            else:
                subject = f"Add {self.added_count} domains to {self.list_name} list"

            body_parts = []
            if self.reason:
                body_parts.append(f"Reason: {self.reason}")
            if self.issue:
                body_parts.append(f"Closes #{self.issue}")
            
            # Show domains added (limit to 10 for readability)
            if self.domains_added:
                domains_to_show = self.domains_added[:10]
                body_parts.append("\nDomains added:")
                for d in domains_to_show:
                    body_parts.append(f"- {d}")
                if len(self.domains_added) > 10:
                    body_parts.append(f"... and {len(self.domains_added) - 10} more")

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
        description="Add domain(s) to a blocklist",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Add single domain
  python scripts/add_domain.py --list ads --domain example.com
  
  # Add from file
  python scripts/add_domain.py --list malware --file domains.txt
  
  # Add and commit
  python scripts/add_domain.py --list ads --domain example.com --commit --reason "User report"
  
  # Add without regenerating formats (faster)
  python scripts/add_domain.py --list ads --domain example.com --no-regenerate
        """,
    )

    parser.add_argument(
        "--list",
        "-l",
        required=True,
        help="List name (e.g., ads, malware, phishing)",
    )
    parser.add_argument(
        "--domain",
        "-d",
        help="Single domain to add",
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
        help="Reason for adding (included in commit message)",
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

    # Initialize adder
    adder = DomainAdder(
        list_name=args.list,
        reason=args.reason,
        issue=args.issue,
        commit=args.commit,
        regenerate=not args.no_regenerate,
    )

    # Validate list exists
    if not adder.validate_list():
        return 1

    print(f"\n📋 Adding domain(s) to {args.list} list...")

    # Add domain(s)
    if args.domain:
        adder.add_domain(args.domain)
    elif args.file:
        adder.add_from_file(args.file)

    # Summary
    print(f"\n📊 Summary:")
    print(f"   Added: {adder.added_count}")
    print(f"   Skipped: {adder.skipped_count}")

    if adder.added_count == 0:
        print("\n✓ No changes needed")
        return 0

    # Write changes
    if not adder.write_changes():
        return 1

    # Regenerate formats
    if not adder.regenerate_formats():
        print("\n⚠️  Warning: Some formats failed to regenerate")
        print("   Run build.py or the generate scripts manually")

    # Commit if requested
    adder.commit_changes()

    print(f"\n✓ Done! Added {adder.added_count} domain(s) to {args.list}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
