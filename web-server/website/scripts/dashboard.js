function switchTab(tabName) {
    const sections = document.querySelectorAll(".content-section");
    sections.forEach(section => section.classList.add("hidden"));

    const activeSection = document.getElementById(tabName);
    if (activeSection) {
        activeSection.classList.remove("hidden");
    }
}


async function loadUserStats() {
    const overviewDiv = document.getElementById('overview');
    const ctx = document.getElementById('statsChart').getContext('2d');
    const fileCountDiv = document.getElementById('file_count');

    try {
        const response = await fetch('/users/info', {
            credentials: "include",
            method: "GET"
        });

        if (!response.ok) {
            throw new Error('Failed to fetch user stats');
        }

        const stats = await response.json();
        const { username, uploaded, downloaded, fileCount } = stats;

        fileCountDiv.innerHTML = `<strong>Total Files: </strong>${fileCount}`;

        new Chart(ctx, {
            type: 'pie',
            data: {
                labels: ['Uploaded Data (MB)', 'Downloaded Data (MB)'],
                datasets: [{
                    data: [uploaded/(1024*1024), downloaded/(1024*1024)],
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
                },
                responsive: true,
                maintainAspectRatio: false
            }
        });

    } catch (error) {
        console.log(error)
        console.error('Error loading user stats:', error);
        overviewDiv.innerHTML = `<p>Sorry, we couldn't load your stats. Please try again later.</p>`;
    }
}

document.addEventListener('DOMContentLoaded', () => {
    loadUserStats();
});
