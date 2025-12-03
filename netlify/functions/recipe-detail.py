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
        recipe = execute_query(
            "SELECT * FROM recipes WHERE id = %s",
            (recipe_id,),
            fetch_one=True
        )

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
        existing = execute_query(
            "SELECT id FROM recipes WHERE id = %s",
            (recipe_id,),
            fetch_one=True
        )

        if not existing:
            return format_response(404, {
                "error": "Recette non trouvée",
                "success": False
            })

        # Check for duplicate title (if title is being changed)
        if 'titre' in body:
            duplicate = execute_query(
                "SELECT id FROM recipes WHERE titre = %s AND id != %s",
                (body['titre'], recipe_id),
                fetch_one=True
            )
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
                update_fields.append(field)
                # Convert lists/dicts to JSON for JSONB fields
                if field in ['ingredients', 'instructions', 'tags']:
                    update_values.append(json.dumps(body[field]))
                else:
                    update_values.append(body[field])

        if not update_fields:
            return format_response(400, {
                "error": "No fields to update",
                "success": False
            })

        # Build UPDATE query
        set_clause = ', '.join([f"{field} = %s" for field in update_fields])
        update_query = f"""
            UPDATE recipes
            SET {set_clause}
            WHERE id = %s
            RETURNING *
        """

        update_values.append(recipe_id)
        recipe = execute_update(update_query, tuple(update_values), returning=True)

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

def delete_recipe(recipe_id):
    """Delete a recipe"""
    try:
        # Check if recipe exists
        existing = execute_query(
            "SELECT id FROM recipes WHERE id = %s",
            (recipe_id,),
            fetch_one=True
        )

        if not existing:
            return format_response(404, {
                "error": "Recette non trouvée",
                "success": False
            })

        # Delete recipe
        rows_deleted = execute_delete(
            "DELETE FROM recipes WHERE id = %s",
            (recipe_id,)
        )

        return format_response(200, {
            "success": True,
            "message": "Recette supprimée avec succès",
            "rows_deleted": rows_deleted
        })

    except Exception as e:
        return handle_error(e)
