// Recipe Detail Component

async function showRecipeDetail(recipeId) {
    const modal = document.getElementById('recipe-modal');
    const modalTitle = document.getElementById('modal-recipe-title');
    const modalContent = document.getElementById('modal-recipe-content');

    // Show loading state
    modalTitle.textContent = 'Chargement...';
    modalContent.innerHTML = '<div class="loading"><div class="spinner"></div></div>';
    modal.classList.add('active');

    try {
        const data = await api.getRecipe(recipeId);

        if (data.success && data.recipe) {
            const recipe = data.recipe;
            modalTitle.textContent = recipe.titre;
            modalContent.innerHTML = createRecipeDetailHTML(recipe);
        } else {
            modalContent.innerHTML = '<p class="alert alert-error">Erreur lors du chargement de la recette</p>';
        }
    } catch (error) {
        modalContent.innerHTML = `<p class="alert alert-error">Erreur: ${error.message}</p>`;
    }
}

function createRecipeDetailHTML(recipe) {
    const isSelected = storage.isRecipeSelected(recipe.id);

    let imageHTML = '';
    if (recipe.image_url) {
        imageHTML = `<img src="${recipe.image_url}" alt="${recipe.titre}">`;
    }

    // Parse ingredients
    const ingredients = typeof recipe.ingredients === 'string'
        ? JSON.parse(recipe.ingredients)
        : recipe.ingredients;

    let ingredientsHTML = '<ul class="ingredient-list">';

    ingredients.forEach(ing => {
        if (ing.groupe) {
            // Grouped ingredients
            ingredientsHTML += `
                <li class="ingredient-group">
                    <h3>${ing.groupe}</h3>
                    <ul>
                        ${ing.liste.map(item => `
                            <li>${formatIngredient(item)}</li>
                        `).join('')}
                    </ul>
                </li>
            `;
        } else {
            // Regular ingredient
            ingredientsHTML += `<li>${formatIngredient(ing)}</li>`;
        }
    });
    ingredientsHTML += '</ul>';

    // Parse instructions
    const instructions = typeof recipe.instructions === 'string'
        ? JSON.parse(recipe.instructions)
        : recipe.instructions;

    const instructionsHTML = `
        <ol>
            ${instructions.map(step => `<li>${step}</li>`).join('')}
        </ol>
    `;

    return `
        <div class="recipe-detail-header">
            ${imageHTML}
            <div class="recipe-meta">
                ${recipe.temps_preparation ? `<span>⏱️ Préparation: ${recipe.temps_preparation}</span>` : ''}
                ${recipe.temps_cuisson ? `<span>🔥 Cuisson: ${recipe.temps_cuisson}</span>` : ''}
                ${recipe.rendement ? `<span>👥 Rendement: ${recipe.rendement}</span>` : ''}
            </div>
            <div class="recipe-actions">
                <button class="btn ${isSelected ? 'btn-danger' : 'btn-success'}"
                        onclick="toggleRecipeSelection(${recipe.id}); showRecipeDetail(${recipe.id})">
                    ${isSelected ? '✓ Retirer de ma sélection' : '+ Ajouter à ma sélection'}
                </button>
                <button class="btn btn-outline" onclick="editRecipe(${recipe.id})">
                    ✏️ Modifier
                </button>
                <button class="btn btn-danger" onclick="confirmDeleteRecipe(${recipe.id})">
                    🗑️ Supprimer
                </button>
            </div>
        </div>

        <div class="ingredients-section">
            <h2>Ingrédients</h2>
            ${ingredientsHTML}
        </div>

        <div class="instructions-section">
            <h2>Instructions</h2>
            ${instructionsHTML}
        </div>
    `;
}

function formatIngredient(ingredient) {
    const qty = ingredient.quantité || ingredient.quantite || '';
    const unit = ingredient.unité || ingredient.unite || '';
    const name = ingredient.nom || '';

    if (qty && unit) {
        return `${qty} ${unit} ${name}`;
    } else if (qty) {
        return `${qty} ${name}`;
    } else {
        return name;
    }
}

function closeModal() {
    const modal = document.getElementById('recipe-modal');
    modal.classList.remove('active');
}

// Close modal when clicking outside
document.addEventListener('click', (e) => {
    const modal = document.getElementById('recipe-modal');
    if (e.target === modal) {
        closeModal();
    }
});

// Close modal with Escape key
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        closeModal();
    }
});

async function confirmDeleteRecipe(recipeId) {
    if (confirm('Êtes-vous sûr de vouloir supprimer cette recette ?')) {
        try {
            await api.deleteRecipe(recipeId);
            showAlert('Recette supprimée avec succès', 'success');
            closeModal();
            storage.removeSelectedRecipe(recipeId);

            // Refresh the current view
            if (router.getCurrentPage() === 'recipes') {
                renderRecipesList();
            } else if (router.getCurrentPage() === 'selection') {
                renderSelection();
            }
        } catch (error) {
            showAlert(`Erreur: ${error.message}`, 'error');
        }
    }
}

function editRecipe(recipeId) {
    closeModal();
    router.navigate('create');
    // Pass the recipe ID to the form
    setTimeout(() => {
        loadRecipeForEdit(recipeId);
    }, 100);
}
