import { json, err } from "./shared/http.mjs";
import { queryAll, queryOne, execReturning } from "./shared/db.mjs";

function parseParams(qs) {
  if (!qs) return {};
  const out = {};
  for (const [k, v] of Object.entries(qs)) {
    if (v != null) out[k] = v;
  }
  return out;
}

export const handler = async (event) => {
  if (event.httpMethod === "OPTIONS") return json(200, {});

  try {
    if (event.httpMethod === "GET") {
      const params = parseParams(event.queryStringParameters || {});
      const search = (params.search || "").trim();
      const category = (params.category || "").trim();
      let limit = 100;
      let offset = 0;
      try {
        limit = Math.min(parseInt(params.limit ?? "100", 10) || 100, 1000);
        offset = Math.max(parseInt(params.offset ?? "0", 10) || 0, 0);
      } catch {
        return err(400, "Invalid pagination parameters");
      }

      const parts = ["SELECT * FROM recipes WHERE 1=1"];
      const args = [];
      if (search) {
        const p = `%${search}%`;
        args.push(p);
        parts.push(`AND (titre ILIKE $${args.length} OR instructions::text ILIKE $${args.length})`);
      }
      if (category) {
        args.push(category);
        parts.push(`AND category = $${args.length}`);
      }
      parts.push("ORDER BY created_at DESC");
      args.push(limit);
      const li = args.length;
      args.push(offset);
      const oi = args.length;
      parts.push(`LIMIT $${li} OFFSET $${oi}`);

      const sql = parts.join(" ");
      const recipes = await queryAll(sql, args);
      return json(200, { success: true, recipes, count: recipes.length });
    }

    if (event.httpMethod === "POST") {
      let body;
      try {
        body = JSON.parse(event.body || "{}");
      } catch {
        return err(400, "Invalid JSON in request body");
      }

      const required = ["titre", "ingredients", "instructions"];
      for (const f of required) {
        if (!(f in body)) return err(400, `Missing required field: ${f}`);
      }
      if (!Array.isArray(body.ingredients)) {
        return err(400, "ingredients must be an array");
      }
      if (typeof body.instructions !== "string" && !Array.isArray(body.instructions)) {
        return err(400, "instructions must be an array or string");
      }

      const dup = await queryOne("SELECT id FROM recipes WHERE titre = $1", [body.titre]);
      if (dup) {
        return err(409, "Une recette avec ce titre existe déjà");
      }

      const row = await execReturning(
        `INSERT INTO recipes (
          titre, temps_preparation, temps_cuisson, rendement,
          ingredients, instructions, image_url, category, tags, source_url
        )
        VALUES ($1, $2, $3, $4, $5::jsonb, $6::jsonb, $7, $8, $9, $10)
        RETURNING *`,
        [
          body.titre,
          body.temps_preparation ?? "",
          body.temps_cuisson ?? "",
          body.rendement ?? "",
          JSON.stringify(body.ingredients),
          JSON.stringify(body.instructions),
          body.image_url ?? "",
          body.category ?? "",
          body.tags ?? [],
          body.source_url ?? "",
        ]
      );

      return json(201, {
        success: true,
        recipe: row,
        message: "Recette créée avec succès",
      });
    }

    return err(405, "Method not allowed");
  } catch (e) {
    console.error(e);
    return json(500, { success: false, error: "An internal error occurred" });
  }
};
