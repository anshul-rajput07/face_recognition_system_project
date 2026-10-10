document.addEventListener("DOMContentLoaded", function () {

    const saveButtons = document.querySelectorAll(".save-btn");

    saveButtons.forEach(function (button) {

        button.addEventListener("click", function () {

            alert("Settings saved successfully!");

        });

    });


    const logoutBtn = document.getElementById("logoutBtn");

    logoutBtn.addEventListener("click", function () {

        const confirmLogout = confirm(
            "Are you sure you want to logout?"
        );

        if (confirmLogout) {

            window.location.href = "index.html";

        }

    });

});