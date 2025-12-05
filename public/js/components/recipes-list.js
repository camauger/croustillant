// Recipes List Component

async function renderRecipesList() {
    const app = document.getElementById('app');

    // Show loading state
    app.innerHTML = `
        <div class="search-container">
            <div class="search-bar">
                <input type="text" id="search-input" placeholder="Rechercher une recette...">
                <button class="btn btn-primary" onclick="searchRecipes()">Rechercher</button>
            </div>
        </div>
        <div class="loading">
            <div class="spinner"></div>
        </div>
    `;

    try {
        const data = await api.getRecipes();

        if (data.success && data.recipes) {
            displayRecipes(data.recipes);

            // Add search functionality
            document.getElementById('search-input').addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    searchRecipes();
                }
            });
        } else {
            showError('Erreur lors du chargement des recettes');
        }
    } catch (error) {
        let errorMessage = error.message;

        // Provide helpful context for local development issues
        if (errorMessage.includes('fonctions Python') || errorMessage.includes('Function') || errorMessage.includes('non disponibles')) {
            errorMessage += '<br><br><small>💡 <strong>Note pour le développement local:</strong> Les fonctions Python peuvent ne pas être disponibles localement à cause de problèmes avec Deno/Edge Functions. Elles fonctionneront correctement en production sur Netlify.</small>';
        }

        showError(errorMessage);
    }
}

function displayRecipes(recipes) {
    const app = document.getElementById('app');
    const searchContainer = app.querySelector('.search-container');

    if (recipes.length === 0) {
        app.innerHTML = searchContainer.outerHTML + `
            <div class="card text-center">
                <h2>Aucune recette trouvée</h2>
                <p>Commencez par ajouter votre première recette!</p>
                <button class="btn btn-primary" onclick="router.navigate('create')">Ajouter une recette</button>
            </div>
        `;
        return;
    }

    const recipesHTML = recipes.map(recipe => createRecipeCard(recipe)).join('');

    app.innerHTML = searchContainer.outerHTML + `
        <h2>Toutes les recettes (${recipes.length})</h2>
        <div class="recipe-grid">
            ${recipesHTML}
        </div>
    `;
}

function createRecipeCard(recipe) {
    const isSelected = storage.isRecipeSelected(recipe.id);
    const imageHTML = recipe.image_url
        ? `<img src="${recipe.image_url}" alt="${recipe.titre}">`
        : `<div class="placeholder-img">🍳</div>`;

    return `
        <div class="card recipe-card" onclick="showRecipeDetail(${recipe.id})">
            ${imageHTML}
            <h3>${recipe.titre}</h3>
            <div class="recipe-meta">
                ${recipe.temps_preparation ? `<span>⏱️ Prep: ${recipe.temps_preparation}</span>` : ''}
                ${recipe.temps_cuisson ? `<span>🔥 Cuisson: ${recipe.temps_cuisson}</span>` : ''}
                ${recipe.rendement ? `<span>👥 ${recipe.rendement}</span>` : ''}
            </div>
            <div class="recipe-actions" onclick="event.stopPropagation()">
                <button class="btn ${isSelected ? 'btn-danger' : 'btn-success'} btn-small"
                        onclick="toggleRecipeSelection(${recipe.id})">
                    ${isSelected ? '✓ Sélectionnée' : '+ Ajouter à ma sélection'}
                </button>
            </div>
        </div>
    `;
}

async function searchRecipes() {
    const searchInput = document.getElementById('search-input');
    const searchTerm = searchInput.value.trim();

    const app = document.getElementById('app');
    const searchContainer = app.querySelector('.search-container');

    app.innerHTML = searchContainer.outerHTML + `
        <div class="loading">
            <div class="spinner"></div>
        </div>
    `;

    try {
        const data = await api.getRecipes({ search: searchTerm });
        if (data.success) {
            displayRecipes(data.recipes);
        }
    } catch (error) {
        showError(`Erreur de recherche: ${error.message}`);
    }
}

function toggleRecipeSelection(recipeId) {
    if (storage.isRecipeSelected(recipeId)) {
        storage.removeSelectedRecipe(recipeId);
        showAlert('Recette retirée de votre sélection', 'info');
    } else {
        storage.addSelectedRecipe(recipeId);
        showAlert('Recette ajoutée à votre sélection', 'success');
    }

    // Refresh the current view
    if (router.getCurrentPage() === 'recipes') {
        renderRecipesList();
    }
}
