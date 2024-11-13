// Import CryptoJS and pako within the worker (if available)
self.importScripts('https://cdnjs.cloudflare.com/ajax/libs/pako/2.0.4/pako.min.js');
self.importScripts('https://cdnjs.cloudflare.com/ajax/libs/crypto-js/3.1.9-1/crypto-js.js');

// Listen for messages from the main script
self.onmessage = async (event) => {
    const { fileChunk, key, fileId, chunkIndex } = event.data;

    try {
        // Encrypt the chunk
        const encryptedChunk = CryptoJS.AES.encrypt(fileChunk, key).toString();

        // Compress the encrypted data
        const compressedChunk = btoa(pako.deflate(encryptedChunk, { to: 'string' }));

        // Send the processed chunk back to the main thread
        self.postMessage({
            fileId,
            chunkIndex,
            chunkData: compressedChunk,
            success: true
        });
    } catch (error) {
        // Handle errors and send back a failure message
        self.postMessage({ fileId, chunkIndex, success: false, error: error.message });
    }
};
