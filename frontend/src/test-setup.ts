/// <reference types="node" />
// @ts-ignore - Node.js crypto for test environment
const { webcrypto } = require('crypto');

if (typeof globalThis.crypto === 'undefined') {
  // @ts-ignore
  globalThis.crypto = webcrypto
} else {
    if (!globalThis.crypto.getRandomValues) {
        // @ts-ignore
        globalThis.crypto.getRandomValues = webcrypto.getRandomValues.bind(webcrypto)
    }
}
