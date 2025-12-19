"""Tests for normalize module."""

from pathlib import Path

from src.normalize import (
    normalize_line,
    normalize_content,
    parse_file_to_set,
    detect_format,
    extract_allowlist_from_hosts,
)


class TestNormalizeLine:
    """Tests for normalize_line function."""
    
    # Hosts format tests
    def test_hosts_format_0000(self):
        """Should parse 0.0.0.0 hosts format."""
        assert normalize_line("0.0.0.0 example.com") == "example.com"
    
    def test_hosts_format_127(self):
        """Should parse 127.0.0.1 hosts format."""
        assert normalize_line("127.0.0.1 example.com") == "example.com"
    
    def test_hosts_with_extra_spaces(self):
        """Should handle extra whitespace."""
        assert normalize_line("0.0.0.0    example.com  ") == "example.com"
    
    # AdGuard format tests
    def test_adguard_format(self):
        """Should parse AdGuard format."""
        assert normalize_line("||example.com^") == "example.com"
    
    def test_adguard_with_subdomain(self):
        """Should parse AdGuard with subdomain."""
        assert normalize_line("||ads.example.com^") == "ads.example.com"
    
    # dnsmasq format tests
    def test_dnsmasq_server_format(self):
        """Should parse dnsmasq server format."""
        assert normalize_line("server=/example.com/") == "example.com"
    
    def test_dnsmasq_address_format(self):
        """Should parse dnsmasq address format."""
        assert normalize_line("address=/example.com/0.0.0.0") == "example.com"
    
    def test_dnsmasq_address_with_hash(self):
        """Should parse dnsmasq address with # (NXDOMAIN)."""
        assert normalize_line("address=/example.com/#") == "example.com"
    
    # Plain domain format tests
    def test_plain_domain(self):
        """Should parse plain domain."""
        assert normalize_line("example.com") == "example.com"
    
    def test_plain_subdomain(self):
        """Should parse plain subdomain."""
        assert normalize_line("ads.tracker.example.com") == "ads.tracker.example.com"
    
    # Case normalization
    def test_lowercase_conversion(self):
        """Should convert to lowercase."""
        assert normalize_line("0.0.0.0 EXAMPLE.COM") == "example.com"
        assert normalize_line("||EXAMPLE.COM^") == "example.com"
    
    # Skip lines
    def test_skip_empty_line(self):
        """Should return None for empty lines."""
        assert normalize_line("") is None
        assert normalize_line("   ") is None
    
    def test_skip_hash_comment(self):
        """Should return None for # comments."""
        assert normalize_line("# This is a comment") is None
        assert normalize_line("  # Indented comment") is None
    
    def test_skip_bang_comment(self):
        """Should return None for ! comments (AdGuard)."""
        assert normalize_line("! This is an AdGuard comment") is None
    
    def test_skip_invalid_domain(self):
        """Should return None for invalid domains."""
        assert normalize_line("not a domain") is None
        assert normalize_line("http://example.com") is None


class TestNormalizeContent:
    """Tests for normalize_content function."""
    
    def test_mixed_format_content(self):
        """Should normalize mixed format content."""
        content = """
# Comment line
0.0.0.0 ads.example.com
||tracker.example.com^
server=/analytics.example.com/
plain.example.com
"""
        domains = list(normalize_content(content))
        assert "ads.example.com" in domains
        assert "tracker.example.com" in domains
        assert "analytics.example.com" in domains
        assert "plain.example.com" in domains
        assert len(domains) == 4


class TestParseFileToSet:
    """Tests for parse_file_to_set function."""
    
    def test_parse_ads_file(self):
        """Should parse the actual ads.txt file."""
        ads_path = Path(__file__).parent.parent / "ads.txt"
        if ads_path.exists():
            domains = parse_file_to_set(ads_path)
            assert len(domains) > 100000  # ads.txt has ~154k entries
            assert "0.fls.doubleclick.net" in domains
    
    def test_parse_adguard_file(self):
        """Should parse AdGuard format file."""
        adguard_path = Path(__file__).parent.parent / "adguard" / "ads-ags.txt"
        if adguard_path.exists():
            domains = parse_file_to_set(adguard_path)
            assert len(domains) > 100000
            assert "0.fls.doubleclick.net" in domains
    
    def test_parse_dnsmasq_file(self):
        """Should parse dnsmasq format file."""
        dnsmasq_path = Path(__file__).parent.parent / "dnsmasq-version" / "ads-dnsmasq.txt"
        if dnsmasq_path.exists():
            domains = parse_file_to_set(dnsmasq_path)
            assert len(domains) > 100000
            assert "0.fls.doubleclick.net" in domains
    
    def test_all_formats_produce_same_domains(self):
        """All format versions should produce identical domain sets."""
        base = Path(__file__).parent.parent
        hosts_path = base / "ads.txt"
        adguard_path = base / "adguard" / "ads-ags.txt"
        dnsmasq_path = base / "dnsmasq-version" / "ads-dnsmasq.txt"
        nl_path = base / "alt-version" / "ads-nl.txt"
        
        if all(p.exists() for p in [hosts_path, adguard_path, dnsmasq_path, nl_path]):
            hosts_domains = parse_file_to_set(hosts_path)
            adguard_domains = parse_file_to_set(adguard_path)
            dnsmasq_domains = parse_file_to_set(dnsmasq_path)
            nl_domains = parse_file_to_set(nl_path)
            
            # All should have the same count
            assert len(hosts_domains) == len(adguard_domains)
            assert len(hosts_domains) == len(dnsmasq_domains)
            assert len(hosts_domains) == len(nl_domains)
            
            # All should be identical sets
            assert hosts_domains == adguard_domains
            assert hosts_domains == dnsmasq_domains
            assert hosts_domains == nl_domains


class TestDetectFormat:
    """Tests for detect_format function."""
    
    def test_detect_hosts_format(self):
        """Should detect hosts format."""
        path = Path(__file__).parent.parent / "ads.txt"
        if path.exists():
            assert detect_format(path) == "hosts"
    
    def test_detect_adguard_format(self):
        """Should detect AdGuard format."""
        path = Path(__file__).parent.parent / "adguard" / "ads-ags.txt"
        if path.exists():
            assert detect_format(path) == "adguard"
    
    def test_detect_dnsmasq_format(self):
        """Should detect dnsmasq format."""
        path = Path(__file__).parent.parent / "dnsmasq-version" / "ads-dnsmasq.txt"
        if path.exists():
            assert detect_format(path) == "dnsmasq"
    
    def test_detect_domains_format(self):
        """Should detect plain domains format."""
        path = Path(__file__).parent.parent / "alt-version" / "ads-nl.txt"
        if path.exists():
            assert detect_format(path) == "domains"


class TestExtractAllowlist:
    """Tests for extract_allowlist_from_hosts function."""
    
    def test_extract_commented_domains(self):
        """Should extract domains from # 0.0.0.0 comments."""
        # Create temp content to test
        from tempfile import NamedTemporaryFile
        content = """# Header comment
0.0.0.0 blocked.com
# 0.0.0.0 allowed.com this was allowlisted
# 0.0.0.0 also-allowed.com another reason
0.0.0.0 another-blocked.com
"""
        with NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(content)
            temp_path = Path(f.name)
        
        try:
            allowlist = extract_allowlist_from_hosts(temp_path)
            assert "allowed.com" in allowlist
            assert "also-allowed.com" in allowlist
            assert "blocked.com" not in allowlist
            assert len(allowlist) == 2
        finally:
            temp_path.unlink()
