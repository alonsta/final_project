const storedPassword = getCookie("pass");
let folderIdStack = [];
let currentLoadToken = null; // Token to track the current load operation
let backButtonCooldown = false;
const progressIndicator = document.getElementById('progress-indicator');
const progressBar = progressIndicator.querySelector('.progress-bar');
const progressText = progressIndicator.querySelector('.progress-text');

const createBtn = document.getElementById('create_folder_btn');
const popup = document.getElementById('folder_popup');
const input = document.getElementById('folder_name_input');

function formatFileSize(bytes) {
  if (bytes === 0) return '0 Bytes';

  const units = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
  const unitIndex = Math.floor(Math.log(bytes) / Math.log(1024));
  const size = (bytes / Math.pow(1024, unitIndex)).toFixed(2);

  return `${size} ${units[unitIndex]}`;
}

document.getElementById('go_back_btn').addEventListener('click', () => {
  if (backButtonCooldown) return;

  backButtonCooldown = true;
  setTimeout(() => {
    backButtonCooldown = false;
  }, 300); // 0.3 second cooldown

  // Cancel all pending file loads
  currentLoadToken = null;

  if (folderIdStack.length > 0) {
    const previousId = folderIdStack.pop();

    document.getElementById('folder_path').setAttribute('current-id', previousId);
    document.getElementById('folder_path').setAttribute('last-id', folderIdStack[folderIdStack.length - 1] || "-1");

    let currentPath = document.getElementById('path_display').textContent;
    let pathParts = currentPath.split('/');
    pathParts.pop(); // remove last
    document.getElementById('path_display').textContent = pathParts.join('/');

    loadUserFiles(); // safe because prior load is now cancelled
  }
});

createBtn.addEventListener('click', (e) => {
  e.stopPropagation();
  
  // Get button position
  const rect = createBtn.getBoundingClientRect();
  const offsetX = 10;
  const offsetY = 5;

  // Position popup next to the button
  popup.style.left = `${rect.right + offsetX}px`;
  popup.style.top = `${rect.top + offsetY}px`;
  popup.style.display = 'block';

  input.value = '';
  input.focus();
});

document.addEventListener('click', (e) => {
  if (!popup.contains(e.target) && e.target !== createBtn) {
    popup.style.display = 'none';
  }
});

input.addEventListener('keydown', (e) => {
  if (e.key === 'Enter') {
    const folderName = input.value.trim();
    let parentId = document.getElementById('folder_path').getAttribute('current-id');
    if (folderName) {
      //here look for the parent id of the folder from the parent div. also create an id for the folder and encrypt it with the secret sauce
      createFolder(folderName, parentId);
      popup.style.display = 'none';
    }
  }
});

async function createFolder(name, parentId) {
  if(name.length > 32)
    {alert("Folder name too long!"); return;}

  let server_key = generateRandomId();
  let password = getCookie("pass");
  let key = generateEncryptionKey(password, server_key);
  let encryptedFolderName = CryptoJS.AES.encrypt(CryptoJS.enc.Utf8.parse(name), key).toString();

  let response = await fetch('/files/create/folder', {
    method: 'POST',
    body: JSON.stringify({
      server_key: server_key,
      folder_name: encryptedFolderName,
      parent_id: parentId
    })
  });

  if (response.ok) {
    console.log('Folder created successfully!');
    
    // Stack push
    folderIdStack.push(parentId);

    document.getElementById('folder_path').setAttribute('last-id', parentId);
    document.getElementById('folder_path').setAttribute('current-id', server_key);
    document.getElementById('path_display').textContent += "/" + name;
    loadUserFiles();
  }
}
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
  const storedPassword = getCookie("pass");
  loadUserStats();
  loadUserFiles();

  setInterval(() => {
      loadUserFiles();
      loadUserStats();
    }, 30000); // Refresh every 15 seconds
  });


/**
 * Switches between different content sections
 * @param {string} tabName - The ID of the tab to switch to
 */
function switchTab(tabName) {
  const sections = document.querySelectorAll('.content-section');
  sections.forEach(section => section.classList.add('hidden'));
  const tabs = document.querySelectorAll('.sidebar .tab');
  tabs.forEach(tab => tab.classList.remove('active'));
  const activeSection = document.getElementById(tabName);
  const activeTab = document.getElementById(tabName + '-tab');
  if (activeSection) {
    activeSection.classList.remove('hidden');
    activeTab.classList.add('active');
  }
}

