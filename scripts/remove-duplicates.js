const fs = require("node:fs").promises;
const path = require("node:path");

(async () => {
	try {
		const directoryPath = path.join(__dirname, "..");
		const files = (await fs.readdir(directoryPath)).filter((file) =>
			file.endsWith(".txt"),
		);

		await Promise.all(
			files.map(async (file) => {
				const filePath = path.join(directoryPath, file);
				const fileContents = await fs.readFile(filePath, "utf8");

				const lines = fileContents.split("\n");
				const existingDomains = new Set();
				const filteredLines = lines.filter((line) => {
					if (line.startsWith("0.0.0.0 ")) {
						const domain = line.replace("0.0.0.0 ", "");
						if (!existingDomains.has(domain)) {
							existingDomains.add(domain);
							return true;
						}
						return false;
					}
					return true;
				});

				await fs.writeFile(filePath, filteredLines.join("\n"), "utf8");
			}),
		);
	} catch (error) {
		console.error("Error processing files:", error);
	}
})();
