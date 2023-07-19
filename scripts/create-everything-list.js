const fs = require("fs").promises;
const path = require("path");

const listsToIncludeInEverythingList = [
	"abuse",
	"ads",
	"crypto",
	// ... (rest of the lists)
];

async function optimizeEverythingList() {
	const files = (await fs.readdir(path.join(__dirname, "..")))
		.filter((file) => file.endsWith(".txt"))
		.filter((file) => listsToIncludeInEverythingList.some((val) => file.startsWith(val)));

	const domains = new Set();

	await Promise.all(
		files.map(async (file) => {
			const fileContents = await fs.readFile(path.join(__dirname, "..", file), "utf8");
			fileContents.split("\n").forEach((line) => {
				if (line.startsWith("0.0.0.0 ")) {
					domains.add(line.slice(8)); // Using slice instead of replace to remove "0.0.0.0 "
				}
			});
		})
	);

	let everythingListContent = `# ------------------------------------[UPDATE]--------------------------------------
# Title: The Block List Project - Everything List
# Expires: 1 day
# Homepage: https://blocklist.site
# Help: https://github.com/blocklistproject/lists/wiki/
# License: https://unlicense.org
# Total number of network filters:
# ------------------------------------[SUPPORT]-------------------------------------
# You can support by:
# - reporting false positives
# - making a donation: https://paypal.me/blocklistproject
# -------------------------------------[INFO]---------------------------------------
#
# Everything list
# ------------------------------------[FILTERS]-------------------------------------\n`;

	everythingListContent += Array.from(domains, (val) => `0.0.0.0 ${val}`).join("\n");

	await fs.writeFile(path.join(__dirname, "..", "everything.txt"), everythingListContent, "utf8");
}

optimizeEverythingList();
