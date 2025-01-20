const dropZone = document.getElementById('files');
const modal = document.getElementById('password-modal');
const fileInput = document.getElementById('file');
const storedPassword = sessionStorage.getItem('filePassword');
const CHUNK_SIZE = 1024 * 1024 * 0.1;  // 100KB

dropZone.addEventListener('dragenter', (e) => e.preventDefault());
dropZone.addEventListener('dragover', (e) => e.preventDefault());
dropZone.addEventListener('drop', handleFileDrop);

function handleFileDrop(e) {
    e.preventDefault();
    fileInput.files = e.dataTransfer.files;
    processFiles(storedPassword, Array.from(fileInput.files)); 
}


async function processFiles(password, files) {
    files.forEach(async (file) => {
        const fileId = generateRandomId();
        const key = generateEncryptionKey(password, fileId);

        const encryptedFileName = CryptoJS.AES.encrypt(file.name, key).toString();

        const fileData = await readFile(file);

        const processedFile = await encryptAndCompressFile(fileData, key);

        const chunkCount = Math.ceil(processedFile.length / 2 / CHUNK_SIZE); // Divide by 2 since hex is 2 chars per byte

        const success = await sendFileMetadata(fileId, encryptedFileName, chunkCount, file.size);
        if (!success) {
            console.error(`Failed to send file metadata for ${file.name}`);
            return;
        } else {
            // UI code remains the same
            const fileSection = document.querySelector('#files.content-section');
            const fileContainer = document.createElement('div');
            fileContainer.className = 'file-item';
            
            const fileLabel = document.createElement('span');
            fileLabel.className = 'file-label';
            fileLabel.textContent = `${file.name} (${(file.size / (1024*1024)).toFixed(2)} MB)`;
            
            const buttonContainer = document.createElement('div');
            buttonContainer.className = 'button-container';
            
            const downloadButton = document.createElement('button');
            downloadButton.className = 'download-button';
            downloadButton.textContent = 'Download';
            
            downloadButton.addEventListener('click', async () => {
                try {
                  const response = await fetch(`/files/download?key=${fileId}`, {
                    method: 'GET',
                    credentials: 'include'
                  });
                  const hexData = await response.text();
    
                  const decryptedBlob = await decryptFile(hexData, key);
              
                  async function decryptFile(hexString, key) {
                    try {
                        // Convert hex string back to bytes
                        const bytes = new Uint8Array(hexString.length / 2);
                        for (let i = 0; i < hexString.length; i += 2) {
                            bytes[i/2] = parseInt(hexString.substr(i, 2), 16);
                        }
                        
                        // Decompress with matching options from upload
                        const decompressed = pako.inflate(bytes, {
                            windowBits: 15,
                            raw: false
                        });
    
                        // Convert Uint8Array to WordArray directly
                        const wordArray = CryptoJS.lib.WordArray.create(decompressed);
                        
                        // Convert to base64
                        const base64String = CryptoJS.enc.Base64.stringify(wordArray);
                        
                        // Decrypt using the same key
                        const decrypted = CryptoJS.AES.decrypt(base64String, key);
                        
                        // Convert to ArrayBuffer
                        const arrayBuffer = new ArrayBuffer(decrypted.sigBytes);
                        const view = new DataView(arrayBuffer);
                        
                        for (let i = 0; i < decrypted.sigBytes; i++) {
                            view.setUint8(i, decrypted.words[i >>> 2] >>> (24 - (i % 4) * 8) & 0xFF);
                        }
                        
                        return new Blob([arrayBuffer]);
                    } catch (error) {
                        console.error('Decompression or decryption failed:', error);
                        throw error;
                    }
                }
              
                  const url = URL.createObjectURL(decryptedBlob);
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
        }
        // Modified chunk handling for hex string
        for (let start = 0; start < processedFile.length; start += CHUNK_SIZE * 2) { // Multiply by 2 for hex chars
            const chunk = processedFile.slice(start, Math.min(start + CHUNK_SIZE * 2, processedFile.length));
            const chunkIndex = Math.floor(start / (CHUNK_SIZE * 2));
        
            await uploadChunkToServer(fileId, chunkIndex, chunk);
        }
    });
}

async function encryptAndCompressFile(fileData, key) {
    try {
        // Create WordArray from file data
        const wordArray = CryptoJS.lib.WordArray.create(new Uint8Array(fileData));
        
        // Encrypt first
        const encrypted = CryptoJS.AES.encrypt(wordArray, key);
        const encryptedBase64 = encrypted.toString();
        
        // Convert base64 to binary array
        const binaryArray = Uint8Array.from(atob(encryptedBase64), c => c.charCodeAt(0));
        
        // Compress with specific options for reliability
        const compressed = pako.deflate(binaryArray, {
            level: 6,              // Moderate compression level (1-9)
            windowBits: 15,        // Default window size
            memLevel: 8,           // Default memory level
            strategy: 2,           // Default strategy
            raw: false            // Add wrapper for more reliable decompression
        });
        
        // Convert to hex string
        const hexString = Array.from(compressed)
            .map(byte => byte.toString(16).padStart(2, '0'))
            .join('');
            
        return hexString;
    } catch (error) {
        console.error("Error encrypting or compressing file:", error);
        throw new Error('Failed to encrypt or compress file');
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

async function uploadChunkToServer(fileId, chunkIndex, chunkData) {
    try {
        const base64Chunk = chunkData

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

function generateRandomId() {
    return Math.random().toString(36).substring(2, 15);
}

function generateEncryptionKey(password, fileId) {
    const masterHash = CryptoJS.SHA256(password).toString();
    const combined = fileId + masterHash;
    return CryptoJS.MD5(combined).toString();
}

async function sendFileMetadata(fileId, encryptedFileName, chunkCount, Size) {
    try {
        const response = await fetch('/files/upload/file', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                server_key: fileId,
                file_name: encryptedFileName,
                chunk_count: chunkCount,
                size: Size
            })
        }); 
        console.log("file metadata uploaded")
        return response.ok;
        
    } catch (error) {
        console.error('Error sending file metadata:', error);
        return false;
    }
}

