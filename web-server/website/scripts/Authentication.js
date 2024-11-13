async function checkAuthentication() {
    try {
        const response = await fetch('/auth', {
            method: 'GET',
            credentials: 'include'
        });

        if (response.status === 401 && window.location.pathname !== '/pages/login.html') {
            window.location.href = '/pages/login.html';
        } else if (response.ok) {
            if (window.location.pathname === '/pages/login.html') {
                window.location.href = '/pages/dashboard.html';
            }
        } else {
            console.error("An error occurred:", response.status);
        }
    } catch (error) {
        console.error("Network or server error:", error);
    }
}

checkAuthentication();