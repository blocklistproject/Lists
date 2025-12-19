"""Tests for src/format.py."""

import tempfile
from pathlib import Path

import pytest

from src.format import (
    FORMATTERS,
    format_adguard,
    format_dnsmasq,
    format_domains,
    format_hosts,
    format_output,
    get_format_for_path,
    write_output,
)


class TestFormatHosts:
    """Tests for format_hosts function."""
    
    def test_basic_format(self):
        """Should format domains in hosts format."""
        domains = ["example.com", "test.net"]
        result = format_hosts(domains)
        
        assert "0.0.0.0 example.com" in result
        assert "0.0.0.0 test.net" in result
    
    def test_includes_header(self):
        """Should include header with metadata."""
        domains = ["example.com"]
        result = format_hosts(
            domains,
            title="Test List",
            description="A test list",
            url="https://example.com/list.txt"
        )
        
        assert "# Title: Test List" in result
        assert "# Description: A test list" in result
        assert "# Entries: 1" in result
        assert "# Format: hosts" in result
    
    def test_empty_list(self):
        """Should handle empty domain list."""
        result = format_hosts([])
        assert "# Entries: 0" in result
    
    def test_preserves_order(self):
        """Should preserve domain order."""
        domains = ["z.com", "a.com", "m.com"]
        result = format_hosts(domains)
        
        lines = result.split("\n")
        domain_lines = [l for l in lines if l.startswith("0.0.0.0")]
        
        assert domain_lines[0] == "0.0.0.0 z.com"
        assert domain_lines[1] == "0.0.0.0 a.com"
        assert domain_lines[2] == "0.0.0.0 m.com"


class TestFormatDomains:
    """Tests for format_domains function."""
    
    def test_basic_format(self):
        """Should format domains as plain list."""
        domains = ["example.com", "test.net"]
        result = format_domains(domains)
        
        assert "example.com" in result
        assert "test.net" in result
        # Should NOT have hosts prefix
        assert "0.0.0.0" not in result
    
    def test_includes_header(self):
        """Should include header with metadata."""
        domains = ["example.com"]
        result = format_domains(domains, title="Test")
        
        assert "# Title: Test" in result
        assert "# Format: domains" in result


class TestFormatAdguard:
    """Tests for format_adguard function."""
    
    def test_basic_format(self):
        """Should format domains in AdGuard format."""
        domains = ["example.com", "test.net"]
        result = format_adguard(domains)
        
        assert "||example.com^" in result
        assert "||test.net^" in result
    
    def test_uses_bang_comments(self):
        """Should use ! for comments (AdGuard convention)."""
        domains = ["example.com"]
        result = format_adguard(domains, title="Test")
        
        assert "! Title: Test" in result
        # Should NOT use # comments
        lines = [l for l in result.split("\n") if l.startswith("#")]
        assert len(lines) == 0
    
    def test_includes_metadata(self):
        """Should include entry count in header."""
        domains = ["a.com", "b.com", "c.com"]
        result = format_adguard(domains)
        
        assert "! Entries: 3" in result


class TestFormatDnsmasq:
    """Tests for format_dnsmasq function."""
    
    def test_basic_format(self):
        """Should format domains in dnsmasq format."""
        domains = ["example.com", "test.net"]
        result = format_dnsmasq(domains)
        
        assert "server=/example.com/" in result
        assert "server=/test.net/" in result
    
    def test_includes_header(self):
        """Should include header with metadata."""
        domains = ["example.com"]
        result = format_dnsmasq(domains, title="Test")
        
        assert "# Title: Test" in result
        assert "# Format: dnsmasq" in result


class TestFormatOutput:
    """Tests for format_output function."""
    
    def test_selects_correct_formatter(self):
        """Should select correct formatter by name."""
        domains = ["example.com"]
        
        hosts_result = format_output(domains, "hosts")
        adguard_result = format_output(domains, "adguard")
        
        assert "0.0.0.0" in hosts_result
        assert "||" in adguard_result
    
    def test_invalid_format_raises(self):
        """Should raise ValueError for unknown format."""
        with pytest.raises(ValueError) as exc:
            format_output(["example.com"], "invalid_format")
        
        assert "Unknown format" in str(exc.value)
        assert "invalid_format" in str(exc.value)
    
    def test_all_formatters_registered(self):
        """All format functions should be in registry."""
        assert "hosts" in FORMATTERS
        assert "domains" in FORMATTERS
        assert "adguard" in FORMATTERS
        assert "dnsmasq" in FORMATTERS


class TestWriteOutput:
    """Tests for write_output function."""
    
    def test_writes_to_file(self):
        """Should write formatted content to file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test.txt"
            domains = ["example.com", "test.net"]
            
            count = write_output(domains, output_path, "hosts")
            
            assert count == 2
            assert output_path.exists()
            content = output_path.read_text()
            assert "0.0.0.0 example.com" in content
    
    def test_creates_parent_directories(self):
        """Should create parent directories if needed."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "nested" / "dir" / "test.txt"
            
            write_output(["example.com"], output_path, "hosts")
            
            assert output_path.exists()
    
    def test_returns_domain_count(self):
        """Should return number of domains written."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test.txt"
            
            count = write_output(
                ["a.com", "b.com", "c.com"],
                output_path,
                "hosts"
            )
            
            assert count == 3


class TestGetFormatForPath:
    """Tests for get_format_for_path function."""
    
    def test_adguard_directory(self):
        """Should detect AdGuard format from directory."""
        path = Path("adguard/ads-ags.txt")
        assert get_format_for_path(path) == "adguard"
    
    def test_alt_version_directory(self):
        """Should detect domains format from alt-version directory."""
        path = Path("alt-version/ads-nl.txt")
        assert get_format_for_path(path) == "domains"
    
    def test_dnsmasq_directory(self):
        """Should detect dnsmasq format from directory."""
        path = Path("dnsmasq-version/ads-dnsmasq.txt")
        assert get_format_for_path(path) == "dnsmasq"
    
    def test_filename_patterns(self):
        """Should detect format from filename patterns."""
        assert get_format_for_path(Path("some/dir/test-ags.txt")) == "adguard"
        assert get_format_for_path(Path("some/dir/test-nl.txt")) == "domains"
        assert get_format_for_path(Path("some/dir/test-dnsmasq.txt")) == "dnsmasq"


class TestIntegration:
    """Integration tests."""
    
    def test_roundtrip_format(self):
        """Format and parse should be inverse operations."""
        from src.normalize import parse_file_to_set
        
        original_domains = {"example.com", "test.net", "sub.domain.org"}
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Write in hosts format
            output_path = Path(tmpdir) / "test.txt"
            write_output(sorted(original_domains), output_path, "hosts")
            
            # Parse back
            parsed = parse_file_to_set(output_path)
            
            assert parsed == original_domains
    
    def test_large_list_formatting(self):
        """Should handle large domain lists efficiently."""
        # Generate 10000 test domains
        domains = [f"domain{i}.example.com" for i in range(10000)]
        
        result = format_hosts(domains)
        
        # Should have all domains
        assert "# Entries: 10,000" in result
        assert "0.0.0.0 domain0.example.com" in result
        assert "0.0.0.0 domain9999.example.com" in result
