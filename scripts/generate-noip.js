const fs = require("node:fs").promises;
const path = require("node:path");

(async () => {
	try {
		// Define directories for better readability and maintainability
		const baseDir = path.join(__dirname, "..");
		const outputDir = path.join(baseDir, "alt-version");

		// Ensure the output directory exists, creating it if necessary
		await fs.mkdir(outputDir, { recursive: true });

		// Filter for .txt files in the base directory
		const files = (await fs.readdir(baseDir)).filter((file) => file.endsWith(".txt"));

		// Process each file concurrently
		await Promise.all(
			files.map(async (file) => {
				try {
					// Read file contents
					const filePath = path.join(baseDir, file);
					const fileContents = await fs.readFile(filePath, "utf8");

					// Perform replacements
					const noIPFileContents = fileContents
						.replace(/^0\.0\.0\.0 /gm, "")
						.replace(/^# 0\.0\.0\.0 /gm, "# ")
						.replace(/^# Title: (.*?)$/gm, "# Title: $1 (NL)");

					// Define output file path
					const outputFilePath = path.join(outputDir, file.replace(".txt", "-nl.txt"));

					// Write modified content to output file
					await fs.writeFile(outputFilePath, noIPFileContents, "utf8");

					console.log(`Processed: ${file}`);
				} catch (fileError) {
					console.error(`Error processing file "${file}":`, fileError);
				}
			})
		);

		console.log("All files processed successfully.");
	} catch (error) {
		console.error("Error during file processing:", error);
	}
})();
