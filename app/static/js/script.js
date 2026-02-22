document.addEventListener("DOMContentLoaded", () => {
    // Utility: open and close modals
    function openModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) modal.style.display = "block";
    }
    function closeModal(modal) {
        if (modal) modal.style.display = "none";
    }

    // Close buttons
    document.querySelectorAll(".closeBtn").forEach(btn => {
        btn.onclick = () => closeModal(btn.closest(".modal"));
    });

    // Close when clicking outside
    window.onclick = (event) => {
        if (event.target.classList.contains("modal")) {
            closeModal(event.target);
        }
    };

    // --- Create User Modal ---
    const openCreateBtn = document.getElementById("openCreateModalBtn");
    if (openCreateBtn) {
        openCreateBtn.onclick = () => openModal("createUserModal");
    }

    // --- Edit User Modal ---
    const editBtns = document.querySelectorAll(".editBtn");
    editBtns.forEach(btn => {
        btn.onclick = () => {
            document.getElementById("edit_id").value = btn.dataset.id;
            document.getElementById("edit_first_name").value = btn.dataset.first;
            document.getElementById("edit_last_name").value = btn.dataset.last;
            document.getElementById("edit_email").value = btn.dataset.email;
            document.getElementById("edit_role").value = btn.dataset.role;
            openModal("editUserModal");
        };
    });

    // --- Delete User Modal ---
    const deleteBtns = document.querySelectorAll(".deleteBtn");
    const deleteMessage = document.getElementById("deleteMessage");
    const deleteIdInput = document.getElementById("delete_id");
    const cancelDeleteBtn = document.getElementById("cancelDeleteBtn");

    deleteBtns.forEach(btn => {
        btn.onclick = () => {
            deleteMessage.textContent = `Are you sure you want to delete ${btn.dataset.name}?`;
            deleteIdInput.value = btn.dataset.id;
            openModal("deleteUserModal");
        };
    });

    if (cancelDeleteBtn) {
        cancelDeleteBtn.onclick = () => closeModal(document.getElementById("deleteUserModal"));
    }
});

document.addEventListener("DOMContentLoaded", () => {
    // Utility functions
    function openModal(id) {
        const modal = document.getElementById(id);
        if (modal) modal.style.display = "block";
    }
    function closeModal(modal) {
        if (modal) modal.style.display = "none";
    }

    // Close buttons
    document.querySelectorAll(".closeBtn").forEach(btn => {
        btn.onclick = () => closeModal(btn.closest(".modal"));
    });

    // Region Modal
    const openRegionBtn = document.getElementById("openRegionModalBtn");
    if (openRegionBtn) openRegionBtn.onclick = () => openModal("regionModal");

    // District Modal
    const openDistrictBtn = document.getElementById("openDistrictModalBtn");
    if (openDistrictBtn) openDistrictBtn.onclick = () => openModal("districtModal");

    // Local Church Modal
    const openLocalBtn = document.getElementById("openLocalModalBtn");
    if (openLocalBtn) openLocalBtn.onclick = () => openModal("localModal");

    // Close when clicking outside
    window.onclick = (event) => {
        if (event.target.classList.contains("modal")) {
            closeModal(event.target);
        }
    };
});