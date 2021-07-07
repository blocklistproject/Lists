const fs = require("fs").promises;
const path = require("path");

(async () => {
	const files = (await fs.readdir(path.join(__dirname, ".."))).filter((file) => file.endsWith(".txt")); // Array of strings, each representing a single file that ends in `.txt`
	await Promise.all(files.map(async (file) => { // For each file
		const fileContents = await fs.readFile(path.join(__dirname, "..", file), "utf8"); // Get file contents as a string
		const adGuardFileContents = fileContents
		.replace(/^# Title: (.*?)$/gmu, "# Title: $1 (adguard)") // Add (adguard) to end of title
		.replaceAll(/^# 0\.0\.0\.0 (.*?) (.*)/gmu, "@@||$1^! $2")
		.replaceAll(/0\.0\.0\.0 (.*?)$/gmu, "||$1^")
		.replaceAll(/^#/gmu, "!");
		await fs.writeFile(path.join(__dirname, "..", "adguard", file.replace(".txt", "-ags.txt")), adGuardFileContents, "utf8"); // Write new file to `adguard` directory
	}));
})();