document.getElementById('logout-btn').addEventListener('click', () => {

  localStorage.clear();
  sessionStorage.clear();


  document.cookie.split(";").forEach(cookie => {
    const eqPos = cookie.indexOf("=");
    const name = eqPos > -1 ? cookie.substr(0, eqPos) : cookie;
    document.cookie = `${name}=;expires=Thu, 01 Jan 1970 00:00:00 GMT;path=/`;
  });
  location.reload();
});

/**
 * Loads and displays user statistics
 */
let userChart = null; // Store the Chart instance globally

async function loadUserStats() {
  const overviewDiv = document.getElementById('overview');
  const canvas = document.getElementById('statsChart');
  const ctx = canvas?.getContext('2d');
  const fileCountDiv = document.getElementById('file_count');
  
  if (!overviewDiv || !fileCountDiv) {
    console.error('Required DOM elements not found');
    return;
  }

  // Reset previous chart if exists
  if (userChart) {
    userChart.destroy();
    userChart = null;
  }

  // Clear previous content safely
  overviewDiv.innerHTML = '';
  fileCountDiv.innerHTML = '';

  try {
    const response = await fetch('/users/info', {
      credentials: 'include',
      method: 'GET'
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const stats = await response.json();
    let { username, uploaded, downloaded, fileCount } = stats;

    let uploadeds = formatFileSize(uploaded);
    let downloadeds = formatFileSize(downloaded);

    overviewDiv.innerHTML = `
      <h2 style="text-align:center;">Welcome back, <strong>${username}</strong>! 🎉</h2>
      <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 20px; margin-top: 20px;">
      
        <div style="background: #f0f9ff; padding: 15px; border-radius: 10px; text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
          <h3>📂 Files</h3>
          <p style="font-size: 1.5em; margin: 10px 0;">${fileCount}</p>
          <small>Total files on system</small>
        </div>

        <div style="background: #e8f5e9; padding: 15px; border-radius: 10px; text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
          <h3>☁️ Uploaded</h3>
          <p style="font-size: 1.5em; margin: 10px 0;">${uploadeds}</p>
          <small>Data stored</small>
        </div>

        <div style="background: #e3f2fd; padding: 15px; border-radius: 10px; text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
          <h3>🔻 Downloaded</h3>
          <p style="font-size: 1.5em; margin: 10px 0;">${downloadeds}</p>
          <small>Data received</small>
        </div>

        <div style="background: #fff3e0; padding: 15px; border-radius: 10px; text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
          <h3>💾 Server Space</h3>
          <div style="background: #e0e0e0; border-radius: 10px; overflow: hidden; height: 20px; width: 100%; margin: 10px 0;">
            <div style="background: #4caf50; width: ${Math.min((uploaded / (20 * 1024 ** 3)) * 100, 100).toFixed(2)}%; height: 100%; transition: width 0.5s;"></div>
          </div>
          <small>Space used out of 20GB</small>
        </div>

      </div>
    `;

    // Create a new chart and store the reference
    userChart = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: ['Uploaded', 'Downloaded'],
        datasets: [{
          label: 'Data Transfer (in MB)',
          data: [uploaded, downloaded],
          backgroundColor: ['#4caf50', '#2196f3'],
          borderRadius: 10,
        }]
      },
      options: {
        responsive: true,
        plugins: {
          legend: { display: false },
          title: {
            display: true,
            text: `📊 Your Data Journey`
          }
        },
        scales: {
          y: {
            beginAtZero: true,
            ticks: {
              stepSize: 50
            }
          }
        }
      }
    });

    // Update file count separately at the bottom
    fileCountDiv.innerHTML = `<strong>📂 Total Files:</strong> ${fileCount}`;

  } catch (error) {
    console.error('Error loading user stats:', error);
    overviewDiv.innerHTML = 'Failed to load user statistics. 😢';
  }
}


