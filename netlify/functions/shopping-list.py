"""
Netlify Function: Shopping List API
Generates shopping list from selected recipes
"""
import json
from utils.db import get_supabase_client, format_response, handle_error
from utils.ingredients import aggregate_ingredients, round_to_practical

def handler(event, context):
    """Main handler for shopping list endpoint"""

    # Handle CORS preflight
    if event['httpMethod'] == 'OPTIONS':
        return format_response(200, {})

    try:
        supabase = get_supabase_client()

        if event['httpMethod'] == 'POST':
            return generate_shopping_list(supabase, event)
        else:
            return format_response(405, {
                "error": "Method not allowed",
                "success": False
            })

    except Exception as e:
        return handle_error(e)

def generate_shopping_list(supabase, event):
    """Generate shopping list from recipe IDs"""
    try:
        # Parse request body
        body = json.loads(event['body'])

        recipe_ids = body.get('recipe_ids', [])
        exclude_pantry = body.get('exclude_pantry', False)

        if not recipe_ids:
            return format_response(400, {
                "error": "No recipes selected",
                "success": False
            })

        # Fetch selected recipes
        response = supabase.table('recipes').select('*').in_('id', recipe_ids).execute()

        if not response.data:
            return format_response(404, {
                "error": "No recipes found",
                "success": False
            })

        # Aggregate ingredients
        categorized_ingredients = aggregate_ingredients(response.data, exclude_pantry)

        # Round quantities to practical amounts
        for category, ingredients in categorized_ingredients.items():
            for ing in ingredients:
                ing['quantite'] = round_to_practical(ing['quantite'], ing['unite'])

        # Calculate statistics
        total_items = sum(len(items) for items in categorized_ingredients.values())

        return format_response(200, {
            "success": True,
            "shopping_list": categorized_ingredients,
            "total_items": total_items,
            "recipe_count": len(response.data),
            "recipes": [{"id": r['id'], "titre": r['titre']} for r in response.data]
        })

    except json.JSONDecodeError:
        return format_response(400, {
            "error": "Invalid JSON in request body",
            "success": False
        })
    except Exception as e:
        return handle_error(e)
