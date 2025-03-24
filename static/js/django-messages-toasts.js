document.addEventListener("DOMContentLoaded", function () {
    // Get existing toast elements from the DOM
    const toastContainer = document.getElementById("toastContainer");
    const toastTemplate = document.getElementById("toastTemplate");
    let toastCounter = 0;

    // Process Django messages
    const messagesContainer = document.getElementById("django-messages");
    if (messagesContainer) {
        const messages = messagesContainer.querySelectorAll(".message");
        messages.forEach(function (messageElement) {
            const message = messageElement.getAttribute("data-message");
            const tag = messageElement.getAttribute("data-tags");
            displayToast(message, tag);
        });
    }

    function displayToast(message, type = "info") {
        toastCounter++;

        // Clone the template
        const newToast = toastTemplate.cloneNode(true);
        newToast.id = `toast-${toastCounter}`;
        newToast.style.display = "block";

        // Configure toast based on message type
        const toastHeader = newToast.querySelector(".toast-header strong");
        const toastBody = newToast.querySelector(".toast-body");

        // Set header and icon based on type
        let title, icon, toastClass;
        switch (type) {
            case "success":
                title = "Success";
                icon = "check-circle";
                toastClass = "toast-success";
                break;
            case "error":
                title = "Error";
                icon = "exclamation-circle";
                toastClass = "toast-error";
                break;
            case "warning":
                title = "Warning";
                icon = "exclamation-triangle";
                toastClass = "toast-warning";
                break;
            default:
                title = "Information";
                icon = "info-circle";
                toastClass = "toast-info";
        }

        // Update toast classes
        newToast.classList.add(toastClass);

        // Set header
        toastHeader.textContent = title;

        // Set content with icon
        toastBody.innerHTML = `
            <div class="toast-icon">
                <i class="fas fa-${icon}"></i>
            </div>
            <div class="toast-message">${message}</div>
        `;

        // Add to container
        toastContainer.appendChild(newToast);

        // Initialize Bootstrap toast with shorter animation duration
        const bsToast = new bootstrap.Toast(newToast, {
            autohide: true,
            delay: 4000,
            animation: true,
        });

        // Handle animations
        const handleAnimationEnd = () => {
            if (newToast.classList.contains("hiding")) {
                newToast.remove();
            }
        };

        newToast.addEventListener("animationend", handleAnimationEnd);

        // Show toast
        requestAnimationFrame(() => {
            newToast.classList.add("showing");
            bsToast.show();
        });

        // Handle hide animation
        newToast.addEventListener("hide.bs.toast", () => {
            newToast.classList.remove("showing");
            newToast.classList.add("hiding");
        });
    }

    // Expose the displayToast function globally
    window.displayToast = displayToast;
});
