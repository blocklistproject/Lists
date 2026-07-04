"""Domain normalization utilities for Block List Project."""

from pathlib import Path
from typing import Set


def normalize_line(line: str) -> str | None:
    """Normalize a line from any blocklist format to a plain domain.
    
    Supported formats:
    - hosts: 0.0.0.0 domain.com
    - domains: domain.com
    - adguard: ||domain.com^
    - dnsmasq: server=/domain.com/
    
    Args:
        line: Line from a blocklist file
        
    Returns:
        Normalized domain or None if line is invalid/empty
    """
    line = line.strip().lower()
    
    if not line or line.startswith('#'):
        return None
    
    # hosts format: 0.0.0.0 domain.com or 127.0.0.1 domain.com
    if line.startswith('0.0.0.0 ') or line.startswith('127.0.0.1 '):
        parts = line.split()
        if len(parts) >= 2:
            return parts[1]
    
    # adguard format: ||domain.com^
    elif line.startswith('||') and line.endswith('^'):
        return line[2:-1]
    
    # dnsmasq format: server=/domain.com/
    elif line.startswith('server=/') and line.endswith('/'):
        return line[8:-1]
    
    # plain domain format
    else:
        # Remove any trailing comments
        if ' #' in line:
            line = line.split(' #')[0].strip()
        if '\t#' in line:
            line = line.split('\t#')[0].strip()
        
        # Basic domain validation (contains at least one dot, no spaces)
        if '.' in line and ' ' not in line:
            return line
    
    return None


def parse_file_to_set(filepath: Path) -> Set[str]:
    """Parse a blocklist file and return a set of normalized domains.
    
    Args:
        filepath: Path to the blocklist file
        
    Returns:
        Set of normalized domain names
    """
    domains = set()
    
    if not filepath.exists():
        return domains
    
    with filepath.open('r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            domain = normalize_line(line)
            if domain:
                domains.add(domain)
    
    return domains
