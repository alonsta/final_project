const dropZone = document.getElementById('files');
const fileInput = document.getElementById('file');
const CHUNK_SIZE = 1024 * 1024 * 2 ; // 2MB chunks

dropZone.addEventListener('dragenter', (e) => e.preventDefault());
dropZone.addEventListener('dragover', (e) => e.preventDefault());
dropZone.addEventListener('drop', handleFileDrop);

function handleFileDrop(e) {
    e.preventDefault();
    fileInput.files = e.dataTransfer.files;
    processFiles(storedPassword, Array.from(fileInput.files));
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


async function processFiles(password, files) {
    let parent_id = document.getElementById('folder_path').getAttribute("current-id")
    for (const file of files) {
        let fileId;
        let totalChunks = 0;
        try {
            fileId = generateRandomId();
            const key = generateEncryptionKey(password, fileId);
            const encryptedFileName = CryptoJS.AES.encrypt(CryptoJS.enc.Utf8.parse(file.name), key).toString();

            // Calculate chunk count
            totalChunks = Math.ceil(file.size / CHUNK_SIZE);

            // --- Show progress for the current file ---
            updateProgress('show', `Starting upload: ${file.name}`, 0);

            // Send file metadata first
            const metadataResult = await sendFileMetadata(fileId, encryptedFileName, totalChunks, file.size, parent_id);

            if (!metadataResult.ok) {
                if (metadataResult.reason === "quota") {
                    showBubble("🚫 Upload denied: you've reached your 20GB storage limit.");
                } else {
                    showBubble("❌ Failed to send file metadata.");
                }
                return; 
            }


            // Process file in chunks
            for (let i = 0; i < totalChunks; i++) { // Use totalChunks
                const start = i * CHUNK_SIZE;
                const end = Math.min(start + CHUNK_SIZE, file.size);
                const chunk = file.slice(start, end);

                // Read chunk
                const chunkData = await readChunk(chunk);
                // Compress and encrypt chunk
                const processedChunk = await compressAndEncryptChunk(chunkData, key);

                // Send chunk
                await uploadChunk(fileId, i, processedChunk);

                // --- Update progress after each chunk ---
                const percentComplete = Math.round(((i + 1) / totalChunks) * 100);
                updateProgress('update', `Uploading ${file.name} ${percentComplete}%`, percentComplete);
            }

             // --- Show success and hide after delay ---
             setTimeout(() => {
                updateProgress('update', `Upload complete: ${file.name}`);
                
                // Now schedule hiding AFTER 2 seconds
                setTimeout(() => {
                  updateProgress('hide');
                }, 2000);
              }, 0); // Start immediately (or after a small delay if needed)

            // Update UI for the file (Your existing UI update code)
            const fileSection = document.getElementById('files_grid');
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
                     updateProgress('show', `Starting download: ${file.name}`, 0, false, true); // isDownload = true

                    while (chunkIndex < totalChunks) { // Use totalChunks
                        const response = await fetch(`/files/download?key=${fileId}&index=${chunkIndex}`, {
                            method: 'GET',
                            credentials: 'include'
                        });

                        if (response.ok) {
                            const encryptedChunk = await response.text();
                            const decryptedChunk = await decryptAndDecompressChunk(encryptedChunk, key);
                            chunks.push(decryptedChunk);
                            chunkIndex++;

                             // --- Update Download Progress ---
                            const percentComplete = Math.round((chunkIndex / totalChunks) * 100);
                            updateProgress('update', `Downloading ${file.name} ${percentComplete}%`, percentComplete, false, true);

                        } else {
                             throw new Error(`Chunk download failed (Index: ${chunkIndex}, Status: ${response.status})`);
                        }
                    }

                    // --- All chunks downloaded, prepare Blob ---
                    updateProgress('update', `Download complete: ${file.name}. Preparing file...`, 100, false, true);

                    const blob = new Blob(chunks);
                    const url = URL.createObjectURL(blob);
                    const tempLink = document.createElement('a');
                    tempLink.href = url;
                    tempLink.download = file.name;
                    document.body.appendChild(tempLink); // Required for Firefox
                    tempLink.click();
                    document.body.removeChild(tempLink); // Clean up
                    URL.revokeObjectURL(url);

                    // --- Hide indicator after success ---
                     setTimeout(() => updateProgress('hide'), 1000); // Hide shortly after click initiated

                } catch (error) {
                    console.error('Download failed:', error);
                     // --- Show error and hide ---
                     updateProgress('show', `Download failed: ${file.name}`, null, true); // isError = true
                     setTimeout(() => updateProgress('hide'), 3000);
                }
            });
            
            function handleDelete(fileId) {
                fetch(`/files/delete/file?key=${fileId}`, {
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
                if (['txt', 'md', 'log',"json"].includes(extension)) return '📃';
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
            const iconSpan = document.createElement('span');
            iconSpan.textContent = getFileIcon(file.name.split('.').pop());
            fileContainer.appendChild(iconSpan);
    
            // File name
            const fileLabel = document.createElement('span');
            fileLabel.className = 'file-label';
            fileLabel.textContent = file.name;
    
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
              handleShare(fileId, key);
            };
          
            deleteBtn.onclick = (event) => {
              event.stopPropagation();
              handleDelete(fileId);
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
              globalMenu.querySelector('.dropdown-btn:nth-child(1)').onclick = () => handleShare(fileId, key);
              globalMenu.querySelector('.dropdown-btn:nth-child(2)').onclick = () => handleDelete(fileId);
          
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
            console.log(`File metadata sent for ${file.name}`);

        } catch (error) {
            console.error(`Error processing file ${file.name}:`, error);
             // --- Show error and hide after delay ---
             updateProgress('show', `Upload failed: ${file.name}`, null, true); // isError = true
             setTimeout(() => updateProgress('hide'), 3000); // Hide after 3 seconds
        }
    }
}


async function readChunk(chunk) {
    return new Promise((resolve) => {
        const reader = new FileReader();
        reader.onload = (e) => resolve(e.target.result);
        reader.readAsArrayBuffer(chunk);
    });
}

async function compressAndEncryptChunk(chunkData, key) {
    // Compress chunk
    const compressed = pako.deflate(new Uint8Array(chunkData));
    
    // Convert to base64 in smaller chunks to avoid stack overflow
    const chunkSize = 32768; // 32KB chunks for string conversion
    let binary = '';
    for (let i = 0; i < compressed.length; i += chunkSize) {
        const slice = compressed.subarray(i, i + chunkSize);
        binary += String.fromCharCode.apply(null, slice);
    }
    
    // Convert to base64
    const base64 = btoa(binary);
    
    // Encrypt
    return CryptoJS.AES.encrypt(base64, key).toString();
}


async function uploadChunk(fileId, index, chunk) {
    const response = await fetch('/files/upload/chunk', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            key: fileId,
            index: index,
            data: chunk
        }),
        credentials: 'include'
    });
    
    if (!response.ok) {
        throw new Error(`Failed to upload chunk ${index}`);
    }
}

