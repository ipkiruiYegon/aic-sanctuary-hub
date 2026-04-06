function showToast(message, type = "error") {
  const colors = {
    error: "alert-error",
    success: "alert-success",
    info: "alert-info"
  };

  const icons = {
    error: `<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-white" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm-1-5a1 1 0 112 0v2a1 1 0 11-2 0v-2zm0-6a1 1 0 012 0v3a1 1 0 11-2 0V7z" clip-rule="evenodd" />
            </svg>`,
    success: `<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-white" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.707a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414L8.586 13l4.121-4.707z" clip-rule="evenodd" />
            </svg>`,
    info: `<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-white" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M18 10c0 4.418-3.582 8-8 8s-8-3.582-8-8 3.582-8 8-8 8 3.582 8 8zm-9-3a1 1 0 011-1h.01a1 1 0 110 2H10a1 1 0 01-1-1zm1 4a1 1 0 00-1 1v3a1 1 0 102 0v-3a1 1 0 00-1-1z" clip-rule="evenodd" />
            </svg>`
  };

  const toast = document.createElement("div");
  toast.className = `alert ${colors[type]} shadow-lg w-full flex items-center justify-between text-white`;
  toast.innerHTML = `
    <div class="flex items-center space-x-2 text-white">
      ${icons[type]}
      <span>${message}</span>
    </div>
    <button class="btn btn-sm btn-ghost text-white" onclick="this.parentElement.remove()">✕</button>
  `;
  document.getElementById("toastContainer").appendChild(toast);
  setTimeout(() => toast.remove(), 4000);
}