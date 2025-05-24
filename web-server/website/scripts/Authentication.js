async function checkAuthentication() {
    try {
        const response = await fetch('/auth', {
            method: 'GET',
            credentials: 'include'
        });

        if (response.status === 401 && window.location.pathname !== '/pages/login.html') {
            window.location.href = '/pages/login.html';
        } else if (response.ok) {
            const data = await response.json();

            if (window.location.pathname === '/pages/login.html') {
                if (data.elevation === 0) {
                    window.location.href = '/pages/dashboard.html';
                } else if (data.elevation === 1) {
                    window.location.href = '/pages/admin.html';
                }
            }
        } else {
            console.error("An error occurred:", response.status);
        }
    } catch (error) {
        console.error("Network or server error:", error);
    }
}

checkAuthentication();
setInterval(() => {
    checkAuthentication();
}, 100000);