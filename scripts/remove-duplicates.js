const fs = require("fs").promises;
const path = require("path");

(async () => {
	const files = (await fs.readdir(path.join(__dirname, ".."))).filter((file) => file.endsWith(".txt")); // Array of strings, each representing a single file that ends in `.txt`

	await Promise.all(files.map(async (file) => { // For each file
		const existingDomains = new Set();

		let fileContents = await fs.readFile(path.join(__dirname, "..", file), "utf8"); // Get file contents as a string

		fileContents.split("\n").forEach((line) => {
			if (line.startsWith("0.0.0.0 ")) {
				const domain = line.replace("0.0.0.0 ", "");
				if (existingDomains.has(domain)) {
					fileContents = fileContents.replace(`${line}\n`, "");
				}
				existingDomains.add(domain);
			}
		});

		await fs.writeFile(path.join(__dirname, "..", file), fileContents, "utf8");
	}));
})();
