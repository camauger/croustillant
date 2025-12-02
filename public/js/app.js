// Main Application Entry Point

// Register routes
router.register('recipes', renderRecipesList);
router.register('create', renderRecipeForm);
router.register('selection', renderSelection);
router.register('shopping', renderShoppingList);

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    // Handle initial route
    router.handleRoute();

    // Update selection badge
    storage.updateSelectionBadge();
});

// Utility functions

function showAlert(message, type = 'info') {
    const alertClass = `alert-${type === 'error' ? 'error' : type === 'success' ? 'success' : 'info'}`;

    const alert = document.createElement('div');
    alert.className = `alert ${alertClass}`;
    alert.textContent = message;
    alert.style.position = 'fixed';
    alert.style.top = '80px';
    alert.style.right = '20px';
    alert.style.zIndex = '3000';
    alert.style.minWidth = '300px';
    alert.style.boxShadow = 'var(--shadow)';

    document.body.appendChild(alert);

    // Auto-remove after 5 seconds
    setTimeout(() => {
        alert.style.opacity = '0';
        alert.style.transition = 'opacity 0.5s';
        setTimeout(() => alert.remove(), 500);
    }, 5000);
}

function showError(message) {
    const app = document.getElementById('app');
    app.innerHTML = `
        <div class="card">
            <div class="alert alert-error">
                ${message}
            </div>
            <button class="btn btn-primary" onclick="router.navigate('recipes')">
                Retour à l'accueil
            </button>
        </div>
    `;
}
