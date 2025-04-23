# 🛡️ cloak-js

A powerful JavaScript code protection tool for frontend apps. Obfuscate, lock to domains, inject anti-debug code, and secure logic with WebAssembly. Works with Vite, Next.js, and Parcel.

## 🚀 Features

- 🔒 Obfuscate JavaScript (using javascript-obfuscator)
- 🌐 Domain lock protection
- 🕵️‍♂️ DevTools detection & self-defending runtime
- 🧪 Tamper detection using SHA-256
- 🧩 Optional WebAssembly support for core logic
- 🧰 Plugin support for Vite, Parcel, and Next.js

## 📦 Installation

```bash
npm install -g cloak-js
```

## 💻 CLI Usage

```bash
cloak ./your-app.js --domain yourdomain.com --inject-runtime --tamper-check
```

| Option | Description |
|--------|-------------|
| `--domain` | Lock script to a specific domain |
| `--inject-runtime` | Adds DevTools and debugger detection |
| `--tamper-check` | Injects SHA-256 hash validation |

## 🔧 Framework Plugins

### 🔌 Vite

```js
import cloakPlugin from 'cloak-js/vite';

export default {
  plugins: [cloakPlugin()]
};
```

### 🔌 Next.js

```js
const cloakPlugin = require('cloak-js/next');

module.exports = cloakPlugin({ /* options */ })(nextConfig);
```

## 🧪 WebAssembly Secure Loader

```js
import { loadSecureWasm } from 'cloak-js/wasm';

const secure = await loadSecureWasm('/secure.wasm');
secure.run();
```

## 🛣️ Roadmap

- ✅ Obfuscation CLI
- ✅ Domain locking
- ✅ DevTools runtime injection
- ✅ Tamper check (SHA-256)
- ✅ WebAssembly loader
- ✅ Vite, Next.js, Parcel plugins
- ⏳ Svelte and Astro plugin
- ⏳ CI/CD integration

## 📝 License

MIT — by @pratikacharya1234