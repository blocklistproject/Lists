const fs = require("fs").promises;
const path = require("path");

(async () => {
  try {
    const files = await fs.readdir(path.join(__dirname, "..")); // Get a list of all files in the parent directory

    // Filter files to keep only those ending with ".txt"
    const txtFiles = files.filter((file) => file.endsWith(".txt"));

    // Create an array to store promises for processing each file
    const promises = txtFiles.map(async (file) => {
      // Read file contents as a string
      const fileContents = await fs.readFile(path.join(__dirname, "..", file), "utf8");

      // Process the file contents
      const adGuardFileContents = fileContents
        .replace(/^# Title: (.*?)$/gm, "# Title: $1 (adguard)") // Use "gm" flag to match multiple lines
        .replaceAll(/^# 0\.0\.0\.0 (.*?) (.*)/gm, "@@||$1^! $2") // Use "gm" flag to match multiple lines
        .replaceAll(/0\.0\.0\.0 (.*?)$/gm, "||$1^") // Use "gm" flag to match multiple lines
        .replaceAll(/^#/gm, "!"); // Use "gm" flag to match multiple lines

      // Write new file to `adguard` directory
      await fs.writeFile(path.join(__dirname, "..", "adguard", file.replace(".txt", "-ags.txt")), adGuardFileContents, "utf8");
    });

    // Wait for all promises to complete
    await Promise.all(promises);

    console.log("All files processed successfully.");
  } catch (error) {
    console.error("Error processing files:", error);
  }
})();
