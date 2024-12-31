const fs = require("fs").promises;
const path = require("path");

(async () => {
	let hasError = false;

	try {
		const directoryPath = path.join(__dirname, "..");
		const files = (await fs.readdir(directoryPath)).filter(file => file.endsWith(".txt") && file !== "everything.txt");

		await Promise.all(files.map(async file => {
			const filePath = path.join(directoryPath, file);
			const fileContents = await fs.readFile(filePath, "utf8");

			const lines = fileContents.split("\n");
			const commentedURLs = lines
				.filter(line => line.startsWith("# 0.0.0.0"))
				.map(line => line.split(" ")[2].trim());
			let isHeaderComplete = false;

			lines.forEach((line, index) => {
				// Mark the end of the header section
@@ -78,6 +80,7 @@ const path = require("path");
			});
		}));

		process.exit(hasError ? 1 : 0);
	} catch (error) {
		console.error("An error occurred during file processing:", error);
