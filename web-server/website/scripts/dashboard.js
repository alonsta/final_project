const passwordModal = document.getElementById('password-modal');
const passwordInput = document.getElementById('password');
const confirmButton = document.getElementById('confirm-button');
const cancelButton = document.getElementById('cancel-button');

document.addEventListener('DOMContentLoaded', () => {
  const storedPassword = localStorage.getItem('filePassword');
  if (!storedPassword) {
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
    localStorage.setItem('filePassword', password);
    passwordModal.style.display = 'none';
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

function generateEncryptionKey(password, fileId) {
    const masterHash = CryptoJS.SHA256(password).toString();
    const combined = fileId + masterHash;
    return CryptoJS.MD5(combined).toString();
}

async function loadUserFiles() {
    const password = localStorage.getItem('filePassword');
    try {
        const response = await fetch('/files/info', {
            credentials: 'include',
            method: 'GET'
        });
        const files = await response.json();
        for(const key in files) {
            const file = files[key];
            let server_key = file.server_key;
            let encryptionKey = generateEncryptionKey(password, server_key);
            let decryptedFileName = CryptoJS.AES.decrypt(file.file_name, encryptionKey).toString(CryptoJS.enc.Utf8);
            let size = file.size;
            const fileSection = document.querySelector('#files.content-section');
            const fileContainer = document.createElement('div');
            fileContainer.className = 'file-item';
            
            const fileLabel = document.createElement('span');
            fileLabel.className = 'file-label';
            fileLabel.textContent = `${decryptedFileName} (${(size / (1024*1024)).toFixed(2)} MB)`;
            
            const buttonContainer = document.createElement('div');
            buttonContainer.className = 'button-container';
            
            const downloadButton = document.createElement('button');
            downloadButton.className = 'download-button';
            downloadButton.textContent = 'Download';
            
            downloadButton.addEventListener('click', async () => {
                try {
                    const response = await fetch(`/files/download?key=${server_key}`, {
                        method: 'GET',
                        credentials: 'include'
                    });
                    const blob = await response.blob();
                    const decryptedBlob = await decryptFile(blob, encryptionKey);

                    async function decryptFile(encryptedBlob, key) {
                      const arrayBuffer = await encryptedBlob.arrayBuffer();
                      const compressedData = new Uint8Array(arrayBuffer);
                  
                      // Decompress first
                      try {
                          const decompressedData = pako.inflate(compressedData);
                          const wordArray = CryptoJS.lib.WordArray.create(decompressedData);
                  
                          // Decrypt
                          const decrypted = CryptoJS.AES.decrypt({ ciphertext: wordArray }, key);
                  
                          // Convert decrypted WordArray to Uint8Array
                          const decryptedArray = new Uint8Array(decrypted.sigBytes);
                          for (let i = 0; i < decrypted.sigBytes; i++) {
                              decryptedArray[i] = (decrypted.words[i >>> 2] >>> (24 - (i % 4) * 8)) & 0xff;
                          }
                  
                          return new Blob([decryptedArray]);
                      } catch (error) {
                          console.error('Decompression failed:', error);
                          throw new Error('Invalid compressed data');
                      }
                  }

                    const url = URL.createObjectURL(decryptedBlob);
                    const tempLink = document.createElement('a');
                    tempLink.href = url;
                    tempLink.download = decryptedFileName;
                    tempLink.click();
                    URL.revokeObjectURL(url);
                } catch (error) {
                    console.error('Download failed:', error);
                    alert('Failed to download file');
                }
            });
            
            buttonContainer.appendChild(downloadButton);
            fileContainer.appendChild(fileLabel);
            fileContainer.appendChild(buttonContainer);
            fileSection.appendChild(fileContainer);
        }
    } catch (error) {
        console.error('Error loading user files:', error);
    }}


