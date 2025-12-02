// API Client for Croustillant

class API {
    constructor(baseURL) {
        this.baseURL = baseURL;
    }

    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;

        try {
            const response = await fetch(url, {
                ...options,
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                }
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || `HTTP error! status: ${response.status}`);
            }

            return data;
        } catch (error) {
            console.error('API request failed:', error);
            throw error;
        }
    }

    // Recipes endpoints
    async getRecipes(params = {}) {
        const queryString = new URLSearchParams(params).toString();
        const endpoint = queryString ? `/recipes?${queryString}` : '/recipes';
        return this.request(endpoint);
    }

    async getRecipe(id) {
        return this.request(`/recipe-detail/${id}`);
    }

    async createRecipe(recipeData) {
        return this.request('/recipes', {
            method: 'POST',
            body: JSON.stringify(recipeData)
        });
    }

    async updateRecipe(id, recipeData) {
        return this.request(`/recipe-detail/${id}`, {
            method: 'PUT',
            body: JSON.stringify(recipeData)
        });
    }

    async deleteRecipe(id) {
        return this.request(`/recipe-detail/${id}`, {
            method: 'DELETE'
        });
    }

    // Shopping list endpoint
    async generateShoppingList(recipeIds, excludePantry = false) {
        return this.request('/shopping-list', {
            method: 'POST',
            body: JSON.stringify({
                recipe_ids: recipeIds,
                exclude_pantry: excludePantry
            })
        });
    }
}

// Create global API instance
const api = new API(CONFIG.API_BASE_URL);
