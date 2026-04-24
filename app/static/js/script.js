// Close sidebar on click outside - mobile devices
const sidebarToggle = document.getElementById("sidebar-toggle");
const drawerSide = document.querySelector(".drawer-side");
const menuButton = document.querySelector(".drawer-toggle");

// Close sidebar when clicking on overlay
document.addEventListener("click", function(event) {
    if (window.innerWidth < 1024 && sidebarToggle.checked) {
        // Don't close if clicking the menu button
        if (event.target === menuButton || menuButton.contains(event.target)) {
            return;
        }
        // Close if clicking outside the sidebar
        if (!drawerSide.contains(event.target)) {
            sidebarToggle.checked = false;
        }
    }
});

// Also close when clicking any sidebar link
const sidebarLinks = document.querySelectorAll(".drawer-side a");
sidebarLinks.forEach(link => {
    link.addEventListener("click", function() {
        if (window.innerWidth < 1024) {
            sidebarToggle.checked = false;
        }
    });
});