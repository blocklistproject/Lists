# The Block List Project

![GitHub issues](https://img.shields.io/github/issues/blocklistproject/Lists?style=for-the-badge)
![GitHub closed issues](https://img.shields.io/github/issues-closed/blocklistproject/Lists?style=for-the-badge)
[![License: Unlicense](https://img.shields.io/badge/license-Unlicense-blue.svg?style=for-the-badge)](http://unlicense.org/)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg?style=for-the-badge)](https://github.com/blocklistproject/Lists/graphs/commit-activity)
![GitHub contributors](https://img.shields.io/github/contributors/blocklistproject/lists?style=for-the-badge)
![GitHub commit activity](https://img.shields.io/github/commit-activity/m/blocklistproject/lists?style=for-the-badge)
![Opensource-info](https://img.shields.io/badge/Open%20Source-Yes-red?style=for-the-badge)
[![ko-fi](https://img.shields.io/badge/Support%20Us-Ko--Fi-orange?style=for-the-badge)](https://ko-fi.com/P5P521OPP)
![GitHub repo size](https://img.shields.io/github/repo-size/blocklistproject/Lists?style=for-the-badge)

&nbsp;

# We are slowly but surely moving away from [Patreon](https://www.patreon.com/bePatron?u=8892646).

Please see below our crypto addresses:

| Ethereum | Algorand | Basic Attention Token | Bitcoin | ZCash | Dash |
| :-------------: | :-------------: | :-------------: | :-------------: | :-------------: | :-------------: |
| <img src="https://blocklistproject.github.io/Lists/img/eth-qr-code.png" width="125"> | <img src="https://blocklistproject.github.io/Lists/img/algo-qr-code.png" width="125"> | <img src="https://blocklistproject.github.io/Lists/img/bat-qr-code.png" width="125"> | <img src="https://blocklistproject.github.io/Lists/img/btc-qr-code.png" width="125"> | <img src="https://blocklistproject.github.io/Lists/img/zcash-qr-code.png" width="125"> | <img src="https://blocklistproject.github.io/Lists/img/dash-qr-code.png" width="125"> |

As we move away from Patreon we are also changing our crypto payment addresses to a more secure Hardware wallet ([Ledger](https://shop.ledger.com/pages/ledger-nano-x?r=f60e80a16431&tracker=github)<--Click here to learn more about Ledger and support the Block List Project).

[Become a Patron](https://www.patreon.com/bePatron?u=8892646)

&nbsp;

- [Details](#details)
- [Updates](#updates)
- [Versions](#versions)
- [Usage](#usage)
- [Lists](#lists)
- [Using with Pi-hole](#using-with-pi-hole)
- [Using with other tools](#using-with-other-tools)
- [Sponsors](#sponsors)
- [License](#license)

&nbsp;

# Details:

These lists were created because the founder of the project wanted something with a little more control over what is being blocked. Many lists are all or nothing. We set out to create lists with more control over what is being blocked.

&nbsp;

## Updates:

As of right now, the "everything" and "everything-nl" lists are NOT being updated. Please update your devices accordingly.

&nbsp;

## Versions:

We have recently created an alternative version (alt-version) of our lists.

<p>Original Version:</p>

<p>&nbsp;All urls in the version of the list are listed in the host file as follows</p>

<p>  &nbsp;&nbsp;0.0.0.0 example.com</p>

<p>Alternative Version:</p>

<p>&nbsp;All urls in this version of the list are listed in the host file as follows</p>

<p>  &nbsp;&nbsp;example.com</p>

Our users brought it to our attention that some devices error out if the url is preceded by an IP address.

&nbsp;

# Usage:

These converted files can be used with various DNS and domain-blocking tools:

## Using with [Pi-hole](https://pi-hole.net/):

1. Copy the link to the Pi-hole format for the desired list (from the appropriate table below).
2. Add the URL to your Pi-hole's block lists (**Login** > **Group Management** > **Adlists** > **Paste list URL in "Address" field, add comment** > **Click "Add"**)
3. Update Gravity (**Tools** > **Update Gravity** > **Click "Update"** )

&nbsp;

# Lists:

## Main Lists

| List | Link | Link w/o leading IP | Description | Sponsor<sup>&#8224;</sup> |
|--|--|--| -- | -- |
| Abuse| [GitHub Pages Link](https://blocklistproject.github.io/Lists/abuse.txt) | [GitHub Pages Link](https://blocklistproject.github.io/Lists/alt-version/abuse-nl.txt) | Lists of sites created to deceive |Armstrong|
| Ads| [GitHub Pages Link](https://blocklistproject.github.io/Lists/ads.txt) | [GitHub Pages Link](https://blocklistproject.github.io/Lists/alt-version/ads-nl.txt) | Ad servers/sites ||
| Crypto| [GitHub Pages Link](https://blocklistproject.github.io/Lists/crypto.txt) | [GitHub Pages Link](https://blocklistproject.github.io/Lists/alt-version/crypto-nl.txt) | Crypto/cryptojacking based sites <br> <sup>Can break normal "good" crypto sites</sup> ||
| Drugs| [GitHub Pages Link](https://blocklistproject.github.io/Lists/drugs.txt) | [GitHub Pages Link](https://blocklistproject.github.io/Lists/alt-version/drugs-nl.txt) | RE sites that deal with illegal drugs <br><sub>Including RX drugs illegal to posses in the US</sub> ||
| Facebook| [GitHub Pages Link](https://blocklistproject.github.io/Lists/facebook.txt) | [GitHub Pages Link](https://blocklistproject.github.io/Lists/alt-version/facebook-nl.txt) | Block FB and FB relate/owned services ||
| Fraud| [GitHub Pages Link](https://blocklistproject.github.io/Lists/fraud.txt) | [GitHub Pages Link](https://blocklistproject.github.io/Lists/alt-version/fraud-nl.txt) | Sites create to fraud ||
| Gambling| [GitHub Pages Link](https://blocklistproject.github.io/Lists/gambling.txt) | [GitHub Pages Link](https://blocklistproject.github.io/Lists/alt-version/gambling-nl.txt) | All gambling based site legit and illegal ||
| Malware| [GitHub Pages Link](https://blocklistproject.github.io/Lists/malware.txt) | [GitHub Pages Link](https://blocklistproject.github.io/Lists/alt-version/malware-nl.txt) | Known sites that host malware ||
| Phishing| [GitHub Pages Link](https://blocklistproject.github.io/Lists/phishing.txt) | [GitHub Pages Link](https://blocklistproject.github.io/Lists/alt-version/phishing-nl.txt) | Sites created to phish info ||
| Piracy| [GitHub Pages Link](https://blocklistproject.github.io/Lists/piracy.txt) | [GitHub Pages Link](https://blocklistproject.github.io/Lists/alt-version/piracy-nl.txt) | Knows sites that allow for illegal downloads ||
| Porn| [GitHub Pages Link](https://blocklistproject.github.io/Lists/porn.txt) | [GitHub Pages Link](https://blocklistproject.github.io/Lists/alt-version/porn-nl.txt)| Porn or sites that promote porn |[W1T3H4T](https://www.patreon.com/user/creators?u=26512074)|
| Ransomware| [GitHub Pages Link](https://blocklistproject.github.io/Lists/ransomware.txt) | [GitHub Pages Link](https://blocklistproject.github.io/Lists/alt-version/ransomware-nl.txt) | Known sites that host or contain ransomware ||
| Redirect| [GitHub Pages Link](https://blocklistproject.github.io/Lists/redirect.txt) | [GitHub Pages Link](https://blocklistproject.github.io/Lists/alt-version/redirect-nl.txt) | Sites that redirect your from your intended site ||
| Scam| [GitHub Pages Link](https://blocklistproject.github.io/Lists/scam.txt) | [GitHub Pages Link](https://blocklistproject.github.io/Lists/alt-version/scam-nl.txt) | Sites that intend to scam ||
| TikTok| [GitHub Pages Link](https://blocklistproject.github.io/Lists/tiktok.txt) | [GitHub Pages Link](https://blocklistproject.github.io/Lists/alt-version/tiktok-nl.txt) | Copy and pasted into your device ||
| Torrent| [GitHub Pages Link](https://blocklistproject.github.io/Lists/torrent.txt) | [GitHub Pages Link](https://blocklistproject.github.io/Lists/alt-version/torrent-nl.txt) | Torrent directory <br> <sub>Will likely block legit torrent sites used for legal software download</sub> ||
| Tracking| [GitHub Pages Link](https://blocklistproject.github.io/Lists/tracking.txt) | [GitHub Pages Link](https://blocklistproject.github.io/Lists/alt-version/tracking-nl.txt) | Sites dedicated to tracking and gathering visitor info ||
| Youtube| [GitHub Pages Link](https://blocklistproject.github.io/Lists/youtube.txt) | [GitHub Pages Link](https://blocklistproject.github.io/Lists/alt-version/youtube-nl.txt) | <sub><sup>This list is not updated and will likely be removed</sup></sub> |[the_c_drive](https://www.patreon.com/user/creators?u=5538103)|

## Beta Lists

| List | Link | Link w/o leading IP | Description | Sponsor<sup>&#8224;</sup> |
|--|--|--| -- | -- |
| Smart TV| [GitHub Pages Link](https://blocklistproject.github.io/Lists/smart-tv.txt) | [GitHub Pages Link](https://blocklistproject.github.io/Lists/alt-version/smart-tv-nl.txt) | Smart TV call home and ads ||  

<sup>Instructions current as of Pi-hole 5.1.2

*Not supported by or affiliated with Pi-hole.</sup>

&nbsp;

<sup>&#8224; A sponsor is someone that supports us on Patreon. All list are free and will always be free. This is just a way to say thank you to those that help keep this project going! </sup>

## Using with other tools:

We are currently working on verifying compatibility with other tools. Please stand by. If you have a suggestion on a tool we should support please comment on our [Reddit](https://www.reddit.com/r/blocklistproject/) page.

## Sponsors:

Special thank you to [Cloud 4 SURE](https://www.cloud4sure.net) for their generous donation every month to help cover our Linode bill.

# License:

For more details, see the [LICENSE](https://github.com/blocklistproject/Lists/blob/master/LICENSE) file.

&nbsp;

<sup>These files are provided "AS IS", without warranty of any kind, express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose and noninfringement. In no event shall the authors or copyright holders be liable for any claim, damages or other liability, arising from, out of or in connection with the files or the use of the files.</sup>

<sub>Any and all trademarks are the property of their respective owners.</sub>
