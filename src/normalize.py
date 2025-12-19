"""Normalize various blocklist formats to canonical domain-only format.

Supported input formats:
- hosts: "0.0.0.0 domain.com" or "127.0.0.1 domain.com"
- adguard: "||domain.com^"
- dnsmasq: "server=/domain.com/" or "address=/domain.com/0.0.0.0"
- domains: plain "domain.com"

Output: Set of lowercase domain strings
"""

import re
from pathlib import Path
from typing import Iterator


# Regex patterns for different formats
HOSTS_PATTERN = re.compile(r'^(?:0\.0\.0\.0|127\.0\.0\.1)\s+(.+)$')
ADGUARD_PATTERN = re.compile(r'^\|\|(.+)\^$')
DNSMASQ_SERVER_PATTERN = re.compile(r'^server=/(.+)/$')
DNSMASQ_ADDRESS_PATTERN = re.compile(r'^address=/(.+)/(?:0\.0\.0\.0|127\.0\.0\.1|#)?$')
# Domain validation: allow underscore at start (for domains like _thums.ero-advertising.com)
# Allow punycode TLDs (xn--xxx) which contain digits and hyphens
DOMAIN_PATTERN = re.compile(r'^[a-zA-Z0-9_][-a-zA-Z0-9._]*\.[a-zA-Z0-9-]{2,}$')


def normalize_line(line: str) -> str | None:
    """Normalize a single line to a domain, or None if not a domain line.
    
    Args:
        line: A single line from a blocklist file
        
    Returns:
        Normalized lowercase domain, or None if line is a comment/empty/invalid
    """
    line = line.strip()
    
    # Skip empty lines
    if not line:
        return None
    
    # Skip comments (various formats)
    if line.startswith('#') or line.startswith('!'):
        return None
    
    # Try hosts format: "0.0.0.0 domain" or "127.0.0.1 domain"
    match = HOSTS_PATTERN.match(line)
    if match:
        return match.group(1).lower().strip()
    
    # Try AdGuard format: "||domain^"
    match = ADGUARD_PATTERN.match(line)
    if match:
        return match.group(1).lower().strip()
    
    # Try dnsmasq server format: "server=/domain/"
    match = DNSMASQ_SERVER_PATTERN.match(line)
    if match:
        return match.group(1).lower().strip()
    
    # Try dnsmasq address format: "address=/domain/0.0.0.0"
    match = DNSMASQ_ADDRESS_PATTERN.match(line)
    if match:
        return match.group(1).lower().strip()
    
    # Try plain domain format
    line_lower = line.lower()
    if DOMAIN_PATTERN.match(line_lower):
        return line_lower
    
    return None


def normalize_file(file_path: Path) -> Iterator[str]:
    """Normalize all lines in a file to domains.
    
    Args:
        file_path: Path to blocklist file
        
    Yields:
        Normalized domains (non-empty, non-comment lines)
    """
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            domain = normalize_line(line)
            if domain:
                yield domain


def normalize_content(content: str) -> Iterator[str]:
    """Normalize content string to domains.
    
    Args:
        content: Blocklist content as string
        
    Yields:
        Normalized domains
    """
    for line in content.splitlines():
        domain = normalize_line(line)
        if domain:
            yield domain


def parse_file_to_set(file_path: Path) -> set[str]:
    """Parse a blocklist file and return unique domains as a set.
    
    Args:
        file_path: Path to blocklist file
        
    Returns:
        Set of unique normalized domains
    """
    return set(normalize_file(file_path))


def detect_format(file_path: Path) -> str:
    """Detect the format of a blocklist file by sampling first non-comment lines.
    
    Args:
        file_path: Path to blocklist file
        
    Returns:
        Format name: 'hosts', 'adguard', 'dnsmasq', 'domains', or 'unknown'
    """
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            line = line.strip()
            
            # Skip empty and comment lines
            if not line or line.startswith('#') or line.startswith('!'):
                continue
            
            # Check formats
            if HOSTS_PATTERN.match(line):
                return 'hosts'
            if ADGUARD_PATTERN.match(line):
                return 'adguard'
            if DNSMASQ_SERVER_PATTERN.match(line) or DNSMASQ_ADDRESS_PATTERN.match(line):
                return 'dnsmasq'
            if DOMAIN_PATTERN.match(line):
                return 'domains'
            
            return 'unknown'
    
    return 'unknown'


def extract_allowlist_from_hosts(file_path: Path) -> set[str]:
    """Extract commented-out domains (allowlist) from hosts format file.
    
    In the current format, allowlisted domains are:
    "# 0.0.0.0 domain.com reason for allowlist"
    
    Args:
        file_path: Path to hosts format file
        
    Returns:
        Set of allowlisted domains
    """
    allowlist = set()
    pattern = re.compile(r'^#\s*0\.0\.0\.0\s+(\S+)')
    
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            match = pattern.match(line.strip())
            if match:
                allowlist.add(match.group(1).lower())
    
    return allowlist
