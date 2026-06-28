# Batch 1 Issues (1176-1167)

## Issue 1176 - liftoff-creatives.io add request
- Labels: request:add
- Title: [Add request] liftoff-creatives.io
- Status: VERIFIED - Domain liftoff-creatives.io does NOT resolve (DNS lookup fails)
- Notes: liftoff.io subdomains are already in lists (abuse.txt, ads.txt), but the specific subdomain liftoff-creatives.io has no DNS records
- Decision: Issue invalid - domain doesn't resolve. Close with comment explaining DNS failure.

## Issue 1175 - doubleclick.net on crypto list
- Labels: request:remove
- Title: [Remove Request] - doubleclick.net on crypto list
- Status: VERIFIED - Domain NOT in crypto.txt (grep confirms 0 matches)
- Present in: abuse.txt, ads.txt, basic.txt, everything.txt, malware.txt, tracking.txt
- Also in adguard/adobe-ags.txt, adguard/malware-ags.txt, adguard/everything-ags.txt
- Decision: Issue incorrectly filed - domain not in crypto list. Close with comment.

## Issue 1174 - miarroba.com
- Labels: request:remove
- Title: [Remove Request] - miarroba.com
- Status: VERIFIED - Domain resolves via DNS/HTTPS, NOT in crypto.txt
- Present in: abuse.txt, ads.txt, basic.txt, everything.txt, malware.txt, porn.txt
- DNS: Resolves (verified)
- HTTPS: Returns 200
- Decision: Legitimate domain incorrectly listed in multiple lists. Removal may be warranted. Need user confirmation on correct list placement.

## Issue 1173 - isprambiente.gov.it
- Labels: request:remove
- Title: [Remove Request] - isprambiente.gov.it
- Status: VERIFIED - Domain resolves via DNS/HTTPS, NOT in crypto.txt
- Present in: abuse.txt, everything.txt, malware.txt
- DNS: Resolves (verified)
- HTTPS: Returns 200 (Italian government domain)
- Decision: Legitimate Italian government domain - false positive. Removal warranted.

## Issue 1172 - komputerswiat.pl
- Labels: request:remove
- Title: [Remove Request] - komputerswiat.pl
- Status: VERIFIED - Domain resolves via DNS/HTTPS, NOT in crypto.txt
- Present in: abuse.txt, everything.txt, malware.txt
- DNS: Resolves (verified)
- HTTPS: Returns 200 (Polish tech site)
- Decision: Legitimate Polish tech site - false positive. Removal warranted.

## Issue 1171 - forum.pclab.pl
- Labels: request:remove
- Title: [Remove Request] - forum.pclab.pl
- Status: VERIFIED - Domain resolves via DNS/HTTPS, NOT in crypto.txt
- Present in: abuse.txt, everything.txt, malware.txt
- DNS: Resolves (verified)
- HTTPS: Returns 200 (Polish hardware forum)
- Decision: Legitimate Polish hardware forum - false positive. Removal warranted.

## Issue 1170 - BloxFlip add request
- Labels: request:add
- Title: [Add request] BloxFlip
- Status: VERIFIED - Domain bloxflip.com resolves, HTTPS returns 403 (blocked/forbidden)
- Present in: crypto.txt, fraud.txt, malware.txt
- DNS: Resolves
- HTTPS: Returns 403 (likely already blocked successfully)
- Decision: Already in crypto.txt list. Issue is duplicate. Close with comment showing existing entries.

## Issue 1169 - blog.logrocket.com
- Labels: None
- Title: [Remove Request] - blog.logrocket.com
- Status: CLOSED (2024-10-09) - Not actionable

## Issue 1168 - nasa.gov
- Labels: None
- Title: remove nasa.gov from torrents
- Status: CLOSED (2025-05-11) - Not actionable

## Issue 1167 - (no domain specified)
- Labels: request:remove
- Title: [Remove Request] -
- Status: INVALID - Issue has empty domain field in title
- Decision: Cannot process without domain. Need user to edit issue with specific domain.

## Issue 1166 - pp.userapi.com
- Labels: request:remove
- Title: [Remove Request] - pp.userapi.com
- Status: VERIFIED - Domain resolves via DNS/HTTPS, NOT in crypto.txt
- Present in: ads.txt (0.0.0.0 pp.userapi.com)
- DNS: Resolves (verified)
- HTTPS: Returns 403 (blocked by server)
- Decision: In ads.txt which is correct for tracking. Removal from ads.txt would be appropriate if user confirms it's not tracking.

## Issue 1165 - tags.tiqcdn.com
- Labels: request:remove
- Title: [Remove Request] - tags.tiqcdn.com
- Status: VERIFIED - Domain resolves via DNS/HTTPS (200), NOT in crypto.txt
- Present in: ads.txt, basic.txt, everything.txt
- DNS: Resolves (verified)
- HTTPS: Returns 200
- Decision: Legitimate ad tracking domain - correctly in ads list. Removal from ads.txt would be appropriate if user confirms not tracking.

## Issue 1164 - cf.nordcurrent.com
- Labels: request:remove
- Title: [Remove Request] - cf.nordcurrent.com
- Status: VERIFIED - Domain resolves via DNS, NOT in crypto.txt
- Present in: ads.txt, basic.txt, everything.txt
- DNS: Resolves (verified)
- Decision: In ads.txt correctly. cf.nordcurrent.com is ad-serving subdomain. Removal from ads.txt would be appropriate if user confirms not tracking.

## Summary

### Issues Requiring Action:
| Issue | Action | Reason |
|-------|--------|--------|
| 1176 | CLOSE - INVALID | Domain doesn't resolve (DNS failure) |
| 1175 | CLOSE - DUPLICATE | Domain not in crypto list (already in correct lists) |
| 1174 | COMMENT - NEEDS INFO | Legitimate domain in multiple lists - confirm correct placement |
| 1173 | REMOVE - CORRECT | Legitimate government domain - remove from abuse/malware |
| 1172 | REMOVE - CORRECT | Legitimate tech site - remove from abuse/malware |
| 1171 | REMOVE - CORRECT | Legitimate forum - remove from abuse/malware |
| 1170 | CLOSE - DUPLICATE | Already in crypto.txt list |
| 1167 | CLOSE - INVALID | Empty domain field |
| 1166 | COMMENT - NEEDS INFO | In ads.txt - confirm if tracking domain |
| 1165 | COMMENT - NEEDS INFO | In ads.txt - confirm if tracking domain |
| 1164 | COMMENT - NEEDS INFO | In ads.txt - confirm if tracking domain |

### Next Steps:
1. Close invalid issues (1176, 1175, 1170, 1167)
2. Comment on issues needing info (1174, 1166, 1165, 1164)
3. Remove verified false positives (1173, 1172, 1171)
4. Update all affected lists and regenerate formats
