const fs = require("fs").promises;
const path = require("path");

(async () => {
	let hasError = false;

	const files = (await fs.readdir(path.join(__dirname, ".."))).filter((file) => file.endsWith(".txt")); // Array of strings, each representing a single file that ends in `.txt`
	await Promise.all(files.filter((file) => file !== "everything.txt").map(async (file) => { // For each file
		const fileContents = await fs.readFile(path.join(__dirname, "..", file), "utf8"); // Get file contents as a string

		fileContents.split("\n").forEach((line, index) => {
			// Ensuring that all lines start with "#" or "0.0.0.0 "
			if (line.length > 0 && !line.startsWith("#") && !line.startsWith("0.0.0.0 ")) {
				console.error(`Line ${index + 1} in ${file} must start with "#" or "0.0.0.0 ".`);
				hasError = true;
			}

			// Checking to ensure all URLs are lowercase
			if (line.startsWith("0.0.0.0 ")) {
				const lineNoIP = line.replace("0.0.0.0 ", "");
				const url = lineNoIP.split("#")[0].trim();
				if (url.toLowerCase() !== url) {
					console.error(`Line ${index + 1} in ${file} url ${url} must be all lowercase.`);
					hasError = true;
				}
			}
		});
	}));

	process.exit(hasError ? 1 : 0);
})();
