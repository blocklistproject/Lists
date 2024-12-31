const fs = require("node:fs").promises;
const path = require("node:path");

(async () => {
	try {
		// Define the base directory containing .txt files
		const directoryPath = path.join(__dirname, "..");

		// Retrieve all .txt files from the directory
		const files = (await fs.readdir(directoryPath)).filter((file) =>
			file.endsWith(".txt")
		);

		// Process each file concurrently
		await Promise.all(
			files.map(async (file) => {
				const filePath = path.join(directoryPath, file);
				const fileContents = await fs.readFile(filePath, "utf8");

				// Extract unique domains starting with "0.0.0.0"
				const existingDomains = new Set(
					fileContents
						.split("\n")
						.filter((line) => line.startsWith("0.0.0.0 "))
						.map((line) => line.slice(8)) // Extract domain after "0.0.0.0 "
				);

				// Update the total number of network filters
				const updatedContents = fileContents.replace(
					/^# Total number of network filters: ?\d*$/m,
					`# Total number of network filters: ${existingDomains.size}`
				);

				// Write the updated content back to the file
				await fs.writeFile(filePath, updatedContents, "utf8");

				console.log(`Updated domain count for: ${file}`);
			})
		);

		console.log("All files processed successfully.");
	} catch (error) {
		console.error("Error processing files:", error);
	}
})();
