#!/usr/bin/env python3
"""Verify all format files are in sync and report discrepancies.

This script checks that all format variations (.txt, adguard, dnsmasq, alt-version)
of each blocklist contain the exact same set of domains.

Usage:
    python scripts/verify_format_sync.py
    python scripts/verify_format_sync.py --fix
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import PROJECT_ROOT
from src.normalize import parse_file_to_set


def check_list_sync(list_name: str, verbose: bool = False) -> tuple[bool, dict]:
    """Check if all formats for a list are in sync.
    
    Args:
        list_name: Name of the list (e.g., 'ads', 'malware')
        verbose: If True, print detailed comparison
        
    Returns:
        Tuple of (is_synced, details_dict)
    """
    hosts_path = PROJECT_ROOT / f"{list_name}.txt"
    adguard_path = PROJECT_ROOT / "adguard" / f"{list_name}-ags.txt"
    dnsmasq_path = PROJECT_ROOT / "dnsmasq-version" / f"{list_name}-dnsmasq.txt"
    alt_path = PROJECT_ROOT / "alt-version" / f"{list_name}-nl.txt"
    
    # Check all files exist
    if not all(p.exists() for p in [hosts_path, adguard_path, dnsmasq_path, alt_path]):
        return True, {"status": "missing_files"}
    
    # Parse all formats
    hosts_domains = parse_file_to_set(hosts_path)
    adguard_domains = parse_file_to_set(adguard_path)
    dnsmasq_domains = parse_file_to_set(dnsmasq_path)
    alt_domains = parse_file_to_set(alt_path)
    
    details = {
        "hosts": len(hosts_domains),
        "adguard": len(adguard_domains),
        "dnsmasq": len(dnsmasq_domains),
        "alt": len(alt_domains),
    }
    
    # Check if all match
    is_synced = (
        hosts_domains == adguard_domains == dnsmasq_domains == alt_domains
    )
    
    if not is_synced:
        # Find differences
        only_in_hosts = hosts_domains - adguard_domains - dnsmasq_domains - alt_domains
        only_in_adguard = adguard_domains - hosts_domains
        only_in_dnsmasq = dnsmasq_domains - hosts_domains
        only_in_alt = alt_domains - hosts_domains
        
        details.update({
            "only_in_hosts": list(sorted(only_in_hosts))[:10] if only_in_hosts else [],
            "only_in_adguard": list(sorted(only_in_adguard))[:10] if only_in_adguard else [],
            "only_in_dnsmasq": list(sorted(only_in_dnsmasq))[:10] if only_in_dnsmasq else [],
            "only_in_alt": list(sorted(only_in_alt))[:10] if only_in_alt else [],
        })
    
    if verbose and not is_synced:
        print(f"\n  Hosts:    {details['hosts']} domains")
        print(f"  AdGuard:  {details['adguard']} domains")
        print(f"  Dnsmasq:  {details['dnsmasq']} domains")
        print(f"  Alt:      {details['alt']} domains")
        
        if details.get('only_in_hosts'):
            print(f"\n  Domains only in hosts format (showing first 10):")
            for d in details['only_in_hosts']:
                print(f"    - {d}")
    
    return is_synced, details


def main():
    parser = argparse.ArgumentParser(
        description="Verify all format files are in sync",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Regenerate out-of-sync lists using build.py",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show detailed comparison for out-of-sync lists",
    )
    
    args = parser.parse_args()
    
    # Get all main list files
    main_lists = sorted([
        p.stem for p in PROJECT_ROOT.glob("*.txt")
        if p.stem not in ["README", "LICENSE", "CHANGELOG"]
        and not p.stem.endswith("-nl")
    ])
    
    print(f"🔍 Checking {len(main_lists)} blocklists for format sync...\n")
    
    out_of_sync = []
    
    for list_name in main_lists:
        is_synced, details = check_list_sync(list_name, verbose=args.verbose)
        
        if details.get("status") == "missing_files":
            print(f"  ⚠️  {list_name}: Missing format files (skipping)")
            continue
        
        if is_synced:
            print(f"  ✅ {list_name}: {details['hosts']} domains (all formats in sync)")
        else:
            print(f"  ❌ {list_name}: OUT OF SYNC")
            print(f"      hosts={details['hosts']}, adguard={details['adguard']}, "
                  f"dnsmasq={details['dnsmasq']}, alt={details['alt']}")
            out_of_sync.append((list_name, details))
    
    # Summary
    print(f"\n{'=' * 70}")
    if out_of_sync:
        print(f"⚠️  Found {len(out_of_sync)} list(s) out of sync:")
        for list_name, details in out_of_sync:
            print(f"   - {list_name}")
        
        if args.fix:
            print(f"\n🔧 Regenerating out-of-sync lists...")
            import subprocess
            
            for list_name, _ in out_of_sync:
                print(f"   Regenerating {list_name}...", end=" ")
                try:
                    subprocess.run(
                        ["python3", "build.py", "--list", list_name],
                        cwd=PROJECT_ROOT,
                        check=True,
                        capture_output=True,
                        text=True,
                    )
                    print("✅")
                except subprocess.CalledProcessError as e:
                    print(f"❌ Failed: {e.stderr.strip() if e.stderr else 'unknown'}")
            
            print(f"\n✅ Regeneration complete. Run this script again to verify.")
        else:
            print(f"\n💡 Run with --fix to regenerate out-of-sync lists:")
            print(f"   python scripts/verify_format_sync.py --fix")
        
        return 1
    else:
        print(f"✅ All lists are in sync!")
        return 0


if __name__ == "__main__":
    sys.exit(main())
