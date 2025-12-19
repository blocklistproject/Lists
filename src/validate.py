"""Validate domains against various criteria.

This module provides validation functions to ensure blocklist quality:
- TLD validation (is this a real TLD?)
- Poisoning detection (critical domains that should never be blocked)
- Syntax validation (is this a valid domain format?)
"""

import re
from pathlib import Path

# Well-known TLDs for validation (subset, extensible)
# In production, consider using tldextract or the PSL
COMMON_TLDS = {
    # Generic TLDs
    "com", "net", "org", "info", "biz", "name", "pro", "aero", "asia",
    "cat", "coop", "edu", "gov", "int", "jobs", "mil", "mobi", "museum",
    "tel", "travel", "xxx", "app", "dev", "io", "co", "ai", "me", "tv",
    "fm", "ws", "cc", "to", "ly", "gl", "gg", "vc", "sh", "la", "pw",
    "club", "online", "site", "store", "tech", "top", "xyz", "work",
    "live", "life", "link", "click", "help", "news", "blog", "one",
    "shop", "world", "zone", "space", "today", "email", "network",
    "download", "bid", "review", "stream", "win", "racing", "date",
    "trade", "science", "party", "faith", "cricket", "webcam", "loan",
    "accountant", "men", "gdn", "fun", "vip", "wang", "icu",
    
    # Country code TLDs
    "ac", "ad", "ae", "af", "ag", "al", "am", "ao", "aq", "ar", "as",
    "at", "au", "aw", "ax", "az", "ba", "bb", "bd", "be", "bf", "bg",
    "bh", "bi", "bj", "bm", "bn", "bo", "br", "bs", "bt", "bv", "bw",
    "by", "bz", "ca", "cd", "cf", "cg", "ch", "ci", "ck", "cl", "cm",
    "cn", "co", "cr", "cu", "cv", "cw", "cx", "cy", "cz", "de", "dj",
    "dk", "dm", "do", "dz", "ec", "ee", "eg", "er", "es", "et", "eu",
    "fi", "fj", "fk", "fm", "fo", "fr", "ga", "gb", "gd", "ge", "gf",
    "gg", "gh", "gi", "gl", "gm", "gn", "gp", "gq", "gr", "gs", "gt",
    "gu", "gw", "gy", "hk", "hm", "hn", "hr", "ht", "hu", "id", "ie",
    "il", "im", "in", "io", "iq", "ir", "is", "it", "je", "jm", "jo",
    "jp", "ke", "kg", "kh", "ki", "km", "kn", "kp", "kr", "kw", "ky",
    "kz", "la", "lb", "lc", "li", "lk", "lr", "ls", "lt", "lu", "lv",
    "ly", "ma", "mc", "md", "me", "mg", "mh", "mk", "ml", "mm", "mn",
    "mo", "mp", "mq", "mr", "ms", "mt", "mu", "mv", "mw", "mx", "my",
    "mz", "na", "nc", "ne", "nf", "ng", "ni", "nl", "no", "np", "nr",
    "nu", "nz", "om", "pa", "pe", "pf", "pg", "ph", "pk", "pl", "pm",
    "pn", "pr", "ps", "pt", "pw", "py", "qa", "re", "ro", "rs", "ru",
    "rw", "sa", "sb", "sc", "sd", "se", "sg", "sh", "si", "sj", "sk",
    "sl", "sm", "sn", "so", "sr", "ss", "st", "su", "sv", "sx", "sy",
    "sz", "tc", "td", "tf", "tg", "th", "tj", "tk", "tl", "tm", "tn",
    "to", "tr", "tt", "tv", "tw", "tz", "ua", "ug", "uk", "us", "uy",
    "uz", "va", "vc", "ve", "vg", "vi", "vn", "vu", "wf", "ws", "ye",
    "yt", "za", "zm", "zw",
}

# Critical domains that should NEVER be blocked (poisoning protection)
CRITICAL_DOMAINS = {
    # OS and system updates
    "windowsupdate.com",
    "update.microsoft.com",
    "download.windowsupdate.com",
    "apple.com",
    "swscan.apple.com",
    "swcdn.apple.com",
    "itunes.apple.com",
    "appldnld.apple.com",
    "swdist.apple.com",
    "updates.cdn-apple.com",
    
    # Security and certificates
    "ocsp.digicert.com",
    "ocsp.comodoca.com",
    "ocsp.globalsign.com",
    "ocsp.usertrust.com",
    "ocsp.entrust.com",
    "crl.microsoft.com",
    "www.microsoft.com",
    "microsoft.com",
    
    # Critical infrastructure
    "google.com",
    "www.google.com",
    "googleapis.com",
    "gstatic.com",
    "github.com",
    "githubusercontent.com",
    "raw.githubusercontent.com",
    
    # Banking/finance (representative sample - users should add their own)
    "paypal.com",
    "www.paypal.com",
    
    # Authentication
    "login.microsoftonline.com",
    "login.live.com",
    "accounts.google.com",
    "oauth.net",
}

# Domains that are commonly false-positived
COMMON_FALSE_POSITIVES = {
    "localhost",
    "localhost.localdomain",
    "local",
    "broadcasthost",
    "ip6-localhost",
    "ip6-loopback",
    "ip6-localnet",
    "ip6-mcastprefix",
    "ip6-allnodes",
    "ip6-allrouters",
}

# Domain syntax pattern
DOMAIN_SYNTAX_PATTERN = re.compile(
    r'^[a-zA-Z0-9_][-a-zA-Z0-9._]*\.[a-zA-Z0-9-]{2,}$'
)


