# Batch 1 - Verified False Positives for Removal

## Domains to Remove (Verified False Positives)

### 1. isprambiente.gov.it
- Current location: abuse.txt, everything.txt, malware.txt
- Status: Legitimate Italian government domain (ISPRA - Istituto Superiore per la Protezione e la Ricerca Ambientale)
- DNS: Resolves correctly
- HTTPS: Returns 301 redirect
- Evidence: Official website at https://www.isprambiente.gov.it/
- Action: Remove from abuse.txt, everything.txt, malware.txt

### 2. komputerswiat.pl
- Current location: abuse.txt, everything.txt, malware.txt
- Status: Legitimate Polish tech news site (komputerswiat.pl)
- DNS: Resolves correctly
- HTTPS: Returns 301 redirect
- Evidence: Official website at https://www.komputerswiat.pl/
- Action: Remove from abuse.txt, everything.txt, malware.txt

### 3. forum.pclab.pl
- Current location: abuse.txt, everything.txt, malware.txt
- Status: Legitimate Polish hardware forum
- DNS: Resolves correctly
- HTTPS: Returns 301 redirect
- Evidence: Official website at https://www.forum.pclab.pl/
- Action: Remove from abuse.txt, everything.txt, malware.txt

## Domains Requiring Confirmation

### 4. miarroba.com
- Current location: abuse.txt, ads.txt, basic.txt, everything.txt, malware.txt, porn.txt
- Status: Domain resolves, but classification unclear
- DNS: Resolves correctly (HTTP 200)
- Decision: Need user confirmation on correct list placement before removal

## Actions Required

1. Remove isprambiente.gov.it, komputerswiat.pl, forum.pclab.pl from:
   - abuse.txt
   - everything.txt
   - malware.txt

2. Update generated formats:
   - alt-version/*-nl.txt
   - adguard/*-ags.txt
   - dnsmasq-version/*-dnsmasq.txt
   - everything/*.txt

3. Run validation before commit:
   - pytest -q
   - ruff check src/ tests/ build.py
   - python build.py --dry-run --validate --verbose

4. Commit with message format:
   "fix: remove false positives from abuse/malware lists (isprambiente.gov.it, komputerswiat.pl, forum.pclab.pl)"

5. Push to origin master and verify CI
