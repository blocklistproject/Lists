<img src="https://raw.githubusercontent.com/blocklistproject/Lists/master/img/logo.webp" height="150px"/>  

# The Block List Project

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
- [Quick Start](#quick-start)
- [Available Lists](#available-lists)
- [Formats](#formats)
- [Contributing](#contributing)
- [For Developers](#for-developers)
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
1. Fork the repository
2. Edit the appropriate `.txt` file in the root directory
3. Submit a Pull Request
4. Our CI will validate the changes automatically

&nbsp;

## For Developers

### Building Locally

```bash
# Clone the repository
git clone https://github.com/blocklistproject/Lists.git
cd Lists

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Install dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Build all lists
python build.py

# Build specific list
python build.py --list ads

# Dry run (preview without writing)
python build.py --dry-run --verbose
```

### CLI Commands

```bash
python build.py --help          # Show all options
python build.py list            # List available blocklists
python build.py stats           # Show domain counts
python build.py verify          # Verify output consistency
python build.py --validate      # Build with validation
```

### Project Structure

```
Lists/
├── *.txt                 # Source blocklists (hosts format)
├── adguard/              # AdGuard format output
├── alt-version/          # Domain-only format output
├── dnsmasq-version/      # dnsmasq format output
├── config/
│   └── lists.yml         # List definitions and settings
├── src/                  # Python source code
│   ├── config.py         # Configuration loader
│   ├── normalize.py      # Format parsing
│   ├── merge.py          # Deduplication
│   ├── validate.py       # Domain validation
│   ├── format.py         # Output formatters
│   └── pipeline.py       # Build orchestration
├── tests/                # Test suite
└── build.py              # CLI entry point
```

&nbsp;

## Sponsors

Special thank you to [Cloud 4 SURE](https://www.cloud4sure.net) for their generous donation to help cover infrastructure costs.

&nbsp;

## License

This project is licensed under the [Unlicense](https://github.com/blocklistproject/Lists/blob/master/LICENSE) — free and open source, no restrictions.

&nbsp;

<sup>These files are provided "AS IS", without warranty of any kind, express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose and noninfringement. In no event shall the authors or copyright holders be liable for any claim, damages or other liability, arising from, out of or in connection with the files or the use of the files.</sup>

<sub>Any and all trademarks are the property of their respective owners.</sub>
