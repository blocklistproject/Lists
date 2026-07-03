<img src="https://raw.githubusercontent.com/blocklistproject/Lists/master/img/logo.webp" height="150px"/>  

# The Block List Project

[![Build](https://github.com/blocklistproject/Lists/workflows/Build%20Blocklists/badge.svg)](https://github.com/blocklistproject/Lists/actions)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![GitHub issues](https://img.shields.io/github/issues/blocklistproject/lists)](https://github.com/blocklistproject/Lists/issues)
[![GitHub closed issues](https://badgen.net/github/closed-issues/blocklistproject/Lists?color=green)](https://github.com/blocklistproject/Lists/issues?q=is%3Aissue+is%3Aclosed)
[![GitHub contributors](https://img.shields.io/github/contributors/blocklistproject/lists)](https://github.com/blocklistproject/Lists/graphs/contributors)
![GitHub repo size](https://img.shields.io/github/repo-size/blocklistproject/lists)
![GitHub](https://img.shields.io/github/license/blocklistproject/lists?color=blue)
![GitHub Maintained](https://img.shields.io/badge/Open%20Source-Yes-green)
![GitHub commit activity](https://img.shields.io/github/commit-activity/y/blocklistproject/lists)
![GitHub last commit](https://img.shields.io/github/last-commit/blocklistproject/lists)
![GitHub Maintained](https://img.shields.io/badge/maintained-yes-green)
[![ko-fi](https://badgen.net/badge/Support%20Us/Ko-Fi?color=orange)](https://ko-fi.com/P5P521OPP)
[![patreon](https://badgen.net/badge/Support%20Us/Patreon?color=red)](https://www.patreon.com/bePatron?u=8892646)

&nbsp;

<p align="center">
<a href="https://www.patreon.com/bePatron?u=8892646"><img src="https://i0.wp.com/thelemicunion.com/wp-content/uploads/2018/07/Patreon-Support-Button.png?w=640&ssl=1" width=250></a>
<a href="https://discord.com/invite/x9KeVQggkc"><img src="https://discord.com/assets/ff41b628a47ef3141164bfedb04fb220.png" width=250 /></a>
</p>

&nbsp;

## Table of Contents

- [About](#about)
- [What's New in v2.0](#whats-new-in-v20)
- [Quick Start](#quick-start)
- [Available Lists](#available-lists)
- [Formats](#formats)
- [Contributing](#contributing)
- [For Developers](#for-developers)
  - [Quick Setup](#quick-setup)
  - [Environment Variables](#environment-variables)
  - [Building Lists](#building-lists)
  - [Code Quality Tools](#code-quality-tools)
  - [Project Structure](#project-structure)
- [License](#license)

&nbsp;

## About

The Block List Project provides curated domain blocklists for various categories of unwanted content. Our lists are designed to give you control over what gets blocked, rather than an all-or-nothing approach.

All lists are:
- ✅ **Free and open source** — always will be
- ✅ **Regularly updated** — automated builds on every change
- ✅ **Available in multiple formats** — Pi-hole, AdGuard, dnsmasq, and more
- ✅ **Community maintained** — submit requests via GitHub Issues

&nbsp;

## What's New in v2.0

We've completely rebuilt the project infrastructure from the ground up. After 6 months of planning, we're excited to share what's changed.

### Why We Rewrote Everything

The old system worked, but it was held together with duct tape. We had a mix of JavaScript and Python scripts that nobody wanted to touch, inconsistent build processes, and no automated testing. When bugs appeared, fixing one thing broke another.

We needed something maintainable — not just for us, but for anyone who wants to contribute.

### What Changed

**For Users:** Nothing breaks! All your existing URLs continue to work. Same lists, same formats, same locations. We rebuilt the engine without changing the car.

**For Contributors:** 
- New structured issue templates make it easier to request additions or removals
- Our triage bot automatically checks if a domain already exists in our lists
- Pull requests now get validated automatically — no more waiting for a human to catch simple errors
- Pre-commit hooks ensure code quality before commits
- Modern Python tooling (Ruff, MyPy) for faster development

**Under the Hood:**
- Replaced 7 JavaScript scripts with a single Python codebase
- Added 151 automated tests (yes, really)
- Config-driven architecture — all list definitions live in `config/lists.yml`
- Proper domain validation catches invalid entries before they ship
- TLD verification ensures we don't accidentally block legitimate domains
- Critical domain protection prevents catastrophic mistakes (no more accidentally blocking google.com)
- Environment-aware configuration for flexible deployments
- Structured logging for better debugging
- Custom exception hierarchy for clear error handling
- Unified domain lookup utility eliminates code duplication

### The Technical Bits

If you're curious about the architecture:

```
Old System:              New System:
─────────────            ─────────────
7 JS scripts             1 Python package
0 tests                  151 tests
Manual validation        Automated validation
Ad-hoc builds            CI/CD pipeline
Mixed formats            Config-driven formats
Hardcoded paths          Environment variables
No code quality tools    Ruff + MyPy + Pre-commit
```

The new build system runs `pytest` on every change, validates domain syntax, checks TLDs against the public suffix list, and generates all four output formats automatically. Everything flows through a single `build.py` CLI.

**Latest Improvements (2026-07-03):**
- ✨ Added structured logging system
- ✨ Created unified domain lookup utility
- ✨ Implemented custom exception hierarchy
- ✨ Environment-aware path configuration
- ✨ Pre-commit hooks for automated quality checks
- ✨ Modern linting with Ruff (10x faster than flake8)
- ✨ Strict type checking with MyPy
- ✨ Organized project structure (scripts in scripts/ directory)

We wrote about the full rationale in our [archived optimization document](docs/Optimize.md) if you want the deep dive.

&nbsp;

## Quick Start

### Pi-hole

1. Copy the link for your desired list from the [Available Lists](#available-lists) section
2. Go to **Group Management** → **Adlists** → Paste URL → **Add**
3. Go to **Tools** → **Update Gravity**

### AdGuard Home

1. Copy the AdGuard format link for your desired list
2. Go to **Filters** → **DNS Blocklists** → **Add blocklist** → **Add a custom list**
3. Paste the URL and click **Save**

### Other DNS Blockers

Use the appropriate format for your software:
- **Hosts file format**: Use the "Original" links
- **Domain-only format**: Use the "No IP" links  
- **dnsmasq**: Use the "DNSMASQ" links
- **AdGuard/AdBlock**: Use the "AdGuard" links

&nbsp;

## Available Lists

### Main Lists

| List | Original | No IP | DNSMASQ | AdGuard | Description |
|------|----------|-------|---------|---------|-------------|
| Abuse | [Link](https://blocklistproject.github.io/Lists/abuse.txt) | [Link](https://blocklistproject.github.io/Lists/alt-version/abuse-nl.txt) | [Link](https://blocklistproject.github.io/Lists/dnsmasq-version/abuse-dnsmasq.txt) | [Link](https://blocklistproject.github.io/Lists/adguard/abuse-ags.txt) | Deceptive/abusive sites |
| Ads | [Link](https://blocklistproject.github.io/Lists/ads.txt) | [Link](https://blocklistproject.github.io/Lists/alt-version/ads-nl.txt) | [Link](https://blocklistproject.github.io/Lists/dnsmasq-version/ads-dnsmasq.txt) | [Link](https://blocklistproject.github.io/Lists/adguard/ads-ags.txt) | Ad servers |
| Crypto | [Link](https://blocklistproject.github.io/Lists/crypto.txt) | [Link](https://blocklistproject.github.io/Lists/alt-version/crypto-nl.txt) | [Link](https://blocklistproject.github.io/Lists/dnsmasq-version/crypto-dnsmasq.txt) | [Link](https://blocklistproject.github.io/Lists/adguard/crypto-ags.txt) | Cryptojacking/crypto scams |
| Drugs | [Link](https://blocklistproject.github.io/Lists/drugs.txt) | [Link](https://blocklistproject.github.io/Lists/alt-version/drugs-nl.txt) | [Link](https://blocklistproject.github.io/Lists/dnsmasq-version/drugs-dnsmasq.txt) | [Link](https://blocklistproject.github.io/Lists/adguard/drugs-ags.txt) | Illegal drug sites |
| Facebook | [Link](https://blocklistproject.github.io/Lists/facebook.txt) | [Link](https://blocklistproject.github.io/Lists/alt-version/facebook-nl.txt) | [Link](https://blocklistproject.github.io/Lists/dnsmasq-version/facebook-dnsmasq.txt) | [Link](https://blocklistproject.github.io/Lists/adguard/facebook-ags.txt) | Facebook/Meta services |
| Fraud | [Link](https://blocklistproject.github.io/Lists/fraud.txt) | [Link](https://blocklistproject.github.io/Lists/alt-version/fraud-nl.txt) | [Link](https://blocklistproject.github.io/Lists/dnsmasq-version/fraud-dnsmasq.txt) | [Link](https://blocklistproject.github.io/Lists/adguard/fraud-ags.txt) | Fraud sites |
| Gambling | [Link](https://blocklistproject.github.io/Lists/gambling.txt) | [Link](https://blocklistproject.github.io/Lists/alt-version/gambling-nl.txt) | [Link](https://blocklistproject.github.io/Lists/dnsmasq-version/gambling-dnsmasq.txt) | [Link](https://blocklistproject.github.io/Lists/adguard/gambling-ags.txt) | Gambling sites |
| Malware | [Link](https://blocklistproject.github.io/Lists/malware.txt) | [Link](https://blocklistproject.github.io/Lists/alt-version/malware-nl.txt) | [Link](https://blocklistproject.github.io/Lists/dnsmasq-version/malware-dnsmasq.txt) | [Link](https://blocklistproject.github.io/Lists/adguard/malware-ags.txt) | Malware hosts |
| Phishing | [Link](https://blocklistproject.github.io/Lists/phishing.txt) | [Link](https://blocklistproject.github.io/Lists/alt-version/phishing-nl.txt) | [Link](https://blocklistproject.github.io/Lists/dnsmasq-version/phishing-dnsmasq.txt) | [Link](https://blocklistproject.github.io/Lists/adguard/phishing-ags.txt) | Phishing sites |
| Piracy | [Link](https://blocklistproject.github.io/Lists/piracy.txt) | [Link](https://blocklistproject.github.io/Lists/alt-version/piracy-nl.txt) | [Link](https://blocklistproject.github.io/Lists/dnsmasq-version/piracy-dnsmasq.txt) | [Link](https://blocklistproject.github.io/Lists/adguard/piracy-ags.txt) | Piracy/illegal downloads |
| Porn | [Link](https://blocklistproject.github.io/Lists/porn.txt) | [Link](https://blocklistproject.github.io/Lists/alt-version/porn-nl.txt) | [Link](https://blocklistproject.github.io/Lists/dnsmasq-version/porn-dnsmasq.txt) | [Link](https://blocklistproject.github.io/Lists/adguard/porn-ags.txt) | Adult content |
| Ransomware | [Link](https://blocklistproject.github.io/Lists/ransomware.txt) | [Link](https://blocklistproject.github.io/Lists/alt-version/ransomware-nl.txt) | [Link](https://blocklistproject.github.io/Lists/dnsmasq-version/ransomware-dnsmasq.txt) | [Link](https://blocklistproject.github.io/Lists/adguard/ransomware-ags.txt) | Ransomware C2/distribution |
| Redirect | [Link](https://blocklistproject.github.io/Lists/redirect.txt) | [Link](https://blocklistproject.github.io/Lists/alt-version/redirect-nl.txt) | [Link](https://blocklistproject.github.io/Lists/dnsmasq-version/redirect-dnsmasq.txt) | [Link](https://blocklistproject.github.io/Lists/adguard/redirect-ags.txt) | Malicious redirects |
| Scam | [Link](https://blocklistproject.github.io/Lists/scam.txt) | [Link](https://blocklistproject.github.io/Lists/alt-version/scam-nl.txt) | [Link](https://blocklistproject.github.io/Lists/dnsmasq-version/scam-dnsmasq.txt) | [Link](https://blocklistproject.github.io/Lists/adguard/scam-ags.txt) | Scam sites |
| TikTok | [Link](https://blocklistproject.github.io/Lists/tiktok.txt) | [Link](https://blocklistproject.github.io/Lists/alt-version/tiktok-nl.txt) | [Link](https://blocklistproject.github.io/Lists/dnsmasq-version/tiktok-dnsmasq.txt) | [Link](https://blocklistproject.github.io/Lists/adguard/tiktok-ags.txt) | TikTok domains |
| Torrent | [Link](https://blocklistproject.github.io/Lists/torrent.txt) | [Link](https://blocklistproject.github.io/Lists/alt-version/torrent-nl.txt) | [Link](https://blocklistproject.github.io/Lists/dnsmasq-version/torrent-dnsmasq.txt) | [Link](https://blocklistproject.github.io/Lists/adguard/torrent-ags.txt) | Torrent sites |
| Tracking | [Link](https://blocklistproject.github.io/Lists/tracking.txt) | [Link](https://blocklistproject.github.io/Lists/alt-version/tracking-nl.txt) | [Link](https://blocklistproject.github.io/Lists/dnsmasq-version/tracking-dnsmasq.txt) | [Link](https://blocklistproject.github.io/Lists/adguard/tracking-ags.txt) | Tracking/analytics |
| Twitter | [Link](https://blocklistproject.github.io/Lists/twitter.txt) | [Link](https://blocklistproject.github.io/Lists/alt-version/twitter-nl.txt) | [Link](https://blocklistproject.github.io/Lists/dnsmasq-version/twitter-dnsmasq.txt) | [Link](https://blocklistproject.github.io/Lists/adguard/twitter-ags.txt) | Twitter/X domains |

### Beta Lists

| List | Original | No IP | DNSMASQ | AdGuard | Description |
|------|----------|-------|---------|---------|-------------|
| Basic | [Link](https://blocklistproject.github.io/Lists/basic.txt) | [Link](https://blocklistproject.github.io/Lists/alt-version/basic-nl.txt) | [Link](https://blocklistproject.github.io/Lists/dnsmasq-version/basic-dnsmasq.txt) | [Link](https://blocklistproject.github.io/Lists/adguard/basic-ags.txt) | Starter protection list |
| Smart TV | [Link](https://blocklistproject.github.io/Lists/smart-tv.txt) | [Link](https://blocklistproject.github.io/Lists/alt-version/smart-tv-nl.txt) | [Link](https://blocklistproject.github.io/Lists/dnsmasq-version/smart-tv-dnsmasq.txt) | [Link](https://blocklistproject.github.io/Lists/adguard/smart-tv-ags.txt) | Smart TV telemetry |
| Vaping | [Link](https://blocklistproject.github.io/Lists/vaping.txt) | [Link](https://blocklistproject.github.io/Lists/alt-version/vaping-nl.txt) | [Link](https://blocklistproject.github.io/Lists/dnsmasq-version/vaping-dnsmasq.txt) | [Link](https://blocklistproject.github.io/Lists/adguard/vaping-ags.txt) | Vaping/e-cigarette sites |
| WhatsApp | [Link](https://blocklistproject.github.io/Lists/whatsapp.txt) | [Link](https://blocklistproject.github.io/Lists/alt-version/whatsapp-nl.txt) | [Link](https://blocklistproject.github.io/Lists/dnsmasq-version/whatsapp-dnsmasq.txt) | [Link](https://blocklistproject.github.io/Lists/adguard/whatsapp-ags.txt) | WhatsApp domains |

&nbsp;

## Formats

| Format | Use Case | Example |
|--------|----------|---------|
| **Original (hosts)** | Pi-hole, hosts file | `0.0.0.0 example.com` |
| **No IP (domains)** | Some routers, simple lists | `example.com` |
| **DNSMASQ** | dnsmasq DNS server | `server=/example.com/` |
| **AdGuard** | AdGuard Home, browser extensions | `\|\|example.com^` |

&nbsp;

## Contributing

We welcome contributions! Here's how you can help:

### Request a Domain Addition
1. [Open an Add Request](https://github.com/blocklistproject/Lists/issues/new?template=add-request.yml)
2. Fill out the form with the domain and evidence
3. Our bot will check if it's already listed
4. A maintainer will review and add it

### Report a False Positive
1. [Open a Remove Request](https://github.com/blocklistproject/Lists/issues/new?template=remove-request.yml)
2. Explain why the domain should be unblocked
3. A maintainer will review and remove it

### Direct Contributions

**Important:** Only edit source `.txt` files in the root directory. Never modify files in `adguard/`, `alt-version/`, or `dnsmasq-version/` — these are auto-generated.

```bash
# 1. Fork and clone the repository
git clone https://github.com/YOUR_USERNAME/Lists.git
cd Lists

# 2. Create a feature branch
git checkout -b add-malicious-domain

# 3. Edit the appropriate source file
# Example: Add domain to ads.txt
echo "0.0.0.0 badads.example.com" >> ads.txt

# 4. Install dependencies and run tests
pip install -e ".[dev]"
pytest

# 5. Build and validate
python build.py --validate

# 6. Commit your changes (pre-commit hooks will run automatically)
git add ads.txt
git commit -m "Add badads.example.com to ads list"

# 7. Push and create Pull Request
git push origin add-malicious-domain
```

Our CI will automatically:
- ✅ Run all 151 tests
- ✅ Validate domain syntax
- ✅ Check for duplicates
- ✅ Verify TLDs
- ✅ Build all output formats
- ✅ Run code quality checks

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

&nbsp;

## For Developers

### Quick Setup

```bash
# Clone the repository
git clone https://github.com/blocklistproject/Lists.git
cd Lists

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Install dependencies (includes dev tools: pytest, ruff, mypy, pre-commit)
pip install -e ".[dev]"

# Install pre-commit hooks (recommended)
pre-commit install

# Run tests to verify setup
pytest
```

### Environment Variables

The project supports environment-based configuration for different deployment scenarios:

```bash
# Project paths (optional - defaults to current directory)
export PROJECT_ROOT=/path/to/Lists
export WORKSPACE_DIR=/path/to/Lists

# Temporary files location (optional - defaults to /tmp)
export TEMP_DIR=/custom/tmp

# GitHub token for API access (optional - for scripts that fetch issues)
export GITHUB_TOKEN=your_github_token_here
```

All paths default to sensible values, so these are only needed for custom deployments.

### Building Lists

```bash
# Build all lists
python build.py

# Build specific list
python build.py --list ads

# Build multiple specific lists
python build.py --list ads --list malware --list phishing

# Dry run (preview without writing)
python build.py --dry-run --verbose

# Build with validation
python build.py --validate --verbose

# Build to custom output directory
python build.py --output-dir /custom/path
```

### Code Quality Tools

We use modern Python tooling to maintain high code quality:

```bash
# Run all tests with coverage
pytest -v --cov=src --cov-report=html

# Lint and format code with Ruff (10x faster than flake8)
ruff check .                    # Check for issues
ruff check . --fix              # Auto-fix issues
ruff format .                   # Format code

# Type checking with MyPy
mypy src/

# Run all pre-commit checks manually
pre-commit run --all-files
```

**Pre-commit Hooks:** Once installed with `pre-commit install`, these checks run automatically before each commit:
- ✅ Ruff linting and formatting
- ✅ YAML, JSON, and TOML validation
- ✅ Trailing whitespace removal
- ✅ End-of-file fixer
- ✅ Private key detection
- ✅ MyPy type checking

### Project Structure

```
Lists/
├── *.txt                      # Source blocklists (hosts format)
├── *.ip                       # IP-based blocklists
├── adguard/                   # AdGuard format output (auto-generated)
├── alt-version/               # Domain-only format output (auto-generated)
├── dnsmasq-version/           # dnsmasq format output (auto-generated)
├── config/
│   └── lists.yml              # List definitions and settings
├── src/                       # Python source code
│   ├── config.py              # Configuration loader + path management
│   ├── logger.py              # Structured logging system
│   ├── exceptions.py          # Custom exception hierarchy
│   ├── domain_lookup.py       # Unified domain search utility
│   ├── normalize.py           # Format parsing
│   ├── merge.py               # Deduplication
│   ├── validate.py            # Domain validation
│   ├── format.py              # Output formatters
│   └── pipeline.py            # Build orchestration
├── scripts/                   # Maintenance and utility scripts
│   ├── fetch_issues.py        # GitHub issue fetching
│   ├── process_maintenance.py # Dead domain checking
│   ├── review_issues_batch.py # Issue triage automation
│   ├── remove_domain.py       # Domain removal utility
│   ├── aggregate.py           # Domain aggregation
│   ├── check-dead-domains.py  # Dead domain scanner
│   ├── generate-stats.py      # Statistics generation
│   └── generate-changelog.py  # Changelog generation
├── tests/                     # Test suite (151 tests)
│   ├── test_config.py
│   ├── test_normalize.py
│   ├── test_validate.py
│   ├── test_merge.py
│   ├── test_format.py
│   └── test_pipeline.py
├── .github/
│   └── workflows/             # CI/CD automation
│       ├── build.yml          # Build and test pipeline
│       ├── triage.yml         # Automatic issue triage
│       └── dead-domains.yml   # Dead domain detection
├── build.py                   # CLI entry point
├── pyproject.toml             # Project configuration
├── .pre-commit-config.yaml    # Pre-commit hooks configuration
└── IMPROVEMENT_PLAN.md        # Development roadmap
```

**Note:** Only edit source `.txt` and `.ip` files. The `adguard/`, `alt-version/`, and `dnsmasq-version/` directories are auto-generated by `build.py`.

&nbsp;

## Sponsors

Special thank you to [Cloud 4 SURE](https://www.cloud4sure.net) for their generous donation to help cover infrastructure costs.

---

## Development

### Requirements
- Python 3.10 or higher
- Git
- (Optional) Pre-commit for automatic code quality checks

### Module Documentation

**`src/config.py`** - Configuration and path management
- Environment-aware paths (PROJECT_ROOT, WORKSPACE_DIR, etc.)
- YAML configuration loader
- Settings and format configuration

**`src/logger.py`** - Structured logging
- Console and file logging
- Configurable log levels
- Proper formatting with timestamps

**`src/exceptions.py`** - Custom exceptions
- BlocklistError (base class)
- ConfigurationError, ValidationError, BuildError
- DomainNotFoundError, NetworkError, FileFormatError

**`src/domain_lookup.py`** - Unified domain search
- Search domains across all list formats
- DomainLocation dataclass for results
- Consistent domain checking logic

**`src/validate.py`** - Domain validation
- Syntax validation
- TLD verification
- Critical domain protection
- False positive detection

**`src/pipeline.py`** - Build orchestration
- Coordinates all build steps
- Handles multiple output formats
- Provides build statistics

### Useful Scripts

Located in `scripts/` directory:

- **`generate-stats.py`** - Generate statistics for all lists
- **`generate-changelog.py`** - Create changelog from git history
- **`check-dead-domains.py`** - Scan for inactive domains
- **`fetch_issues.py`** - Fetch open GitHub issues
- **`review_issues_batch.py`** - Automated issue triage

Run scripts with: `python scripts/<script-name>.py`

### Troubleshooting

**Import errors after updates:**
```bash
pip install -e ".[dev]" --force-reinstall
```

**Pre-commit hooks not running:**
```bash
pre-commit install
pre-commit autoupdate
```

**Tests failing:**
```bash
# Run specific test
pytest tests/test_validate.py -v

# Run with detailed output
pytest -vv --tb=long
```

---

&nbsp;

## License

This project is licensed under the [Unlicense](https://github.com/blocklistproject/Lists/blob/master/LICENSE) — free and open source, no restrictions.

&nbsp;

<sup>These files are provided "AS IS", without warranty of any kind, express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose and noninfringement. In no event shall the authors or copyright holders be liable for any claim, damages or other liability, arising from, out of or in connection with the files or the use of the files.</sup>

<sub>Any and all trademarks are the property of their respective owners.</sub>
