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


async function loadUserFiles() {
    fetch('/files/info', {
      credentials: 'include',
      method: 'GET'
    })
}