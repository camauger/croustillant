"""
Netlify Function: Shopping List API
Generates shopping list from selected recipes
"""

import json
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from utils.db import execute_query, format_response, handle_error
from utils.ingredients import aggregate_ingredients, round_to_practical


def handler(event, context):
    """Main handler for shopping list endpoint"""

    # Handle CORS preflight
    if event["httpMethod"] == "OPTIONS":
        return format_response(200, {})

    try:
        if event["httpMethod"] == "POST":
            return generate_shopping_list(event)
        else:
            return format_response(
                405, {"error": "Method not allowed", "success": False}
            )

    except Exception as e:
        return handle_error(e)


def generate_shopping_list(event):
    """Generate shopping list from recipe IDs"""
    try:
        # Parse request body
        body = json.loads(event["body"])

        recipe_ids = body.get("recipe_ids", [])
        exclude_pantry = body.get("exclude_pantry", False)

        if not recipe_ids:
            return format_response(
                400, {"error": "No recipes selected", "success": False}
            )

        # Validate recipe_ids is a list
        if not isinstance(recipe_ids, list):
            return format_response(
                400, {"error": "recipe_ids must be an array", "success": False}
            )

        # Limit number of recipes
        if len(recipe_ids) > 50:
            return format_response(
                400,
                {
                    "error": "Maximum 50 recipes allowed per shopping list",
                    "success": False,
                },
            )

        # Convert recipe_ids to integers and validate
        try:
            recipe_ids = [int(rid) for rid in recipe_ids]
        except (ValueError, TypeError):
            return format_response(
                400, {"error": "Invalid recipe ID format", "success": False}
            )

        # Build query with IN clause
        # Use %s placeholders for each ID to prevent SQL injection
        placeholders = ", ".join(["%s"] * len(recipe_ids))
        query = f"SELECT * FROM recipes WHERE id IN ({placeholders})"

        # Fetch selected recipes
        recipes = execute_query(query, tuple(recipe_ids), fetch="all")

        if not recipes:
            return format_response(404, {"error": "No recipes found", "success": False})

        # Aggregate ingredients
        categorized_ingredients = aggregate_ingredients(recipes, exclude_pantry)

        # Round quantities to practical amounts
        for category, ingredients in categorized_ingredients.items():
            for ing in ingredients:
                ing["quantite"] = round_to_practical(ing["quantite"], ing["unite"])

        # Calculate statistics
        total_items = sum(len(items) for items in categorized_ingredients.values())

        return format_response(
            200,
            {
                "success": True,
                "shopping_list": categorized_ingredients,
                "total_items": total_items,
                "recipe_count": len(recipes),
                "recipes": [{"id": r["id"], "titre": r["titre"]} for r in recipes],
            },
        )

    except json.JSONDecodeError:
        return format_response(
            400, {"error": "Invalid JSON in request body", "success": False}
        )
    except Exception as e:
        return handle_error(e)