def is_valid_syntax(domain: str) -> bool:
    """Check if a domain has valid syntax.
    
    Args:
        domain: Domain string to validate
        
    Returns:
        True if syntax is valid
    """
    if not domain or len(domain) > 253:
        return False
    
    # Check each label
    labels = domain.split('.')
    if len(labels) < 2:
        return False
    
    for label in labels:
        if not label or len(label) > 63:
            return False
        # Each label must start/end with alphanumeric (not hyphen)
        if label.startswith('-') or label.endswith('-'):
            return False
    
    return bool(DOMAIN_SYNTAX_PATTERN.match(domain))


def has_valid_tld(domain: str, strict: bool = False) -> bool:
    """Check if a domain has a valid TLD.
    
    Args:
        domain: Domain string to check
        strict: If True, only accept TLDs in COMMON_TLDS list
        
    Returns:
        True if TLD is valid/known
    """
    parts = domain.rsplit('.', 1)
    if len(parts) != 2:
        return False
    
    tld = parts[1].lower()
    
    # Punycode TLDs are always considered valid
    if tld.startswith("xn--"):
        return True
    
    if strict:
        return tld in COMMON_TLDS
    
    # Non-strict: accept any TLD that looks reasonable
    return len(tld) >= 2 and tld.isalnum()


def is_critical_domain(domain: str) -> bool:
    """Check if a domain is in the critical/protected list.
    
    These domains should NEVER be blocked as it could break
    essential system functionality.
    
    Args:
        domain: Domain to check
        
    Returns:
        True if domain is critical and should not be blocked
    """
    domain_lower = domain.lower()
    
    # Exact match
    if domain_lower in CRITICAL_DOMAINS:
        return True
    
    # Check if it's a subdomain of a critical domain
    for critical in CRITICAL_DOMAINS:
        if domain_lower.endswith("." + critical):
            return True
    
    return False


def is_false_positive(domain: str) -> bool:
    """Check if a domain is a common false positive.
    
    Args:
        domain: Domain to check
        
    Returns:
        True if domain is a known false positive
    """
    return domain.lower() in COMMON_FALSE_POSITIVES


def validate_domain(
    domain: str,
    check_syntax: bool = True,
    check_tld: bool = True,
    check_critical: bool = True,
    check_false_positive: bool = True,
    strict_tld: bool = False,
) -> tuple[bool, str | None]:
    """Validate a domain against multiple criteria.
    
    Args:
        domain: Domain string to validate
        check_syntax: Validate domain syntax
        check_tld: Validate TLD is known
        check_critical: Check against critical domains
        check_false_positive: Check against false positive list
        strict_tld: Only accept TLDs in known list
        
    Returns:
        Tuple of (is_valid, error_message or None)
    """
    if not domain:
        return False, "Empty domain"
    
    domain = domain.strip().lower()
    
    if check_false_positive and is_false_positive(domain):
        return False, f"False positive: {domain}"
    
    if check_syntax and not is_valid_syntax(domain):
        return False, f"Invalid syntax: {domain}"
    
    if check_tld and not has_valid_tld(domain, strict=strict_tld):
        return False, f"Invalid TLD: {domain}"
    
    if check_critical and is_critical_domain(domain):
        return False, f"Critical domain: {domain}"
    
    return True, None


def validate_domain_set(
    domains: set[str],
    check_syntax: bool = True,
    check_tld: bool = True,
    check_critical: bool = True,
    strict_tld: bool = False,
) -> tuple[set[str], list[tuple[str, str]]]:
    """Validate a set of domains and return valid ones plus errors.
    
    Args:
        domains: Set of domains to validate
        check_syntax: Validate domain syntax
        check_tld: Validate TLD is known
        check_critical: Check against critical domains
        strict_tld: Only accept TLDs in known list
        
    Returns:
        Tuple of (valid_domains, list of (domain, error) tuples)
    """
    valid: set[str] = set()
    errors: list[tuple[str, str]] = []
    
    for domain in domains:
        is_valid, error = validate_domain(
            domain,
            check_syntax=check_syntax,
            check_tld=check_tld,
            check_critical=check_critical,
            check_false_positive=True,
            strict_tld=strict_tld,
        )
        
        if is_valid:
            valid.add(domain.lower())
        else:
            errors.append((domain, error or "Unknown error"))
    
    return valid, errors


def find_suspicious_patterns(domains: set[str]) -> list[tuple[str, str]]:
    """Find domains with suspicious patterns that may indicate issues.
    
    Args:
        domains: Set of domains to analyze
        
    Returns:
        List of (domain, reason) tuples for suspicious domains
    """
    suspicious: list[tuple[str, str]] = []
    
    for domain in domains:
        domain_lower = domain.lower()
        
        # Very long domains (often malware/phishing)
        if len(domain_lower) > 100:
            suspicious.append((domain, "Very long domain name"))
            continue
        
        # Many consecutive digits (often auto-generated)
        if re.search(r'\d{10,}', domain_lower):
            suspicious.append((domain, "Many consecutive digits"))
            continue
        
        # Many hyphens (often DGA malware)
        if domain_lower.count('-') > 5:
            suspicious.append((domain, "Many hyphens"))
            continue
        
        # Very deep subdomain nesting
        if domain_lower.count('.') > 6:
            suspicious.append((domain, "Very deep subdomain nesting"))
            continue
    
    return suspicious


def load_critical_domains_from_file(path: Path) -> set[str]:
    """Load additional critical domains from a file.
    
    File format: one domain per line, # for comments
    
    Args:
        path: Path to file
        
    Returns:
        Set of critical domains
    """
    if not path.exists():
        return set()
    
    domains: set[str] = set()
    
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                domains.add(line.lower())
    
    return domains