async function loadUserFiles() {
    const thisToken = Symbol();
    currentLoadToken = thisToken; // Set the current load token
    const password = getCookie("pass");
    const fileSection = document.getElementById('files_grid');

    fileSection.querySelectorAll('.file-item').forEach(item => item.remove());


    try {
      let parent_id = document.getElementById('folder_path').getAttribute('current-id');
        const response = await fetch(`/files/folder?parent=${parent_id}`, {
            credentials: 'include',
            method: 'GET'
        });
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`); // Check response ok

        const files = await response.json();

        for (const key in files) {
            if (currentLoadToken !== thisToken) return;
            const file = files[key];
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
            let type = file.type; // Get type for file type check

            // Create UI elements (Your existing code)
            const fileContainer = document.createElement('div');
            fileContainer.className = 'file-item';
            
            if(type === 0){
              fileContainer.addEventListener('dblclick', async () => {
                if (progressIndicator.style.display === 'block') {
                  alert("Another operation is already in progress."); // Prevent concurrent operations on the same indicator
                  return;
                }
                try {
                  let currentId = document.getElementById('folder_path').getAttribute('current-id');
                  // Stack push
                  folderIdStack.push(currentId);

                  document.getElementById('folder_path').setAttribute('last-id', currentId);
                  document.getElementById('folder_path').setAttribute('current-id', server_key);
                  
                  const pathDisplay = document.getElementById('path_display');
                  pathDisplay.textContent += "/" + decryptedFileName;

                  loadUserFiles(); // Reload files to show the new folder
                } catch (error) {alert('Failed to open folder. Please try again later.');}

              });

            }
            else{
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
              });}
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
              if (extension === '') return '📁';
              return '🥸'; // Default/fallback
          }
          // Create file type icon
          function handleDelete(fileId) {
            fetch(`/files/delete/file?key=${fileId}`, {
                method: 'DELETE',
                credentials: 'include'
            })
            .then(response => {
                if (response.ok) {
                    console.log(`File ${decryptedFileName} deleted successfully.`);
                    fileContainer.remove();
                } else {
                    console.error(`Failed to delete file ${decryptedFileName}. Status: ${response.status}`);
                }
            })
            .catch(error => {
                console.error(`Error deleting file ${decryptedFileName}:`, error);
            });
        }
        const iconSpan = document.createElement('span');
        const extension = decryptedFileName.includes('.') ? decryptedFileName.split('.').pop() : '';
        iconSpan.textContent = getFileIcon(extension);
        fileContainer.appendChild(iconSpan);

        // File name
        const fileLabel = document.createElement('span');
        fileLabel.className = 'file-label';
        fileLabel.textContent = decryptedFileName;

        // File size
        const fileSize = document.createElement('span');
        fileSize.className = 'file-size';
        fileSize.textContent = formatFileSize(file.size);
        if(type === 0) {fileSize.style.display = 'none';} // Hide size for folders
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
        if(type === 0) {shareBtn.style.display = 'none';} // Hide share button for folders

        const deleteBtn = document.createElement('button');
        deleteBtn.className = 'dropdown-btn';
        deleteBtn.textContent = 'Delete';

        shareBtn.onclick = (event) => {
          event.stopPropagation();
          handleShare(server_key, encryptionKey);
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
          globalMenu.querySelector('.dropdown-btn:nth-child(1)').onclick = () => handleShare(server_key, encryptionKey);
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

function generateEncryptionKey(password, fileId) {
    const masterHash = CryptoJS.SHA256(password).toString();
    const combined = fileId + masterHash;
    return CryptoJS.MD5(combined).toString();
}

async function hashString(password, salt) {
  let saltedInput = salt + password;
  let hash = CryptoJS.SHA256(saltedInput);
  return hash.toString(CryptoJS.enc.Hex);
}

function generateRandomId() {
  return Math.random().toString(36).substring(2, 15);
}

function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(';').shift();
  return null;
}

function handleShare(fileId, key) {
            fetch('/share', {
                method: 'POST',
                credentials: 'include',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    password: key,
                    server_key: fileId
                })
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Failed to unlock file. Status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                if (data && data.share_link) {
                    navigator.clipboard.writeText(data.share_link)
                        .then(() => {
                            showBubble("✅ Share link copied to clipboard!");
                        })
                        .catch(() => {
                            showBubble("⚠️ Couldn't copy to clipboard");
                        });
                } else {
                    showBubble("❌ Invalid response from server.");
                }
            })
            .catch(error => {
                console.error("Error:", error);
                showBubble("❌ Failed to unlock or copy link.");
            });
        }
      
function showBubble(message) {
    const bubble = document.getElementById("bubble");
    bubble.textContent = message;
    bubble.style.opacity = 1;

    setTimeout(() => {
        bubble.style.opacity = 0;
    }, 3000); // hide after 3 seconds
}
