async function hashString(input) {
  
  const encoder = new TextEncoder();
  const data = encoder.encode(input);

  const hashBuffer = await crypto.subtle.digest('SHA-256', data);

  const hashArray = Array.from(new Uint8Array(hashBuffer));

  const hashHex = hashArray.map(b => b.toString(16).padStart(2, '0')).join('');

  return hashHex;
}

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
    input.setAttribute('type', 'password');
    input.setAttribute('placeholder', 'Re-enter password');
    input.setAttribute('id', 'Re_enter_password');
    input.setAttribute('name', 'Reenter_password');
    input.required = true;

    form.insertBefore(input, submitButton);

    toggleLink.parentElement.firstChild.textContent = "Already have an account? ";

  } else {
    const Re_enterInput = document.getElementById('Re_enter_password');
    if (Re_enterInput) {
      form.removeChild(Re_enterInput);
    }

    formTitle.textContent = "Login";
    submitButton.textContent = "Submit";
    toggleLink.textContent = "Sign Up";
    toggleLink.parentElement.firstChild.textContent = "Don't have an account? ";
  }
});

document.getElementById("auth-form").addEventListener("submit", async function (e) {
  e.preventDefault();
  const formTitle = document.getElementById("form-title");
  const username = document.getElementById("username").value;
  let password = document.getElementById("password").value;
  const Repassword = document.getElementById("Re_enter_password")?.value;

  if (formTitle.textContent === "Sign Up" && Repassword) {
    if (Repassword === password) {
      password = await hashString(password);
      fetch("/users/signup", {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ username, password })
      }).then(response => response.json())
        .then(data => {
          if (data.success) {
            window.location.href = "/pages/dashboard.html";
          } else {
            alert(data.message);
          }
        });
    } else {
      alert("Passwords do not match");
    }
  } else if (username && password) {
    password = await hashString(password);
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
        window.location.href = "/pages/dashboard.html";
      } else {
        alert(data.message);
      }
    })
    .catch(error => {
      console.error("Error:", error);
    });
  } else {
    alert("Please fill out both fields.");
  }
});