"""
Netlify Function: Recipes API
Handles GET (list all recipes) and POST (create new recipe)
"""

import json
from utils.db import execute_insert, execute_query, format_response, handle_error


def handler(event, context):
    """Main handler for recipes endpoint"""

    # Handle CORS preflight
    if event["httpMethod"] == "OPTIONS":
        return format_response(200, {})

    try:
        # GET: List all recipes
        if event["httpMethod"] == "GET":
            return get_recipes(event)

        # POST: Create new recipe
        elif event["httpMethod"] == "POST":
            return create_recipe(event)

        else:
            return format_response(
                405, {"error": "Method not allowed", "success": False}
            )

    except Exception as e:
        return handle_error(e)


def get_recipes(event):
    """Get all recipes with optional filtering"""
    try:
        # Parse query parameters
        params = event.get("queryStringParameters") or {}
        search = params.get("search", "").strip()
        category = params.get("category", "").strip()

        # Validate and sanitize limit/offset
        try:
            limit = min(int(params.get("limit", 100)), 1000)  # Cap at 1000
            offset = max(int(params.get("offset", 0)), 0)  # No negative offsets
        except ValueError:
            return format_response(
                400, {"error": "Invalid pagination parameters", "success": False}
            )

        # Build query with proper parameterization
        query = "SELECT * FROM recipes WHERE 1=1"
        query_params = []

        # Apply search filter (parameterized to prevent SQL injection)
        if search:
            query += " AND (titre ILIKE %s OR instructions::text ILIKE %s)"
            search_pattern = f"%{search}%"
            query_params.extend([search_pattern, search_pattern])

        # Apply category filter
        if category:
            query += " AND category = %s"
            query_params.append(category)

        # Order by creation date (newest first)
        query += " ORDER BY created_at DESC"

        # Apply pagination
        query += " LIMIT %s OFFSET %s"
        query_params.extend([limit, offset])

        # Execute query
        recipes = execute_query(query, tuple(query_params), fetch="all")

        return format_response(
            200, {"success": True, "recipes": recipes, "count": len(recipes)}
        )

    except Exception as e:
        return handle_error(e)


def create_recipe(event):
    """Create a new recipe"""
    try:
        # Parse request body
        body = json.loads(event["body"])

        # Validate required fields
        required_fields = ["titre", "ingredients", "instructions"]
        for field in required_fields:
            if field not in body:
                return format_response(
                    400, {"error": f"Missing required field: {field}", "success": False}
                )

        # Validate data types
        if not isinstance(body["ingredients"], list):
            return format_response(
                400, {"error": "ingredients must be an array", "success": False}
            )

        if not isinstance(body["instructions"], (list, str)):
            return format_response(
                400,
                {"error": "instructions must be an array or string", "success": False},
            )

        # Check for duplicate recipe title
        check_query = "SELECT id FROM recipes WHERE titre = %s"
        existing = execute_query(check_query, (body["titre"],), fetch="one")
        if existing:
            return format_response(
                409,
                {"error": "Une recette avec ce titre existe déjà", "success": False},
            )

        # Prepare recipe data
        insert_query = """
            INSERT INTO recipes (
                titre, temps_preparation, temps_cuisson, rendement,
                ingredients, instructions, image_url, category, tags
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING *
        """

        recipe_params = (
            body["titre"],
            body.get("temps_preparation", ""),
            body.get("temps_cuisson", ""),
            body.get("rendement", ""),
            json.dumps(body["ingredients"]),
            json.dumps(body["instructions"]),
            body.get("image_url", ""),
            body.get("category", ""),
            body.get("tags", []),
        )

        # Insert recipe
        recipe = execute_insert(insert_query, recipe_params)

        return format_response(
            201,
            {"success": True, "recipe": recipe, "message": "Recette créée avec succès"},
        )

    except json.JSONDecodeError:
        return format_response(
            400, {"error": "Invalid JSON in request body", "success": False}
        )
    except Exception as e:
        return handle_error(e)

