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
				const dnsmasqFileContents = fileContents
					.replaceAll(/0\.0\.0\.0 (.*?)( .*)?$/gmu, "0.0.0.0 $1/")
					.replaceAll(/^0\.0\.0\.0 /gmu, "server=/")
					.replaceAll(/^# 0\.0\.0\.0 /gmu, "# server=/")
					.replace(/^# Title: (.*?)$/gmu, "# Title: $1 (dnsmasq)");
				await fs.writeFile(
					path.join(
						__dirname,
						"..",
						"dnsmasq-version",
						file.replace(".txt", "-dnsmasq.txt"),
					),
					dnsmasqFileContents,
					"utf8",
				);
			}),
		);
	} catch (error) {
		console.error("Error processing files:", error);
	}
})();
