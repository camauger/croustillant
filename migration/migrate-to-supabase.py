"""
Migration script to transfer data from SQLite to Supabase
Run this after setting up your Supabase database
"""

import os
import sys
import json
import sqlite3
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_KEY')  # Use service key for migration
SQLITE_DB = os.getenv('SQLITE_DB', 'recipes.db')

def get_supabase_client() -> Client:
    """Create Supabase client"""
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_KEY must be set in .env file")

    return create_client(SUPABASE_URL, SUPABASE_KEY)

def get_sqlite_recipes():
    """Fetch all recipes from SQLite database"""
    if not os.path.exists(SQLITE_DB):
        print(f"Error: SQLite database '{SQLITE_DB}' not found")
        return []

    conn = sqlite3.connect(SQLITE_DB)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    try:
        recipes = cursor.execute('SELECT * FROM recipes').fetchall()
        return [dict(recipe) for recipe in recipes]
    except Exception as e:
        print(f"Error reading from SQLite: {e}")
        return []
    finally:
        conn.close()

def parse_json_field(field_value):
    """Parse JSON field if it's a string"""
    if isinstance(field_value, str):
        try:
            return json.loads(field_value)
        except json.JSONDecodeError:
            return []
    return field_value or []

def migrate_recipes(recipes):
    """Migrate recipes to Supabase"""
    supabase = get_supabase_client()

    success_count = 0
    error_count = 0
    errors = []

    for recipe in recipes:
        try:
            # Prepare recipe data for Supabase
            recipe_data = {
                'titre': recipe['titre'],
                'temps_preparation': recipe.get('temps_preparation', ''),
                'temps_cuisson': recipe.get('temps_cuisson', ''),
                'rendement': recipe.get('rendement', ''),
                'ingredients': parse_json_field(recipe.get('ingredients')),
                'instructions': parse_json_field(recipe.get('instructions')),
                'image_url': recipe.get('image_url', ''),
                'category': recipe.get('category', ''),
                'tags': []
            }

            # Insert into Supabase
            response = supabase.table('recipes').insert(recipe_data).execute()

            if response.data:
                success_count += 1
                print(f"✓ Migrated: {recipe['titre']}")
            else:
                error_count += 1
                errors.append(f"Failed to migrate: {recipe['titre']}")

        except Exception as e:
            error_count += 1
            error_msg = f"Error migrating '{recipe['titre']}': {str(e)}"
            errors.append(error_msg)
            print(f"✗ {error_msg}")

    return success_count, error_count, errors

def main():
    print("=" * 60)
    print("Croustillant - SQLite to Supabase Migration")
    print("=" * 60)
    print()

    # Check environment variables
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("Error: Missing environment variables")
        print("Please set SUPABASE_URL and SUPABASE_SERVICE_KEY in .env file")
        sys.exit(1)

    print(f"Supabase URL: {SUPABASE_URL}")
    print(f"SQLite DB: {SQLITE_DB}")
    print()

    # Fetch recipes from SQLite
    print("Fetching recipes from SQLite...")
    recipes = get_sqlite_recipes()

    if not recipes:
        print("No recipes found in SQLite database")
        sys.exit(1)

    print(f"Found {len(recipes)} recipes to migrate")
    print()

    # Confirm migration
    confirm = input("Do you want to proceed with migration? (yes/no): ")
    if confirm.lower() not in ['yes', 'y']:
        print("Migration cancelled")
        sys.exit(0)

    print()
    print("Starting migration...")
    print("-" * 60)

    # Migrate recipes
    success_count, error_count, errors = migrate_recipes(recipes)

    # Print summary
    print()
    print("=" * 60)
    print("Migration Summary")
    print("=" * 60)
    print(f"Total recipes: {len(recipes)}")
    print(f"Successfully migrated: {success_count}")
    print(f"Errors: {error_count}")

    if errors:
        print()
        print("Errors encountered:")
        for error in errors:
            print(f"  - {error}")

    print()
    print("Migration complete!")

if __name__ == '__main__':
    main()
