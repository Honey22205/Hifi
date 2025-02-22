// document.addEventListener("DOMContentLoaded", function () {
//     // Get input fields and button
//     const username = document.getElementById("username");
//     const password = document.getElementById("password");
//     const loginBtn = document.querySelector(".submit");

//     // Login function
//     function validateLogin() {
//         let userValue = username.value.trim();
//         let passValue = password.value.trim();

//         // Check if fields are empty
//         if (userValue === "" || passValue === "") {
//             alert("Please fill in both fields!");
//             return;
//         }

//         // Simple username & password check (for demo purposes)
//         if (userValue === "admin" && passValue === "password123") {
//             alert("Login Successful! 🎉");
//             window.location.href = "dashboard.html"; // Redirect to another page (if needed)
//         } else {
//             alert("Invalid Username or Password! ❌");
//         }
//     }

//     // Event listener for button click
//     loginBtn.addEventListener("click", validateLogin);

//     // Allow pressing Enter to login
//     document.addEventListener("keypress", function (event) {
//         if (event.key === "Enter") {
//             validateLogin();
//         }
//     });
// });

// document.addEventListener("DOMContentLoaded", function () {
//     const username = document.getElementById("username");
//     const password = document.getElementById("password");
//     const loginBtn = document.querySelector(".submit");

//     function validateLogin() {
//         let userValue = username.value.trim();
//         let passValue = password.value.trim();

//         if (userValue === "" || passValue === "") {
//             alert("Please fill in both fields!");
//             return;
//         }

//         if (userValue === "admin" && passValue === "password123") {
//             alert("Login Successful! 🎉");
//             window.location.href = "dashboard.html"; // Change to your actual dashboard page
//         } else {
//             alert("Invalid Username or Password! ❌");
//         }
//     }

//     loginBtn.addEventListener("click", validateLogin);

//     document.addEventListener("keydown", function (event) {
//         if (event.key === "Enter") {
//             validateLogin();
//         }
//     });
// });
function validateLogin() {
    let userValue = document.getElementById("username").value.trim();
    let passValue = document.getElementById("password").value.trim();

    if (userValue === "" || passValue === "") {
        alert("Please fill in both fields!");
        return;
    }

    if (userValue === "admin" && passValue === "password123") {
        alert("Login Successful! 🎉");
        localStorage.setItem("username", userValue); // Store username
        window.location.href = "dashboard.html"; // Redirect to dashboard
    } else {
        alert("Invalid Username or Password! ❌");
    }
}

