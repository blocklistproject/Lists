const fs = require("fs").promises;
const path = require("path");

(async () => {
	const files = (await fs.readdir(path.join(__dirname, ".."))).filter((file) => file.endsWith(".txt")); // Array of strings, each representing a single file that ends in `.txt`
	await Promise.all(files.map(async (file) => { // For each file
		const fileContents = await fs.readFile(path.join(__dirname, "..", file), "utf8"); // Get file contents as a string
		const noIPFileContents = fileContents
		.replaceAll(/^0\.0\.0\.0 /gmu, "server=/") // Replace all occurances of "0.0.0.0 " at the beginning of the line with "server=/"
		.replaceAll(/^# 0\.0\.0\.0 /gmu, "# server=/") // Replace all occurances of "# 0.0.0.0 " at the beginning of the line with "# server=/"
		.replaceAll(/^(.*)$/gmu, "$0/") // I need this line to add "/" at the end of each URL
		.replace(/^# Title: (.*?)$/gmu, "# Title: $1 (NL)"); // Add (NL) to end of title
		await fs.writeFile(path.join(__dirname, "..", "dnsmasq-version", file.replace(".txt", "-dnsmasq.txt")), noIPFileContents, "utf8"); // Write new file to `alt-version` directory
	}));
})();
