// Recipe Form Component

let editingRecipeId = null;
let ingredientCounter = 0;
let instructionCounter = 0;

function renderRecipeForm() {
    const app = document.getElementById('app');

    app.innerHTML = `
        <div class="card">
            <h2 id="form-title">Ajouter une nouvelle recette</h2>
            <form id="recipe-form" onsubmit="handleRecipeSubmit(event)">
                <div class="form-group">
                    <label for="titre">Titre de la recette *</label>
                    <input type="text" id="titre" name="titre" required>
                </div>

                <div class="form-group">
                    <label for="temps_preparation">Temps de préparation</label>
                    <input type="text" id="temps_preparation" name="temps_preparation" placeholder="Ex: 20 minutes">
                </div>

                <div class="form-group">
                    <label for="temps_cuisson">Temps de cuisson</label>
                    <input type="text" id="temps_cuisson" name="temps_cuisson" placeholder="Ex: 30 minutes">
                </div>

                <div class="form-group">
                    <label for="rendement">Rendement</label>
                    <input type="text" id="rendement" name="rendement" placeholder="Ex: 4 portions">
                </div>

                <div class="form-group">
                    <label for="image_url">URL de l'image (optionnel)</label>
                    <input type="url" id="image_url" name="image_url" placeholder="https://...">
                </div>

                <div class="form-group">
                    <label>Ingrédients *</label>
                    <div id="ingredients-container"></div>
                    <button type="button" class="btn btn-outline btn-small" onclick="addIngredientField()">
                        + Ajouter un ingrédient
                    </button>
                </div>

                <div class="form-group">
                    <label>Instructions *</label>
                    <div id="instructions-container"></div>
                    <button type="button" class="btn btn-outline btn-small" onclick="addInstructionField()">
                        + Ajouter une étape
                    </button>
                </div>

                <div class="recipe-actions">
                    <button type="submit" class="btn btn-primary">
                        <span id="submit-btn-text">Créer la recette</span>
                    </button>
                    <button type="button" class="btn btn-outline" onclick="resetForm()">
                        Réinitialiser
                    </button>
                    <button type="button" class="btn btn-outline" onclick="router.navigate('recipes')">
                        Annuler
                    </button>
                </div>
            </form>
        </div>
    `;

    // Initialize with one ingredient and one instruction field
    ingredientCounter = 0;
    instructionCounter = 0;
    addIngredientField();
    addInstructionField();
}

function addIngredientField() {
    const container = document.getElementById('ingredients-container');
    const id = ingredientCounter++;

    const fieldHTML = `
        <div class="ingredient-item" id="ingredient-${id}">
            <input type="text" placeholder="Nom" class="ing-name" required>
            <input type="number" step="0.01" placeholder="Quantité" class="ing-qty">
            <input type="text" placeholder="Unité" class="ing-unit">
            <button type="button" class="btn btn-danger btn-small" onclick="removeIngredient(${id})">
                ✕
            </button>
        </div>
    `;

    container.insertAdjacentHTML('beforeend', fieldHTML);
}

function removeIngredient(id) {
    const element = document.getElementById(`ingredient-${id}`);
    if (element) {
        element.remove();
    }
}

function addInstructionField() {
    const container = document.getElementById('instructions-container');
    const id = instructionCounter++;

    const fieldHTML = `
        <div class="ingredient-item" id="instruction-${id}">
            <input type="text" placeholder="Étape ${id + 1}" class="instruction-text" required>
            <button type="button" class="btn btn-danger btn-small" onclick="removeInstruction(${id})">
                ✕
            </button>
        </div>
    `;

    container.insertAdjacentHTML('beforeend', fieldHTML);
}

function removeInstruction(id) {
    const element = document.getElementById(`instruction-${id}`);
    if (element) {
        element.remove();
    }
}

