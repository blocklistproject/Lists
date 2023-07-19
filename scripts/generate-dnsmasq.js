const fs = require("fs").promises;
const path = require("path");

(async () => {
  const inputDirectory = path.join(__dirname, "..");
  const outputDirectory = path.join(__dirname, "..", "dnsmasq-version");
  
  try {
    const files = await fs.readdir(inputDirectory);
    const txtFiles = files.filter(file => file.endsWith(".txt"));

    await Promise.all(txtFiles.map(async (file) => {
      const filePath = path.join(inputDirectory, file);
      const fileContents = await fs.readFile(filePath, "utf8");

      const noIPFileContents = fileContents
        .replaceAll(/0\.0\.0\.0 (.*?)( .*)?$/gmu, "0.0.0.0 $1/$2") // Add "/" at the end of each URL
        .replaceAll(/^0\.0\.0\.0 /gmu, "server=/") // Replace all occurrences of "0.0.0.0 " at the beginning of the line with "server=/"
        .replaceAll(/^# 0\.0\.0\.0 /gmu, "# server=/") // Replace all occurrences of "# 0.0.0.0 " at the beginning of the line with "# server=/"
        .replace(/^# Title: (.*?)$/gmu, "# Title: $1 (dnsmasq)"); // Add (dnsmasq) to end of title
      
      const outputFilePath = path.join(outputDirectory, file.replace(".txt", "-dnsmasq.txt"));
      await fs.writeFile(outputFilePath, noIPFileContents, "utf8");
    }));
    
    console.log("Files processed successfully!");
  } catch (error) {
    console.error("Error occurred while processing files:", error);
  }
})();
