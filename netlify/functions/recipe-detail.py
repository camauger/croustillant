"""
Netlify Function: Recipe Detail API
Handles GET (single recipe), PUT (update), DELETE (delete)
"""
import json
from utils.db import execute_query, execute_update, execute_delete, format_response, handle_error

def handler(event, context):
    """Main handler for recipe detail endpoint"""

    # Handle CORS preflight
    if event['httpMethod'] == 'OPTIONS':
        return format_response(200, {})

    try:
        # Extract recipe ID from path
        path = event.get('path', '')
        recipe_id = path.split('/')[-1]

        if not recipe_id or not recipe_id.isdigit():
            return format_response(400, {
                "error": "Invalid recipe ID",
                "success": False
            })

        recipe_id = int(recipe_id)

        # GET: Get single recipe
        if event['httpMethod'] == 'GET':
            return get_recipe(recipe_id)

        # PUT: Update recipe
        elif event['httpMethod'] == 'PUT':
            return update_recipe(recipe_id, event)

        # DELETE: Delete recipe
        elif event['httpMethod'] == 'DELETE':
            return delete_recipe(recipe_id)

        else:
            return format_response(405, {
                "error": "Method not allowed",
                "success": False
            })

    except Exception as e:
        return handle_error(e)

def get_recipe(recipe_id):
    """Get a single recipe by ID"""
    try:
        query = "SELECT * FROM recipes WHERE id = %s"
        recipe = execute_query(query, (recipe_id,), fetch='one')

        if not recipe:
            return format_response(404, {
                "error": "Recette non trouvée",
                "success": False
            })

        return format_response(200, {
            "success": True,
            "recipe": recipe
        })

    except Exception as e:
        return handle_error(e)

def update_recipe(recipe_id, event):
    """Update an existing recipe"""
    try:
        # Parse request body
        body = json.loads(event['body'])

        # Check if recipe exists
        check_query = "SELECT id FROM recipes WHERE id = %s"
        existing = execute_query(check_query, (recipe_id,), fetch='one')
        if not existing:
            return format_response(404, {
                "error": "Recette non trouvée",
                "success": False
            })

        # Check for duplicate title (if title is being changed)
        if 'titre' in body:
            dup_query = "SELECT id FROM recipes WHERE titre = %s AND id != %s"
            duplicate = execute_query(dup_query, (body['titre'], recipe_id), fetch='one')
            if duplicate:
                return format_response(409, {
                    "error": "Une autre recette avec ce titre existe déjà",
                    "success": False
                })

        # Prepare update data (only include fields that are present)
        allowed_fields = ['titre', 'temps_preparation', 'temps_cuisson', 'rendement',
                         'ingredients', 'instructions', 'image_url', 'category', 'tags']

        update_fields = []
        update_values = []

        for field in allowed_fields:
            if field in body:
                update_fields.append(f"{field} = %s")
                # Convert lists/dicts to JSON strings for JSONB fields
                if field in ['ingredients', 'instructions']:
                    update_values.append(json.dumps(body[field]))
                else:
                    update_values.append(body[field])

        if not update_fields:
            return format_response(400, {
                "error": "No fields to update",
                "success": False
            })

        # Build and execute update query
        update_query = f"""
            UPDATE recipes
            SET {', '.join(update_fields)}
            WHERE id = %s
            RETURNING *
        """
        update_values.append(recipe_id)

        recipe = execute_update(update_query, tuple(update_values))

        return format_response(200, {
            "success": True,
            "recipe": recipe,
            "message": "Recette mise à jour avec succès"
        })

    except json.JSONDecodeError:
        return format_response(400, {
            "error": "Invalid JSON in request body",
            "success": False
        })
    except Exception as e:
        return handle_error(e)

def delete_recipe_handler(recipe_id):
    """Delete a recipe"""
    try:
        # Check if recipe exists
        check_query = "SELECT id FROM recipes WHERE id = %s"
        existing = execute_query(check_query, (recipe_id,), fetch='one')
        if not existing:
            return format_response(404, {
                "error": "Recette non trouvée",
                "success": False
            })

        # Delete recipe
        delete_query = "DELETE FROM recipes WHERE id = %s"
        execute_delete(delete_query, (recipe_id,))

        return format_response(200, {
            "success": True,
            "message": "Recette supprimée avec succès",
            "rows_deleted": rows_deleted
        })

    except Exception as e:
        return handle_error(e)
