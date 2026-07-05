# Exclusion Lists

This folder contains exclusion lists for each blocklist. Domains listed in these files will **not** be added from upstream sources during automatic updates.

## Purpose

When a domain is removed from a blocklist (typically as a false positive), it should be added to the corresponding exclusion list to prevent it from being automatically re-added by the `monitor_upstream.py` script when fetching updates from upstream sources.

## File Format

Each exclusion list follows this format:

```
# Exclusion list for {list_name}
# Domains in this list will not be added from upstream sources
# One domain per line, comments start with #

example.com
another-domain.com
```

## Usage

### Automatic (Recommended)

When using the `remove_domain.py` script, domains are automatically added to the appropriate exclusion list(s):

```bash
python scripts/remove_domain.py --list ads --domain example.com
```

This will:
1. Remove the domain from the ads blocklist
2. Add it to `config/exclusions/ads.txt`

To skip adding to exclusion list:

```bash
python scripts/remove_domain.py --list ads --domain example.com --no-exclude
```

### Manual

You can manually edit exclusion files to add domains:

```bash
echo "example.com" >> config/exclusions/ads.txt
```

## File Naming

- `ads.txt` - Exclusions for the ads blocklist
- `malware.txt` - Exclusions for the malware blocklist
- `tracking.txt` - Exclusions for the tracking blocklist
- etc.

Each file corresponds to a `{list_name}.txt` file in the repository root.

## How It Works

When `monitor_upstream.py` fetches updates from upstream sources:

1. It downloads the upstream blocklist
2. Loads the corresponding exclusion list from this folder
3. Removes any excluded domains from the upstream list before comparing
4. Only new domains (not in exclusions) are proposed for addition

This ensures that false positives or intentionally removed domains stay removed even as upstream sources are updated.
