document.addEventListener('DOMContentLoaded', function () {
    // Get existing toast elements from the DOM
    const toastContainer = document.getElementById('toastContainer');
    const toastTemplate = document.getElementById('toastTemplate');
    let toastCounter = 0;

    // Process Django messages
    const messagesContainer = document.getElementById('django-messages');
    if (messagesContainer) {
        const messages = messagesContainer.querySelectorAll('.message');
        messages.forEach(function (messageElement) {
            const message = messageElement.getAttribute('data-message');
            const tag = messageElement.getAttribute('data-tags');
            displayToast(message, tag);
        });
    }

    function displayToast(message, type) {
        toastCounter++;

        // Clone the template
        const newToast = toastTemplate.cloneNode(true);
        newToast.id = `toast-${toastCounter}`;
        newToast.style.display = 'block';

        // Configure toast based on message type
        const toastHeader = newToast.querySelector('.toast-header strong');
        const toastBody = newToast.querySelector('.toast-body p');

        // Set header and icon based on type
        let bgColor, icon;

        switch (type) {
            case 'success':
                toastHeader.textContent = 'Success';
                bgColor = '#28a745';
                icon = 'fa-check';
                break;
            case 'error':
                toastHeader.textContent = 'Error';
                bgColor = '#dc3545';
                icon = 'fa-exclamation-triangle';
                break;
            case 'warning':
                toastHeader.textContent = 'Warning';
                bgColor = '#ffc107';
                icon = 'fa-exclamation-circle';
                break;
            default:
                toastHeader.textContent = 'Notification';
                bgColor = '#17a2b8';
                icon = 'fa-info-circle';
        }

        // Set content with icon
        toastBody.innerHTML = `
            <span style="background-color: ${bgColor}; color: white; padding: 5px 8px; border-radius: 50%; margin-right: 10px;">
                <i class="fas ${icon}"></i>
            </span>
            ${message}
        `;

        // Add to container and show
        toastContainer.appendChild(newToast);
        new bootstrap.Toast(newToast, {
            autohide: true,
            delay: 5000
        }).show();
    }
});