const uploadButton = document.getElementById('upload-button');
const cancelButton = document.getElementById('cancel-button');
const dropZone = document.getElementById('files');
const modal = document.getElementById('password-modal');
const passwordInput = document.getElementById('password');
const fileInput = document.getElementById('file');

const CHUNK_SIZE = 1024 * 1024 * 0.1;  // 100KB

dropZone.addEventListener('dragenter', (e) => e.preventDefault());
dropZone.addEventListener('dragover', (e) => e.preventDefault());
dropZone.addEventListener('drop', handleFileDrop);

function handleFileDrop(e) {
    e.preventDefault();
    fileInput.files = e.dataTransfer.files;
    modal.style.display = 'flex';
    modal.classList.remove('hidden');
}

cancelButton.addEventListener('click', () => {
    passwordInput.setAttribute("value", "")
    modal.classList.add('hidden');
    modal.style.display = 'none';
});

uploadButton.addEventListener('click', () => {
    const password = passwordInput.value;
    if (password.length < 8) {
        alert('Password length must be 8 or more characters');
        return;
    }
    processFiles(password, Array.from(fileInput.files));
    modal.classList.add('hidden');
    modal.style.display = 'none';
    passwordInput.value = "";
});

async function processFiles(password, files) {
    files.forEach(async (file) => {
        const fileId = generateRandomId();
        const key = generateEncryptionKey(password, fileId);

        const encryptedFileName = CryptoJS.AES.encrypt(file.name, key).toString();

        const fileData = await readFile(file);

        const processedFile = await encryptAndCompressFile(fileData, key);

        const chunkCount = Math.ceil(processedFile.byteLength / CHUNK_SIZE);

        const success = await sendFileMetadata(fileId, encryptedFileName, chunkCount, file.size);
        if (!success) {
            console.error(`Failed to send file metadata for ${file.name}`);
            return;
        }

        for (let start = 0; start < processedFile.byteLength; start += CHUNK_SIZE) {
            const chunk = processedFile.slice(start, Math.min(start + CHUNK_SIZE, processedFile.byteLength));
            const chunkIndex = Math.floor(start / CHUNK_SIZE);
        
            await uploadChunkToServer(fileId, chunkIndex, chunk);
        }
    });
}


async function encryptAndCompressFile(fileData, key) {
    try {
        const wordArray = CryptoJS.lib.WordArray.create(new Uint8Array(fileData));

        const encryptedData = CryptoJS.AES.encrypt(wordArray, key).toString();

        const compressedData = pako.deflate(encryptedData);

        return compressedData;
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
        const base64Chunk = btoa(String.fromCharCode.apply(null, chunkData));

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

