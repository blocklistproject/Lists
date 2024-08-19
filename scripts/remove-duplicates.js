const fs = require("fs").promises;
const path = require("path");

(async () => {
	try {
		const directoryPath = path.join(__dirname, "..");
		const files = (await fs.readdir(directoryPath)).filter(file => file.endsWith(".txt"));

		await Promise.all(files.map(async file => {
			const filePath = path.join(directoryPath, file);
			let fileContents = await fs.readFile(filePath, "utf8");

			const lines = fileContents.split("\n");
			const existingDomains = new Set();
			const filteredLines = [];

			lines.forEach(line => {
				if (line.startsWith("0.0.0.0 ")) {
					const domain = line.replace("0.0.0.0 ", "");
					if (!existingDomains.has(domain)) {
						existingDomains.add(domain);
						filteredLines.push(line);
					}
				} else {
					filteredLines.push(line);
				}
			});

			// Combine the filtered lines back into a single string
			const updatedContents = filteredLines.join("\n");

			await fs.writeFile(filePath, updatedContents, "utf8");
		}));
	} catch (error) {
		console.error("Error processing files:", error);
	}
})();
