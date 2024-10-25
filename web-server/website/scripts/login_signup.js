document.getElementById("toggle-link").addEventListener("click", function (e) {
    e.preventDefault();
    
    const formTitle = document.getElementById("form-title");
    const submitButton = document.getElementById("submit_button");
    const toggleLink = document.getElementById("toggle-link");
    const form = document.querySelector("form");
    
    if (formTitle.textContent === "Login") {
      formTitle.textContent = "Sign Up";
      submitButton.textContent = "Sign Up";
      toggleLink.textContent = "Login";
  
      const input = document.createElement("input");
      input.setAttribute('type', 'email');
      input.setAttribute('placeholder', 'Email');
      input.setAttribute('id', 'email');
      input.setAttribute('name', 'email');
      input.required = true;
      
      form.insertBefore(input, submitButton);  
      
      toggleLink.parentElement.firstChild.textContent = "Already have an account? ";
      
    } else {
      const emailInput = document.getElementById('email');
      if (emailInput) {
        form.removeChild(emailInput);
      }
      
      formTitle.textContent = "Login";
      submitButton.textContent = "Submit";
      toggleLink.textContent = "Sign Up";
      toggleLink.parentElement.firstChild.textContent = "Don't have an account? ";
    }
  });
  
  document.getElementById("auth-form").addEventListener("submit", function (e) {
    e.preventDefault();
  
    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;
  
    if (username && password) {
      fetch("/users/login", {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ username, password })
      })
      .then(response => response.json())
      .then(data => {
        if (data.success) {
          alert("Login successful!");
          window.location.href = "/dashboard";
        } else {
          alert("Login failed: " + data.message);
        }
      })
      .catch(error => {
        console.error("Error:", error);
      });
    } else {
      alert("Please fill out both fields.");
    }
  });