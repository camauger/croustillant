// Local Storage Management

class Storage {
    constructor() {
        this.keys = CONFIG.STORAGE_KEYS;
    }

    // Selected recipes management
    getSelectedRecipes() {
        const recipes = localStorage.getItem(this.keys.SELECTED_RECIPES);
        return recipes ? JSON.parse(recipes) : [];
    }

    addSelectedRecipe(recipeId) {
        const recipes = this.getSelectedRecipes();
        if (!recipes.includes(recipeId)) {
            recipes.push(recipeId);
            localStorage.setItem(this.keys.SELECTED_RECIPES, JSON.stringify(recipes));
            this.updateSelectionBadge();
            return true;
        }
        return false;
    }

    removeSelectedRecipe(recipeId) {
        let recipes = this.getSelectedRecipes();
        recipes = recipes.filter(id => id !== recipeId);
        localStorage.setItem(this.keys.SELECTED_RECIPES, JSON.stringify(recipes));
        this.updateSelectionBadge();
    }

    clearSelectedRecipes() {
        localStorage.setItem(this.keys.SELECTED_RECIPES, JSON.stringify([]));
        this.updateSelectionBadge();
    }

    isRecipeSelected(recipeId) {
        return this.getSelectedRecipes().includes(recipeId);
    }

    updateSelectionBadge() {
        const count = this.getSelectedRecipes().length;
        const badge = document.getElementById('selection-count');
        if (badge) {
            badge.textContent = count;
            badge.style.display = count > 0 ? 'inline-block' : 'none';
        }
    }

    // User preferences
    getPreferences() {
        const prefs = localStorage.getItem(this.keys.USER_PREFERENCES);
        return prefs ? JSON.parse(prefs) : CONFIG.DEFAULT_PREFERENCES;
    }

    setPreferences(preferences) {
        localStorage.setItem(this.keys.USER_PREFERENCES, JSON.stringify(preferences));
    }

    updatePreference(key, value) {
        const prefs = this.getPreferences();
        prefs[key] = value;
        this.setPreferences(prefs);
    }
}

// Create global storage instance
const storage = new Storage();

// Initialize badge on page load
document.addEventListener('DOMContentLoaded', () => {
    storage.updateSelectionBadge();
});
