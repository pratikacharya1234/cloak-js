const { obfuscate } = require('../lib/obfuscate');

module.exports = function cloakWebpackPlugin(options = {}) {
  return {
    webpack(config) {
      config.plugins.push({
        apply: (compiler) => {
          compiler.hooks.emit.tapAsync('CloakPlugin', (compilation, cb) => {
            for (const file in compilation.assets) {
              if (file.endsWith('.js')) {
                const raw = compilation.assets[file].source();
                const obfuscated = obfuscate(raw, options);
                compilation.assets[file] = {
                  source: () => obfuscated.getObfuscatedCode(),
                  size: () => obfuscated.getObfuscatedCode().length
                };
              }
            }
            cb();
          });
        }
      });
      return config;
    }
  };
};
