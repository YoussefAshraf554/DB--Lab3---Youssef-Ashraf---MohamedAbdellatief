
document.getElementById("loginForm").addEventListener("submit", function (e) {
    var email = document.getElementById("email");
    var password = document.getElementById("password");
    var emailMsg = email.value.trim() === "" ? "Email is required" : "";
    var passMsg = password.value === "" ? "Password is required" : "";

    document.getElementById("emailError").textContent = emailMsg;
    document.getElementById("passwordError").textContent = passMsg;
    email.classList.toggle("invalid", emailMsg !== "");
    password.classList.toggle("invalid", passMsg !== "");

    if (emailMsg || passMsg) e.preventDefault();   
});
