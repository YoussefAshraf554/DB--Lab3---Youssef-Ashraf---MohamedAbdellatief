var EMAIL_PATTERN = /^[^@ ]+@[^@ .]+([.][^@ .]+)+$/;

function show(id, message) {
    document.getElementById(id + "Error").textContent = message;
    document.getElementById(id).classList.toggle("invalid", message !== "");
}

document.getElementById("registerForm").addEventListener("submit", function (e) {
    var name = document.getElementById("name").value.trim();
    var email = document.getElementById("email").value.trim();
    var password = document.getElementById("password").value;
    var confirm = document.getElementById("confirm_password").value;

    var nameMsg = name === "" ? "Name is required" : "";
    var emailMsg = "";
        if (email === "") emailMsg = "Email is required";
        else if (!EMAIL_PATTERN.test(email)) emailMsg = "Email is not valid";
    var passMsg = password === "" ? "Password is required" : "";
    var confirmMsg = "";
    if (confirm === "") confirmMsg = "Confirm password is required";
    else if (password !== confirm) confirmMsg = "Passwords do not match";

    show("name", nameMsg);
    show("email", emailMsg);
    show("password", passMsg);
    show("confirm_password", confirmMsg);

    if (nameMsg || emailMsg || passMsg || confirmMsg) e.preventDefault();   
});
