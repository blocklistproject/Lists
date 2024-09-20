const fs = require("node:fs").promises;
const path = require("node:path");

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
	try {
		const files = (await fs.readdir(path.join(__dirname, ".."))).filter(
			(file) =>
				file.endsWith(".txt") &&
				listsToIncludeInEverythingList.some((val) => file.startsWith(val)),
		);
		const domains = new Set();

		await Promise.all(
			files.map(async (file) => {
				const fileContents = await fs.readFile(
					path.join(__dirname, "..", file),
					"utf8",
				);
				for (const line of fileContents.split("\n")) {
					if (line.startsWith("0.0.0.0 ")) {
						domains.add(line.replace("0.0.0.0 ", ""));
					}
				}
			}),
		);

		let everythingListContent = `# ------------------------------------[UPDATE]--------------------------------------
# Title: The Block List Project - Everything List
# Expires: 1 day
# Homepage: https://blocklistproject.github.io/Lists/
# Help: https://github.com/blocklistproject/lists/wiki/
# License: https://unlicense.org
# Total number of network filters: ${domains.size}
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

		for (const val of domains) {
			everythingListContent += `0.0.0.0 ${val}\n`;
		}

		await fs.writeFile(
			path.join(__dirname, "..", "everything.txt"),
			everythingListContent,
			"utf8",
		);
	} catch (error) {
		console.error("Error processing files:", error);
	}
})();
