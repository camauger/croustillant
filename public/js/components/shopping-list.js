// Shopping List Component

let currentShoppingList = null;

async function renderShoppingList() {
    const app = document.getElementById('app');
    const selectedIds = storage.getSelectedRecipes();

    if (selectedIds.length === 0) {
        app.innerHTML = `
            <div class="card text-center">
                <h2>Aucune recette sélectionnée</h2>
                <p>Sélectionnez des recettes pour générer une liste de courses.</p>
                <button class="btn btn-primary" onclick="router.navigate('recipes')">
                    Parcourir les recettes
                </button>
            </div>
        `;
        return;
    }

    // Show loading
    app.innerHTML = `
        <div class="card">
            <h2>Liste de courses</h2>
            <p>Génération de la liste de courses pour ${selectedIds.length} recettes...</p>
        </div>
        <div class="loading">
            <div class="spinner"></div>
        </div>
    `;

    try {
        const prefs = storage.getPreferences();
        const data = await api.generateShoppingList(selectedIds, prefs.excludePantryItems);

        if (data.success) {
            currentShoppingList = data;
            displayShoppingList(data);
        } else {
            showError('Erreur lors de la génération de la liste de courses');
        }
    } catch (error) {
        showError(`Erreur: ${error.message}`);
    }
}

function displayShoppingList(data) {
    const app = document.getElementById('app');
    const prefs = storage.getPreferences();

    // Create header with options
    const headerHTML = `
        <div class="card">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem;">
                <div>
                    <h2>Liste de courses</h2>
                    <p>${data.total_items} articles pour ${data.recipe_count} recettes</p>
                </div>
                <div style="display: flex; gap: 1rem; align-items: center; flex-wrap: wrap;">
                    <label style="display: flex; align-items: center; gap: 0.5rem;">
                        <input type="checkbox" id="exclude-pantry"
                               ${prefs.excludePantryItems ? 'checked' : ''}
                               onchange="toggleExcludePantry()">
                        Exclure les articles de base
                    </label>
                    <button class="btn btn-primary" onclick="exportShoppingList()">
                        📋 Copier la liste
                    </button>
                    <button class="btn btn-primary" onclick="printShoppingList()">
                        🖨️ Imprimer
                    </button>
                </div>
            </div>
        </div>
    `;

    // Display selected recipes
    const recipesHTML = `
        <div class="card">
            <h3>Recettes sélectionnées</h3>
            <ul>
                ${data.recipes.map(r => `<li>${r.titre}</li>`).join('')}
            </ul>
        </div>
    `;

    // Display categorized shopping list
    let categoriesHTML = '';
    const categories = data.shopping_list;

    for (const [category, items] of Object.entries(categories)) {
        const itemsHTML = items.map((item, index) => `
            <li id="shopping-item-${category}-${index}" onclick="toggleShoppingItem('${category}', ${index})">
                <input type="checkbox" id="checkbox-${category}-${index}">
                <span>
                    ${item.quantite && item.quantite > 0 ? `${item.quantite} ${item.unite}` : ''}
                    ${item.nom}
                </span>
            </li>
        `).join('');

        categoriesHTML += `
            <div class="shopping-category">
                <h3>${category}</h3>
                <ul class="shopping-items">
                    ${itemsHTML}
                </ul>
            </div>
        `;
    }

    app.innerHTML = headerHTML + recipesHTML + categoriesHTML;
}

function toggleShoppingItem(category, index) {
    const item = document.getElementById(`shopping-item-${category}-${index}`);
    const checkbox = document.getElementById(`checkbox-${category}-${index}`);

    if (item && checkbox) {
        checkbox.checked = !checkbox.checked;
        item.classList.toggle('checked');
    }
}

async function toggleExcludePantry() {
    const checkbox = document.getElementById('exclude-pantry');
    storage.updatePreference('excludePantryItems', checkbox.checked);

    // Regenerate list
    await renderShoppingList();
}

function exportShoppingList() {
    if (!currentShoppingList) return;

    let text = '📋 LISTE DE COURSES - CROUSTILLANT\n\n';

    // Add recipes
    text += '🍳 Recettes:\n';
    currentShoppingList.recipes.forEach(r => {
        text += `  • ${r.titre}\n`;
    });
    text += '\n';

    // Add items by category
    const categories = currentShoppingList.shopping_list;
    for (const [category, items] of Object.entries(categories)) {
        text += `\n${category.toUpperCase()}:\n`;
        items.forEach(item => {
            const qty = item.quantite && item.quantite > 0
                ? `${item.quantite} ${item.unite}`
                : '';
            text += `  ☐ ${qty} ${item.nom}\n`;
        });
    }

    text += `\n\nTotal: ${currentShoppingList.total_items} articles`;

    // Copy to clipboard
    navigator.clipboard.writeText(text).then(() => {
        showAlert('Liste copiée dans le presse-papiers!', 'success');
    }).catch(() => {
        // Fallback: show text in alert
        alert(text);
    });
}

function printShoppingList() {
    window.print();
}
