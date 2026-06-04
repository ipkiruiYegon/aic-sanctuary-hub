
function showToast(message, type = "error") {
  const colors = {
    error: "alert-error",
    success: "alert-success",
    info: "alert-info"
  };

  // Use fa-lg to make the icon size naturally fill the container
  const icons = {
    error: `<i class="fa-solid fa-circle-exclamation fa-lg"></i>`,
    success: `<i class="fa-solid fa-circle-check fa-lg"></i>`,
    info: `<i class="fa-solid fa-circle-info fa-lg"></i>`
  };

  const toast = document.createElement("div");
  toast.className = `alert ${colors[type]} shadow-xl border-none
                   pointer-events-auto flex items-center 
                   w-full sm:w-[28rem] p-0 min-h-0 overflow-hidden`;

  toast.innerHTML = `
  <div class="flex items-center gap-3 py-3 px-4 w-full text-white">
    <!-- Clean Icon -->
    <div class="flex-shrink-0 flex items-center justify-center">
      ${icons[type]}
    </div>
    
    <!-- Message -->
    <div class="flex-1 text-sm font-medium leading-snug">
      ${message}
    </div>

    <!-- Minimal Close Button -->
    <button class="flex-shrink-0 opacity-70 hover:opacity-100 transition-opacity ml-2" 
            onclick="this.closest('.alert').remove()">
      <i class="fa-solid fa-xmark text-sm"></i>
    </button>
  </div>
`;



  document.getElementById("toastContainer").appendChild(toast);
  setTimeout(() => toast.remove(), 4000);
}