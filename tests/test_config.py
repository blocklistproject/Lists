"""Tests for configuration loading."""

import pytest
from pathlib import Path

from src.config import load_config, get_list_names, get_format_config, get_settings


class TestLoadConfig:
    """Tests for load_config function."""
    
    def test_load_default_config(self):
        """Should load config/lists.yml by default."""
        config = load_config()
        assert config is not None
        assert "lists" in config
        assert "formats" in config
        assert "settings" in config
    
    def test_config_has_required_lists(self):
        """Should have all expected list definitions."""
        config = load_config()
        expected_lists = [
            "abuse", "ads", "crypto", "drugs", "facebook", "fraud",
            "gambling", "malware", "phishing", "piracy", "porn",
            "ransomware", "redirect", "scam", "tiktok", "torrent",
            "tracking", "twitter"
        ]
        for list_name in expected_lists:
            assert list_name in config["lists"], f"Missing list: {list_name}"
    
    def test_config_has_all_formats(self):
        """Should have all 4 output formats defined."""
        config = load_config()
        expected_formats = ["hosts", "domains", "adguard", "dnsmasq"]
        for fmt in expected_formats:
            assert fmt in config["formats"], f"Missing format: {fmt}"


class TestGetListNames:
    """Tests for get_list_names function."""
    
    def test_get_all_lists(self):
        """Should return all list names when no filter."""
        config = load_config()
        names = get_list_names(config)
        assert len(names) > 0
        assert "ads" in names
        assert "malware" in names
    
    def test_filter_by_stable_status(self):
        """Should filter by stable status."""
        config = load_config()
        names = get_list_names(config, status=["stable"])
        assert "ads" in names
        assert "malware" in names
        # Beta lists should be excluded
        assert "basic" not in names
        assert "smart-tv" not in names
    
    def test_filter_by_beta_status(self):
        """Should filter by beta status."""
        config = load_config()
        names = get_list_names(config, status=["beta"])
        assert "basic" in names
        assert "smart-tv" in names
        # Stable lists should be excluded
        assert "ads" not in names


class TestGetFormatConfig:
    """Tests for get_format_config function."""
    
    def test_hosts_format(self):
        """Should return correct hosts format config."""
        config = load_config()
        fmt = get_format_config(config, "hosts")
        assert fmt["prefix"] == "0.0.0.0 "
        assert fmt["comment_char"] == "#"
        assert fmt["output_dir"] == "."
    
    def test_adguard_format(self):
        """Should return correct AdGuard format config."""
        config = load_config()
        fmt = get_format_config(config, "adguard")
        assert fmt["prefix"] == "||"
        assert fmt["suffix"] == "^"
        assert fmt["comment_char"] == "!"
        assert fmt["output_dir"] == "adguard"
    
    def test_dnsmasq_format(self):
        """Should return correct dnsmasq format config."""
        config = load_config()
        fmt = get_format_config(config, "dnsmasq")
        assert fmt["prefix"] == "server=/"
        assert fmt["suffix"] == "/"
        assert fmt["output_dir"] == "dnsmasq-version"
    
    def test_domains_format(self):
        """Should return correct domains (NL) format config."""
        config = load_config()
        fmt = get_format_config(config, "domains")
        assert fmt["prefix"] == ""
        assert fmt["output_dir"] == "alt-version"


class TestGetSettings:
    """Tests for get_settings function."""
    
    def test_has_homepage(self):
        """Should have homepage setting."""
        config = load_config()
        settings = get_settings(config)
        assert "homepage" in settings
        assert "blocklist.site" in settings["homepage"]
    
    def test_has_license(self):
        """Should have license setting."""
        config = load_config()
        settings = get_settings(config)
        assert "license" in settings
        assert "unlicense" in settings["license"].lower()
