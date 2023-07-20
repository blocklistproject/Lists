const fs = require("fs").promises;
const path = require("path");

(async () => {
	const files = (await fs.readdir(path.join(__dirname, ".."))).filter((file) => file.endsWith(".txt")); // Array of strings, each representing a single file that ends in `.txt`

	await Promise.all(files.map(async (file) => { // For each file
		const existingDomains = new Set();

		const fileContents = await fs.readFile(path.join(__dirname, "..", file), "utf8"); // Get file contents as a string

		fileContents.split("\n").forEach((line) => {
			if (line.startsWith("0.0.0.0 ")) {
				existingDomains.add(line.replace("0.0.0.0 ", ""));
			}
		});

		await fs.writeFile(path.join(__dirname, "..", file), fileContents.replace(/^# Total number of network filters: ?(\d*)$/gmu, `# Total number of network filters: ${existingDomains.size}`), "utf8");
	}));
})();
