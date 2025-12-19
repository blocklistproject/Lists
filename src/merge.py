"""Merge and deduplicate domain sets from multiple sources.

This module handles:
- Deduplication across multiple input sources
- Override/allowlist processing (domains to exclude)
- Sorting for deterministic output
"""

from pathlib import Path
from typing import Iterable

# Support both relative and absolute imports
try:
    from .normalize import parse_file_to_set
except ImportError:
    from normalize import parse_file_to_set


def deduplicate(domains: Iterable[str]) -> set[str]:
    """Remove duplicate domains from an iterable.
    
    Args:
        domains: Iterable of domain strings
        
    Returns:
        Set of unique lowercase domains
    """
    return {d.lower() for d in domains}


def merge_domain_sets(*sets: set[str]) -> set[str]:
    """Merge multiple domain sets into one.
    
    Args:
        *sets: Variable number of domain sets to merge
        
    Returns:
        Union of all input sets
    """
    result: set[str] = set()
    for s in sets:
        result.update(s)
    return result


def apply_allowlist(domains: set[str], allowlist: set[str]) -> set[str]:
    """Remove allowlisted domains from a domain set.
    
    Args:
        domains: Set of domains to filter
        allowlist: Set of domains to exclude
        
    Returns:
        Domain set with allowlisted domains removed
    """
    return domains - {a.lower() for a in allowlist}


def sort_domains(domains: set[str]) -> list[str]:
    """Sort domains for deterministic output.
    
    Sorting is important for:
    - Reproducible builds (git diffs are meaningful)
    - Efficient distribution (gzip compression benefits from sorted data)
    
    Args:
        domains: Set of domains to sort
        
    Returns:
        Alphabetically sorted list of domains
    """
    return sorted(domains)


def merge_from_files(
    input_files: list[Path],
    allowlist_file: Path | None = None
) -> set[str]:
    """Merge domains from multiple input files, optionally applying allowlist.
    
    Args:
        input_files: List of paths to blocklist files (any supported format)
        allowlist_file: Optional path to file with domains to exclude
        
    Returns:
        Merged, deduplicated domain set
    """
    merged: set[str] = set()
    
    for path in input_files:
        if path.exists():
            domains = parse_file_to_set(path)
            merged.update(domains)
    
    if allowlist_file and allowlist_file.exists():
        allowlist = parse_file_to_set(allowlist_file)
        merged = apply_allowlist(merged, allowlist)
    
    return merged


def count_by_tld(domains: set[str]) -> dict[str, int]:
    """Count domains grouped by TLD.
    
    Useful for statistics and detecting anomalies.
    
    Args:
        domains: Set of domains
        
    Returns:
        Dictionary mapping TLD to count
    """
    tld_counts: dict[str, int] = {}
    
    for domain in domains:
        parts = domain.rsplit('.', 1)
        if len(parts) == 2:
            tld = parts[1].lower()
            tld_counts[tld] = tld_counts.get(tld, 0) + 1
    
    return tld_counts


def remove_subdomains_of(domains: set[str], parent: str) -> set[str]:
    """Remove all subdomains of a given parent domain.
    
    Useful for removing entire domain trees.
    
    Args:
        domains: Set of domains
        parent: Parent domain whose subdomains should be removed
        
    Returns:
        Domain set with subdomains of parent removed
    """
    parent = parent.lower()
    suffix = "." + parent
    
    return {
        d for d in domains
        if d != parent and not d.endswith(suffix)
    }


def get_subdomains_of(domains: set[str], parent: str) -> set[str]:
    """Get all subdomains of a given parent domain.
    
    Args:
        domains: Set of domains to search
        parent: Parent domain to find subdomains for
        
    Returns:
        Set of domains that are subdomains of parent
    """
    parent = parent.lower()
    suffix = "." + parent
    
    return {d for d in domains if d.endswith(suffix)}


def collapse_subdomains(domains: set[str], threshold: int = 10) -> set[str]:
    """Collapse excessive subdomains to parent domain.
    
    If a domain has more than `threshold` subdomains blocked,
    consider blocking the parent domain instead.
    
    This is an OPTIONAL optimization - use with care as it may
    cause false positives.
    
    Args:
        domains: Set of domains
        threshold: Minimum subdomains before collapsing
        
    Returns:
        Domain set with some subdomains collapsed to parents
    """
    # Get unique second-level domains (rough approximation)
    parent_counts: dict[str, int] = {}
    
    for domain in domains:
        parts = domain.split('.')
        if len(parts) >= 2:
            # Get last two parts as parent approximation
            parent = '.'.join(parts[-2:])
            parent_counts[parent] = parent_counts.get(parent, 0) + 1
    
    # Find parents exceeding threshold
    hot_parents = {p for p, c in parent_counts.items() if c >= threshold}
    
    # Remove subdomains and keep hot parents
    result = set()
    for domain in domains:
        parts = domain.split('.')
        if len(parts) >= 2:
            parent = '.'.join(parts[-2:])
            if parent in hot_parents:
                result.add(parent)
            else:
                result.add(domain)
        else:
            result.add(domain)
    
    return result
