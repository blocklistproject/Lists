const fs = require("fs").promises;
const path = require("path");

(async () => {
	let hasError = false;

	const files = (await fs.readdir(path.join(__dirname, ".."))).filter((file) => file.endsWith(".txt")); // Array of strings, each representing a single file that ends in `.txt`
	await Promise.all(files.filter((file) => file !== "everything.txt").map(async (file) => { // For each file
		const fileContents = await fs.readFile(path.join(__dirname, "..", file), "utf8"); // Get file contents as a string

		const commentedURLs = fileContents.split("\n").map((line) => {
			if (line.startsWith("# 0.0.0.0")) {
				return line.split(" ")[2].trim();
			}

			return null;
		}).filter((a) => a !== null && !!a);

		let isHeaderComplete = false;
		fileContents.split("\n").forEach((line, index) => {
			if (line.startsWith("0.0.0.0")) {
				isHeaderComplete = true;
			}

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

			// Ensuring that all lines that start with `#` are followed by a space
			if (line.startsWith("#") && line.length > 1 && line[1] !== " ") {
				console.error(`Line ${index + 1} in ${file} should have a space after #.`);
				hasError = true;
			}

			// Ensure that after header is complete that all lines that start with `#` start with `# 0.0.0.0`
			if (isHeaderComplete && line.startsWith("#") && !line.startsWith("# 0.0.0.0")) {
				console.error(`Line ${index + 1} in ${file} should start with "# 0.0.0.0".`);
				hasError = true;
			}

			// Ensure that the URL doesn't exist in the commentedURLs array
			if (line.startsWith("0.0.0.0 ")) {
				const lineNoIP = line.replace("0.0.0.0 ", "");
				const url = lineNoIP.split("#")[0].trim();
				if (commentedURLs.includes(url)) {
					console.error(`Line ${index + 1} in ${file} url ${url} is commented out in this file. This suggests an error. Please either remove this line or remove the commented URL.`);
					hasError = true;
				}
			}

			// Ensure that the URL doesn't contain whitespace characters
			if (line.startsWith("0.0.0.0 ")) {
				const lineNoIP = line.replace("0.0.0.0 ", "");
				const url = lineNoIP.split("#")[0].trim();
				if (/\s/gmu.test(url)) {
					console.error(`Line ${index + 1} in ${file} url ${url} contains whitespace in the URL.`);
					hasError = true;
				}
			}
		});
	}));

	process.exit(hasError ? 1 : 0);
})();
