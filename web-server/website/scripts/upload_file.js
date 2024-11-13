async function uploadFile(password, file) {

    const fileId = generateRandomId();
    const aesKey = generateEncryptionKey(password, fileId);

    const encryptedFile = await encryptFile(file, aesKey);
    postEncryptedFile(fileId, encryptedFile);
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

function postEncryptedFile(fileId, encryptedFile) {
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
