const passwordModal = document.getElementById('password-modal');
const passwordInput = document.getElementById('password');
const confirmButton = document.getElementById('confirm-button');
const cancelButton = document.getElementById('cancel-button');


const progressIndicator = document.getElementById('progress-indicator');
const progressBar = progressIndicator.querySelector('.progress-bar');
const progressText = progressIndicator.querySelector('.progress-text');

// --- Helper function to show/update/hide indicator ---
function updateProgress(state, message, percentage = null, isError = false, isDownload = false) {
    if (state === 'show') {
        progressIndicator.classList.remove('error', 'download'); // Reset classes
        if(isError) progressIndicator.classList.add('error');
        if(isDownload) progressIndicator.classList.add('download');

        progressText.textContent = message;
        progressBar.style.width = (percentage !== null) ? `${percentage}%` : '0%';
        progressIndicator.style.display = 'block';
        progressIndicator.style.opacity = '1';
    } else if (state === 'update') {
         progressText.textContent = message;
         if (percentage !== null) {
             progressBar.style.width = `${percentage}%`;
         }
    } else if (state === 'hide') {
        progressIndicator.style.opacity = '0';
        // Wait for fade out before hiding completely
        setTimeout(() => {
            progressIndicator.style.display = 'none';
            progressIndicator.classList.remove('error', 'download'); // Clean up classes
        }, 500); // Matches CSS transition duration
    }
}

