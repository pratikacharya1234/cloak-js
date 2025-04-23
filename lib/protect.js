const fs = require("fs");

module.exports = async function protect(filePath, options) {
  let content = fs.readFileSync(filePath, "utf-8");

  if (options.domain) {
    const lockScript = `
      if (window.location.hostname !== "${options.domain}") {
        document.body.innerHTML = "<h2>Access Denied</h2>";
        throw new Error("Domain not allowed.");
      }
    `;
    content = lockScript + "\n" + content;
    console.log(`🔐 Domain locked to: ${options.domain}`);
  }

  if (options.injectRuntime) {
    const runtime = `
      setInterval(() => {
        const devtools = window.outerWidth - window.innerWidth > 160;
        if (devtools) {
          document.body.innerHTML = "<h1>⚠️ Protected Code</h1>";
          throw new Error("DevTools are blocked.");
        }
      }, 1000);
    `;
    content = runtime + "\n" + content;
    console.log("🛡️ DevTools protection injected");
  }

  fs.writeFileSync(filePath, content, "utf-8");
};
