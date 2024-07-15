<img src="https://raw.githubusercontent.com/blocklistproject/Lists/master/img/logo.webp" height="150px"/>  

# MAJOR UPDATE:
## We are moving forward with a merge of this project and a complete rewrite. As more details are available we will update the repo.

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
![Hits](https://hits.seeyoufarm.com/api/count/incr/badge.svg?url=https%3A%2F%2Fgithub.com%2Fblocklistproject%2FLists&count_bg=%2379C83D&title_bg=%23555555&icon=&icon_color=%23E7E7E7&title=Traffic+%28Daily%2FTotal%29&edge_flat=false)

&nbsp;

## Make sure to join our discord! This project does take a fair amount of time to maintain. Please consider joining our patreon and help support our efforts, thank you!

&nbsp;

<p align="center">
<a href="https://www.patreon.com/bePatron?u=8892646"><img src="https://i0.wp.com/thelemicunion.com/wp-content/uploads/2018/07/Patreon-Support-Button.png?w=640&ssl=1" width=250></a>
<a href="https://ulnk.it/blp-discord"><img src="https://discord.com/assets/ff41b628a47ef3141164bfedb04fb220.png" width=250 /></a>
</p>
&nbsp;

&nbsp;

- [Details](#details)
- [Versions](#versions)
- [Usage](#usage)
- [Lists](#lists)
- [Using with Pi-hole](#pi-hole-instructions)
- [Using with other tools](#using-with-other-tools)
- [Sponsors](#sponsors)
- [License](#license)

&nbsp;

# Details:

These lists were created because the founder of the project wanted something with a little more control over what is being blocked. Many lists out there are all or nothing. We set out to create lists with more control over what is being blocked and believe that we have accomplished that. 

&nbsp;

# Versions:

<details>
<summary>Original Version:</summary>

<Original>&nbsp;All urls in the version of the list are listed in the host file as follows</Original>

<p>  &nbsp;&nbsp;0.0.0.0 example.com</p>
</details>
&nbsp;
<details>
<summary>No Leading 0s Version:</summary>

<p>&nbsp;All urls in this version of the list are listed in the host file as follows</p>

<p>  &nbsp;&nbsp;example.com</p>

Our users brought it to our attention that some devices error out if the url is preceded by an IP address.

</details>
&nbsp;
<details>
<summary>DNSMASQ Version:</summary>

<p>&nbsp;All urls in this version of the list are listed in the host file as follows</p>

<p>  &nbsp;&nbsp;server=/example.com/</p>

It was requested to add support for dnsmasq. Please provide feedback.

</details>
&nbsp;
<details>
<summary>Adguard Version:</summary>

<p>&nbsp;All urls in this version of the list are listed in the host file as follows</p>

<p>  &nbsp;&nbsp;||example.com^</p>

It was requested to add support for AdGuard. We are currently testing our lists. Please provide feedback.

</details>
&nbsp;

# Usage:

<details>
    <summary>Using with <a href="https://pi-hole.net" target="_blank">Pi-Hole</a>:</summary>

## Pi-Hole instructions:

1. Copy the link to the Pi-hole format ('Original') for the desired list (from the appropriate table below).
2. Add the URL to your Pi-hole's block lists (**Login** > **Group Management** > **Adlists** > **Paste list URL in "Address" field, add comment** > **Click "Add"**)
3. Update Gravity (**Tools** > **Update Gravity** > **Click "Update"** )

&nbsp;
<sup>Instructions current as of Pi-hole 5.2.4. Instructions may currently be slightly different. Instructions will be updated once ver. 6 is release. Thank you</sup>

</details>
&nbsp;
<details>
    <summary>Using with <a href="https://adguard.com/en/adguard-home/overview.html">AdGuard Home</a>:</summary>

## AdGuard instructions:

1. Copy the link to the AdGuard format for the desired list (from the appropriate table below).
2. Add the URL to you AdGuard's block list (**Login** > **Filters** > **DNS Blocklists** > **Add blocklist** > **Add a custom list** > **Enter Name** > **Paste copied link URL**)
3. List is automatically enabled and ready to start blocking.

&nbsp;
<sup>Instructions are current as of AdGuard Home version 0.106.3</sup>

</details>
&nbsp;

# Lists:

&nbsp;

## Main Lists

| List       | Original                                                        | No IP                                                                          | DNSMASQ                                                                                 | AdGuard <br> <sup>BETA</sup>                                                | Description                                                                                              |
| ---------- | --------------------------------------------------------------- | ------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------- | --------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------- |
| Abuse      | [Link](https://blocklistproject.github.io/Lists/abuse.txt)      | [Link](https://blocklistproject.github.io/Lists/alt-version/abuse-nl.txt)      | [Link](https://blocklistproject.github.io/Lists/dnsmasq-version/abuse-dnsmasq.txt)      | [Link](https://blocklistproject.github.io/Lists/adguard/abuse-ags.txt)      | Lists of sites created to deceive                                                                        |
| Ads        | [Link](https://blocklistproject.github.io/Lists/ads.txt)        | [Link](https://blocklistproject.github.io/Lists/alt-version/ads-nl.txt)        | [Link](https://blocklistproject.github.io/Lists/dnsmasq-version/ads-dnsmasq.txt)        | [Link](https://blocklistproject.github.io/Lists/adguard/ads-ags.txt)        | Ad servers / sites                                                                                       |
| Crypto     | [Link](https://blocklistproject.github.io/Lists/crypto.txt)     | [Link](https://blocklistproject.github.io/Lists/alt-version/crypto-nl.txt)     | [Link](https://blocklistproject.github.io/Lists/dnsmasq-version/crypto-dnsmasq.txt)     | [Link](https://blocklistproject.github.io/Lists/adguard/crypto-ags.txt)     | Crypto / cryptojacking based sites <br> <sup>Can break normal "good" crypto sites</sup>                  |
| Drugs      | [Link](https://blocklistproject.github.io/Lists/drugs.txt)      | [Link](https://blocklistproject.github.io/Lists/alt-version/drugs-nl.txt)      | [Link](https://blocklistproject.github.io/Lists/dnsmasq-version/drugs-dnsmasq.txt)      | [Link](https://blocklistproject.github.io/Lists/adguard/drugs-ags.txt)      | RE sites that deal with illegal drugs <br><sub>Including RX drugs illegal to posses in the US</sub>      |
| Everything | [Link](https://blocklistproject.github.io/Lists/everything.txt) | [Link](https://blocklistproject.github.io/Lists/alt-version/everything-nl.txt) | [Link](https://blocklistproject.github.io/Lists/dnsmasq-version/everything-dnsmasq.txt) | [Link](https://blocklistproject.github.io/Lists/adguard/everything-ags.txt) | List including all non beta list domains                                                                 |
| Facebook   | [Link](https://blocklistproject.github.io/Lists/facebook.txt)   | [Link](https://blocklistproject.github.io/Lists/alt-version/facebook-nl.txt)   | [Link](https://blocklistproject.github.io/Lists/dnsmasq-version/facebook-dnsmasq.txt)   | [Link](https://blocklistproject.github.io/Lists/adguard/facebook-ags.txt)   | Block FB and FB related / owned services                                                                 |
| Fraud      | [Link](https://blocklistproject.github.io/Lists/fraud.txt)      | [Link](https://blocklistproject.github.io/Lists/alt-version/fraud-nl.txt)      | [Link](https://blocklistproject.github.io/Lists/dnsmasq-version/fraud-dnsmasq.txt)      | [Link](https://blocklistproject.github.io/Lists/adguard/fraud-ags.txt)      | Sites created to defraud                                                                                    |
| Gambling   | [Link](https://blocklistproject.github.io/Lists/gambling.txt)   | [Link](https://blocklistproject.github.io/Lists/alt-version/gambling-nl.txt)   | [Link](https://blocklistproject.github.io/Lists/dnsmasq-version/gambling-dnsmasq.txt)   | [Link](https://blocklistproject.github.io/Lists/adguard/gambling-ags.txt)   | All gambling based site legit and illegal                                                                |
| Malware    | [Link](https://blocklistproject.github.io/Lists/malware.txt)    | [Link](https://blocklistproject.github.io/Lists/alt-version/malware-nl.txt)    | [Link](https://blocklistproject.github.io/Lists/dnsmasq-version/malware-dnsmasq.txt)    | [Link](https://blocklistproject.github.io/Lists/adguard/malware-ags.txt)    | Known sites that host malware                                                                            |
| Phishing   | [Link](https://blocklistproject.github.io/Lists/phishing.txt)   | [Link](https://blocklistproject.github.io/Lists/alt-version/phishing-nl.txt)   | [Link](https://blocklistproject.github.io/Lists/dnsmasq-version/phishing-dnsmasq.txt)   | [Link](https://blocklistproject.github.io/Lists/adguard/phishing-ags.txt)   | Sites created to phish info                                                                              |
| Piracy     | [Link](https://blocklistproject.github.io/Lists/piracy.txt)     | [Link](https://blocklistproject.github.io/Lists/alt-version/piracy-nl.txt)     | [Link](https://blocklistproject.github.io/Lists/dnsmasq-version/piracy-dnsmasq.txt)     | [Link](https://blocklistproject.github.io/Lists/adguard/piracy-ags.txt)     | Known sites that allow for illegal downloads                                                             |
| Porn       | [Link](https://blocklistproject.github.io/Lists/porn.txt)       | [Link](https://blocklistproject.github.io/Lists/alt-version/porn-nl.txt)       | [Link](https://blocklistproject.github.io/Lists/dnsmasq-version/porn-dnsmasq.txt)       | [Link](https://blocklistproject.github.io/Lists/adguard/porn-ags.txt)       | Porn or sites that promote porn                                                                          |
| Ransomware | [Link](https://blocklistproject.github.io/Lists/ransomware.txt) | [Link](https://blocklistproject.github.io/Lists/alt-version/ransomware-nl.txt) | [Link](https://blocklistproject.github.io/Lists/dnsmasq-version/ransomware-dnsmasq.txt) | [Link](https://blocklistproject.github.io/Lists/adguard/ransomware-ags.txt) | Known sites that host or contain ransomware                                                              |
| Redirect   | [Link](https://blocklistproject.github.io/Lists/redirect.txt)   | [Link](https://blocklistproject.github.io/Lists/alt-version/redirect-nl.txt)   | [Link](https://blocklistproject.github.io/Lists/dnsmasq-version/redirect-dnsmasq.txt)   | [Link](https://blocklistproject.github.io/Lists/adguard/redirect-ags.txt)   | Sites that redirect you from your intended site                                                         |
| Scam       | [Link](https://blocklistproject.github.io/Lists/scam.txt)       | [Link](https://blocklistproject.github.io/Lists/alt-version/scam-nl.txt)       | [Link](https://blocklistproject.github.io/Lists/dnsmasq-version/scam-dnsmasq.txt)       | [Link](https://blocklistproject.github.io/Lists/adguard/scam-ags.txt)       | Sites that intend to scam                                                                                |
| TikTok     | [Link](https://blocklistproject.github.io/Lists/tiktok.txt)     | [Link](https://blocklistproject.github.io/Lists/alt-version/tiktok-nl.txt)     | [Link](https://blocklistproject.github.io/Lists/dnsmasq-version/tiktok-dnsmasq.txt)     | [Link](https://blocklistproject.github.io/Lists/adguard/tiktok-ags.txt)     | Copy and pasted into your device                                                                         |
| Torrent    | [Link](https://blocklistproject.github.io/Lists/torrent.txt)    | [Link](https://blocklistproject.github.io/Lists/alt-version/torrent-nl.txt)    | [Link](https://blocklistproject.github.io/Lists/dnsmasq-version/torrent-dnsmasq.txt)    | [Link](https://blocklistproject.github.io/Lists/adguard/torrent-ags.txt)    | Torrent directory <br> <sub>Will likely block legit torrent sites used for legal software download</sub> |
| Tracking   | [Link](https://blocklistproject.github.io/Lists/tracking.txt)   | [Link](https://blocklistproject.github.io/Lists/alt-version/tracking-nl.txt)   | [Link](https://blocklistproject.github.io/Lists/dnsmasq-version/tracking-dnsmasq.txt)   | [Link](https://blocklistproject.github.io/Lists/adguard/tracking-ags.txt)   | Sites dedicated to tracking and gathering visitor info                                                   |

&nbsp;

## Beta Lists

| List             | Original                                                      | No IP                                                                        | dnsmasq                                                                               | Description                                            |
| ---------------- | ------------------------------------------------------------- | ---------------------------------------------------------------------------- | ------------------------------------------------------------------------------------- | ------------------------------------------------------ |
| Smart TV         | [Link](https://blocklistproject.github.io/Lists/smart-tv.txt) | [Link](https://blocklistproject.github.io/Lists/alt-version/smart-tv-nl.txt) | [Link](https://blocklistproject.github.io/Lists/dnsmasq-version/smart-tv-dnsmasq.txt) | Smart TV call home and ads                             |
| Basic Start List | [Link](https://blocklistproject.github.io/Lists/basic.txt)    | [Link](https://blocklistproject.github.io/Lists/alt-version/basic-nl.txt)    | [Link](https://blocklistproject.github.io/Lists/dnsmasq-version/basic-dnsmasq.txt)    | Just a quick basic starter list                        |
| WhatsApp List    | [Link](https://blocklistproject.github.io/Lists/whatsapp.txt) | [Link](https://blocklistproject.github.io/Lists/alt-version/whatsapp-nl.txt) | [Link](https://blocklistproject.github.io/Lists/dnsmasq-version/whatsapp-dnsmasq.txt) | User requested list that blocks only WhatsApp          |
| Vaping list      | [Link](https://blocklistproject.github.io/Lists/vaping.txt)   | [Link](https://blocklistproject.github.io/Lists/alt-version/vaping-nl.txt)   | [Link](https://blocklistproject.github.io/Lists/dnsmasq-version/vaping-dnsmasq.txt)   | User requested list that blocks sites promoting vaping |

&nbsp;

## Alpha Lists

| List  | Original                                                   | No IP                                                                     | dnsmasq                                                                            | Description     |
| ----- | ---------------------------------------------------------- | ------------------------------------------------------------------------- | ---------------------------------------------------------------------------------- | --------------- |
| Adobe | [Link](https://blocklistproject.github.io/Lists/adobe.txt) | [Link](https://blocklistproject.github.io/Lists/alt-version/adobe-nl.txt) | [Link](https://blocklistproject.github.io/Lists/dnsmasq-version/adobe-dnsmasq.txt) | Adobe Telemetry |

&nbsp;

## Deprecated Lists

| List    | Description                                                  | Deletion date (dd.mm.yyyy) |
| ------- | ------------------------------------------------------------ | -------------------------- |
| YouTube | This lists was removed due to the way YouTube serves its ads | 01.10.2021                 |

<sup>\*Not supported by or affiliated with Pi-hole.</sup>

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
