export async function loadSecureWasm(url) {
    const response = await fetch(url);
    const buffer = await response.arrayBuffer();
    const module = await WebAssembly.instantiate(buffer);
    return module.instance.exports;
  }