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

            // Check if response is JSON before parsing
            const contentType = response.headers.get('content-type');
            let data;

            if (contentType && contentType.includes('application/json')) {
                try {
                    data = await response.json();
                } catch (jsonError) {
                    // If JSON parsing fails, try to get text for debugging
                    const text = await response.text();
                    console.error('Failed to parse JSON response:', text.substring(0, 200));
                    throw new Error('Réponse invalide du serveur. Les fonctions Python ne sont peut-être pas disponibles localement.');
                }
            } else {
                // Response is not JSON (probably HTML error page)
                const text = await response.text();
                console.error('Non-JSON response received:', text.substring(0, 200));

                if (response.status === 404) {
                    throw new Error('Fonction API non trouvée. Vérifiez que le serveur Netlify est démarré.');
                } else if (response.status >= 500) {
                    throw new Error('Erreur serveur. Les fonctions Python ne sont peut-être pas disponibles localement.');
                } else {
                    throw new Error(`Erreur HTTP ${response.status}: Réponse non-JSON reçue`);
                }
            }

            if (!response.ok) {
                throw new Error(data.error || `HTTP error! status: ${response.status}`);
            }

            return data;
        } catch (error) {
            console.error('API request failed:', error);

            // Provide user-friendly error messages
            if (error.message.includes('Function') || error.message.includes('Function n')) {
                throw new Error('Les fonctions Python ne sont pas disponibles localement. Elles fonctionneront en production sur Netlify.');
            }

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
