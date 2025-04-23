const fs = require("fs");
const path = require("path");
const obfuscator = require("javascript-obfuscator");

module.exports = async function obfuscate(filePath) {
  const code = fs.readFileSync(filePath, "utf-8");
  const obfuscated = obfuscator.obfuscate(code, {
    compact: true,
    controlFlowFlattening: true,
    selfDefending: true
  });
  const outputPath = path.join(
    path.dirname(filePath),
    `obf-${path.basename(filePath)}`
  );
  fs.writeFileSync(outputPath, obfuscated.getObfuscatedCode(), "utf-8");
  console.log(`🔒 Obfuscated code saved to ${outputPath}`);
};
