const dropZone = document.getElementById('files');
const modal = document.getElementById('password-modal');
const fileInput = document.getElementById('file');
const storedPassword = sessionStorage.getItem('filePassword');
const CHUNK_SIZE = 1024 * 1024 * 2 ; // 2MB chunks

dropZone.addEventListener('dragenter', (e) => e.preventDefault());
dropZone.addEventListener('dragover', (e) => e.preventDefault());
dropZone.addEventListener('drop', handleFileDrop);

function handleFileDrop(e) {
    e.preventDefault();
    fileInput.files = e.dataTransfer.files;
    processFiles(storedPassword, Array.from(fileInput.files));
}

async function processFiles(password, files) {
    for (const file of files) {
        try {
            const fileId = generateRandomId();
            const key = generateEncryptionKey(password, fileId);
            const encryptedFileName = CryptoJS.AES.encrypt(CryptoJS.enc.Utf8.parse(file.name), key).toString();

            // Calculate chunk count
            const chunkCount = Math.ceil(file.size / CHUNK_SIZE);

            // Send file metadata first
            await sendFileMetadata(fileId, encryptedFileName, chunkCount, file.size);

            // Process file in chunks
            for (let i = 0; i < chunkCount; i++) {
                const start = i * CHUNK_SIZE;
                const end = Math.min(start + CHUNK_SIZE, file.size);
                const chunk = file.slice(start, end);

                // Read chunk
                const chunkData = await readChunk(chunk);
                // Compress and encrypt chunk
                const processedChunk = await compressAndEncryptChunk(chunkData, key);

                // Send chunk
                await uploadChunk(fileId, i, processedChunk);
            }

            // Update UI for the file
            const fileSection = document.querySelector('#files.content-section');
            const fileContainer = document.createElement('div');
            fileContainer.className = 'file-item';

            const fileLabel = document.createElement('span');
            fileLabel.className = 'file-label';
            fileLabel.textContent = `${file.name} (${formatFileSize(file.size)})`; // Use the helper function here

            const buttonContainer = document.createElement('div');
            buttonContainer.className = 'button-container';

            const downloadButton = document.createElement('button');
            downloadButton.className = 'download-button';
            downloadButton.textContent = 'Download';

            downloadButton.addEventListener('click', async () => {
                try {
                    const chunks = [];
                    for (let chunkIndex = 0; chunkIndex < chunkCount; chunkIndex++) {
                        const response = await fetch(`/files/download?key=${fileId}&index=${chunkIndex}`, {
                            method: 'GET',
                            credentials: 'include'
                        });

                        if (response.ok) {
                            const encryptedChunk = await response.text();
                            const decryptedChunk = await decryptAndDecompressChunk(encryptedChunk, key);
                            chunks.push(decryptedChunk);
                        } else {
                            console.error("Chunk download failed");
                        }
                    }

                    const blob = new Blob(chunks);
                    const url = URL.createObjectURL(blob);
                    const tempLink = document.createElement('a');
                    tempLink.href = url;
                    tempLink.download = file.name;
                    tempLink.click();
                    URL.revokeObjectURL(url);
                } catch (error) {
                    console.error('Download failed:', error);
                }
            });

            buttonContainer.appendChild(downloadButton);
            fileContainer.appendChild(fileLabel);
            fileContainer.appendChild(buttonContainer);
            fileSection.appendChild(fileContainer);

            console.log(`File metadata sent for ${file.name}`);
        } catch (error) {
            console.error(`Error processing file ${file.name}:`, error);
        }
    }
}

async function readChunk(chunk) {
    return new Promise((resolve) => {
        const reader = new FileReader();
        reader.onload = (e) => resolve(e.target.result);
        reader.readAsArrayBuffer(chunk);
    });
}

