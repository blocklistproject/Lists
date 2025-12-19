"""Tests for src/merge.py."""

import tempfile
from pathlib import Path

import pytest

from src.merge import (
    apply_allowlist,
    collapse_subdomains,
    count_by_tld,
    deduplicate,
    get_subdomains_of,
    merge_domain_sets,
    merge_from_files,
    remove_subdomains_of,
    sort_domains,
)


class TestDeduplicate:
    """Tests for deduplicate function."""
    
    def test_removes_duplicates(self):
        """Should remove duplicate domains."""
        domains = ["example.com", "test.com", "example.com", "example.com"]
        result = deduplicate(domains)
        assert result == {"example.com", "test.com"}
    
    def test_lowercases_all(self):
        """Should lowercase all domains."""
        domains = ["Example.COM", "TEST.com", "Mixed.Case.NET"]
        result = deduplicate(domains)
        assert result == {"example.com", "test.com", "mixed.case.net"}
    
    def test_empty_input(self):
        """Should handle empty input."""
        assert deduplicate([]) == set()
    
    def test_returns_set(self):
        """Should return a set."""
        result = deduplicate(["a.com", "b.com"])
        assert isinstance(result, set)


class TestMergeDomainSets:
    """Tests for merge_domain_sets function."""
    
    def test_merges_two_sets(self):
        """Should merge two domain sets."""
        set1 = {"a.com", "b.com"}
        set2 = {"c.com", "d.com"}
        result = merge_domain_sets(set1, set2)
        assert result == {"a.com", "b.com", "c.com", "d.com"}
    
    def test_merges_multiple_sets(self):
        """Should merge multiple domain sets."""
        result = merge_domain_sets({"a.com"}, {"b.com"}, {"c.com"})
        assert result == {"a.com", "b.com", "c.com"}
    
    def test_deduplicates_across_sets(self):
        """Should deduplicate across input sets."""
        set1 = {"a.com", "b.com"}
        set2 = {"b.com", "c.com"}
        result = merge_domain_sets(set1, set2)
        assert result == {"a.com", "b.com", "c.com"}
    
    def test_empty_sets(self):
        """Should handle empty sets."""
        result = merge_domain_sets(set(), set())
        assert result == set()
    
    def test_no_arguments(self):
        """Should handle no arguments."""
        result = merge_domain_sets()
        assert result == set()


class TestApplyAllowlist:
    """Tests for apply_allowlist function."""
    
    def test_removes_allowlisted_domains(self):
        """Should remove allowlisted domains."""
        domains = {"a.com", "b.com", "c.com"}
        allowlist = {"b.com"}
        result = apply_allowlist(domains, allowlist)
        assert result == {"a.com", "c.com"}
    
    def test_case_insensitive(self):
        """Should be case-insensitive."""
        domains = {"example.com"}
        allowlist = {"EXAMPLE.COM"}
        result = apply_allowlist(domains, allowlist)
        assert result == set()
    
    def test_empty_allowlist(self):
        """Should handle empty allowlist."""
        domains = {"a.com", "b.com"}
        result = apply_allowlist(domains, set())
        assert result == {"a.com", "b.com"}
    
    def test_allowlist_with_extra_domains(self):
        """Should ignore allowlist entries not in domains."""
        domains = {"a.com", "b.com"}
        allowlist = {"b.com", "not-in-domains.com"}
        result = apply_allowlist(domains, allowlist)
        assert result == {"a.com"}


class TestSortDomains:
    """Tests for sort_domains function."""
    
    def test_sorts_alphabetically(self):
        """Should sort domains alphabetically."""
        domains = {"z.com", "a.com", "m.com"}
        result = sort_domains(domains)
        assert result == ["a.com", "m.com", "z.com"]
    
    def test_returns_list(self):
        """Should return a list."""
        result = sort_domains({"a.com"})
        assert isinstance(result, list)
    
    def test_empty_set(self):
        """Should handle empty set."""
        assert sort_domains(set()) == []


