document.addEventListener("DOMContentLoaded", function () {
  const sidebar = document.getElementById("sidebar");
  const sidebarToggle = document.getElementById("sidebarToggle");
  const mobileMoreMenuToggle = document.getElementById("mobileMoreMenuToggle");
  const mobileDropdownMenu = document.getElementById("mobileDropdownMenu");
  const userProfileToggle = document.getElementById("userProfileToggle");
  const accountDropdown = document.getElementById("accountDropdown");

  // Sidebar toggle
  if (sidebarToggle && sidebar) {
    sidebarToggle.addEventListener("click", function (e) {
      e.preventDefault();
      sidebar.classList.toggle("collapsed");
    });
  }

  // Mobile more menu functionality
  if (mobileMoreMenuToggle && mobileDropdownMenu) {
    mobileMoreMenuToggle.addEventListener("click", function (e) {
      e.preventDefault();
      e.stopPropagation(); // Stop event from bubbling up

      // Close any other open dropdowns first
      if (accountDropdown) accountDropdown.classList.remove("show");

      mobileDropdownMenu.classList.toggle("show");
    });

    // Close the mobile dropdown when clicking outside
    document.addEventListener("click", function (event) {
      if (
        mobileDropdownMenu.classList.contains("show") &&
        !mobileMoreMenuToggle.contains(event.target) &&
        !mobileDropdownMenu.contains(event.target)
      ) {
        mobileDropdownMenu.classList.remove("show");
      }
    });
  }

  // User profile dropdown functionality
  if (userProfileToggle && accountDropdown) {
    userProfileToggle.addEventListener("click", function (e) {
      e.preventDefault();
      e.stopPropagation(); // Stop event from bubbling up

      // Close mobile dropdown if open
      if (mobileDropdownMenu) mobileDropdownMenu.classList.remove("show");

      accountDropdown.classList.toggle("show");
    });

    document.addEventListener("click", function (event) {
      if (
        accountDropdown.classList.contains("show") &&
        !userProfileToggle.contains(event.target) &&
        !accountDropdown.contains(event.target)
      ) {
        accountDropdown.classList.remove("show");
      }
    });
  }

  function setActiveNavLink() {
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll(".sidebar .nav-link");

    navLinks.forEach((link) => {
      link.classList.remove("active");
      const href = link.getAttribute("href");
      if (href === "/" && currentPath === "/") {
        link.classList.add("active");
      } else if (
        href === "/shipments/" &&
        (currentPath === "/shipments/" ||
          /^\/shipments\/(?!suppliers)/.test(currentPath))
      ) {
        link.classList.add("active");
      } else if (currentPath.includes("/shipments/suppliers/")) {
        if (href.includes("/shipments/suppliers/")) {
          link.classList.add("active");
        }
      } else if (
        href !== "/" &&
        href !== "#" &&
        (currentPath === href || currentPath === `${href}/`)
      ) {
        link.classList.add("active");
      }
    });
  }

  // Call setActiveNavLink when the page loads
  setActiveNavLink();

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

  // Initial layout adjustment
  adjustLayout();

  // Adjust layout on window resize
  window.addEventListener("resize", adjustLayout);
});
