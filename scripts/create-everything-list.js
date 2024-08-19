const fs = require("fs").promises;
const path = require("path");

const listsToIncludeInEverythingList = [
	"abuse",
	"ads",
	"crypto",
	"drugs",
	"facebook",
	"fraud",
	"gambling",
	"malware",
	"phishing",
	"piracy",
	"porn",
	"ransomware",
	"redirect",
	"scam",
	"tiktok",
	"torrent",
	"tracking",

	// The following lists are in beta and therefore not included in the everything list:

	// "smart-tv",
	// "basic",
	// "whatsapp",
	// "vaping"
];

(async () => {
	const files = (await fs.readdir(path.join(__dirname, ".."))).filter((file) => file.endsWith(".txt")).filter((file) => listsToIncludeInEverythingList.some((val) => file.startsWith(val))); // Array of strings, each representing a single file that ends in `.txt`

	const domains = new Set();

	await Promise.all(files.map(async (file) => { // For each file

		const fileContents = await fs.readFile(path.join(__dirname, "..", file), "utf8"); // Get file contents as a string

		fileContents.split("\n").forEach((line) => {
			if (line.startsWith("0.0.0.0 ")) {
				domains.add(line.replace("0.0.0.0 ", ""));
			}
		});
	}));

	let everythingListContent =
`# ------------------------------------[UPDATE]--------------------------------------
# Title: The Block List Project - Everything List
# Expires: 1 day
# Homepage: https://blocklistproject.github.io/Lists/
# Help: https://github.com/blocklistproject/lists/wiki/
# License: https://unlicense.org
# Total number of network filters:
# ------------------------------------[SUPPORT]-------------------------------------
# You can support by:
# - reporting false positives
# - making a donation via paypal: https://paypal.me/blocklistproject
# - making a donation via patreon: https://www.patreon.com/theblocklistproject
# -------------------------------------[INFO]---------------------------------------
#
# Everything list
# ------------------------------------[FILTERS]-------------------------------------
`;
	domains.forEach((val) => everythingListContent += `0.0.0.0 ${val}\n`);

	await fs.writeFile(path.join(__dirname, "..", "everything.txt"), everythingListContent, "utf8");
})();
