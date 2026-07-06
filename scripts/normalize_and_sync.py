#!/usr/bin/env python3
"""
Normalize and sync all blocklist formats.

This script:
1. Detects and removes invalid entries from source .txt files
2. Regenerates all format variations to ensure synchronization
3. Reports all changes made

Invalid entries include:
- Domains starting with # (comment character)
- Domains containing / (paths)
- Domains ending with . (trailing dot, except valid TLDs)
- Domains containing non-ASCII characters
- Domains containing URL fragments (#)
"""

import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple

# Get project root
PROJECT_ROOT = Path(__file__).parent.parent
CONFIG_DIR = PROJECT_ROOT / "config"


def load_config() -> Dict:
    """Load the lists configuration."""
    config_file = CONFIG_DIR / "lists.yml"
    if not config_file.exists():
        print(f"❌ Config file not found: {config_file}")
        sys.exit(1)
    
    import yaml
    with open(config_file, 'r') as f:
        return yaml.safe_load(f)


def is_valid_domain(domain: str) -> Tuple[bool, str]:
    """
    Check if a domain entry is valid.
    
    Returns:
        Tuple of (is_valid, reason_if_invalid)
    """
    if not domain or domain.startswith('#'):
        return False, "starts with # (comment)"
    
    if '/' in domain:
        return False, "contains / (path)"
    
    if domain.endswith('.') and not domain.endswith(('.com.', '.org.', '.net.')):
        return False, "ends with . (trailing dot)"
    
    if not domain.isascii():
        return False, "contains non-ASCII characters"
    
    # Check for URL fragments (but not valid domain parts)
    if '#' in domain:
        return False, "contains # (URL fragment)"
    
    # Check for query parameters
    if '?' in domain:
        return False, "contains ? (query parameter)"
    
    # Check for protocol
    if domain.startswith(('http://', 'https://', 'ftp://')):
        return False, "contains protocol (http/https/ftp)"
    
    return True, ""


def clean_list_file(list_file: Path) -> Tuple[int, List[str]]:
    """
    Clean invalid entries from a list file.
    
    Returns:
        Tuple of (removed_count, list_of_removed_domains)
    """
    if not list_file.exists():
        return 0, []
    
    lines = list_file.read_text(encoding='utf-8').split('\n')
    cleaned_lines = []
    removed_domains = []
    
    for line in lines:
        # Keep headers and empty lines
        if line.startswith('#') or not line.strip():
            cleaned_lines.append(line)
            continue
        
        # Extract domain part (assuming hosts format: 0.0.0.0 domain)
        if line.startswith('0.0.0.0 '):
            domain = line[8:].strip()
            
            is_valid, reason = is_valid_domain(domain)
            if not is_valid:
                removed_domains.append(f"{domain} ({reason})")
                continue
        
        cleaned_lines.append(line)
    
    # Write back if changes were made
    if removed_domains:
        list_file.write_text('\n'.join(cleaned_lines), encoding='utf-8')
    
    return len(removed_domains), removed_domains


def get_buildable_lists(config: Dict) -> Set[str]:
    """Get list of all buildable list names."""
    lists = set()
    for list_name, list_config in config.get('lists', {}).items():
        # Skip the special "everything" list (not buildable with build.py)
        if list_name == 'everything':
            continue
        lists.add(list_name)
    return lists


def regenerate_lists(list_names: Set[str]) -> bool:
    """
    Regenerate format files for the specified lists.
    
    Returns:
        True if successful, False otherwise
    """
    if not list_names:
        return True
    
    print(f"\n🔄 Regenerating {len(list_names)} list(s)...")
    
    # Build the command
    cmd = ['python3', str(PROJECT_ROOT / 'build.py')]
    for list_name in sorted(list_names):
        cmd.extend(['--list', list_name])
    
    try:
        result = subprocess.run(
            cmd,
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            check=True
        )
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to regenerate lists: {e}")
        print(e.stdout)
        print(e.stderr)
        return False


def regenerate_everything_list() -> bool:
    """
    Regenerate the special 'everything' combined list.
    
    Returns:
        True if successful, False otherwise
    """
    regenerate_script = PROJECT_ROOT / 'scripts' / 'regenerate_everything.py'
    if not regenerate_script.exists():
        print("⚠️  regenerate_everything.py not found, skipping")
        return True
    
    print("\n🔄 Regenerating 'everything' list...")
    
    try:
        result = subprocess.run(
            ['python3', str(regenerate_script)],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            check=True
        )
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to regenerate 'everything' list: {e}")
        print(e.stdout)
        print(e.stderr)
        return False


def main():
    """Main execution function."""
    print("=" * 70)
    print("Normalizing and Syncing Blocklists")
    print("=" * 70)
    
    # Load configuration
    config = load_config()
    buildable_lists = get_buildable_lists(config)
    
    # Phase 1: Clean invalid entries
    print("\n📋 Phase 1: Cleaning invalid entries from source files")
    print("-" * 70)
    
    total_removed = 0
    lists_with_changes = set()
    
    for list_name in sorted(buildable_lists):
        list_file = PROJECT_ROOT / f"{list_name}.txt"
        
        if not list_file.exists():
            continue
        
        removed_count, removed_domains = clean_list_file(list_file)
        
        if removed_count > 0:
            print(f"\n✓ {list_name}: Removed {removed_count} invalid entries")
            lists_with_changes.add(list_name)
            total_removed += removed_count
            
            # Show first few removed domains
            for domain in removed_domains[:5]:
                print(f"    - {domain}")
            if len(removed_domains) > 5:
                print(f"    ... and {len(removed_domains) - 5} more")
    
    if total_removed == 0:
        print("\n✅ No invalid entries found in any list")
    else:
        print(f"\n✅ Cleaned {total_removed} invalid entries from {len(lists_with_changes)} list(s)")
    
    # Phase 2: Regenerate formats
    print("\n📋 Phase 2: Regenerating format files")
    print("-" * 70)
    
    if lists_with_changes:
        success = regenerate_lists(lists_with_changes)
        if not success:
            print("\n❌ Failed to regenerate some lists")
            sys.exit(1)
    else:
        print("✓ No lists need regeneration")
    
    # Phase 3: Regenerate everything list
    print("\n📋 Phase 3: Regenerating 'everything' combined list")
    print("-" * 70)
    
    success = regenerate_everything_list()
    if not success:
        print("\n❌ Failed to regenerate 'everything' list")
        sys.exit(1)
    
    # Final summary
    print("\n" + "=" * 70)
    print("✅ Normalization and sync complete!")
    print("=" * 70)
    
    if lists_with_changes:
        print(f"\nModified lists: {', '.join(sorted(lists_with_changes))}")
        print(f"Total invalid entries removed: {total_removed}")
    else:
        print("\nNo changes were needed - all lists were already clean and in sync")
    
    sys.exit(0)


if __name__ == '__main__':
    main()
