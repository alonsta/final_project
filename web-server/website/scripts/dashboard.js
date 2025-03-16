const passwordModal = document.getElementById('password-modal');
const passwordInput = document.getElementById('password');
const confirmButton = document.getElementById('confirm-button');
const cancelButton = document.getElementById('cancel-button');

document.addEventListener('DOMContentLoaded', () => {
  const storedPassword = sessionStorage.getItem('filePassword');
  if (!storedPassword) {
    loadUserStats();
    showPasswordModal(true);
  } else {
    loadUserStats();
    loadUserFiles();
  }
});

/**
 * Shows the password modal with appropriate content based on context
 * @param {boolean} isInitial - Whether this is the initial password setup
 */
function showPasswordModal(isInitial = false) {
  passwordModal.style.display = 'flex';
  passwordModal.classList.remove('hidden');
  
  const modalTitle = document.querySelector('#password-modal h2');
  const noteText = document.getElementById('note');
  
  if (isInitial) {
    modalTitle.textContent = 'Set Your File Password';
    noteText.textContent = 'This password will be used to encrypt all your files. Keep it safe!';
    cancelButton.style.display = 'none';
    confirmButton.textContent = 'Set Password';
  } else {
    modalTitle.textContent = 'Confirm File Upload';
    noteText.textContent = 'Your stored password will be used to encrypt this file.';
    cancelButton.style.display = 'block';
    confirmButton.textContent = 'Confirm';
  }
}

confirmButton.addEventListener('click', () => {
  const password = passwordInput.value;
  
  if (password.length < 8) {
    alert('Password length must be 8 or more characters');
    return;
  }
  
  try {
    sessionStorage.setItem('filePassword', password);
    passwordModal.style.display = 'none';
    loadUserFiles();
    loadUserStats();
  } catch (error) {
    console.error('Error storing password:', error);
    alert('Failed to store password. Please try again.');
  }
});

/**
 * Switches between different content sections
 * @param {string} tabName - The ID of the tab to switch to
 */
function switchTab(tabName) {
  const sections = document.querySelectorAll('.content-section');
  sections.forEach(section => section.classList.add('hidden'));
  
  const activeSection = document.getElementById(tabName);
  if (activeSection) {
    activeSection.classList.remove('hidden');
  }
}

/**
 * Loads and displays user statistics
 */
