document.getElementById('website-button').addEventListener('click', function() {
    window.location.href = '/pages/login.html';
});
document.getElementById('app-button').addEventListener('click', function() {
    fetch('/app', {
        method: 'GET',
    }).then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.blob(); // Convert the response to a Blob
    }).then(blob => {
        // Create a URL for the blob and trigger a download
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = url;
        a.download = 'RAFT_pc.exe'; // The file name for the download
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url); // Clean up the URL object
    })
    .catch(error => {
        console.error('There was a problem with the fetch operation:', error);
    });
});