const fs = require("node:fs").promises;
const path = require("node:path");

(async () => {
	try {
		// Define base and output directories
		const baseDir = path.join(__dirname, "..");
		const outputDir = path.join(baseDir, "dnsmasq-version");

		// Ensure the output directory exists
		await fs.mkdir(outputDir, { recursive: true });

		// Get a list of all .txt files in the base directory
		const files = (await fs.readdir(baseDir)).filter((file) => file.endsWith(".txt"));

		// Process each file concurrently
		await Promise.all(
			files.map(async (file) => {
				try {
					// Read the file contents
					const filePath = path.join(baseDir, file);
					const fileContents = await fs.readFile(filePath, "utf8");

					// Perform replacements to format for dnsmasq
					const dnsmasqFileContents = fileContents
						.replace(/0\.0\.0\.0 (.*?)( .*)?$/gm, "0.0.0.0 $1/")
						.replace(/^0\.0\.0\.0 /gm, "server=/")
						.replace(/^# 0\.0\.0\.0 /gm, "# server=/")
						.replace(/^# Title: (.*?)$/gm, "# Title: $1 (dnsmasq)");

					// Define output file path
					const outputFilePath = path.join(outputDir, file.replace(".txt", "-dnsmasq.txt"));

					// Write modified content to output file
					await fs.writeFile(outputFilePath, dnsmasqFileContents, "utf8");

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
