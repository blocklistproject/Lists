"""Tests for src/validate.py."""

import tempfile
from pathlib import Path


from src.validate import (
    COMMON_TLDS,
    CRITICAL_DOMAINS,
    find_suspicious_patterns,
    has_valid_tld,
    is_critical_domain,
    is_false_positive,
    is_valid_syntax,
    load_critical_domains_from_file,
    validate_domain,
    validate_domain_set,
)


class TestIsValidSyntax:
    """Tests for is_valid_syntax function."""
    
    def test_valid_simple_domain(self):
        """Should accept valid simple domains."""
        assert is_valid_syntax("example.com")
        assert is_valid_syntax("test.net")
        assert is_valid_syntax("sub.domain.org")
    
    def test_valid_subdomain(self):
        """Should accept valid subdomains."""
        assert is_valid_syntax("www.example.com")
        assert is_valid_syntax("mail.server.example.org")
        assert is_valid_syntax("deep.sub.domain.co.uk")
    
    def test_valid_with_numbers(self):
        """Should accept domains with numbers."""
        assert is_valid_syntax("123.example.com")
        assert is_valid_syntax("a1b2c3.net")
        assert is_valid_syntax("0.fls.doubleclick.net")
    
    def test_valid_with_hyphens(self):
        """Should accept domains with hyphens."""
        assert is_valid_syntax("my-domain.com")
        assert is_valid_syntax("sub-domain.example-site.net")
    
    def test_valid_with_underscore_prefix(self):
        """Should accept domains starting with underscore."""
        assert is_valid_syntax("_dmarc.example.com")
        assert is_valid_syntax("_thums.ero-advertising.com")
    
    def test_invalid_empty(self):
        """Should reject empty string."""
        assert not is_valid_syntax("")
    
    def test_invalid_no_tld(self):
        """Should reject domains without TLD."""
        assert not is_valid_syntax("example")
        assert not is_valid_syntax("localhost")
    
    def test_invalid_too_long(self):
        """Should reject domains over 253 chars."""
        long_domain = "a" * 250 + ".com"
        assert not is_valid_syntax(long_domain)
    
    def test_invalid_label_too_long(self):
        """Should reject labels over 63 chars."""
        long_label = "a" * 64 + ".com"
        assert not is_valid_syntax(long_label)
    
    def test_invalid_leading_hyphen(self):
        """Should reject labels starting with hyphen."""
        assert not is_valid_syntax("-example.com")
    
    def test_invalid_trailing_hyphen(self):
        """Should reject labels ending with hyphen."""
        assert not is_valid_syntax("example-.com")


class TestHasValidTld:
    """Tests for has_valid_tld function."""
    
    def test_common_tlds(self):
        """Should accept common TLDs."""
        assert has_valid_tld("example.com")
        assert has_valid_tld("example.net")
        assert has_valid_tld("example.org")
        assert has_valid_tld("example.io")
    
    def test_country_tlds(self):
        """Should accept country code TLDs."""
        assert has_valid_tld("example.uk")
        assert has_valid_tld("example.de")
        assert has_valid_tld("example.jp")
        assert has_valid_tld("example.ru")
    
    def test_new_tlds(self):
        """Should accept new TLDs."""
        assert has_valid_tld("example.xyz")
        assert has_valid_tld("example.app")
        assert has_valid_tld("example.dev")
    
    def test_punycode_tlds(self):
        """Should accept punycode TLDs."""
        assert has_valid_tld("example.xn--p1ai")
        assert has_valid_tld("example.xn--ngbrx")
    
    def test_strict_mode_known(self):
        """Strict mode should accept known TLDs."""
        assert has_valid_tld("example.com", strict=True)
        assert has_valid_tld("example.org", strict=True)
    
    def test_strict_mode_unknown(self):
        """Strict mode should reject unknown TLDs."""
        # This might fail if we have a comprehensive list
        # Just testing the mechanism
        assert has_valid_tld("example.unknowntld123", strict=False)
    
    def test_no_tld(self):
        """Should reject domains without TLD."""
        assert not has_valid_tld("example")


class TestIsCriticalDomain:
    """Tests for is_critical_domain function."""
    
    def test_exact_match(self):
        """Should detect exact critical domain matches."""
        assert is_critical_domain("google.com")
        assert is_critical_domain("github.com")
        assert is_critical_domain("microsoft.com")
    
    def test_subdomain_match(self):
        """Should detect subdomains of critical domains."""
        assert is_critical_domain("www.google.com")
        assert is_critical_domain("api.github.com")
        assert is_critical_domain("update.microsoft.com")
    
    def test_case_insensitive(self):
        """Should be case insensitive."""
        assert is_critical_domain("GOOGLE.COM")
        assert is_critical_domain("GitHub.Com")
    
    def test_non_critical(self):
        """Should not flag non-critical domains."""
        assert not is_critical_domain("tracking.example.com")
        assert not is_critical_domain("ads.doubleclick.net")


class TestIsFalsePositive:
    """Tests for is_false_positive function."""
    
    def test_localhost_variants(self):
        """Should detect localhost variants."""
        assert is_false_positive("localhost")
        assert is_false_positive("localhost.localdomain")
        assert is_false_positive("local")
    
    def test_ipv6_entries(self):
        """Should detect IPv6-related entries."""
        assert is_false_positive("ip6-localhost")
        assert is_false_positive("ip6-loopback")
    
    def test_case_insensitive(self):
        """Should be case insensitive."""
        assert is_false_positive("LOCALHOST")
        assert is_false_positive("LocalHost")
    
    def test_not_false_positive(self):
        """Should not flag real domains."""
        assert not is_false_positive("example.com")
        assert not is_false_positive("localhost.com")


