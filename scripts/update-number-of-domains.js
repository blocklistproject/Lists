const fs = require("fs").promises;
const path = require("path");

(async () => {
  const files = (await fs.readdir(path.join(__dirname, ".."))).filter(file => file.endsWith(".txt"));

  await Promise.all(files.map(async (file) => {
    const filePath = path.join(__dirname, "..", file);

    // Read the file contents asynchronously
    let fileContents = await fs.readFile(filePath, "utf8");

    // Count the number of network filters using a regex
    const existingDomainsCount = (fileContents.match(/^0\.0\.0\.0 /gm) || []).length;

    // Replace the total number of network filters in the fileContents
    fileContents = fileContents.replace(/^# Total number of network filters: ?(\d*)$/gmu, `# Total number of network filters: ${existingDomainsCount}`);

    // Write the updated file contents asynchronously
    await fs.writeFile(filePath, fileContents, "utf8");
  }));
})();
