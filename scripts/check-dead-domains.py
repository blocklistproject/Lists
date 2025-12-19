#!/usr/bin/env python3
"""Check for dead domains that no longer resolve.

This script checks if blocked domains still have DNS records.
Domains that don't resolve are candidates for removal.

Usage:
    python scripts/check-dead-domains.py --list ads --sample 1000
    python scripts/check-dead-domains.py --all --sample 500 --output dead-domains.txt
"""

import argparse
import random
import socket
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import NamedTuple

# Try relative imports first
try:
    from src.normalize import parse_file_to_set
except ImportError:
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from src.normalize import parse_file_to_set


class DomainCheckResult(NamedTuple):
    """Result of checking a domain."""
    domain: str
    resolves: bool
    error: str | None = None


def check_domain_resolves(domain: str, timeout: float = 2.0) -> DomainCheckResult:
    """Check if a domain has any DNS records.
    
    Args:
        domain: Domain name to check
        timeout: Socket timeout in seconds
        
    Returns:
        DomainCheckResult with resolution status
    """
    socket.setdefaulttimeout(timeout)
    
    try:
        # Try to resolve the domain (A record)
        socket.gethostbyname(domain)
        return DomainCheckResult(domain=domain, resolves=True)
    except socket.gaierror as e:
        # Name resolution failed
        return DomainCheckResult(domain=domain, resolves=False, error=str(e))
    except socket.timeout:
        return DomainCheckResult(domain=domain, resolves=False, error="timeout")
    except Exception as e:
        return DomainCheckResult(domain=domain, resolves=False, error=str(e))


def check_domains_parallel(
    domains: list[str],
    max_workers: int = 50,
    timeout: float = 2.0,
    progress_callback=None,
) -> list[DomainCheckResult]:
    """Check multiple domains in parallel.
    
    Args:
        domains: List of domains to check
        max_workers: Number of parallel threads
        timeout: Socket timeout per domain
        progress_callback: Optional callback for progress updates
        
    Returns:
        List of DomainCheckResult objects
    """
    results: list[DomainCheckResult] = []
    checked = 0
    total = len(domains)
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(check_domain_resolves, domain, timeout): domain
            for domain in domains
        }
        
        for future in as_completed(futures):
            result = future.result()
            results.append(result)
            checked += 1
            
            if progress_callback and checked % 100 == 0:
                progress_callback(checked, total)
    
    return results


def load_domains_from_list(list_name: str) -> set[str]:
    """Load domains from a blocklist file."""
    root = Path(".")
    
    # Try root .txt file
    txt_path = root / f"{list_name}.txt"
    if txt_path.exists():
        return parse_file_to_set(txt_path)
    
    return set()


def get_all_list_names() -> list[str]:
    """Get names of all blocklists."""
    root = Path(".")
    names = []
    
    for txt_file in root.glob("*.txt"):
        if txt_file.name not in ["README.md", "LICENSE", "everything.txt"]:
            if not txt_file.name.startswith("."):
                names.append(txt_file.stem)
    
    return sorted(names)


def main():
    parser = argparse.ArgumentParser(
        description="Check for dead domains that no longer resolve"
    )
    parser.add_argument(
        "--list", "-l",
        help="Specific list to check (e.g., 'ads', 'malware')"
    )
    parser.add_argument(
        "--all", "-a",
        action="store_true",
        help="Check all lists"
    )
    parser.add_argument(
        "--sample", "-s",
        type=int,
        default=100,
        help="Number of domains to sample per list (default: 100)"
    )
    parser.add_argument(
        "--workers", "-w",
        type=int,
        default=50,
        help="Number of parallel workers (default: 50)"
    )
    parser.add_argument(
        "--timeout", "-t",
        type=float,
        default=2.0,
        help="DNS timeout in seconds (default: 2.0)"
    )
    parser.add_argument(
        "--output", "-o",
        help="Output file for dead domains"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show detailed output"
    )
    
    args = parser.parse_args()
    
    if not args.list and not args.all:
        parser.error("Either --list or --all is required")
    
    # Determine which lists to check
    if args.all:
        list_names = get_all_list_names()
    else:
        list_names = [args.list]
    
    all_dead_domains: dict[str, list[str]] = {}
    total_checked = 0
    total_dead = 0
    
    for list_name in list_names:
        print(f"\n{'='*50}")
        print(f"Checking list: {list_name}")
        print(f"{'='*50}")
        
        domains = load_domains_from_list(list_name)
        if not domains:
            print(f"  No domains found for {list_name}")
            continue
        
        print(f"  Total domains: {len(domains):,}")
        
        # Sample domains
        sample_size = min(args.sample, len(domains))
        sampled = random.sample(sorted(domains), sample_size)
        print(f"  Sampling: {sample_size:,} domains")
        
        # Check domains
        def progress(checked, total):
            print(f"  Progress: {checked}/{total}", end="\r")
        
        results = check_domains_parallel(
            sampled,
            max_workers=args.workers,
            timeout=args.timeout,
            progress_callback=progress if args.verbose else None,
        )
        
        # Analyze results
        dead = [r for r in results if not r.resolves]
        alive = [r for r in results if r.resolves]
        
        total_checked += len(results)
        total_dead += len(dead)
        
        print("\n  Results:")
        print(f"    Resolving: {len(alive):,} ({len(alive)/len(results)*100:.1f}%)")
        print(f"    Dead: {len(dead):,} ({len(dead)/len(results)*100:.1f}%)")
        
        if dead:
            all_dead_domains[list_name] = [r.domain for r in dead]
            
            if args.verbose:
                print("\n  Dead domains (sample):")
                for r in dead[:10]:
                    print(f"    - {r.domain}: {r.error}")
                if len(dead) > 10:
                    print(f"    ... and {len(dead) - 10} more")
    
    # Summary
    print(f"\n{'='*50}")
    print("SUMMARY")
    print(f"{'='*50}")
    print(f"Total domains checked: {total_checked:,}")
    print(f"Total dead domains: {total_dead:,} ({total_dead/total_checked*100:.1f}%)")
    
    # Estimate total dead in full lists
    if args.sample < 10000:
        print("\nNote: Based on sampling. Actual dead domain count may vary.")
    
    # Output dead domains
    if args.output and all_dead_domains:
        with open(args.output, "w") as f:
            f.write("# Dead domains found by check-dead-domains.py\n")
            f.write(f"# Checked on: {__import__('datetime').datetime.now().isoformat()}\n")
            f.write(f"# Sample size per list: {args.sample}\n\n")
            
            for list_name, dead in sorted(all_dead_domains.items()):
                f.write(f"\n# List: {list_name} ({len(dead)} dead)\n")
                for domain in sorted(dead):
                    f.write(f"{domain}\n")
        
        print(f"\nDead domains written to: {args.output}")
    
    # Exit with error if significant dead domains found
    dead_rate = total_dead / total_checked if total_checked > 0 else 0
    if dead_rate > 0.5:
        print("\nWarning: Over 50% of sampled domains are dead!")
        sys.exit(1)


if __name__ == "__main__":
    main()
