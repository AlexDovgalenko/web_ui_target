// Toast notification system
function showToast(message, category = 'info', duration = 4000) {
    const toastContainer = document.getElementById('toast-container');
    
    // Create toast element
    const toast = document.createElement('div');
    toast.className = `toast toast-${category} toast-show`;
    
    // Add close button
    const closeBtn = document.createElement('button');
    closeBtn.className = 'toast-close';
    closeBtn.innerHTML = '×';
    closeBtn.onclick = () => removeToast(toast);
    
    // Add message content
    const messageSpan = document.createElement('span');
    messageSpan.textContent = message;
    
    // Assemble toast
    toast.appendChild(messageSpan);
    toast.appendChild(closeBtn);
    
    // Add to container
    toastContainer.appendChild(toast);
    
    // Auto-remove after duration
    setTimeout(() => {
        removeToast(toast);
    }, duration);
}

function removeToast(toast) {
    if (toast && toast.parentNode) {
        toast.classList.add('toast-hide');
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 500); // Match CSS transition duration
    }
}

// Process Flask flash messages on page load
document.addEventListener('DOMContentLoaded', function() {
    const flashMessagesContainer = document.getElementById('flash-messages');
    if (flashMessagesContainer) {
        const messages = flashMessagesContainer.querySelectorAll('[data-category]');
        messages.forEach(msg => {
            const category = msg.getAttribute('data-category');
            const message = msg.getAttribute('data-message');
            showToast(message, category);
        });
    }
});

function changeViewMode() {
    const viewMode = document.getElementById('view-mode').value;
    const currentUrl = new URL(window.location);
    
    // Update the view parameter
    currentUrl.searchParams.set('view', viewMode);
    
    // Show toast notification for view change
    showToast(`Switched to ${viewMode} view`, 'info', 3000);
    
    // Reload the page with the new view mode
    setTimeout(() => {
        window.location.href = currentUrl.toString();
    }, 500);
}

// Function to manually trigger toast (for testing or other uses)
function triggerToast(message, type = 'info') {
    showToast(message, type);
}
