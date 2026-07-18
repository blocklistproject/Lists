<div align="center">

<img src="https://raw.githubusercontent.com/blocklistproject/Lists/main/img/logo.webp" height="150px" alt="Block List Project Logo"/>

# The Block List Project

**Curated, community-maintained domain blocklists for network-level content filtering**

[![Build](https://github.com/blocklistproject/Lists/workflows/Build%20Blocklists/badge.svg)](https://github.com/blocklistproject/Lists/actions)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/github/license/blocklistproject/lists?color=blue)](LICENSE)
[![GitHub Issues](https://img.shields.io/github/issues/blocklistproject/lists)](https://github.com/blocklistproject/Lists/issues)
[![Contributors](https://img.shields.io/github/contributors/blocklistproject/lists)](https://github.com/blocklistproject/Lists/graphs/contributors)

[Discord](https://discord.com/invite/x9KeVQggkc) • [Patreon](https://www.patreon.com/bePatron?u=8892646) • [Ko-fi](https://ko-fi.com/P5P521OPP) • [Documentation](docs/)

</div>

---

## Table of Contents

- [About](#about)
- [Features](#features)
- [Quick Start](#quick-start)
- [Available Lists](#available-lists)
- [Supported Formats](#supported-formats)
- [Automation & Updates](#automation--updates)
- [Contributing](#contributing)
- [For Developers](#for-developers)
- [License](#license)

---

## About

The Block List Project provides **free, open-source domain blocklists** for network-level content filtering. Our curated lists help you control what gets blocked on your network — from ads and trackers to malware and adult content.

### Why Block List Project?

- **🎯 Granular Control** — Choose specific categories instead of all-or-nothing blocking
- **🔄 Always Updated** — Automated builds, upstream monitoring, and community contributions
- **🔧 Format Flexibility** — Pi-hole, AdGuard Home, dnsmasq, hosts files, and more
- **✅ Battle-Tested** — Validated with 151+ automated tests on every change
- **🤝 Community-Driven** — Submit additions/removals via GitHub Issues
- **💯 Truly Free** — No premium tiers, no paywalls, no restrictions

---

![Alt](https://repobeats.axiom.co/api/embed/89ccaea6c37737f54fc57933bfb05b050316c4e0.svg "Repobeats analytics image")

---

## Features

### 🤖 Automated Maintenance
- **Upstream Source Monitoring** — Automatically sync with trusted upstream blocklists
- **Dead Domain Detection** — Weekly scans remove defunct domains
- **Issue Triage Bot** — Automatically validates submissions and checks duplicates
- **DNS/HTTP Validation** — Verifies domains before adding them

### 🛡️ Quality Assurance
- **TLD Verification** — Ensures valid top-level domains
- **Duplicate Detection** — Prevents redundant entries across lists
- **Critical Domain Protection** — Safeguards against blocking essential services
- **Format Sync** — All formats generated from single source

### 📊 Comprehensive Coverage
- **18 Main Lists** — Ads, malware, phishing, tracking, gambling, and more
- **4 Beta Lists** — Basic protection, Smart TV, vaping, WhatsApp
- **Multiple Formats** — hosts, domain-only, dnsmasq, AdGuard
- **Regular Updates** — New domains added daily from community and upstream sources
---

## Quick Start

### Pi-hole Setup

1. Navigate to **Group Management** → **Adlists**
2. Paste a list URL from the [Available Lists](#available-lists) section
3. Click **Add**, then go to **Tools** → **Update Gravity**

### AdGuard Home Setup

1. Go to **Filters** → **DNS Blocklists** → **Add blocklist**
2. Select **Add a custom list**
3. Paste an AdGuard format URL and click **Save**

### Other DNS Solutions

Choose the appropriate format for your software:

| Software | Format to Use | Example |
|----------|---------------|---------|
| Hosts file | Original | `0.0.0.0 example.com` |
| Unbound, pfBlockerNG | No IP (domains) | `example.com` |
| dnsmasq | DNSMASQ | `server=/example.com/` |
| AdGuard, uBlock Origin | AdGuard | `||example.com^` |

---

## Available Lists

### Main Lists

| List | Original/Pi-Hole Native | No IP | DNSMASQ | AdGuard | Description |
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

> **📌 Note about the "Everything" List**  
> The combined "everything" list (which merged all stable lists) has been **removed as of July 2026** due to exceeding GitHub's 100MB file size limit. The files grew too large for the repository:
> - `everything.txt`: 125 MB
> - `everything-ags.txt`: 102 MB  
> - `everything-nl.txt`: 125 MB
> - `everything-dnsmasq.txt`: 130 MB
>
> **Alternative:** To achieve similar coverage, subscribe to multiple individual lists in your DNS solution. Most tools support multiple blocklist subscriptions and will automatically merge them.

---

## Supported Formats

All lists are available in four formats, automatically generated from a single source:

| Format | Use Case | Syntax | File Extension |
|--------|----------|--------|----------------|
| **Original (hosts)** | Pi-hole, hosts file, RPZ | `0.0.0.0 example.com` | `.txt` |
| **No IP (domains)** | Unbound, routers, simple lists | `example.com` | `-nl.txt` |
| **DNSMASQ** | dnsmasq DNS server | `server=/example.com/` | `-dnsmasq.txt` |
| **AdGuard** | AdGuard Home, browser extensions | `||example.com^` | `-ags.txt` |

---

## Automation & Updates

### Upstream Source Monitoring

The project automatically syncs with **14 trusted upstream blocklists** across 8 categories:

- **Daily Monitoring** — GitHub Actions checks for updates at 2 AM UTC
- **Auto-PR Creation** — New domains trigger pull requests with size-based labels
- **Smart Merging** — Small updates (≤10 domains) are auto-merge candidates
- **Exclusion Support** — Removed domains stay removed, even if upstream re-adds them

**Current Sources:** ShadowWhisperer, zachlagden, Hagezi, and more.

See [UPSTREAM_MONITORING.md](UPSTREAM_MONITORING.md) for configuration details.

### Automated Maintenance

- **Dead Domain Removal** — Weekly scans identify and remove inactive domains
- **Issue Triage** — Bot automatically validates submissions, checks for duplicates
- **Stale Issue Cleanup** — Inactive issues auto-close after 60 days (PRs after 90 days)
- **Weekly Reports** — Automated statistics and activity summaries

### CI/CD Pipeline

Every change triggers:
- ✅ 151 automated tests
- ✅ Domain syntax validation
- ✅ TLD verification
- ✅ Duplicate detection
- ✅ Format regeneration for all outputs
- ✅ Code quality checks (Ruff, MyPy)

---

## Contributing

We welcome and encourage community contributions! There are several ways to help:

### 🎯 Request Domain Changes

**Add a malicious domain:**
- [Open an Add Request](https://github.com/blocklistproject/Lists/issues/new?template=add-request.yml)
- Provide the domain and evidence (why it should be blocked)
- Our triage bot will check if it's already listed

**Remove a false positive:**
- [Open a Remove Request](https://github.com/blocklistproject/Lists/issues/new?template=remove-request.yml)
- Explain why the domain is incorrectly blocked
- Maintainers will review and process the removal

### 💻 Direct Code Contributions

**Important:** Only edit source `.txt` files in the root directory. Files in `adguard/`, `alt-version/`, and `dnsmasq-version/` are auto-generated — never edit these directly.

```bash
# 1. Fork and clone
git clone https://github.com/YOUR_USERNAME/Lists.git
cd Lists

# 2. Install dev dependencies
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pre-commit install

# 3. Create feature branch
git checkout -b add-malicious-domain

# 4. Edit the source file
echo "0.0.0.0 badads.example.com" >> ads.txt

# 5. Test and validate
pytest
python build.py --validate

# 6. Commit and push
git add ads.txt
git commit -m "Add badads.example.com to ads list"
git push origin add-malicious-domain

# 7. Open Pull Request on GitHub
```

Our CI automatically validates PRs with:
- ✅ Domain syntax checking
- ✅ Duplicate detection
- ✅ TLD verification
- ✅ All 151 test suite
- ✅ Code quality checks

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

---

## For Developers

### Quick Setup

```bash
# Clone and setup
git clone https://github.com/blocklistproject/Lists.git
cd Lists
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install with dev dependencies
pip install -e ".[dev]"

# Setup pre-commit hooks
pre-commit install

# Verify installation
pytest
```

### Building Lists

```bash
# Build all lists
python build.py

# Build specific list(s)
python build.py --list ads
python build.py --list ads --list malware --list phishing

# Validate without building
python build.py --dry-run --validate

# Build with verbose output
python build.py --verbose
```

### Code Quality

We use modern Python tooling for code quality:

```bash
# Run tests with coverage
pytest -v --cov=src --cov-report=html

# Lint and format (Ruff - 10-100x faster than flake8/black)
ruff check .           # Check for issues
ruff check . --fix     # Auto-fix issues
ruff format .          # Format code

# Type checking
mypy src/

# Run all pre-commit hooks
pre-commit run --all-files
```

**Pre-commit hooks** automatically run on every commit:
- Ruff linting and formatting
- YAML/JSON/TOML validation
- Trailing whitespace removal
- MyPy type checking
- Private key detection

### Environment Variables

Optional configuration for custom deployments:

```bash
# Project paths (defaults to current directory)
export PROJECT_ROOT=/path/to/Lists
export WORKSPACE_DIR=/path/to/Lists

# Temporary files location (defaults to /tmp)
export TEMP_DIR=/custom/tmp

# GitHub API access (for scripts that fetch issues)
export GITHUB_TOKEN=your_github_token_here
```

### Project Structure

```
Lists/
├── *.txt                      # Source blocklists (hosts format) - EDIT THESE
├── *.ip                       # IP-based blocklists
├── adguard/                   # AdGuard format (auto-generated)
├── alt-version/               # Domain-only format (auto-generated)
├── dnsmasq-version/           # dnsmasq format (auto-generated)
├── build.py                   # CLI build tool
├── pyproject.toml             # Project configuration
├── requirements.txt           # Python dependencies
├── .pre-commit-config.yaml    # Pre-commit hooks
│
├── config/
│   └── lists.yml              # List definitions and upstream sources
│
├── src/                       # Python package
│   ├── config.py              # Configuration and path management
│   ├── logger.py              # Structured logging
│   ├── exceptions.py          # Custom exception types
│   ├── domain_lookup.py       # Unified domain search
│   ├── normalize.py           # Format parsing and normalization
│   ├── merge.py               # Deduplication logic
│   ├── validate.py            # Domain validation and TLD checking
│   ├── format.py              # Output format generators
│   └── pipeline.py            # Build orchestration
│
├── scripts/                   # Utility scripts
│   ├── monitor_upstream.py    # Upstream source monitoring
│   ├── remove_domain.py       # Domain removal automation
│   ├── review_issues_batch.py # Issue triage automation
│   ├── fetch_issues.py        # GitHub issue fetching
│   ├── process_maintenance.py # Dead domain checking
│   └── ...                    # Additional utilities
│
├── tests/                     # Test suite (151+ tests)
│   ├── test_config.py
│   ├── test_normalize.py
│   ├── test_validate.py
│   ├── test_merge.py
│   ├── test_format.py
│   └── test_pipeline.py
│
└── .github/workflows/         # CI/CD automation
    ├── build.yml              # Build and test pipeline
    ├── upstream-monitor.yml   # Upstream source monitoring
    ├── triage.yml             # Automatic issue triage
    ├── scheduled-triage.yml   # Daily issue processing
    ├── stale.yml              # Stale issue cleanup
    ├── weekly-report.yml      # Weekly statistics
    └── dead-domains.yml       # Dead domain detection
```

### Key Modules

| Module | Purpose |
|--------|---------|
| **`src/config.py`** | Environment-aware configuration, YAML loading, path management |
| **`src/validate.py`** | Domain syntax validation, TLD verification, critical domain protection |
| **`src/pipeline.py`** | Build orchestration, coordinates all build steps |
| **`src/domain_lookup.py`** | Unified domain search across all list formats |
| **`src/logger.py`** | Structured logging with console and file output |
| **`src/exceptions.py`** | Custom exception hierarchy (ConfigurationError, ValidationError, etc.) |

### Utility Scripts

Located in `scripts/` directory:

| Script | Description |
|--------|-------------|
| **`monitor_upstream.py`** | Monitor upstream sources and create PRs for updates |
| **`remove_domain.py`** | Automated domain removal with exclusion support |
| **`review_issues_batch.py`** | Automated issue triage and batch processing |
| **`fetch_issues.py`** | Fetch and cache GitHub issues |
| **`process_maintenance.py`** | Scan for and remove dead domains |

Run with: `python scripts/<script-name>.py`

### Troubleshooting

**Import errors:**
```bash
pip install -e ".[dev]" --force-reinstall
```

**Pre-commit hooks not working:**
```bash
pre-commit clean
pre-commit install
pre-commit autoupdate
```

**Test failures:**
```bash
pytest tests/test_validate.py -v      # Run specific test
pytest -vv --tb=long                  # Verbose with full tracebacks
pytest --lf                           # Re-run last failed tests
```

**Build errors:**
```bash
python build.py --validate --verbose  # Validate with detailed output
python build.py --list <name> --verbose  # Build specific list with logging
```

---

## What's New

### v2.0 Complete Rewrite (2026)

We rebuilt the entire project infrastructure from the ground up:

**For Users:**
- ✅ All existing URLs continue to work
- ✅ Same lists, formats, and locations
- ✅ Improved accuracy and quality

**For Contributors:**
- ✅ Structured issue templates
- ✅ Automated triage bot
- ✅ Pre-commit hooks
- ✅ Modern Python tooling (Ruff, MyPy)

**Technical Improvements:**
- Replaced 7 JavaScript scripts with unified Python codebase
- Added 151 automated tests
- Config-driven architecture
- Proper domain validation and TLD verification
- Critical domain protection
- Upstream source monitoring
- Dead domain detection
- Structured logging and error handling

See [docs/Optimize.md](docs/Optimize.md) for the full technical deep dive.

---

## Sponsors & Support

Special thanks to [Cloud 4 SURE](https://www.cloud4sure.net) for helping cover infrastructure costs.

Support the project:
- ☕ [Ko-fi](https://ko-fi.com/P5P521OPP)
- 🎨 [Patreon](https://www.patreon.com/bePatron?u=8892646)
- ⭐ Star this repository
- 🐛 Report issues and suggest improvements
- 💬 Join our [Discord community](https://discord.com/invite/x9KeVQggkc)

---


## License

This project is licensed under the [Unlicense](LICENSE) — completely free and open source with no restrictions.

<sub>These files are provided "AS IS", without warranty of any kind, express or implied. In no event shall the authors or copyright holders be liable for any claim, damages or other liability arising from the use of these files.</sub>

<sub>All trademarks are the property of their respective owners.</sub>
