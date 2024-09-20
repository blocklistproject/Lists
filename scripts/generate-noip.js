const fs = require("node:fs").promises;
const path = require("node:path");

(async () => {
	try {
		const files = (await fs.readdir(path.join(__dirname, ".."))).filter(
			(file) => file.endsWith(".txt"),
		);
		await Promise.all(
			files.map(async (file) => {
				const fileContents = await fs.readFile(
					path.join(__dirname, "..", file),
					"utf8",
				);
				const noIPFileContents = fileContents
					.replaceAll(/^0\.0\.0\.0 /gmu, "")
					.replaceAll(/^# 0\.0\.0\.0 /gmu, "# ")
					.replace(/^# Title: (.*?)$/gmu, "# Title: $1 (NL)");
				await fs.writeFile(
					path.join(
						__dirname,
						"..",
						"alt-version",
						file.replace(".txt", "-nl.txt"),
					),
					noIPFileContents,
					"utf8",
				);
			}),
		);
	} catch (error) {
		console.error("Error processing files:", error);
	}
})();
