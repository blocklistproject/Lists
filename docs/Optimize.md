# Archive: Optimization Recommendations

> **Note:** This document has been archived. The recommendations below were implemented as part of the 2025 rewrite. See the main [README](../README.md) for current documentation.

---

Yep — and you can cut maintenance time *dramatically* by turning this repo into a **config-driven build pipeline** (instead of "hand-curated files + a pile of scripts").

A couple things I can tell from the repo itself:

* Your **alt formats** (dnsmasq/adguard/etc) are already expected to be **script-generated** and not manually edited. ([GitHub][1])
* You’re already publishing **daily-ish “Aggregated Lists YYYYMMDD” releases via github-actions**, which is the right direction. ([GitHub][2])

The big win now is to **standardize the entire build around one pipeline + one source of truth**.

---

## The “new architecture” that cuts maintenance the most

### 1) Make *one* canonical representation

Pick a single internal format as the “truth,” e.g.:

* **normalized domain lines only** (one domain per line)
* lowercased
* punycode normalized
* comments stripped (except metadata header)
* invalid domains removed

Everything else (hosts / dnsmasq / adguard / etc) becomes **pure output rendering** from that canonical set.

**Why this saves time:** format bugs and “why is it different between versions?” disappear because you only curate *one* dataset.

---

### 2) Replace “scripts per list” with a declarative config

Create something like `config/lists.yml`:

* list name
* category (ads, malware, phishing, etc)
* upstream sources (URLs)
* local overrides:

  * allowlist exceptions
  * forced blocks
  * regex exclusions (rare, but sometimes needed)
* output formats to generate

Then the build system loops over the config.

**Result:** Adding a new list becomes “add 15 lines to YAML,” not “copy script X and hope it works.”

---

### 3) Make the pipeline incremental

Most time waste in list projects is reprocessing everything from scratch.

Do this:

* Cache downloaded sources by `ETag/Last-Modified` when possible
* Hash each upstream content (sha256)
* Only rebuild a list if any of its upstream hashes changed or overrides changed
* Always regenerate outputs from the canonical file for that list (fast)

---

## The pipeline stages (clean + boring + reliable)

### Stage A — Fetch

* download upstreams in parallel with retries/backoff
* store `build/cache/<source_id>.txt` and metadata json

### Stage B — Normalize

* parse all known formats (hosts, adblock-ish, dnsmasq, plain domains)
* output canonical domain stream

### Stage C — Merge + Dedup + Apply Overrides

* dedup with a set (or disk-backed sqlite if huge)
* apply:

  * allowlist removals
  * forced additions
  * optional “safety filters” (drop single-character, invalid TLD, etc.)

### Stage D — Validate

* ensure no IPs, no spaces, no wildcard junk unless you explicitly support it
* sanity thresholds:

  * if a list drops by 80% in one run -> fail build (prevents upstream breaking you silently)
  * if a list grows by 5x -> warn/fail (prevents poisoning)

### Stage E — Render Outputs

From canonical domains, generate:

* `0.0.0.0 domain`
* `domain`
* `server=/domain/`
* `||domain^`

…and any future formats.

### Stage F — Publish

* commit changes to repo
* create release artifact(s)
* optionally publish a `manifest.json` with counts + sources + build info

---

## GitHub Actions: stop “manual babysitting”

### Daily scheduled build + PR (recommended)

Instead of pushing straight to `master`, have actions open an automated PR:

* Maintainer reviews diffs (quick sanity)
* Merge
* Release auto-publishes

This alone prevents “oops we shipped a bad upstream day.”

Here’s a minimal workflow skeleton:

```yaml
name: Build Lists

on:
  schedule:
    - cron: "12 6 * * *" # daily
  workflow_dispatch: {}

jobs:
  build:
    runs-on: ubuntu-latest
    permissions:
      contents: write
      pull-requests: write

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install deps
        run: |
          pip install -r scripts/requirements.txt

      - name: Build
        run: |
          python scripts/build.py --config config/lists.yml --out .

      - name: Create Pull Request
        uses: peter-evans/create-pull-request@v6
        with:
          title: "Automated list build"
          commit-message: "Automated list build"
          branch: "bot/list-build"
          labels: "automation"
```

(If you already publish releases via github-actions, this fits right into what you’re doing now. ([GitHub][2]))

---

## Automate 80% of issue/PR maintenance (add/remove requests)

This is usually the *real* time sink.

### 1) Issue forms (required fields)

Use GitHub Issue Forms for:

* Add request
* Remove request
* False positive report

Required fields should include:

* domain
* which list(s)
* evidence / reason
* “breaks what” (for removals)

### 2) Bot triage comments automatically

On issue open:

* check if domain is present in repo files
* comment with:

  * “found in X lists”
  * “not found”
* auto-label and route

This reduces back-and-forth to near zero.

---

## “Greatly update it” ideas that *also* reduce your workload

### Add a machine-readable manifest

Generate `manifest.json` (and optionally `manifest.csv`) with:

* list -> domain count
* sources used
* build timestamp
* git commit
* diff vs previous build (added/removed counts)

This makes debugging *fast* when users complain.

### Add “poisoning protection”

It’s common for upstreams to get compromised or to ship garbage.
Add build fails for:

* sudden massive growth
* sudden massive shrink
* too many non-FQDNs
* too many single-label domains

### Add provenance headers

At the top of each generated list:

* build date
* count
* source count
* link to manifest

This cuts repeated “is this still maintained?” questions. (You already get those. ([GitHub][3]))

---

## What I can do next (without guessing)

Right now, GitHub’s web view for that `/scripts` folder isn’t loading cleanly in my browsing tool (it returns GitHub’s “Uh oh! error”), so I can’t reliably read your current scripts line-by-line from that link in this chat.

If you **paste the main build script(s)** here (or upload them), I can:

* refactor them into the config-driven pipeline above
* give you a drop-in `build.py` + `lists.yml`
* add the validation + “poisoning protection”
* add the PR-based GitHub Action so you’re not babysitting builds

If you only paste *one* file, paste **the entrypoint** script that orchestrates everything (the one you run to generate outputs).

[1]: https://github.com/blocklistproject/Lists/blob/master/CONTRIBUTING.md?utm_source=chatgpt.com "Lists/CONTRIBUTING.md at master · blocklistproject/Lists"
[2]: https://github.com/blocklistproject/Lists/releases?utm_source=chatgpt.com "Releases · blocklistproject/Lists"
[3]: https://github.com/blocklistproject/Lists/discussions/1313?utm_source=chatgpt.com "How active/up to date are these lists? #1313 - GitHub"
