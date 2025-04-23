const { Command } = require("commander");
const path = require("path");
const obfuscate = require("../lib/obfuscate");
const protect = require("../lib/protect");
const hashChecker = require("../lib/hash-checker");

const program = new Command();
program
  .name("cloak")
  .description("Obfuscate and protect your frontend code")
  .argument("<file>", "Path to JS file")
  .option("-d, --domain <url>", "Lock to specific domain")
  .option("--inject-runtime", "Inject DevTools protection")
  .option("--tamper-check", "Add tamper detection")
  .action(async (file, options) => {
    await obfuscate(file);
    if (options.domain || options.injectRuntime) {
      await protect(`obf-${file}`, options);
    }
    if (options.tamperCheck) {
      await hashChecker(`obf-${file}`);
    }
    console.log("✅ Code secured!");
  });

program.parse();
