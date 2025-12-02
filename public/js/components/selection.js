// Selection Component - User's selected recipes

async function renderSelection() {
    const app = document.getElementById('app');
    const selectedIds = storage.getSelectedRecipes();

    if (selectedIds.length === 0) {
        app.innerHTML = `
            <div class="card text-center">
                <h2>Votre sélection est vide</h2>
                <p>Ajoutez des recettes à votre sélection pour générer une liste de courses.</p>
                <button class="btn btn-primary" onclick="router.navigate('recipes')">
                    Parcourir les recettes
                </button>
            </div>
        `;
        return;
    }

    // Show loading
    app.innerHTML = `
        <h2>Ma sélection (${selectedIds.length} recettes)</h2>
        <div class="loading">
            <div class="spinner"></div>
        </div>
    `;

    try {
        // Fetch all selected recipes
        const promises = selectedIds.map(id => api.getRecipe(id));
        const results = await Promise.allSettled(promises);

        const recipes = results
            .filter(result => result.status === 'fulfilled' && result.value.success)
            .map(result => result.value.recipe);

        if (recipes.length === 0) {
            app.innerHTML = `
                <div class="card text-center">
                    <h2>Aucune recette trouvée</h2>
                    <p>Les recettes sélectionnées n'ont pas pu être chargées.</p>
                    <button class="btn btn-primary" onclick="storage.clearSelectedRecipes(); renderSelection()">
                        Vider la sélection
                    </button>
                </div>
            `;
            return;
        }

        const recipesHTML = recipes.map(recipe => createSelectionCard(recipe)).join('');

        app.innerHTML = `
            <div class="card">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                    <h2>Ma sélection (${recipes.length} recettes)</h2>
                    <div style="display: flex; gap: 1rem;">
                        <button class="btn btn-primary" onclick="router.navigate('shopping')">
                            📋 Générer la liste de courses
                        </button>
                        <button class="btn btn-danger" onclick="clearSelection()">
                            🗑️ Vider la sélection
                        </button>
                    </div>
                </div>
            </div>
            <div class="recipe-grid">
                ${recipesHTML}
            </div>
        `;
    } catch (error) {
        showError(`Erreur: ${error.message}`);
    }
}

function createSelectionCard(recipe) {
    const imageHTML = recipe.image_url
        ? `<img src="${recipe.image_url}" alt="${recipe.titre}">`
        : `<div class="placeholder-img">🍳</div>`;

    return `
        <div class="card recipe-card">
            <div onclick="showRecipeDetail(${recipe.id})" style="cursor: pointer;">
                ${imageHTML}
                <h3>${recipe.titre}</h3>
                <div class="recipe-meta">
                    ${recipe.temps_preparation ? `<span>⏱️ Prep: ${recipe.temps_preparation}</span>` : ''}
                    ${recipe.temps_cuisson ? `<span>🔥 Cuisson: ${recipe.temps_cuisson}</span>` : ''}
                    ${recipe.rendement ? `<span>👥 ${recipe.rendement}</span>` : ''}
                </div>
            </div>
            <div class="recipe-actions" onclick="event.stopPropagation()">
                <button class="btn btn-danger btn-small" onclick="removeFromSelection(${recipe.id})">
                    ✕ Retirer
                </button>
            </div>
        </div>
    `;
}

function removeFromSelection(recipeId) {
    storage.removeSelectedRecipe(recipeId);
    showAlert('Recette retirée de votre sélection', 'info');
    renderSelection();
}

function clearSelection() {
    if (confirm('Êtes-vous sûr de vouloir vider votre sélection ?')) {
        storage.clearSelectedRecipes();
        showAlert('Sélection vidée', 'info');
        renderSelection();
    }
}
