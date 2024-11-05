const fs = require("node:fs").promises;
const path = require("node:path");

// Lists to include in the "everything" list
const listsToIncludeInEverythingList = [
	"abuse", "ads", "crypto", "drugs", "facebook", "fraud",
	"gambling", "malware", "phishing", "piracy", "porn",
	"ransomware", "redirect", "scam", "tiktok", "torrent", "tracking",
	// Beta lists (excluded from "everything" list)
	// "smart-tv", "basic", "whatsapp", "vaping"
];

(async () => {
	try {
		const baseDir = path.join(__dirname, "..");

		// Filter and collect relevant .txt files
		const files = (await fs.readdir(baseDir)).filter((file) =>
			file.endsWith(".txt") &&
			listsToIncludeInEverythingList.some((prefix) => file.startsWith(prefix))
		);

		// Use a Set to store unique domains
		const domains = new Set();

		// Process each file to extract domains
		await Promise.all(
			files.map(async (file) => {
				const filePath = path.join(baseDir, file);
				const fileContents = await fs.readFile(filePath, "utf8");

				// Extract domains starting with "0.0.0.0"
				fileContents.split("\n").forEach((line) => {
					if (line.startsWith("0.0.0.0 ")) {
						domains.add(line.slice(8)); // Add the domain after "0.0.0.0 "
					}
				});
			})
		);

		// Generate content for the "everything" list
		const header = `# ------------------------------------[UPDATE]--------------------------------------
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

		// Concatenate domains into a single list with the header
		const everythingListContent = `${header}${Array.from(domains)
			.map((domain) => `0.0.0.0 ${domain}`)
			.join("\n")}\n`;

		// Write the final "everything" list file
		const outputFilePath = path.join(baseDir, "everything.txt");
		await fs.writeFile(outputFilePath, everythingListContent, "utf8");

		console.log("Everything list generated successfully.");
	} catch (error) {
		console.error("Error processing files:", error);
	}
})();
