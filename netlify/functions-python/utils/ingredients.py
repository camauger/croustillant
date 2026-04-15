"""Utilities for ingredient processing and shopping list generation"""

UNIT_CONVERSIONS = {
    # Volume conversions (all to ml)
    'ml': 1,
    'millilitre': 1,
    'millilitres': 1,
    'l': 1000,
    'litre': 1000,
    'litres': 1000,
    'tasse': 250,
    'tasses': 250,
    'c. à soupe': 15,
    'c. à thé': 5,
    'cuillère à soupe': 15,
    'cuillères à soupe': 15,
    'cuillère à thé': 5,
    'cuillères à thé': 5,

    # Weight conversions (all to grams)
    'g': 1,
    'gramme': 1,
    'grammes': 1,
    'kg': 1000,
    'kilogramme': 1000,
    'kilogrammes': 1000,
    'oz': 28.35,
    'once': 28.35,
    'onces': 28.35,
    'lb': 453.59,
    'livre': 453.59,
    'livres': 453.59,
}

INGREDIENT_CATEGORIES = {
    'Produits laitiers': ['lait', 'beurre', 'crème', 'fromage', 'yogourt', 'yaourt'],
    'Viandes et poissons': ['poulet', 'boeuf', 'porc', 'poisson', 'saumon', 'thon', 'bacon', 'jambon'],
    'Fruits et légumes': ['tomate', 'oignon', 'ail', 'carotte', 'pomme', 'banane', 'laitue', 'épinard', 'poivron'],
    'Céréales et pains': ['pain', 'farine', 'riz', 'pâtes', 'céréales', 'avoine'],
    'Condiments et épices': ['sel', 'poivre', 'huile', 'vinaigre', 'sauce', 'épice', 'herbe'],
    'Conserves': ['conserve', 'boîte'],
    'Surgelés': ['surgelé', 'congelé'],
}

COMMON_PANTRY_ITEMS = [
    'sel', 'poivre', 'huile', 'farine', 'sucre', 'eau'
]

def normalize_unit(unit: str) -> tuple:
    """
    Normalize unit to base unit and return conversion factor
    Returns: (base_unit, factor, unit_type)
    """
    unit_lower = unit.lower().strip()

    # Check volume units
    if unit_lower in UNIT_CONVERSIONS:
        factor = UNIT_CONVERSIONS[unit_lower]
        if unit_lower in ['ml', 'millilitre', 'millilitres', 'l', 'litre', 'litres', 'tasse', 'tasses', 'c. à soupe', 'c. à thé', 'cuillère à soupe', 'cuillères à soupe', 'cuillère à thé', 'cuillères à thé']:
            return ('ml', factor, 'volume')

    # Check weight units
    if unit_lower in UNIT_CONVERSIONS:
        factor = UNIT_CONVERSIONS[unit_lower]
        if unit_lower in ['g', 'gramme', 'grammes', 'kg', 'kilogramme', 'kilogrammes', 'oz', 'once', 'onces', 'lb', 'livre', 'livres']:
            return ('g', factor, 'weight')

    # Return original unit if no conversion available
    return (unit_lower, 1, 'other')

def convert_quantity(quantity: float, from_unit: str, to_unit: str = None) -> tuple:
    """
    Convert quantity to normalized unit
    Returns: (converted_quantity, base_unit)
    """
    base_unit, factor, unit_type = normalize_unit(from_unit)

    if unit_type == 'other':
        return (quantity, from_unit)

    normalized_quantity = quantity * factor

    # Convert to more readable units if large quantities
    if unit_type == 'volume':
        if normalized_quantity >= 1000:
            return (normalized_quantity / 1000, 'l')
        return (normalized_quantity, 'ml')

    if unit_type == 'weight':
        if normalized_quantity >= 1000:
            return (normalized_quantity / 1000, 'kg')
        return (normalized_quantity, 'g')

    return (normalized_quantity, base_unit)

def categorize_ingredient(ingredient_name: str) -> str:
    """Categorize ingredient based on its name"""
    name_lower = ingredient_name.lower()

    for category, keywords in INGREDIENT_CATEGORIES.items():
        for keyword in keywords:
            if keyword in name_lower:
                return category

    return 'Autres'

def is_pantry_item(ingredient_name: str) -> bool:
    """Check if ingredient is a common pantry item"""
    name_lower = ingredient_name.lower()
    return any(item in name_lower for item in COMMON_PANTRY_ITEMS)

def aggregate_ingredients(recipes: list, exclude_pantry: bool = False) -> dict:
    """
    Aggregate ingredients from multiple recipes
    Returns dict with categories as keys
    """
    aggregated = {}

    for recipe in recipes:
        ingredients = recipe.get('ingredients', [])

        for ing in ingredients:
            # Handle grouped ingredients
            if 'groupe' in ing:
                for item in ing.get('liste', []):
                    process_ingredient(item, aggregated, exclude_pantry)
            else:
                process_ingredient(ing, aggregated, exclude_pantry)

    # Organize by category
    categorized = {}
    for key, data in aggregated.items():
        category = data['category']
        if category not in categorized:
            categorized[category] = []

        categorized[category].append({
            'nom': data['nom'],
            'quantite': round(data['quantite'], 2),
            'unite': data['unite']
        })

    return categorized

def process_ingredient(ingredient: dict, aggregated: dict, exclude_pantry: bool):
    """Process a single ingredient and add to aggregated dict"""
    name = ingredient.get('nom', '').strip()
    quantity = float(ingredient.get('quantité', 0) or ingredient.get('quantite', 0))
    unit = ingredient.get('unité', '') or ingredient.get('unite', '')

    if not name:
        return

    # Skip pantry items if requested
    if exclude_pantry and is_pantry_item(name):
        return

    # Normalize quantities and units
    converted_qty, converted_unit = convert_quantity(quantity, unit)
    category = categorize_ingredient(name)

    # Create unique key for ingredient
    key = (name.lower(), converted_unit.lower())

    if key in aggregated:
        aggregated[key]['quantite'] += converted_qty
    else:
        aggregated[key] = {
            'nom': name,
            'quantite': converted_qty,
            'unite': converted_unit,
            'category': category
        }

def round_to_practical(quantity: float, unit: str) -> float:
    """Round quantities to practical amounts"""
    # For units (eggs, cans, etc.), round up to nearest whole number
    if unit in ['unité', 'unités', '', 'pièce', 'pièces']:
        return round(quantity + 0.49)  # Round 2.3 to 3, 2.7 to 3

    # For small quantities, keep 1 decimal
    if quantity < 10:
        return round(quantity, 1)

    # For larger quantities, round to nearest 5 or 10
    if quantity >= 100:
        return round(quantity / 10) * 10

    return round(quantity)
