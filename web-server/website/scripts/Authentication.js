async function checkAuthentication() {
    try {
        const response = await fetch('/auth', {
            method: 'GET',
            credentials: 'include'
        });

        if (response.status === 401) {
            window.location.href = '/pages/login.html';
        } else if (response.ok) {
            console.log("User is authenticated");
        } else {
            console.error("An error occurred:", response.status);
        }
    } catch (error) {
        console.error("Network or server error:", error);
    }
}
checkAuthentication();