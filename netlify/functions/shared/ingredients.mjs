/** Shopping list: unit conversion, categories (aligned with Python utils/ingredients.py). */

const UNIT_CONVERSIONS = {
  ml: 1,
  millilitre: 1,
  millilitres: 1,
  l: 1000,
  litre: 1000,
  litres: 1000,
  tasse: 250,
  tasses: 250,
  "c. à soupe": 15,
  "c. à thé": 5,
  "cuillère à soupe": 15,
  "cuillères à soupe": 15,
  "cuillère à thé": 5,
  "cuillères à thé": 5,
  g: 1,
  gramme: 1,
  grammes: 1,
  kg: 1000,
  kilogramme: 1000,
  kilogrammes: 1000,
  oz: 28.35,
  once: 28.35,
  onces: 28.35,
  lb: 453.59,
  livre: 453.59,
  livres: 453.59,
};

const VOLUME_UNITS = new Set([
  "ml",
  "millilitre",
  "millilitres",
  "l",
  "litre",
  "litres",
  "tasse",
  "tasses",
  "c. à soupe",
  "c. à thé",
  "cuillère à soupe",
  "cuillères à soupe",
  "cuillère à thé",
  "cuillères à thé",
]);

const WEIGHT_UNITS = new Set([
  "g",
  "gramme",
  "grammes",
  "kg",
  "kilogramme",
  "kilogrammes",
  "oz",
  "once",
  "onces",
  "lb",
  "livre",
  "livres",
]);

const INGREDIENT_CATEGORIES = {
  "Produits laitiers": ["lait", "beurre", "crème", "fromage", "yogourt", "yaourt"],
  "Viandes et poissons": ["poulet", "boeuf", "porc", "poisson", "saumon", "thon", "bacon", "jambon"],
  "Fruits et légumes": ["tomate", "oignon", "ail", "carotte", "pomme", "banane", "laitue", "épinard", "poivron"],
  "Céréales et pains": ["pain", "farine", "riz", "pâtes", "céréales", "avoine"],
  "Condiments et épices": ["sel", "poivre", "huile", "vinaigre", "sauce", "épice", "herbe"],
  Conserves: ["conserve", "boîte"],
  Surgelés: ["surgelé", "congelé"],
};

const COMMON_PANTRY_ITEMS = ["sel", "poivre", "huile", "farine", "sucre", "eau"];

function normalizeUnit(unit) {
  const unitLower = (unit || "").toLowerCase().trim();
  if (!unitLower || !(unitLower in UNIT_CONVERSIONS)) {
    return [unitLower, 1, "other"];
  }
  const factor = UNIT_CONVERSIONS[unitLower];
  if (VOLUME_UNITS.has(unitLower)) return ["ml", factor, "volume"];
  if (WEIGHT_UNITS.has(unitLower)) return ["g", factor, "weight"];
  return [unitLower, 1, "other"];
}

function convertQuantity(quantity, fromUnit) {
  const [baseUnit, factor, unitType] = normalizeUnit(fromUnit);
  if (unitType === "other") {
    return [quantity, fromUnit];
  }
  const normalizedQuantity = quantity * factor;
  if (unitType === "volume") {
    if (normalizedQuantity >= 1000) return [normalizedQuantity / 1000, "l"];
    return [normalizedQuantity, "ml"];
  }
  if (unitType === "weight") {
    if (normalizedQuantity >= 1000) return [normalizedQuantity / 1000, "kg"];
    return [normalizedQuantity, "g"];
  }
  return [normalizedQuantity, baseUnit];
}

function categorizeIngredient(ingredientName) {
  const nameLower = ingredientName.toLowerCase();
  for (const [category, keywords] of Object.entries(INGREDIENT_CATEGORIES)) {
    for (const keyword of keywords) {
      if (nameLower.includes(keyword)) return category;
    }
  }
  return "Autres";
}

function isPantryItem(ingredientName) {
  const nameLower = ingredientName.toLowerCase();
  return COMMON_PANTRY_ITEMS.some((item) => nameLower.includes(item));
}

function processIngredient(ingredient, aggregated, excludePantry) {
  const name = (ingredient.nom || "").trim();
  const quantity = Number(
    ingredient.quantité ?? ingredient.quantite ?? 0
  );
  const unit = ingredient.unité ?? ingredient.unite ?? "";

  if (!name) return;
  if (excludePantry && isPantryItem(name)) return;

  const [convertedQty, convertedUnit] = convertQuantity(quantity, unit || "");
  const category = categorizeIngredient(name);
  const key = `${name.toLowerCase()}\t${String(convertedUnit).toLowerCase()}`;

  if (aggregated[key]) {
    aggregated[key].quantite += convertedQty;
  } else {
    aggregated[key] = {
      nom: name,
      quantite: convertedQty,
      unite: convertedUnit,
      category,
    };
  }
}

export function aggregateIngredients(recipes, excludePantry = false) {
  const aggregated = {};

  for (const recipe of recipes) {
    const ingredients = recipe.ingredients || [];
    for (const ing of ingredients) {
      if (ing.groupe) {
        for (const item of ing.liste || []) {
          processIngredient(item, aggregated, excludePantry);
        }
      } else {
        processIngredient(ing, aggregated, excludePantry);
      }
    }
  }

  const categorized = {};
  for (const data of Object.values(aggregated)) {
    const cat = data.category;
    if (!categorized[cat]) categorized[cat] = [];
    categorized[cat].push({
      nom: data.nom,
      quantite: Math.round(data.quantite * 100) / 100,
      unite: data.unite,
    });
  }
  return categorized;
}

export function roundToPractical(quantity, unit) {
  const u = String(unit || "").toLowerCase();
  if (
    ["unité", "unités", "", "pièce", "pièces"].includes(u) ||
    u === ""
  ) {
    return Math.round(quantity + 0.49);
  }
  if (quantity < 10) return Math.round(quantity * 10) / 10;
  if (quantity >= 100) return Math.round(quantity / 10) * 10;
  return Math.round(quantity);
}
