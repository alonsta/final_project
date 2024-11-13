const uploadButton = document.getElementById('upload-button');
const cancelButton = document.getElementById('cancel-button');
const dropZone = document.getElementById('files');
const modal = document.getElementById('password-modal');
const passwordInput = document.getElementById('password');
const fileInput = document.getElementById('file');

// Initialize the Web Worker
const fileWorker = new Worker('/scripts/uploadWorker.js');

// Chunk size in bytes (e.g., 1 MB per chunk)
const CHUNK_SIZE = 1024 * 1024 * 2;

// Handle file drop events
dropZone.addEventListener('dragenter', (e) => e.preventDefault());
dropZone.addEventListener('dragover', (e) => e.preventDefault());
dropZone.addEventListener('drop', handleFileDrop);

function handleFileDrop(e) {
    e.preventDefault();
    fileInput.files = e.dataTransfer.files;
    modal.style.display = 'flex'
    modal.classList.remove('hidden');
     // Show the modal to enter password
}

cancelButton.addEventListener('click', () => {
    passwordInput.setAttribute("value", "")
    modal.classList.add('hidden')
    modal.style.display = 'none'
})
// Upload Button Click
uploadButton.addEventListener('click', () => {
    const password = passwordInput.value;
    if (password.length < 8) {
        alert('Password length must be 8 or more characters');
        return;
    }
    processFiles(password, Array.from(fileInput.files));
    modal.classList.add('hidden')
    modal.style.display = 'none'
    passwordInput.value = "";
});

// Process files by chunk and send metadata to server
function processFiles(password, files) {
    files.forEach(async (file) => {
        const fileId = generateRandomId();
        const key = generateEncryptionKey(password, fileId);

        // Encrypt the file name
        const encryptedFileName = CryptoJS.AES.encrypt(file.name, key).toString();

        // Calculate the number of chunks
        const chunkCount = Math.ceil(file.size / CHUNK_SIZE);

        // Send file metadata to server
        const success = await sendFileMetadata(fileId, encryptedFileName, chunkCount);
        if (!success) {
            console.error(`Failed to send file metadata for ${file.name}`);
            return;
        }

        // Process and upload each chunk
        for (let start = 0; start < file.size; start += CHUNK_SIZE) {
            const chunk = file.slice(start, start + CHUNK_SIZE);
            const chunkIndex = start / CHUNK_SIZE;

            // Read each chunk as text
            const chunkText = await readFileChunk(chunk);

            // Send chunk to the worker for encryption and compression
            fileWorker.postMessage({
                fileChunk: chunkText,
                key,
                fileId,
                chunkIndex
            });
        }
    });
}

// Read file chunk as text
function readFileChunk(chunk) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => resolve(reader.result);
        reader.onerror = reject;
        reader.readAsText(chunk);
    });
}

// Send file metadata to the server
async function sendFileMetadata(fileId, encryptedFileName, chunkCount) {
    try {
        const response = await fetch('/files/upload/file', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                server_key: fileId,
                file_name: encryptedFileName,
                chunk_count: chunkCount
            })
        });
        return response.ok;
    } catch (error) {
        console.error('Error sending file metadata:', error);
        return false;
    }
}

// Listen for messages from the worker
fileWorker.onmessage = (event) => {
    const { fileId, chunkIndex, chunkData, success, error } = event.data;
    if (success) {
        // Upload the chunk to the server
        uploadChunkToServer(fileId, chunkIndex, chunkData);
    } else {
        console.error(`Error processing chunk ${chunkIndex} of file ${fileId}:`, error);
    }
};

// Function to upload encrypted chunk to the server
function uploadChunkToServer(fileId, chunkIndex, chunkData) {
    fetch('/files/upload/chunk', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            server_key: fileId,
            index: chunkIndex,
            content: chunkData
        })
    }).then(response => {
        if (response.ok) {
            console.log(`Chunk ${chunkIndex} of file ${fileId} uploaded successfully`);
        } else {
            console.error(`Upload failed for chunk ${chunkIndex} of file ${fileId}`);
        }
    }).catch(error => console.error(`Error uploading chunk ${chunkIndex}:`, error));
}

// Helper functions
function generateRandomId() {
    return Math.random().toString(36).substring(2, 15);
}

function generateEncryptionKey(password, fileId) {
    const masterHash = CryptoJS.SHA256(password).toString();
    const combined = fileId + masterHash;
    return CryptoJS.MD5(combined).toString();
}
