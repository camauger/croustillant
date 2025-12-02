"""
Netlify Function: Recipe Detail API
Handles GET (single recipe), PUT (update), DELETE (delete)
"""
import json
from utils.db import get_supabase_client, format_response, handle_error

def handler(event, context):
    """Main handler for recipe detail endpoint"""

    # Handle CORS preflight
    if event['httpMethod'] == 'OPTIONS':
        return format_response(200, {})

    try:
        supabase = get_supabase_client()

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
            return get_recipe(supabase, recipe_id)

        # PUT: Update recipe
        elif event['httpMethod'] == 'PUT':
            return update_recipe(supabase, recipe_id, event)

        # DELETE: Delete recipe
        elif event['httpMethod'] == 'DELETE':
            return delete_recipe(supabase, recipe_id)

        else:
            return format_response(405, {
                "error": "Method not allowed",
                "success": False
            })

    except Exception as e:
        return handle_error(e)

def get_recipe(supabase, recipe_id):
    """Get a single recipe by ID"""
    try:
        response = supabase.table('recipes').select('*').eq('id', recipe_id).execute()

        if not response.data:
            return format_response(404, {
                "error": "Recette non trouvée",
                "success": False
            })

        return format_response(200, {
            "success": True,
            "recipe": response.data[0]
        })

    except Exception as e:
        return handle_error(e)

def update_recipe(supabase, recipe_id, event):
    """Update an existing recipe"""
    try:
        # Parse request body
        body = json.loads(event['body'])

        # Check if recipe exists
        existing = supabase.table('recipes').select('id').eq('id', recipe_id).execute()
        if not existing.data:
            return format_response(404, {
                "error": "Recette non trouvée",
                "success": False
            })

        # Check for duplicate title (if title is being changed)
        if 'titre' in body:
            duplicate = supabase.table('recipes').select('id').eq('titre', body['titre']).neq('id', recipe_id).execute()
            if duplicate.data:
                return format_response(409, {
                    "error": "Une autre recette avec ce titre existe déjà",
                    "success": False
                })

        # Prepare update data (only include fields that are present)
        update_data = {}
        allowed_fields = ['titre', 'temps_preparation', 'temps_cuisson', 'rendement',
                         'ingredients', 'instructions', 'image_url', 'category', 'tags']

        for field in allowed_fields:
            if field in body:
                update_data[field] = body[field]

        if not update_data:
            return format_response(400, {
                "error": "No fields to update",
                "success": False
            })

        # Update recipe
        response = supabase.table('recipes').update(update_data).eq('id', recipe_id).execute()

        return format_response(200, {
            "success": True,
            "recipe": response.data[0],
            "message": "Recette mise à jour avec succès"
        })

    except json.JSONDecodeError:
        return format_response(400, {
            "error": "Invalid JSON in request body",
            "success": False
        })
    except Exception as e:
        return handle_error(e)

def delete_recipe(supabase, recipe_id):
    """Delete a recipe"""
    try:
        # Check if recipe exists
        existing = supabase.table('recipes').select('id').eq('id', recipe_id).execute()
        if not existing.data:
            return format_response(404, {
                "error": "Recette non trouvée",
                "success": False
            })

        # Delete recipe
        supabase.table('recipes').delete().eq('id', recipe_id).execute()

        return format_response(200, {
            "success": True,
            "message": "Recette supprimée avec succès"
        })

    except Exception as e:
        return handle_error(e)
