const fs = require("fs").promises;
const path = require("path");

(async () => {
  const files = await fs.readdir(path.join(__dirname, ".."));
  const txtFiles = files.filter((file) => file.endsWith(".txt"));

  for (const file of txtFiles) {
    const filePath = path.resolve(__dirname, "..", file);
    const fileContents = await fs.readFile(filePath, "utf8");

    const noIPFileContents = fileContents.replace(/^#? ?0\.0\.0\.0 ?/gm, "").replace(/^# Title: (.*?)$/gm, "# Title: $1 (NL)");

    const newFileName = file.replace(".txt", "-nl.txt");
    const newFilePath = path.resolve(__dirname, "..", "alt-version", newFileName);
    await fs.writeFile(newFilePath, noIPFileContents, "utf8");
  }
})();
