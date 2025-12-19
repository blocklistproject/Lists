"""Output formatters for various blocklist formats.

This module generates output in different formats:
- hosts: Standard hosts file format (0.0.0.0 domain)
- domains: Plain domain list (one per line)
- adguard: AdGuard DNS filter format (||domain^)
- dnsmasq: dnsmasq configuration format (server=/domain/)

Each format includes appropriate headers and metadata.
"""

from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


def _generate_header(
    title: str,
    description: str,
    url: str,
    count: int,
    format_name: str,
) -> list[str]:
    """Generate a standard header for blocklist files.
    
    Args:
        title: List title
        description: List description
        url: URL where the list is hosted
        count: Number of domains
        format_name: Format identifier
        
    Returns:
        List of header lines (with # prefix)
    """
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    
    return [
        f"# Title: {title}",
        f"# Description: {description}",
        f"# Homepage: https://github.com/blocklistproject/Lists",
        f"# License: MIT",
        f"# Last modified: {now}",
        f"# Format: {format_name}",
        f"# Entries: {count:,}",
        f"# URL: {url}",
        "#",
        "# This list is maintained by The Block List Project",
        "# https://github.com/blocklistproject/Lists",
        "#",
        "",
    ]


def format_hosts(
    domains: Iterable[str],
    title: str = "Block List",
    description: str = "Domain blocklist",
    url: str = "",
) -> str:
    """Format domains as a hosts file.
    
    Format: 0.0.0.0 domain.com
    
    Args:
        domains: Iterable of domain strings (should be sorted)
        title: List title for header
        description: List description for header
        url: URL for header
        
    Returns:
        Complete hosts file content as string
    """
    domain_list = list(domains)
    count = len(domain_list)
    
    lines = _generate_header(title, description, url, count, "hosts")
    
    for domain in domain_list:
        lines.append(f"0.0.0.0 {domain}")
    
    return "\n".join(lines) + "\n"


def format_domains(
    domains: Iterable[str],
    title: str = "Block List",
    description: str = "Domain blocklist",
    url: str = "",
) -> str:
    """Format domains as a plain list (newline-separated).
    
    Format: domain.com (one per line)
    
    Args:
        domains: Iterable of domain strings (should be sorted)
        title: List title for header
        description: List description for header
        url: URL for header
        
    Returns:
        Complete domain list content as string
    """
    domain_list = list(domains)
    count = len(domain_list)
    
    lines = _generate_header(title, description, url, count, "domains")
    lines.extend(domain_list)
    
    return "\n".join(lines) + "\n"


def format_adguard(
    domains: Iterable[str],
    title: str = "Block List",
    description: str = "Domain blocklist",
    url: str = "",
) -> str:
    """Format domains as AdGuard DNS filter rules.
    
    Format: ||domain.com^
    
    Args:
        domains: Iterable of domain strings (should be sorted)
        title: List title for header
        description: List description for header
        url: URL for header
        
    Returns:
        Complete AdGuard filter content as string
    """
    domain_list = list(domains)
    count = len(domain_list)
    
    # AdGuard format uses ! for comments
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    
    lines = [
        f"! Title: {title}",
        f"! Description: {description}",
        f"! Homepage: https://github.com/blocklistproject/Lists",
        f"! License: MIT",
        f"! Last modified: {now}",
        f"! Format: AdGuard",
        f"! Entries: {count:,}",
        f"! URL: {url}",
        "!",
        "! This list is maintained by The Block List Project",
        "! https://github.com/blocklistproject/Lists",
        "!",
        "",
    ]
    
    for domain in domain_list:
        lines.append(f"||{domain}^")
    
    return "\n".join(lines) + "\n"


def format_dnsmasq(
    domains: Iterable[str],
    title: str = "Block List",
    description: str = "Domain blocklist",
    url: str = "",
) -> str:
    """Format domains as dnsmasq server configuration.
    
    Format: server=/domain.com/
    
    This tells dnsmasq to return NXDOMAIN for these domains.
    
    Args:
        domains: Iterable of domain strings (should be sorted)
        title: List title for header
        description: List description for header
        url: URL for header
        
    Returns:
        Complete dnsmasq config content as string
    """
    domain_list = list(domains)
    count = len(domain_list)
    
    lines = _generate_header(title, description, url, count, "dnsmasq")
    
    for domain in domain_list:
        lines.append(f"server=/{domain}/")
    
    return "\n".join(lines) + "\n"


# Format function registry for dynamic selection
FORMATTERS = {
    "hosts": format_hosts,
    "domains": format_domains,
    "adguard": format_adguard,
    "dnsmasq": format_dnsmasq,
}


def format_output(
    domains: Iterable[str],
    format_name: str,
    title: str = "Block List",
    description: str = "Domain blocklist",
    url: str = "",
) -> str:
    """Format domains using the specified formatter.
    
    Args:
        domains: Iterable of domain strings
        format_name: One of 'hosts', 'domains', 'adguard', 'dnsmasq'
        title: List title for header
        description: List description for header
        url: URL for header
        
    Returns:
        Formatted output string
        
    Raises:
        ValueError: If format_name is not recognized
    """
    if format_name not in FORMATTERS:
        valid = ", ".join(FORMATTERS.keys())
        raise ValueError(f"Unknown format '{format_name}'. Valid: {valid}")
    
    return FORMATTERS[format_name](domains, title, description, url)


def write_output(
    domains: Iterable[str],
    output_path: Path,
    format_name: str,
    title: str = "Block List",
    description: str = "Domain blocklist",
    url: str = "",
) -> int:
    """Write formatted output to a file.
    
    Args:
        domains: Iterable of domain strings
        output_path: Path to write output to
        format_name: One of 'hosts', 'domains', 'adguard', 'dnsmasq'
        title: List title for header
        description: List description for header
        url: URL for header
        
    Returns:
        Number of domains written
    """
    # Convert to list to get count and allow multiple iterations
    domain_list = list(domains)
    
    content = format_output(domain_list, format_name, title, description, url)
    
    # Ensure parent directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    output_path.write_text(content, encoding="utf-8")
    
    return len(domain_list)


def get_format_for_path(path: Path) -> str | None:
    """Infer format from file path based on directory structure.
    
    Uses the Block List Project's directory conventions:
    - Root *.txt files -> hosts
    - adguard/*-ags.txt -> adguard
    - alt-version/*-nl.txt -> domains
    - dnsmasq-version/*-dnsmasq.txt -> dnsmasq
    
    Args:
        path: File path to analyze
        
    Returns:
        Format name or None if can't determine
    """
    # Check parent directory first
    parent = path.parent.name
    
    if parent == "adguard":
        return "adguard"
    elif parent == "alt-version":
        return "domains"
    elif parent == "dnsmasq-version":
        return "dnsmasq"
    
    # Check if it's in the root (no subdirectory)
    if path.parent == path.parent.parent or parent == "":
        return "hosts"
    
    # Check filename patterns
    name = path.name
    if "-ags.txt" in name:
        return "adguard"
    elif "-nl.txt" in name:
        return "domains"
    elif "-dnsmasq.txt" in name:
        return "dnsmasq"
    
    return None
