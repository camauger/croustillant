import os
from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import json

app = Flask(__name__)
app.secret_key = 'votre_cle_secrete'  # Remplacez par une clé plus sécurisée


@app.before_first_request
def initialize_db_data():
    conn = get_db_connection()
    cursor = conn.cursor()
    # Vérifier si la table recipes est vide
    count = cursor.execute("SELECT COUNT(*) FROM recipes").fetchone()[0]
    if count == 0:
        dossier_json = 'recettes_json'  # Ce dossier doit être dans votre dépôt
        for fichier in os.listdir(dossier_json):
            if fichier.endswith('.json'):
                chemin_fichier = os.path.join(dossier_json, fichier)
                with open(chemin_fichier, 'r', encoding='utf-8') as f:
                    recette = json.load(f)
                # Convertir les listes en chaînes JSON
                ingredients_json = json.dumps(
                    recette["ingrédients"], ensure_ascii=False)
                instructions_json = json.dumps(
                    recette["instructions"], ensure_ascii=False)
                cursor.execute('''
                    INSERT INTO recipes (titre, temps_preparation, temps_cuisson, rendement, ingredients, instructions)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    recette["titre"],
                    recette["temps_preparation"],
                    recette["temps_cuisson"],
                    recette["rendement"],
                    ingredients_json,
                    instructions_json
                ))
                print(
                    f"Recette '{recette['titre']}' ajoutée depuis le fichier {fichier}.")
        conn.commit()
        print("Toutes les recettes ont été ajoutées à la base de données.")
    conn.close()


def get_db_connection():
    conn = sqlite3.connect('recipes.db')
    conn.row_factory = sqlite3.Row
    # Créer la table si elle n'existe pas
    conn.execute('''
        CREATE TABLE IF NOT EXISTS recipes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titre TEXT NOT NULL UNIQUE,
            temps_preparation TEXT,
            temps_cuisson TEXT,
            rendement TEXT,
            ingredients TEXT,
            instructions TEXT
        )
    ''')
    conn.commit()
    return conn


@app.route('/')
def index():
    conn = get_db_connection()
    recipes = conn.execute('SELECT * FROM recipes').fetchall()
    conn.close()
    return render_template('index.html', recipes=recipes)


@app.route('/create_recipe', methods=['GET', 'POST'])
def create_recipe():
    if request.method == 'POST':
        titre = request.form['titre']
        temps_preparation = request.form.get('temps_preparation', '')
        temps_cuisson = request.form.get('temps_cuisson', '')
        rendement = request.form.get('rendement', '')
        ingredients = request.form.get('ingredients', '')
        instructions = request.form.get('instructions', '')

        conn = get_db_connection()
        conn.execute('''
            INSERT INTO recipes (titre, temps_preparation, temps_cuisson, rendement, ingredients, instructions)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (titre, temps_preparation, temps_cuisson, rendement, ingredients, instructions))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    return render_template('create_recipe.html')


@app.route('/recipe/<int:id>')
def display_recipe(id):
    conn = get_db_connection()
    recipe = conn.execute(
        'SELECT * FROM recipes WHERE id = ?', (id,)).fetchone()
    conn.close()
    if recipe is None:
        return "Recette non trouvée", 404
    ingredients = json.loads(recipe['ingredients'])
    instructions = json.loads(recipe['instructions'])
    return render_template('recipe.html', recipe=recipe, ingredients=ingredients, instructions=instructions)


@app.route('/add_to_list/<int:recipe_id>')
def add_to_list(recipe_id):
    if 'recipe_list' not in session:
        session['recipe_list'] = []
    # Ajoute l'identifiant si il n'est pas déjà dans la liste
    if recipe_id not in session['recipe_list']:
        session['recipe_list'].append(recipe_id)
        session.modified = True  # Forcer l'enregistrement de la modification
    return redirect(url_for('display_recipe', id=recipe_id))


@app.route('/remove_from_list/<int:recipe_id>')
def remove_from_list(recipe_id):
    if 'recipe_list' in session:
        recipe_list = session['recipe_list']
        if recipe_id in recipe_list:
            recipe_list.remove(recipe_id)
            session['recipe_list'] = recipe_list
            session.modified = True
    return redirect(url_for('my_list'))


@app.route('/clear_list')
def clear_list():
    session.pop('recipe_list', None)
    return redirect(url_for('my_list'))


@app.route('/my_list')
def my_list():
    recipe_ids = session.get('recipe_list', [])
    recipes = []
    if recipe_ids:
        placeholders = ','.join('?' for _ in recipe_ids)
        query = f'SELECT * FROM recipes WHERE id IN ({placeholders})'
        conn = get_db_connection()
        recipes = conn.execute(query, recipe_ids).fetchall()
        conn.close()
    return render_template('my_list.html', recipes=recipes)


@app.route('/generate_shopping_list')
def generate_shopping_list():
    recipe_ids = session.get('recipe_list', [])
    aggregated = {}
    if recipe_ids:
        placeholders = ','.join('?' for _ in recipe_ids)
        query = f'SELECT * FROM recipes WHERE id IN ({placeholders})'
        conn = get_db_connection()
        recipes = conn.execute(query, recipe_ids).fetchall()
        conn.close()
        for recipe in recipes:
            try:
                ingredients = json.loads(recipe['ingredients'])
            except Exception as e:
                ingredients = []
            for ing in ingredients:
                # Vérifier si l'ingrédient est groupé (contient la clé "groupe")
                if 'groupe' in ing:
                    for item in ing.get("liste", []):
                        name = item.get("nom")
                        quantity = item.get("quantité", 0)
                        unit = item.get("unité", "")
                        key = (name, unit)
                        aggregated[key] = aggregated.get(key, 0) + quantity
                else:
                    name = ing.get("nom")
                    quantity = ing.get("quantité", 0)
                    unit = ing.get("unité", "")
                    key = (name, unit)
                    aggregated[key] = aggregated.get(key, 0) + quantity
    aggregated_list = [
        {"nom": key[0], "quantité": aggregated[key], "unité": key[1]} for key in aggregated]
    return render_template('shopping_list.html', ingredients=aggregated_list)


if __name__ == '__main__':
    app.run(debug=True)
