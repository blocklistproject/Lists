const fs = require("fs").promises;
const path = require("path");

(async () => {
	const directory = path.join(__dirname, "..");
	const files = (await fs.readdir(directory)).filter((file) => file.endsWith(".txt"));

	await Promise.all(
		files.map(async (file) => {
			const existingDomains = new Set();
			const filePath = path.join(directory, file);

			const lines = await fs.readFile(filePath, "utf8");
			const updatedLines = lines
				.split("\n")
				.filter((line) => {
					if (line.startsWith("0.0.0.0 ")) {
						const domain = line.replace("0.0.0.0 ", "");
						if (existingDomains.has(domain)) {
							return false;
						}
						existingDomains.add(domain);
					}
					return true;
				})
				.join("\n");

			await fs.writeFile(filePath, updatedLines, "utf8");
		})
	);
})();
