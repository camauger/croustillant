// Application Configuration
const CONFIG = {
    // API base URL - will use relative paths for Netlify Functions
    API_BASE_URL: '/api',

    // Local storage keys
    STORAGE_KEYS: {
        SELECTED_RECIPES: 'croustillant_selected_recipes',
        USER_PREFERENCES: 'croustillant_preferences'
    },

    // Default preferences
    DEFAULT_PREFERENCES: {
        excludePantryItems: false,
        theme: 'light'
    }
};
