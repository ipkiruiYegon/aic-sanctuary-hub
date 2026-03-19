function showToast(message, type = "info") {
    const container = document.getElementById("toastContainer");

    // Create toast element
    const toast = document.createElement("div");
    toast.className = "toast " + type;
    toast.textContent = message;

    container.appendChild(toast);

    // Show with animation
    setTimeout(() => toast.classList.add("show"), 100);

    // Auto-remove after 4 seconds
    setTimeout(() => {
        toast.classList.remove("show");
        setTimeout(() => toast.remove(), 400);
    }, 4000);

}






