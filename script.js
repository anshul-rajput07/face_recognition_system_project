// ================================
// SHOW / HIDE PASSWORD
// ================================

const togglePassword = document.getElementById("togglePassword");
const passwordInput = document.getElementById("password");

togglePassword.addEventListener("click", function () {

    // Check current password type
    const isPassword = passwordInput.type === "password";

    // Change input type
    passwordInput.type = isPassword ? "text" : "password";

    // Change eye icon
    this.classList.toggle("fa-eye");
    this.classList.toggle("fa-eye-slash");

});


// ================================
// LOGIN FORM
// ================================

const loginForm = document.getElementById("loginForm");

loginForm.addEventListener("submit", function (event) {

    // Prevent page refresh
    event.preventDefault();

    // Get user input
    const email = document.getElementById("email").value.trim();
    const password = passwordInput.value.trim();


    // Basic Validation
    if (email === "" || password === "") {

        alert("Please enter your email and password!");

        return;
    }


    // Temporary Login Success
    // Backend authentication will be added later

    alert("Login Successful! Welcome to AttendPro.");

    // Redirect to Dashboard
    window.location.href = "dashboard.html";

});