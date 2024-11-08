function switchTab(tabName) {
    const sections = document.querySelectorAll(".content-section");
    sections.forEach(section => section.classList.add("hidden"));
    
    const activeSection = document.getElementById(tabName);
    if (activeSection) {
        activeSection.classList.remove("hidden");
    }
}

const dropZone = document.querySelector('#files');

dropZone.addEventListener('dragenter', (e) => {
    e.preventDefault(); 
});

dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
});

dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    document.getElementById('file').files = e.dataTransfer.files;
    const fileInput = document.getElementById('file');

    const files = fileInput.files;

    for (const file of files) {
        const fileName = file.name;

        const fileType = file.type;

        const fileSize = file.size;

        const fileReader = new FileReader();
        fileReader.onload = function(e) {
            const fileData = e.target.result;
            console.log('File content:', fileData);
        };
        fileReader.readAsText(file);

        console.log(`File Name: ${fileName}`);
        console.log(`File Type: ${fileType}`);
        console.log(`File Size: ${fileSize} bytes`);

        modal.style.display = 'flex'
    }
});

//tests

const modal = document.getElementById('password-modal');
const uploadButton = document.getElementById('upload-button');
const cancelButton = document.getElementById('cancel-button');

cancelButton.addEventListener('click', () => {
    modal.style.display = 'none';  // Hide modal
});

uploadButton.addEventListener('click', () => {
    const password = document.getElementById('password').value;

    // Validate password length (128, 192, or 256 bits)
    const isValidPassword = password.length === 16 || password.length === 24 || password.length === 32;

    if (!isValidPassword) {
        alert('Password length must be 16, 24, or 32 bits long.');
        return;
    }

    // Encrypt the file and upload (your encryption logic would go here)
    for (const file of droppedFiles) {
        console.log('Encrypting and uploading file:', file.name);
    }

    // Close modal after upload
    modal.style.display = 'none';
});