"""Configuration loader for Block List Project."""

import os
from pathlib import Path
from typing import Any

import yaml


# ============================================================================
# Path Configuration (Environment-aware)
# ============================================================================

# Project directories (configurable via environment variables)
PROJECT_ROOT = Path(os.environ.get("PROJECT_ROOT", Path(__file__).parent.parent))
WORKSPACE_DIR = Path(os.environ.get("WORKSPACE_DIR", PROJECT_ROOT))
VAULT_DIR = Path(os.environ.get("HERMES_VAULT", Path.home() / ".hermes" / "vault"))

# Temporary files
TEMP_DIR = Path(os.environ.get("TEMP_DIR", "/tmp"))
ISSUES_FILE = TEMP_DIR / "issues.json"
RESULTS_FILE = TEMP_DIR / "batch_results.json"

# Config directory
CONFIG_DIR = PROJECT_ROOT / "config"


# ============================================================================
# Configuration Loading
# ============================================================================


def load_config(config_path: Path | None = None) -> dict[str, Any]:
    """Load the lists.yml configuration file.
    
    Args:
        config_path: Path to config file. Defaults to config/lists.yml
        
    Returns:
        Parsed configuration dictionary
    """
    if config_path is None:
        config_path = CONFIG_DIR / "lists.yml"
    
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
        
        if config is None:
            return {}
        
        return config


def get_list_names(config: dict[str, Any], status: list[str] | None = None) -> list[str]:
    """Get list names, optionally filtered by status.
    
    Args:
        config: Loaded configuration
        status: Filter by status (e.g., ['stable', 'beta']). None = all.
        
    Returns:
        List of list names
    """
    lists = config.get("lists", {})
    if status is None:
        return list(lists.keys())
    
    return [
        name for name, info in lists.items()
        if info.get("status") in status
    ]


def get_format_config(config: dict[str, Any], format_name: str) -> dict[str, Any]:
    """Get configuration for a specific output format.
    
    Args:
        config: Loaded configuration
        format_name: Format name (hosts, domains, adguard, dnsmasq)
        
    Returns:
        Format configuration dictionary
    """
    return config.get("formats", {}).get(format_name, {})


def get_settings(config: dict[str, Any]) -> dict[str, Any]:
    """Get global settings from config.
    
    Args:
        config: Loaded configuration
        
    Returns:
        Settings dictionary
    """
    return config.get("settings", {})