// --- Add this to your existing event listeners ---
document.addEventListener('DOMContentLoaded', () => {
  switchTab('overview'); // Default tab on load
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
  
  if (password.length < 8 || password.length > 32) {
    alert('Password must be between 8 and 32 characters long.');
    passwordInput.value = ''; // Clear input
    passwordInput.focus(); // Focus back on input
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
    const fileSection = document.getElementById('files_grid');

    fileSection.querySelectorAll('.file-item').forEach(item => item.remove());


    try {
        const response = await fetch('/files/folder', {
            credentials: 'include',
            method: 'GET'
        });
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`); // Check response ok

        const files = await response.json();

        for (const key in files) {
          
            const file = files[key];
            if(file.type == 0) continue;
            const server_key = file.server_key;
            const encryptionKey = generateEncryptionKey(password, server_key);
            let decryptedFileName = "Filename Error"; // Default filename in case of decryption error
             try {
                decryptedFileName = CryptoJS.AES.decrypt(file.file_name, encryptionKey).toString(CryptoJS.enc.Utf8);
                 if (!decryptedFileName) { // Handle cases where decryption results in empty string
                     decryptedFileName = "corrupt/unnamed File";
                 }
            } catch (e) {
                 console.error(`Failed to decrypt filename for key ${server_key}:`, e);
            }

            const size = file.size;
            const chunk_count = file.chunk_count; // Get chunk_count for progress calculation

            // Create UI elements (Your existing code)
            const fileContainer = document.createElement('div');
            fileContainer.className = 'file-item';
            
            fileContainer.addEventListener('dblclick', async () => {
                 if (progressIndicator.style.display === 'block') {
                    alert("Another operation is already in progress."); // Prevent concurrent operations on the same indicator
                    return;
                }

                try {
                    const chunks = [];
                    let chunkIndex = 0;

                    // --- Show Progress Indicator for Download ---
                     updateProgress('show', `Starting download: ${decryptedFileName}`, 0, false, true); // isDownload = true

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

                             // --- Update Download Progress ---
                            const percentComplete = Math.round((chunkIndex / chunk_count) * 100);
                            updateProgress('update', `Downloading ${decryptedFileName} ${percentComplete}%`, percentComplete, false, true);

                        } else {
                             throw new Error(`Chunk download failed (Index: ${chunkIndex}, Status: ${response.status})`);
                        }
                    }

                    // --- All chunks downloaded, prepare Blob ---
                    updateProgress('update', `Download complete: ${decryptedFileName}. Preparing file...`, 100, false, true);

                    const blob = new Blob(chunks);
                    const url = URL.createObjectURL(blob);
                    const tempLink = document.createElement('a');
                    tempLink.href = url;
                    tempLink.download = decryptedFileName;
                    document.body.appendChild(tempLink); // Required for Firefox
                    tempLink.click();
                    document.body.removeChild(tempLink); // Clean up
                    URL.revokeObjectURL(url);

                    // --- Hide indicator after success ---
                     setTimeout(() => updateProgress('hide'), 1000); // Hide shortly after click initiated

                } catch (error) {
                    console.error('Download failed:', error);
                     // --- Show error and hide ---
                     updateProgress('show', `Download failed: ${decryptedFileName}`, null, true); // isError = true
                     setTimeout(() => updateProgress('hide'), 3000);
                }
            });
            // --- END OF MODIFIED Listener ---

            function getFileIcon(extension) {
              extension = extension.toLowerCase();
          
              const imageExts = ['png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp', 'svg'];
              const videoExts = ['mp4', 'mov', 'avi', 'mkv', 'webm'];
              const audioExts = ['mp3', 'wav', 'ogg', 'flac', 'm4a'];
              const docExts   = ['doc', 'docx'];
              const pptExts   = ['ppt', 'pptx'];
              const xlsExts   = ['xls', 'xlsx'];
              const codeExts  = ['js', 'ts', 'jsx', 'tsx', 'html', 'css', 'py', 'java', 'c', 'cpp', 'rb', 'php', 'cs', 'go', 'swift', 'sql', 'bash', 'sh', 'pl', 'r', 'dart', 'kotlin', 'lua', 'yaml', 'json'];
          
              if (imageExts.includes(extension)) return '🖼️';
              if (videoExts.includes(extension)) return '🎬';
              if (audioExts.includes(extension)) return '🎧';
              if (extension === 'pdf') return '📄';
              if (['zip', 'rar', '7z', 'tar', 'gz'].includes(extension)) return '🗜️';
              if (['txt', 'md', 'log'].includes(extension)) return '📃';
              if (['csv'].includes(extension)) return '📊';
              if (xlsExts.includes(extension)) return '📊';
              if (pptExts.includes(extension)) return '📽️';
              if (docExts.includes(extension)) return '📝';
              if (['json', 'xml'].includes(extension)) return '🧾';
              if (['db', 'sqlite'].includes(extension)) return '🗄️';
              if (['apk'].includes(extension)) return '📱';
              if (['exe', 'msi'].includes(extension)) return '💻';
              if (codeExts.includes(extension)) return '💻';
          
              return '🥸'; // Default/fallback
          }
          // Create file type icon
          function handleDelete(fileId) {
            fetch(`/files/delete?key=${fileId}`, {
                method: 'DELETE',
                credentials: 'include'
            })
            .then(response => {
                if (response.ok) {
                    console.log(`File ${file.name} deleted successfully.`);
                    fileContainer.remove();
                } else {
                    console.error(`Failed to delete file ${file.name}. Status: ${response.status}`);
                }
            })
            .catch(error => {
                console.error(`Error deleting file ${file.name}:`, error);
            });
        }
        const iconSpan = document.createElement('span');
        iconSpan.textContent = getFileIcon(decryptedFileName.split('.').pop());
        fileContainer.appendChild(iconSpan);

        // File name
        const fileLabel = document.createElement('span');
        fileLabel.className = 'file-label';
        fileLabel.textContent = decryptedFileName;

        // File size
        const fileSize = document.createElement('span');
        fileSize.className = 'file-size';
        fileSize.textContent = formatFileSize(file.size);

        // Dropdown toggle arrow
        const toggleArrow = document.createElement('span');
        toggleArrow.className = 'dropdown-toggle';
        toggleArrow.textContent = '▼';

        // Dropdown menu
        const dropdownMenu = document.createElement('div');
        dropdownMenu.className = 'dropdown-menu';
        dropdownMenu.style.display = 'none'; // Initially hidden

        const shareBtn = document.createElement('button');
        shareBtn.className = 'dropdown-btn';
        shareBtn.textContent = 'Share';

        const deleteBtn = document.createElement('button');
        deleteBtn.className = 'dropdown-btn';
        deleteBtn.textContent = 'Delete';

        shareBtn.onclick = (event) => {
          event.stopPropagation();
          handleShare(server_key);
        };
      
      deleteBtn.onclick = (event) => {
          event.stopPropagation();
          handleDelete(server_key);
        };

        dropdownMenu.appendChild(shareBtn);
        dropdownMenu.appendChild(deleteBtn);

        toggleArrow.onclick = (event) => {
          event.stopPropagation();
      
          // Remove any existing dropdown to avoid duplicates
          const existingMenu = document.querySelector('.dropdown-menu.global');
          if (existingMenu) existingMenu.remove();
      
          const rect = toggleArrow.getBoundingClientRect();
      
          // Clone dropdown to body
          const globalMenu = dropdownMenu.cloneNode(true);
          globalMenu.classList.add('global');
          globalMenu.style.display = 'block';
          globalMenu.style.position = 'fixed';
          globalMenu.style.top = `${rect.bottom}px`;
          globalMenu.style.left = `${rect.left}px`;
      
          // Add functionality back to buttons
          globalMenu.querySelector('.dropdown-btn:nth-child(1)').onclick = () => handleShare(server_key);
          globalMenu.querySelector('.dropdown-btn:nth-child(2)').onclick = () => handleDelete(server_key);
      
          document.body.appendChild(globalMenu);
      };

      document.addEventListener('click', () => {
        const existingMenu = document.querySelector('.dropdown-menu.global');
        if (existingMenu) existingMenu.remove();
      });

        fileContainer.appendChild(dropdownMenu);
        fileContainer.appendChild(fileLabel);
        fileContainer.appendChild(fileSize);
        fileContainer.appendChild(toggleArrow);

        fileSection.appendChild(fileContainer);
        }
    } catch (error) {
        console.error('Error loading user files:', error);
        fileSection.innerHTML = '<p style="color: red;">Error loading files. Please check console or try again later.</p>';
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