async function loadUserStats() {
  const overviewDiv = document.getElementById('overview');
  const ctx = document.getElementById('statsChart')?.getContext('2d');
  const fileCountDiv = document.getElementById('file_count');
  
  if (!ctx || !overviewDiv || !fileCountDiv) {
    console.error('Required DOM elements not found');
    return;
  }
  
  try {
    const response = await fetch('/users/info', {
      credentials: 'include',
      method: 'GET'
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const stats = await response.json();
    const { username, uploaded, downloaded, fileCount } = stats;
    
    fileCountDiv.innerHTML = `<strong>Total Files: </strong>${fileCount}`;
    
    // Create chart with sanitized data
    new Chart(ctx, {
      type: 'pie',
      data: {
        labels: ['Uploaded Data (MB)', 'Downloaded Data (MB)'],
        datasets: [{
          data: [
            Number(uploaded) / (1024 * 1024) || 0,
            Number(downloaded) / (1024 * 1024) || 0
          ],
          backgroundColor: ['#4caf50', '#2196f3'],
          hoverBackgroundColor: ['#45a049', '#1e88e5']
        }]
      },
      options: {
        plugins: {
          legend: {
            display: true,
            position: 'bottom'
          },
        title: {
          display: true,
          text: `Stats for ${username}`
        }
      }
    }});
  } catch (error) {
    console.error('Error loading user stats:', error);
    overviewDiv.innerHTML = 'Failed to load user statistics';
  }}

async function loadUserFiles() {
  const password = sessionStorage.getItem('filePassword');
  try {
      const response = await fetch('/files/info', {
          credentials: 'include',
          method: 'GET'
      });
      const files = await response.json();
      for (const key in files) {
          const file = files[key];
          const server_key = file.server_key;
          const encryptionKey = generateEncryptionKey(password, server_key);
          const decryptedFileName = CryptoJS.AES.decrypt(file.file_name, encryptionKey).toString(CryptoJS.enc.Utf8);
          const size = file.size;

          // Create UI elements
          const fileSection = document.querySelector('#files.content-section');
          const fileContainer = document.createElement('div');
          fileContainer.className = 'file-item';

          const fileLabel = document.createElement('span');
          fileLabel.className = 'file-label';
          fileLabel.textContent = `${decryptedFileName} (${(size / (1024 * 1024)).toFixed(2)} MB)`;

          const buttonContainer = document.createElement('div');
          buttonContainer.className = 'button-container';

          const downloadButton = document.createElement('button');
          downloadButton.className = 'download-button';
          downloadButton.textContent = 'Download';

          downloadButton.addEventListener('click', async () => {
              try {
                  const chunks = [];
                  let chunkIndex = 0;
                  let chunk_count = file.chunk_count;

                  while (chunkIndex < chunk_count) {
                      const response = await fetch(`/files/download?key=${server_key}&index=${chunkIndex}`, {
                          method: 'GET',
                          credentials: 'include'
                      });

                      if (response.ok) {
                          const encryptedChunk = await response.text();
                          const decryptedChunk = await decryptAndDecompressChunk(encryptedChunk, encryptionKey);
                          chunks.push(decryptedChunk);
                          chunkIndex++;
                      } else {
                          console.error("chunk counting corruption or other problems")
                      }
                  }

                  const blob = new Blob(chunks);
                  const url = URL.createObjectURL(blob);
                  const tempLink = document.createElement('a');
                  tempLink.href = url;
                  tempLink.download = decryptedFileName;
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
      }
  } catch (error) {
      console.error('Error loading user files:', error);
  }
}

async function decryptAndDecompressChunk(encryptedChunk, key) {
    // Decrypt
    const decrypted = CryptoJS.AES.decrypt(encryptedChunk, key);
    const base64 = decrypted.toString(CryptoJS.enc.Utf8);
    
    // Convert base64 to binary
    const binary = atob(base64);
    const bytes = new Uint8Array(binary.length);
    for (let i = 0; i < binary.length; i++) {
        bytes[i] = binary.charCodeAt(i);
    }
    
    // Decompress
    return pako.inflate(bytes);
}

function decryptChunk(encryptedChunk, key) {
    const decrypted = CryptoJS.AES.decrypt(encryptedChunk, key);
    const decryptedData = decrypted.toString(CryptoJS.enc.Utf8);

    const byteCharacters = atob(decryptedData);
    const byteNumbers = new Array(byteCharacters.length);
    for (let i = 0; i < byteCharacters.length; i++) {
        byteNumbers[i] = byteCharacters.charCodeAt(i);
    }
    return new Uint8Array(byteNumbers);
}

function generateEncryptionKey(password, fileId) {
    const masterHash = CryptoJS.SHA256(password).toString();
    const combined = fileId + masterHash;
    return CryptoJS.MD5(combined).toString();
}

async function decryptFile(base64String, key) {
  try {
      // 1. Decode Base64 to binary
      const rawData = atob(base64String);
      const bytes = new Uint8Array(rawData.length);
      for (let i = 0; i < rawData.length; i++) {
          bytes[i] = rawData.charCodeAt(i);
      }

      // 2. Decrypt binary data
      const decrypted = CryptoJS.AES.decrypt(
          { ciphertext: CryptoJS.lib.WordArray.create(bytes) },
          key
      );

      // 3. Convert to Uint8Array
      const decryptedBytes = new Uint8Array(decrypted.sigBytes);
      for (let i = 0; i < decrypted.sigBytes; i++) {
          decryptedBytes[i] = (decrypted.words[i >>> 2] >>> (24 - (i % 4) * 8)) & 0xff;
      }

      // 4. Decompress
      const decompressed = pako.inflate(decryptedBytes);
      
      return new Blob([decompressed]);
  } catch (error) {
      console.error('Decryption failed:', error);
      throw error;
  }
}