class TestMergeFromFiles:
    """Tests for merge_from_files function."""
    
    def test_merges_hosts_files(self):
        """Should merge domains from hosts format files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file1 = Path(tmpdir) / "file1.txt"
            file2 = Path(tmpdir) / "file2.txt"
            
            file1.write_text("0.0.0.0 a.com\n0.0.0.0 b.com\n")
            file2.write_text("0.0.0.0 c.com\n0.0.0.0 d.com\n")
            
            result = merge_from_files([file1, file2])
            assert result == {"a.com", "b.com", "c.com", "d.com"}
    
    def test_applies_allowlist_file(self):
        """Should apply allowlist from file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            blocklist = Path(tmpdir) / "blocklist.txt"
            allowlist = Path(tmpdir) / "allowlist.txt"
            
            blocklist.write_text("0.0.0.0 a.com\n0.0.0.0 b.com\n0.0.0.0 c.com\n")
            allowlist.write_text("b.com\n")  # Plain domain format
            
            result = merge_from_files([blocklist], allowlist_file=allowlist)
            assert result == {"a.com", "c.com"}
    
    def test_handles_missing_files(self):
        """Should skip missing files gracefully."""
        with tempfile.TemporaryDirectory() as tmpdir:
            existing = Path(tmpdir) / "existing.txt"
            missing = Path(tmpdir) / "missing.txt"
            
            existing.write_text("0.0.0.0 a.com\n")
            
            result = merge_from_files([existing, missing])
            assert result == {"a.com"}


class TestCountByTld:
    """Tests for count_by_tld function."""
    
    def test_counts_tlds(self):
        """Should count domains by TLD."""
        domains = {"a.com", "b.com", "c.net", "d.org"}
        result = count_by_tld(domains)
        assert result == {"com": 2, "net": 1, "org": 1}
    
    def test_handles_empty_set(self):
        """Should handle empty set."""
        assert count_by_tld(set()) == {}
    
    def test_handles_subdomains(self):
        """Should extract TLD from subdomains."""
        domains = {"sub.example.com", "deep.sub.example.net"}
        result = count_by_tld(domains)
        assert result == {"com": 1, "net": 1}


class TestRemoveSubdomainsOf:
    """Tests for remove_subdomains_of function."""
    
    def test_removes_subdomains(self):
        """Should remove all subdomains of a parent."""
        domains = {"a.example.com", "b.example.com", "other.net"}
        result = remove_subdomains_of(domains, "example.com")
        assert result == {"other.net"}
    
    def test_removes_parent_too(self):
        """Should also remove the parent domain itself."""
        domains = {"example.com", "sub.example.com", "other.net"}
        result = remove_subdomains_of(domains, "example.com")
        assert result == {"other.net"}
    
    def test_case_insensitive(self):
        """Should be case-insensitive."""
        domains = {"sub.example.com"}
        result = remove_subdomains_of(domains, "EXAMPLE.COM")
        assert result == set()


class TestGetSubdomainsOf:
    """Tests for get_subdomains_of function."""
    
    def test_finds_subdomains(self):
        """Should find all subdomains of a parent."""
        domains = {"a.example.com", "b.example.com", "other.net"}
        result = get_subdomains_of(domains, "example.com")
        assert result == {"a.example.com", "b.example.com"}
    
    def test_excludes_parent(self):
        """Should not include the parent domain itself."""
        domains = {"example.com", "sub.example.com"}
        result = get_subdomains_of(domains, "example.com")
        assert result == {"sub.example.com"}


class TestCollapseSubdomains:
    """Tests for collapse_subdomains function."""
    
    def test_collapses_when_threshold_exceeded(self):
        """Should collapse subdomains when threshold exceeded."""
        # Create 15 subdomains of example.com
        domains = {f"sub{i}.example.com" for i in range(15)}
        domains.add("other.net")
        
        result = collapse_subdomains(domains, threshold=10)
        
        # Should collapse to example.com plus other.net
        assert "example.com" in result
        assert "other.net" in result
        # Original subdomains should not be there
        assert "sub0.example.com" not in result
    
    def test_keeps_below_threshold(self):
        """Should keep subdomains when below threshold."""
        domains = {"a.example.com", "b.example.com", "other.net"}
        result = collapse_subdomains(domains, threshold=10)
        
        # Should keep original domains
        assert result == domains


class TestIntegration:
    """Integration tests with actual blocklist files."""
    
    def test_merge_ads_lists(self):
        """Should merge real ads lists correctly."""
        base = Path(__file__).parent.parent
        hosts_path = base / "ads.txt"
        
        if hosts_path.exists():
            result = merge_from_files([hosts_path])
            assert len(result) > 100000
            # Result should be deduplicated
            assert len(result) == len(set(result))