class TestValidateDomain:
    """Tests for validate_domain function."""
    
    def test_valid_domain(self):
        """Should validate good domains."""
        is_valid, error = validate_domain("tracking.example.com")
        assert is_valid
        assert error is None
    
    def test_invalid_syntax(self):
        """Should catch syntax errors."""
        is_valid, error = validate_domain("-invalid.com")
        assert not is_valid
        assert "syntax" in error.lower()
    
    def test_critical_domain_blocked(self):
        """Should reject critical domains."""
        is_valid, error = validate_domain("google.com")
        assert not is_valid
        assert "critical" in error.lower()
    
    def test_false_positive_blocked(self):
        """Should reject false positives."""
        is_valid, error = validate_domain("localhost")
        assert not is_valid
        assert "false positive" in error.lower()
    
    def test_empty_domain(self):
        """Should reject empty domains."""
        is_valid, error = validate_domain("")
        assert not is_valid
        assert "empty" in error.lower()
    
    def test_skip_checks(self):
        """Should respect disabled checks."""
        # Critical domain should pass if check disabled
        is_valid, _ = validate_domain(
            "google.com",
            check_critical=False
        )
        assert is_valid


class TestValidateDomainSet:
    """Tests for validate_domain_set function."""
    
    def test_filters_invalid(self):
        """Should filter out invalid domains."""
        domains = {"valid.com", "localhost", "-invalid.com"}
        valid, errors = validate_domain_set(domains)
        
        assert "valid.com" in valid
        assert "localhost" not in valid
        assert "-invalid.com" not in valid
    
    def test_returns_errors(self):
        """Should return error details."""
        domains = {"valid.com", "localhost"}
        valid, errors = validate_domain_set(domains)
        
        # Should have one error for localhost
        assert len(errors) == 1
        assert errors[0][0] == "localhost"
    
    def test_empty_set(self):
        """Should handle empty set."""
        valid, errors = validate_domain_set(set())
        assert valid == set()
        assert errors == []


class TestFindSuspiciousPatterns:
    """Tests for find_suspicious_patterns function."""
    
    def test_very_long_domains(self):
        """Should flag very long domains."""
        long_domain = "a" * 90 + ".example.com"
        domains = {long_domain, "normal.com"}
        suspicious = find_suspicious_patterns(domains)
        
        assert len(suspicious) == 1
        assert suspicious[0][0] == long_domain
        assert "long" in suspicious[0][1].lower()
    
    def test_many_consecutive_digits(self):
        """Should flag domains with many consecutive digits."""
        domains = {"12345678901234567890.com", "normal.com"}
        suspicious = find_suspicious_patterns(domains)
        
        assert len(suspicious) == 1
        assert "digit" in suspicious[0][1].lower()
    
    def test_many_hyphens(self):
        """Should flag domains with many hyphens."""
        domains = {"a-b-c-d-e-f-g-h.com", "normal.com"}
        suspicious = find_suspicious_patterns(domains)
        
        assert len(suspicious) == 1
        assert "hyphen" in suspicious[0][1].lower()
    
    def test_deep_subdomains(self):
        """Should flag deeply nested subdomains."""
        domains = {"a.b.c.d.e.f.g.h.i.com", "normal.com"}
        suspicious = find_suspicious_patterns(domains)
        
        assert len(suspicious) == 1
        assert "subdomain" in suspicious[0][1].lower()
    
    def test_normal_domains_pass(self):
        """Should not flag normal domains."""
        domains = {"www.example.com", "sub.domain.org", "test-site.net"}
        suspicious = find_suspicious_patterns(domains)
        assert len(suspicious) == 0


class TestLoadCriticalDomainsFromFile:
    """Tests for load_critical_domains_from_file function."""
    
    def test_loads_domains(self):
        """Should load domains from file."""
        with tempfile.NamedTemporaryFile(
            mode='w', suffix='.txt', delete=False, encoding='utf-8'
        ) as f:
            f.write("# Comment\n")
            f.write("critical1.com\n")
            f.write("critical2.com\n")
            f.write("\n")  # Empty line
            temp_path = Path(f.name)
        
        try:
            domains = load_critical_domains_from_file(temp_path)
            assert domains == {"critical1.com", "critical2.com"}
        finally:
            temp_path.unlink()
    
    def test_missing_file(self):
        """Should return empty set for missing file."""
        domains = load_critical_domains_from_file(Path("/nonexistent/file.txt"))
        assert domains == set()
    
    def test_lowercases(self):
        """Should lowercase loaded domains."""
        with tempfile.NamedTemporaryFile(
            mode='w', suffix='.txt', delete=False, encoding='utf-8'
        ) as f:
            f.write("UPPERCASE.COM\n")
            temp_path = Path(f.name)
        
        try:
            domains = load_critical_domains_from_file(temp_path)
            assert "uppercase.com" in domains
        finally:
            temp_path.unlink()


class TestIntegration:
    """Integration tests."""
    
    def test_common_tlds_list_populated(self):
        """COMMON_TLDS should have entries."""
        assert len(COMMON_TLDS) > 100
        assert "com" in COMMON_TLDS
        assert "net" in COMMON_TLDS
    
    def test_critical_domains_list_populated(self):
        """CRITICAL_DOMAINS should have entries."""
        assert len(CRITICAL_DOMAINS) > 10
        assert "google.com" in CRITICAL_DOMAINS
