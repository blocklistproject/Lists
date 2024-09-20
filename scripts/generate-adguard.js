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
				const adGuardFileContents = fileContents
					.replace(/^# Title: (.*?)$/gmu, "# Title: $1 (adguard)")
					.replaceAll(/^# 0\.0\.0\.0 (.*?) (.*)/gmu, "@@||$1^! $2")
					.replaceAll(/0\.0\.0\.0 (.*?)$/gmu, "||$1^")
					.replaceAll(/^#/gmu, "!");
				await fs.writeFile(
					path.join(
						__dirname,
						"..",
						"adguard",
						file.replace(".txt", "-ags.txt"),
					),
					adGuardFileContents,
					"utf8",
				);
			}),
		);
	} catch (error) {
		console.error("Error processing files:", error);
	}
})();
