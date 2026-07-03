"""Unified domain lookup across all list formats.

This module provides consistent domain checking across all blocklist formats
(hosts, domains, adguard, dnsmasq) without duplicating logic in multiple scripts.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Set

from src.logger import get_logger

logger = get_logger(__name__)


@dataclass
class DomainLocation:
    """Location of a domain in blocklists."""

    domain: str
    lists: List[str]
    formats: List[str]

    @property
    def found(self) -> bool:
        """Check if domain was found in any list."""
        return len(self.lists) > 0


def _check_hosts_format(line: str, domain: str) -> bool:
    """Check if line matches domain in hosts format (0.0.0.0 domain)."""
    if not line or line.startswith("#"):
        return False
    parts = line.strip().split()
    # Format: 0.0.0.0 domain [comment]
    return len(parts) >= 2 and parts[0] in ("0.0.0.0", "::1") and parts[1] == domain


def _check_plain_format(line: str, domain: str) -> bool:
    """Check if line matches domain in plain format (just domain name)."""
    if not line or line.startswith("#"):
        return False
    return line.strip() == domain


def _check_adguard_format(line: str, domain: str) -> bool:
    """Check if line matches domain in AdGuard format (||domain^)."""
    if not line or line.startswith("!"):
        return False
    stripped = line.strip()
    return stripped == f"||{domain}^"


def _check_dnsmasq_format(line: str, domain: str) -> bool:
    """Check if line matches domain in dnsmasq format (server=/domain/)."""
    if not line or line.startswith("#"):
        return False
    stripped = line.strip()
    return stripped == f"server=/{domain}/"


def domain_in_file(domain: str, file_path: Path, format_type: str = "hosts") -> bool:
    """Check if domain exists in a specific file.
    
    Args:
        domain: Domain to search for
        file_path: Path to file to search
        format_type: Format of the file (hosts, plain, adguard, dnsmasq)
        
    Returns:
        True if domain found, False otherwise
    """
    if not file_path.exists():
        return False
    
    # Select appropriate checker function
    checker = {
        "hosts": _check_hosts_format,
        "plain": _check_plain_format,
        "adguard": _check_adguard_format,
        "dnsmasq": _check_dnsmasq_format,
    }.get(format_type, _check_hosts_format)
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                if checker(line, domain):
                    return True
    except Exception as e:
        logger.warning(f"Error reading {file_path}: {e}")
    
    return False


def find_domain_in_lists(domain: str, base_dir: Path) -> DomainLocation:
    """Find domain across all lists and formats.
    
    Args:
        domain: Domain to search for (e.g., "example.com")
        base_dir: Base directory containing blocklists
        
    Returns:
        DomainLocation with lists and formats where domain was found
        
    Example:
        >>> from pathlib import Path
        >>> location = find_domain_in_lists("ads.example.com", Path("."))
        >>> if location.found:
        ...     print(f"Found in: {', '.join(location.lists)}")
    """
    lists_found: Set[str] = set()
    formats_found: Set[str] = set()
    
    # Define list files and their formats
    list_files = {
        "hosts": base_dir.glob("*.txt"),
        "plain": (base_dir / "alt-version").glob("*-nl.txt") if (base_dir / "alt-version").exists() else [],
        "adguard": (base_dir / "adguard").glob("*-ags.txt") if (base_dir / "adguard").exists() else [],
        "dnsmasq": (base_dir / "dnsmasq-version").glob("*-dnsmasq.txt") if (base_dir / "dnsmasq-version").exists() else [],
    }
    
    # Check hosts format (root directory .txt files)
    for file_path in list_files["hosts"]:
        # Skip special files
        if file_path.name in ("everything.txt", "dead-domains.txt", "README.txt"):
            continue
        
        if domain_in_file(domain, file_path, "hosts"):
            list_name = file_path.stem
            lists_found.add(list_name)
            formats_found.add("hosts")
    
    # Check plain domain format
    for file_path in list_files["plain"]:
        if domain_in_file(domain, file_path, "plain"):
            list_name = file_path.stem.replace("-nl", "")
            lists_found.add(list_name)
            formats_found.add("domains")
    
    # Check AdGuard format
    for file_path in list_files["adguard"]:
        if domain_in_file(domain, file_path, "adguard"):
            list_name = file_path.stem.replace("-ags", "")
            lists_found.add(list_name)
            formats_found.add("adguard")
    
    # Check dnsmasq format
    for file_path in list_files["dnsmasq"]:
        if domain_in_file(domain, file_path, "dnsmasq"):
            list_name = file_path.stem.replace("-dnsmasq", "")
            lists_found.add(list_name)
            formats_found.add("dnsmasq")
    
    return DomainLocation(
        domain=domain,
        lists=sorted(list(lists_found)),
        formats=sorted(list(formats_found)),
    )


def domain_exists(domain: str, list_name: str, base_dir: Path) -> bool:
    """Check if domain exists in a specific list.
    
    Args:
        domain: Domain to check
        list_name: Name of the list (e.g., "ads", "malware")
        base_dir: Base directory containing blocklists
        
    Returns:
        True if domain exists in the specified list, False otherwise
        
    Example:
        >>> domain_exists("tracker.example.com", "tracking", Path("."))
        True
    """
    # Check main hosts file
    hosts_file = base_dir / f"{list_name}.txt"
    if hosts_file.exists() and domain_in_file(domain, hosts_file, "hosts"):
        return True
    
    return False
