const fs = require("node:fs").promises;
const path = require("node:path");

(async () => {
	const hasError = false;

	try {
		const directoryPath = path.join(__dirname, "..");
		const files = (await fs.readdir(directoryPath)).filter(
			(file) => file.endsWith(".txt") && file !== "everything.txt",
		);

		await Promise.all(
			files.map(async (file) => {
				const filePath = path.join(directoryPath, file);
				const fileContents = await fs.readFile(filePath, "utf8");
				const lines = fileContents.split("\n");
				const commentedURLs = lines
					.filter((line) => line.startsWith("# 0.0.0.0"))
					.map((line) => line.split(" ")[2].trim());

				let isHeaderComplete = false;

			lines.forEach((line, index) => {
				// Mark the end of the header section
				if (line.startsWith("0.0.0.0")) {
					isHeaderComplete = true;
				}

				// Check if the line contains a Version or Date, which should be avoided
				if (line.includes("Version") || line.includes("Date")) {
					console.error(`Line ${index + 1} in ${file} must not contain a Version/Date.`);
					hasError = true;
				}

				// Validate that each line starts with "#" or "0.0.0.0 "
				if (line.trim() && !line.startsWith("#") && !line.startsWith("0.0.0.0 ")) {
					console.error(`Line ${index + 1} in ${file} must start with "#" or "0.0.0.0 ".`);
					hasError = true;
				}

				// Ensure URLs in the file are lowercase
				if (line.startsWith("0.0.0.0 ")) {
					const url = line.split(" ")[1].split("#")[0].trim();
					if (url.toLowerCase() !== url) {
						console.error(`Line ${index + 1} in ${file} URL ${url} must be all lowercase.`);
						hasError = true;
					}
				}

				// Validate that lines starting with "#" have a space following the "#"
				if (line.startsWith("#") && line.length > 1 && line[1] !== " ") {
					console.error(`Line ${index + 1} in ${file} should have a space after "#".`);
					hasError = true;
				}

				// Check that lines after the header with "#" start with "# 0.0.0.0" or "# NOTE:"
				if (isHeaderComplete && line.startsWith("#") && !line.startsWith("# 0.0.0.0") && !line.startsWith("# NOTE:")) {
					console.error(`Line ${index + 1} in ${file} should start with "# 0.0.0.0" or "# NOTE:".`);
					hasError = true;
				}

				// Ensure that no active URL matches a commented-out URL
				if (line.startsWith("0.0.0.0 ")) {
					const url = line.split(" ")[1].split("#")[0].trim();
					if (commentedURLs.includes(url)) {
						console.error(`Line ${index + 1} in ${file} URL ${url} is commented out in this file. Please remove the duplicate or uncomment the URL.`);
						hasError = true;
					}
				}

				// Ensure URLs do not contain whitespace
				if (line.startsWith("0.0.0.0 ")) {
					const url = line.split(" ")[1].split("#")[0].trim();
					if (/\s/g.test(url)) {
						console.error(`Line ${index + 1} in ${file} URL ${url} contains whitespace.`);
						hasError = true;
					}
				}
			});
		}));


		process.exit(hasError ? 1 : 0);
	} catch (error) {
		console.error("An error occurred during file processing:", error);
		process.exit(1);
	}
})();
