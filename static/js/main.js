/**
 * Project Kashi — Banking Management System
 * Client-Side Enhancements (Vanilla JS)
 */

document.addEventListener("DOMContentLoaded", function () {
    // Confirmation prompts for financial state mutations
    const transferForm = document.querySelector("#transfer-form");
    if (transferForm) {
        transferForm.addEventListener("submit", function (e) {
            const amount = document.querySelector("#amount")?.value || "0";
            const confirmed = confirm(`Are you sure you want to execute this fund transfer of ₹${amount}? This action will immediately adjust both account balances.`);
            if (!confirmed) {
                e.preventDefault();
            }
        });
    }

    const withdrawalForm = document.querySelector("#withdrawal-form");
    if (withdrawalForm) {
        withdrawalForm.addEventListener("submit", function (e) {
            const amount = document.querySelector("#amount")?.value || "0";
            const confirmed = confirm(`Confirm cash/ATM withdrawal of ₹${amount}?`);
            if (!confirmed) {
                e.preventDefault();
            }
        });
    }

    // Auto-dismiss alerts after 6 seconds
    const alerts = document.querySelectorAll(".alert");
    alerts.forEach(function (alert) {
        setTimeout(function () {
            alert.style.transition = "opacity 0.5s ease";
            alert.style.opacity = "0";
            setTimeout(function () {
                alert.remove();
            }, 500);
        }, 6000);
    });
});