async function compressAndEncryptChunk(chunkData, key) {
    // Compress chunk
    const compressed = pako.deflate(new Uint8Array(chunkData));
    
    // Convert to base64 in smaller chunks to avoid stack overflow
    const chunkSize = 32768; // 32KB chunks for string conversion
    let binary = '';
    for (let i = 0; i < compressed.length; i += chunkSize) {
        const slice = compressed.subarray(i, i + chunkSize);
        binary += String.fromCharCode.apply(null, slice);
    }
    
    // Convert to base64
    const base64 = btoa(binary);
    
    // Encrypt
    return CryptoJS.AES.encrypt(base64, key).toString();
}

async function compressAndEncryptFile(fileData, key) {
    try {
        // Compress first
        const compressed = pako.deflate(new Uint8Array(fileData), {
            level: 6,
            windowBits: 15,
            memLevel: 8,
            strategy: 2,
            raw: false
        });

        // Encrypt the compressed data
        const wordArray = CryptoJS.lib.WordArray.create(compressed);
        const encrypted = CryptoJS.AES.encrypt(wordArray, key);
        const encryptedBase64 = encrypted.toString();

        return encryptedBase64;
    } catch (error) {
        console.error("Error compressing or encrypting file:", error);
        throw new Error('Failed to compress or encrypt file');
    }
}

function readFile(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => resolve(reader.result);
        reader.onerror = reject;
        reader.readAsArrayBuffer(file);
    });
}

async function uploadChunk(fileId, index, chunk) {
    const response = await fetch('/files/upload/chunk', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            key: fileId,
            index: index,
            data: chunk
        }),
        credentials: 'include'
    });
    
    if (!response.ok) {
        throw new Error(`Failed to upload chunk ${index}`);
    }
}

async function uploadChunkToServer(fileId, chunkIndex, chunkData) {
    try {
        // Convert base64 chunk to a string for the server
        const base64Chunk = chunkData;

        const response = await fetch('/files/upload/chunk', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                server_key: fileId,
                index: chunkIndex,
                content: base64Chunk
            })
        });

        if (response.ok) {
            console.log(`Chunk ${chunkIndex} of file ${fileId} uploaded successfully`);
        } else {
            console.error(`Upload failed for chunk ${chunkIndex} of file ${fileId}`);
        }
    } catch (error) {
        console.error(`Error uploading chunk ${chunkIndex}:`, error);
    }
}

async function decryptFile(base64String, key) {
    try {
        // Decrypt the base64 string
        const decrypted = CryptoJS.AES.decrypt(base64String, key);

        // Convert to Uint8Array
        const bytes = new Uint8Array(decrypted.sigBytes);
        for (let i = 0; i < decrypted.sigBytes; i++) {
            bytes[i] = (decrypted.words[i >>> 2] >>> (24 - (i % 4) * 8)) & 0xff;
        }

        // Decompress the data
        const decompressed = pako.inflate(bytes, {
            windowBits: 15,
            raw: false
        });

        return new Blob([decompressed]);
    } catch (error) {
        console.error('Decryption or decompression failed:', error);
        throw error;
    }
}

function generateRandomId() {
    return Math.random().toString(36).substring(2, 15);
}

function generateEncryptionKey(password, fileId) {
    // Placeholder for a secure key derivation function (e.g., PBKDF2)
    const masterHash = CryptoJS.SHA256(password).toString();
    const combined = fileId + masterHash;
    return CryptoJS.MD5(combined).toString();
}

async function sendFileMetadata(fileId, encryptedFileName, chunkCount, size) {
    try {
        const response = await fetch('/files/upload/file', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                server_key: fileId,
                file_name: encryptedFileName,
                chunk_count: chunkCount,
                size: size
            })
        });
        console.log("File metadata uploaded");
        return response.ok;
    } catch (error) {
        console.error('Error sending file metadata:', error);
        return false;
    }
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
  
    const units = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    const unitIndex = Math.floor(Math.log(bytes) / Math.log(1024));
    const size = (bytes / Math.pow(1024, unitIndex)).toFixed(2);
  
    return `${size} ${units[unitIndex]}`;
  }