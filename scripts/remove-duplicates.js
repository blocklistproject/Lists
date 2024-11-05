const fs = require("node:fs").promises;
const path = require("node:path");

(async () => {
	try {
		// Define the base directory containing .txt files
		const directoryPath = path.join(__dirname, "..");

		// Retrieve all .txt files in the directory
		const files = (await fs.readdir(directoryPath)).filter((file) =>
			file.endsWith(".txt")
		);

		// Process each file concurrently
		await Promise.all(
			files.map(async (file) => {
				const filePath = path.join(directoryPath, file);
				const fileContents = await fs.readFile(filePath, "utf8");

				// Initialize a Set to keep track of unique domains
				const existingDomains = new Set();
				const filteredLines = fileContents
					.split("\n")
					.filter((line) => {
						// Filter duplicate "0.0.0.0" entries
						if (line.startsWith("0.0.0.0 ")) {
							const domain = line.slice(8); // Extract domain after "0.0.0.0 "
							if (existingDomains.has(domain)) {
								return false; // Exclude duplicate
							}
							existingDomains.add(domain); // Add unique domain to Set
						}
						return true; // Include non-duplicate or non-"0.0.0.0" lines
					});

				// Write the filtered content back to the file
				await fs.writeFile(filePath, filteredLines.join("\n"), "utf8");

				console.log(`Processed and removed duplicates in: ${file}`);
			})
		);

		console.log("All files processed successfully.");
	} catch (error) {
		console.error("Error processing files:", error);
	}
})();
