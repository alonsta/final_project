const uploadButton = document.getElementById('upload-button');
const cancelButton = document.getElementById('cancel-button');
const dropZone = document.getElementById('files');
const modal = document.getElementById('password-modal');
const passwordInput = document.getElementById('password');
const fileInput = document.getElementById('file');

function switchTab(tabName) {
    const sections = document.querySelectorAll(".content-section");
    sections.forEach(section => section.classList.add("hidden"));
    
    const activeSection = document.getElementById(tabName);
    if (activeSection) {
        activeSection.classList.remove("hidden");
    }
}

dropZone.addEventListener('dragenter', (e) => e.preventDefault());
dropZone.addEventListener('dragover', (e) => e.preventDefault());
dropZone.addEventListener('drop', handleFileDrop);

function handleFileDrop(e) {
    e.preventDefault();
    fileInput.files = e.dataTransfer.files;
    previewFiles(Array.from(fileInput.files));
    modal.style.display = 'flex';
}

function previewFiles(files) {
    files.forEach(file => {
        
        
        const fileReader = new FileReader();
        fileReader.onload = (e) => console.log('File content:', e.target.result);
        fileReader.readAsText(file);
    });
}

cancelButton.addEventListener('click', () => {
    modal.style.display = 'none';
    passwordInput.value = "";
});

uploadButton.addEventListener('click', () => {
    const password = passwordInput.value;
    passwordInput.value = "";
    const isValidPassword = password.length >= 8;

    if (!isValidPassword) {
        alert('Password length must be 8 or more characters');
        return;
    }

    uploadFiles(password, Array.from(fileInput.files));
    localStorage.setItem('masterPassword', password);
    modal.style.display = 'none';
});

async function uploadFiles(password, files) {
    for (const file of files) {
        const fileId = generateRandomId();
        const aesKey = generateEncryptionKey(password, fileId);

        const encryptedFile = await encryptFile(file, aesKey);
        postEncryptedFile(fileId, encryptedFile);
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

async function encryptFile(file, key) {
    const fileReader = new FileReader();

    return new Promise((resolve, reject) => {
        fileReader.onload = (e) => {
            const fileData = e.target.result;
            const encryptedData = {
                name: CryptoJS.AES.encrypt(file.name, key).toString(),
                type: CryptoJS.AES.encrypt(file.type, key).toString(),
                content: CryptoJS.AES.encrypt(fileData, key).toString()
            };
            resolve(encryptedData);
        };

        fileReader.onerror = reject;
        fileReader.readAsText(file);
    });
}

function compress(uncompressedString) {
    const binaryString = pako.deflate(uncompressedString, { to: 'string' });
    return btoa(binaryString);
}

function decompress(compressedString) {
    const binaryString = atob(compressedString);
    const decompressedString = pako.inflate(binaryString, { to: 'string' });
    return decompressedString;
}

function postEncryptedFile(fileId, encryptedFile) {//need to slice into a bunch of smaller files with serial for reconstruction
    fetch('/files/upload', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            id: fileId,
            name: encryptedFile.name,
            type: encryptedFile.type,
            content: compress(encryptedFile.content)
        })
    }).then(response => {
        if (response.ok) {
            console.log('File uploaded successfully');
        } else {
            console.error('Upload failed');
        }
    }).catch(error => console.error('Error uploading file:', error));
}