async function handleRecipeSubmit(event) {
    event.preventDefault();

    const form = document.getElementById('recipe-form');
    const submitBtn = document.getElementById('submit-btn-text');
    const originalText = submitBtn.textContent;

    submitBtn.textContent = 'Enregistrement...';

    try {
        // Collect form data
        const recipeData = {
            titre: form.titre.value.trim(),
            temps_preparation: form.temps_preparation.value.trim(),
            temps_cuisson: form.temps_cuisson.value.trim(),
            rendement: form.rendement.value.trim(),
            image_url: form.image_url.value.trim(),
            ingredients: collectIngredients(),
            instructions: collectInstructions()
        };

        // Validate
        if (recipeData.ingredients.length === 0) {
            showAlert('Veuillez ajouter au moins un ingrédient', 'error');
            submitBtn.textContent = originalText;
            return;
        }

        if (recipeData.instructions.length === 0) {
            showAlert('Veuillez ajouter au moins une instruction', 'error');
            submitBtn.textContent = originalText;
            return;
        }

        // Submit
        let response;
        if (editingRecipeId) {
            response = await api.updateRecipe(editingRecipeId, recipeData);
            showAlert('Recette mise à jour avec succès!', 'success');
        } else {
            response = await api.createRecipe(recipeData);
            showAlert('Recette créée avec succès!', 'success');
        }

        // Reset and redirect
        editingRecipeId = null;
        setTimeout(() => {
            router.navigate('recipes');
        }, 1000);

    } catch (error) {
        showAlert(`Erreur: ${error.message}`, 'error');
        submitBtn.textContent = originalText;
    }
}

function collectIngredients() {
    const ingredients = [];
    const container = document.getElementById('ingredients-container');
    const items = container.querySelectorAll('.ingredient-item');

    items.forEach(item => {
        const name = item.querySelector('.ing-name').value.trim();
        const qty = item.querySelector('.ing-qty').value.trim();
        const unit = item.querySelector('.ing-unit').value.trim();

        if (name) {
            ingredients.push({
                nom: name,
                quantité: qty ? parseFloat(qty) : 0,
                unité: unit
            });
        }
    });

    return ingredients;
}

function collectInstructions() {
    const instructions = [];
    const container = document.getElementById('instructions-container');
    const items = container.querySelectorAll('.ingredient-item');

    items.forEach(item => {
        const text = item.querySelector('.instruction-text').value.trim();
        if (text) {
            instructions.push(text);
        }
    });

    return instructions;
}

function resetForm() {
    editingRecipeId = null;
    renderRecipeForm();
}

async function loadRecipeForEdit(recipeId) {
    try {
        const data = await api.getRecipe(recipeId);

        if (data.success && data.recipe) {
            const recipe = data.recipe;
            editingRecipeId = recipeId;

            // Update form title
            document.getElementById('form-title').textContent = 'Modifier la recette';
            document.getElementById('submit-btn-text').textContent = 'Mettre à jour';

            // Populate form
            document.getElementById('titre').value = recipe.titre || '';
            document.getElementById('temps_preparation').value = recipe.temps_preparation || '';
            document.getElementById('temps_cuisson').value = recipe.temps_cuisson || '';
            document.getElementById('rendement').value = recipe.rendement || '';
            document.getElementById('image_url').value = recipe.image_url || '';

            // Clear and populate ingredients
            const ingredientsContainer = document.getElementById('ingredients-container');
            ingredientsContainer.innerHTML = '';
            ingredientCounter = 0;

            const ingredients = typeof recipe.ingredients === 'string'
                ? JSON.parse(recipe.ingredients)
                : recipe.ingredients;

            ingredients.forEach(ing => {
                if (ing.groupe) {
                    // Handle grouped ingredients
                    ing.liste.forEach(item => {
                        addIngredientField();
                        populateIngredientField(ingredientCounter - 1, item);
                    });
                } else {
                    addIngredientField();
                    populateIngredientField(ingredientCounter - 1, ing);
                }
            });

            // Clear and populate instructions
            const instructionsContainer = document.getElementById('instructions-container');
            instructionsContainer.innerHTML = '';
            instructionCounter = 0;

            const instructions = typeof recipe.instructions === 'string'
                ? JSON.parse(recipe.instructions)
                : recipe.instructions;

            instructions.forEach(instruction => {
                addInstructionField();
                const element = document.getElementById(`instruction-${instructionCounter - 1}`);
                element.querySelector('.instruction-text').value = instruction;
            });
        }
    } catch (error) {
        showAlert(`Erreur lors du chargement de la recette: ${error.message}`, 'error');
    }
}

function populateIngredientField(id, ingredient) {
    const element = document.getElementById(`ingredient-${id}`);
    if (element) {
        element.querySelector('.ing-name').value = ingredient.nom || '';
        element.querySelector('.ing-qty').value = ingredient.quantité || ingredient.quantite || '';
        element.querySelector('.ing-unit').value = ingredient.unité || ingredient.unite || '';
    }
}
