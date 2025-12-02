"""
Netlify Function: Recipes API
Handles GET (list all recipes) and POST (create new recipe)
"""
import json
from utils.db import get_supabase_client, format_response, handle_error

def handler(event, context):
    """Main handler for recipes endpoint"""

    # Handle CORS preflight
    if event['httpMethod'] == 'OPTIONS':
        return format_response(200, {})

    try:
        supabase = get_supabase_client()

        # GET: List all recipes
        if event['httpMethod'] == 'GET':
            return get_recipes(supabase, event)

        # POST: Create new recipe
        elif event['httpMethod'] == 'POST':
            return create_recipe(supabase, event)

        else:
            return format_response(405, {
                "error": "Method not allowed",
                "success": False
            })

    except Exception as e:
        return handle_error(e)

def get_recipes(supabase, event):
    """Get all recipes with optional filtering"""
    try:
        # Parse query parameters
        params = event.get('queryStringParameters') or {}
        search = params.get('search', '').strip()
        category = params.get('category', '').strip()
        limit = int(params.get('limit', 100))
        offset = int(params.get('offset', 0))

        # Build query
        query = supabase.table('recipes').select('*')

        # Apply search filter
        if search:
            query = query.or_(f'titre.ilike.%{search}%,instructions.ilike.%{search}%')

        # Apply category filter (if implemented)
        if category:
            query = query.eq('category', category)

        # Apply pagination
        query = query.range(offset, offset + limit - 1)

        # Order by creation date (newest first)
        query = query.order('created_at', desc=True)

        # Execute query
        response = query.execute()

        return format_response(200, {
            "success": True,
            "recipes": response.data,
            "count": len(response.data)
        })

    except Exception as e:
        return handle_error(e)

def create_recipe(supabase, event):
    """Create a new recipe"""
    try:
        # Parse request body
        body = json.loads(event['body'])

        # Validate required fields
        required_fields = ['titre', 'ingredients', 'instructions']
        for field in required_fields:
            if field not in body:
                return format_response(400, {
                    "error": f"Missing required field: {field}",
                    "success": False
                })

        # Check for duplicate recipe title
        existing = supabase.table('recipes').select('id').eq('titre', body['titre']).execute()
        if existing.data:
            return format_response(409, {
                "error": "Une recette avec ce titre existe déjà",
                "success": False
            })

        # Prepare recipe data
        recipe_data = {
            'titre': body['titre'],
            'temps_preparation': body.get('temps_preparation', ''),
            'temps_cuisson': body.get('temps_cuisson', ''),
            'rendement': body.get('rendement', ''),
            'ingredients': body['ingredients'],
            'instructions': body['instructions'],
            'image_url': body.get('image_url', ''),
            'category': body.get('category', ''),
            'tags': body.get('tags', [])
        }

        # Insert recipe
        response = supabase.table('recipes').insert(recipe_data).execute()

        return format_response(201, {
            "success": True,
            "recipe": response.data[0],
            "message": "Recette créée avec succès"
        })

    except json.JSONDecodeError:
        return format_response(400, {
            "error": "Invalid JSON in request body",
            "success": False
        })
    except Exception as e:
        return handle_error(e)
