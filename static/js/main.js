document.addEventListener("DOMContentLoaded", function () {
    const sidebar = document.getElementById("sidebar");

    const sidebarToggle = document.getElementById("sidebarToggle");

    sidebarToggle.addEventListener("click", function (e) {
        e.preventDefault();

        sidebar.classList.toggle("collapsed");
    });

    const userProfileToggle = document.getElementById("userProfileToggle");
    const accountDropdown = document.getElementById("accountDropdown");

    if (userProfileToggle && accountDropdown) {
        userProfileToggle.addEventListener("click", function () {
            accountDropdown.classList.toggle("show");
        });

        document.addEventListener("click", function (event) {
            if (
                !userProfileToggle.contains(event.target) &&
                !accountDropdown.contains(event.target)
            ) {
                accountDropdown.classList.remove("show");
            }
        });
    }

    function isMobile() {
        return window.innerWidth <= 768;
    }

    function adjustLayout() {
        const mainContent = document.querySelector(".main-content");
        if (!mainContent) return;
        if (isMobile()) {
            mainContent.style.paddingBottom = "70px";
        } else {
            mainContent.style.paddingBottom = "";
        }
    }

    adjustLayout();

    window.addEventListener("resize", adjustLayout);
});
