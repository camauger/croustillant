import { json, err } from "./shared/http.mjs";
import { queryAll } from "./shared/db.mjs";
import { aggregateIngredients, roundToPractical } from "./shared/ingredients.mjs";

export const handler = async (event) => {
  if (event.httpMethod === "OPTIONS") return json(200, {});

  try {
    if (event.httpMethod !== "POST") {
      return err(405, "Method not allowed");
    }

    let body;
    try {
      body = JSON.parse(event.body || "{}");
    } catch {
      return err(400, "Invalid JSON in request body");
    }

    const recipeIds = body.recipe_ids || [];
    const excludePantry = Boolean(body.exclude_pantry);

    if (!recipeIds.length) return err(400, "No recipes selected");
    if (!Array.isArray(recipeIds)) return err(400, "recipe_ids must be an array");
    if (recipeIds.length > 50) {
      return err(400, "Maximum 50 recipes allowed per shopping list");
    }

    let ids;
    try {
      ids = recipeIds.map((rid) => parseInt(rid, 10));
      if (ids.some((n) => Number.isNaN(n))) throw new Error("nan");
    } catch {
      return err(400, "Invalid recipe ID format");
    }

    const placeholders = ids.map((_, i) => `$${i + 1}`).join(", ");
    const sql = `SELECT * FROM recipes WHERE id IN (${placeholders})`;
    const recipes = await queryAll(sql, ids);

    if (!recipes.length) return err(404, "No recipes found");

    let categorized = aggregateIngredients(recipes, excludePantry);
    categorized = Object.fromEntries(
      Object.entries(categorized).map(([cat, items]) => [
        cat,
        items.map((ing) => ({
          ...ing,
          quantite: roundToPractical(ing.quantite, ing.unite),
        })),
      ])
    );

    const totalItems = Object.values(categorized).reduce(
      (sum, items) => sum + items.length,
      0
    );

    return json(200, {
      success: true,
      shopping_list: categorized,
      total_items: totalItems,
      recipe_count: recipes.length,
      recipes: recipes.map((r) => ({ id: r.id, titre: r.titre })),
    });
  } catch (e) {
    console.error(e);
    return json(500, { success: false, error: "An internal error occurred" });
  }
};
