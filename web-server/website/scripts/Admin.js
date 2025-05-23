function formatFileSize(bytes) {
  if (bytes === 0) return '0 Bytes';

  const units = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
  const unitIndex = Math.floor(Math.log(bytes) / Math.log(1024));
  const size = (bytes / Math.pow(1024, unitIndex)).toFixed(2);

  return `${size} ${units[unitIndex]}`;
}

async function appendUserRow(tuple) {
  const tableBody = document.getElementById("user-list");

  if (!Array.isArray(tuple) || tuple.length !== 4) {
    console.error("Invalid tuple data. Expected 4 elements.");
    return;
  }

  const tr = document.createElement("tr");

  tuple.forEach((data, index) => {
    const td = document.createElement("td");

    // Format the 4th element (index 3) with file size formatter
    if (index === 3) {
      td.textContent = formatFileSize(Number(data));
    } else {
      td.textContent = data;
    }

    tr.appendChild(td);
  });

  tableBody.appendChild(tr);
}

async function fetchUsers() {
  try {
    const response = await fetch("/users/admin", {
      method: 'GET',
      credentials: 'include'
    });

    if (response.ok) {
      const data = await response.json();

      const tableBody = document.getElementById("user-list");
      tableBody.innerHTML = ''; // 💥 Clear before appending

      data.forEach(user => {
        appendUserRow(user);
      });
    } else {
      console.error("Failed to fetch users:", response.status);
    }
  } catch (error) {
    console.error("Network error:", error);
  }
}

document.addEventListener("DOMContentLoaded", () => {
    fetchUsers();
    setInterval(fetchUsers, 10000);
});

document.getElementById("logoutBtn").addEventListener("click", () => {
  // Clear localStorage and sessionStorage
  localStorage.clear();
  sessionStorage.clear();

  // Clear all cookies
  document.cookie.split(";").forEach(cookie => {
    const eqPos = cookie.indexOf("=");
    const name = eqPos > -1 ? cookie.substring(0, eqPos) : cookie;
    document.cookie = name + "=;expires=Thu, 01 Jan 1970 00:00:00 GMT;path=/";
  });

  // Reload the page
  location.reload();
});