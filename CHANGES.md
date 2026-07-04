# Local Changes - 2026-06-28

These changes are pending review before committing:

## Changes Summary

### abuse.txt
- Removed: `ai.com` (likely false positive - ai.com is an active AI platform)

### ads.txt
- Removed: Comment line `#`
- Removed: `consent.cookiebot.com`
- Removed: `dc.trafficmanager.net`
- Added: `my.onetrust.com`, `mobile-data.onetrust.io`, `bzib.nelreports.net`, `clientfd.family.microsoft.com`

### malware.txt
- Removed: `ai.com` (same as abuse.txt - likely false positive)

### piracy.txt
- Added: `nullforums.net`

### tracking.txt
- Removed: `tracker2.itzmx.com`
- Added: `wwwstat.rz.uni-leipzig.de`, `uni.wwwstat.rz.uni-leipzig.de`, `rtnl.bxcl.de`

### porn.txt
- Added: `twitch.tv`, `camwhorez.tv`, `indianprn.com`, `rj2jzgv.brave-peter.de`, `thotbay.com`

### everything.txt
- Removed: 4 duplicate entries matching changes in other files

### alt-version/everything-nl.txt
- Removed: 1 entry matching changes in other files

## Analysis

1. **ai.com removal** - This appears to be a false positive. ai.com is a legitimate AI platform (AI.com by OpenAI). Should be removed from blocklists.

2. **nullforums.net** - Added to piracy list, matches issue #1160.

3. **twitch.tv and related domains** - Added to porn list. twitch.tv is a streaming platform that hosts adult content but is not exclusively pornographic. Should verify with issue #1136.

4. **tracker2.itzmx.com** - Removed from tracking list. Need to verify this is a false positive.

5. **OneTrust domains** - Added to ads list. These are consent management domains that should be in tracking list, not ads.

6. **rtnl.bxcl.de** - Added to tracking list. This is a known tracking domain for internet measurement.

## Recommendation

These changes should be reviewed against open issues and PRs before committing.
