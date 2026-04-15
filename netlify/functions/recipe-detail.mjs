import { json, err } from "./lib/http.mjs";
import { queryOne, execReturning, execCommand } from "./lib/db.mjs";

function recipeIdFromPath(event) {
  const path = event.path || event.rawPath || "";
  const last = path.split("/").filter(Boolean).pop() || "";
  return last;
}

export const handler = async (event) => {
  if (event.httpMethod === "OPTIONS") return json(200, {});

  const rawId = recipeIdFromPath(event);
  if (!rawId || !/^\d+$/.test(rawId)) {
    return err(400, "Invalid recipe ID");
  }
  const recipeId = parseInt(rawId, 10);

  try {
    if (event.httpMethod === "GET") {
      const recipe = await queryOne("SELECT * FROM recipes WHERE id = $1", [recipeId]);
      if (!recipe) return err(404, "Recette non trouvée");
      return json(200, { success: true, recipe });
    }

    if (event.httpMethod === "PUT") {
      let body;
      try {
        body = JSON.parse(event.body || "{}");
      } catch {
        return err(400, "Invalid JSON in request body");
      }

      const existing = await queryOne("SELECT id FROM recipes WHERE id = $1", [recipeId]);
      if (!existing) return err(404, "Recette non trouvée");

      if (body.titre != null) {
        const duplicate = await queryOne(
          "SELECT id FROM recipes WHERE titre = $1 AND id != $2",
          [body.titre, recipeId]
        );
        if (duplicate) {
          return err(409, "Une autre recette avec ce titre existe déjà");
        }
      }

      const allowed = [
        "titre",
        "temps_preparation",
        "temps_cuisson",
        "rendement",
        "ingredients",
        "instructions",
        "image_url",
        "category",
        "tags",
        "source_url",
      ];

      const sets = [];
      const args = [];
      for (const field of allowed) {
        if (!(field in body)) continue;
        args.push(
          field === "ingredients" || field === "instructions"
            ? JSON.stringify(body[field])
            : body[field]
        );
        const cast =
          field === "ingredients" || field === "instructions" ? "::jsonb" : "";
        sets.push(`${field} = $${args.length}${cast}`);
      }

      if (sets.length === 0) return err(400, "No fields to update");

      args.push(recipeId);
      const sql = `UPDATE recipes SET ${sets.join(", ")} WHERE id = $${args.length} RETURNING *`;
      const recipe = await execReturning(sql, args);
      return json(200, {
        success: true,
        recipe,
        message: "Recette mise à jour avec succès",
      });
    }

    if (event.httpMethod === "DELETE") {
      const existing = await queryOne("SELECT id FROM recipes WHERE id = $1", [recipeId]);
      if (!existing) return err(404, "Recette non trouvée");

      const rows = await execCommand("DELETE FROM recipes WHERE id = $1", [recipeId]);
      return json(200, {
        success: true,
        message: "Recette supprimée avec succès",
        rows_deleted: rows,
      });
    }

    return err(405, "Method not allowed");
  } catch (e) {
    console.error(e);
    return json(500, { success: false, error: "An internal error occurred" });
  }
};
