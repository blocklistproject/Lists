"""Configuration paths for Block List Project."""

from pathlib import Path

# Project root directory (where the main list files are)
PROJECT_ROOT = Path(__file__).parent.parent

# Configuration directory
CONFIG_DIR = PROJECT_ROOT / "config"

# Temporary directory for caches and intermediate files
TEMP_DIR = Path("/tmp")
