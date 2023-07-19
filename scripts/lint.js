const fs = require("fs").promises;
const path = require("path");

(async () => {
  let hasError = false;

  const files = (await fs.readdir(path.join(__dirname, ".."))).filter((file) => file.endsWith(".txt"));

  await Promise.all(
    files.filter((file) => file !== "everything.txt").map(async (file) => {
      const filePath = path.join(__dirname, "..", file);
      const fileContents = await fs.readFile(filePath, "utf8");

      const lines = fileContents.split("\n");
      const commentedURLs = [];

      let isHeaderComplete = false;

      lines.forEach((line, index) => {
        if (line.startsWith("0.0.0.0")) {
          isHeaderComplete = true;
        }

        // Checking to ensure no version/date might confuse users that read the raw text-file(s)
        if (line.length > 0 && line.includes("Version")) {
          console.error(`Line ${index + 1} in ${file} must not contain a Version/Date.`);
          hasError = true;
        }

        // Ensuring that all lines start with "#" or "0.0.0.0 "
        if (line.length > 0 && !line.startsWith("#") && !line.startsWith("0.0.0.0 ")) {
          console.error(`Line ${index + 1} in ${file} must start with "#" or "0.0.0.0 ".`);
          hasError = true;
        }

        // Checking to ensure all URLs are lowercase
        if (line.startsWith("0.0.0.0 ")) {
          const url = line.split("#")[0].trim().replace("0.0.0.0 ", "");
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

        // Ensure that after the header is complete, all lines that start with `#` start with `# 0.0.0.0` or `# NOTE:`
        if (isHeaderComplete && line.startsWith("#") && !line.startsWith("# 0.0.0.0") && !line.startsWith("# NOTE:")) {
          console.error(`Line ${index + 1} in ${file} should start with "# 0.0.0.0" or "# NOTE:".`);
          hasError = true;
        }

        // Ensure that the URL doesn't exist in the commentedURLs array
        if (line.startsWith("0.0.0.0 ")) {
          const url = line.split("#")[0].trim().replace("0.0.0.0 ", "");
          if (commentedURLs.includes(url)) {
            console.error(`Line ${index + 1} in ${file} url ${url} is commented out in this file. This suggests an error. Please either remove this line or remove the commented URL.`);
            hasError = true;
          } else {
            commentedURLs.push(url);
          }
        }

        // Ensure that the URL doesn't contain whitespace characters
        if (line.startsWith("0.0.0.0 ")) {
          const url = line.split("#")[0].trim().replace("0.0.0.0 ", "");
          if (/\s/gmu.test(url)) {
            console.error(`Line ${index + 1} in ${file} url ${url} contains whitespace in the URL.`);
            hasError = true;
          }
        }
      });
    })
  );

  process.exit(hasError ? 1 : 0);
})();