function generateRandomId() {
    return Math.random().toString(36).substring(2, 15);
}

function generateEncryptionKey(password, fileId) {
    const salt = CryptoJS.enc.Utf8.parse(fileId);
    const key = CryptoJS.PBKDF2(password, salt, {
        keySize: 256 / 32,
        iterations: 100000,
        hasher: CryptoJS.algo.SHA256
    });
    return key.toString();
}

async function sendFileMetadata(fileId, encryptedFileName, chunkCount, size, parentId) {
    try {
        const response = await fetch('/files/upload/file', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                server_key: fileId,
                file_name: encryptedFileName,
                chunk_count: chunkCount,
                size: size,
                parent_id: parentId
            })
        });

        const result = await response.json();

        if (!response.ok || result.failed) {
            // Check if the message contains quota exceeded info
            const msg = result.message?.toString() || "";
            if (msg.includes("quota")) {
                return { ok: false, reason: "quota" };
            }

            return { ok: false };
        }

        console.log("File metadata uploaded");
        return { ok: true };
    } catch (error) {
        console.error('Error sending file metadata:', error);
        return { ok: false };
    }
}


function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
  
    const units = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    const unitIndex = Math.floor(Math.log(bytes) / Math.log(1024));
    const size = (bytes / Math.pow(1024, unitIndex)).toFixed(2);
  
    return `${size} ${units[unitIndex]}`;
  }
