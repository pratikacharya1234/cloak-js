import { obfuscate } from '../lib/obfuscate.js';

export default function cloakPlugin(options = {}) {
  return {
    name: 'vite-plugin-cloak',
    apply: 'build',
    generateBundle(_, bundle) {
      for (const file in bundle) {
        if (file.endsWith('.js')) {
          bundle[file].code = obfuscate(bundle[file].code, options).getObfuscatedCode();
        }
      }
    }
  };
}