document.addEventListener("DOMContentLoaded", function () {
    const navToggle = document.getElementById("navToggle");
    const navMenu = document.getElementById("navMenu");

    if (navToggle && navMenu) {
        navToggle.addEventListener("click", function () {
            navMenu.classList.toggle("open");
            navToggle.setAttribute("aria-expanded", navMenu.classList.contains("open"));
        });
    }

    document.querySelectorAll("form[data-confirm]").forEach(function (form) {
        form.addEventListener("submit", function (event) {
            if (!window.confirm(form.dataset.confirm)) {
                event.preventDefault();
            }
        });
    });

    document.querySelectorAll("[data-confirm]").forEach(function (button) {
        if (button.tagName === "BUTTON" && button.form) {
            button.addEventListener("click", function (event) {
                if (!window.confirm(button.dataset.confirm)) {
                    event.preventDefault();
                }
            });
        }
    });

    window.setTimeout(function () {
        document.querySelectorAll(".alert").forEach(function (alert) {
            alert.style.transition = "opacity 0.4s ease";
            alert.style.opacity = "0";
            window.setTimeout(function () { alert.remove(); }, 450);
        });
    }, 7000);

    const transferForm = document.getElementById("transferForm");
    if (transferForm) {
        transferForm.addEventListener("submit", function (event) {
            const from = document.getElementById("FromAccountID");
            const to = document.getElementById("ToAccountID");
            if (from && to && from.value && from.value === to.value) {
                event.preventDefault();
                window.alert("Source and destination accounts must be different.");
            }
        });
    }

    const dateInputs = document.querySelectorAll('input[type="date"]');
    const today = new Date().toISOString().split("T")[0];
    dateInputs.forEach(function (input) {
        if (input.name === "DateOfBirth") {
            input.max = today;
        }
        if (input.name === "JoiningDate" || input.name === "StartDate") {
            input.max = today;
        }
    });
});
