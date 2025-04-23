const crypto = require("crypto");
const fs = require("fs");

function getHash(content) {
  return crypto.createHash("sha256").update(content).digest("hex");
}

module.exports = function appendTamperCheck(filePath) {
  const content = fs.readFileSync(filePath, "utf-8");
  const hash = getHash(content);

  const script = `
    (function() {
      const expectedHash = "${hash}";
      const scriptContent = document.currentScript.textContent;
      const actualHash = sha256(scriptContent);
      if (actualHash !== expectedHash) {
        alert("Tampering detected!");
        throw new Error("Code has been altered.");
      }
    })();
  `;

  const tamperProtectedCode = script + "\n" + content;
  fs.writeFileSync(filePath, tamperProtectedCode, "utf-8");
  console.log("🧪 Tamper check injected");
};
