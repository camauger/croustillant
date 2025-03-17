import sqlite3
import json
import os
# Chemin vers le fichier JSON modifié (par exemple, "01.json")
dir_path = "recettes_json"
json_file_path = os.path.join(dir_path, "01.json")


# Lecture du fichier JSON mis à jour
with open(json_file_path, "r", encoding="utf-8") as f:
    updated_recipe = json.load(f)

# Connexion à la base de données
conn = sqlite3.connect('recipes.db')
cursor = conn.cursor()

# Conversion des listes en chaînes JSON pour le stockage
ingredients_json = json.dumps(updated_recipe["ingrédients"], ensure_ascii=False)
instructions_json = json.dumps(updated_recipe["instructions"], ensure_ascii=False)

# Utilisation de l'ID pour identifier la recette à mettre à jour
recipe_id = updated_recipe["id"]

cursor.execute('''
    UPDATE recipes
    SET titre = ?, temps_preparation = ?, temps_cuisson = ?, rendement = ?,
        ingredients = ?, instructions = ?
    WHERE id = ?
''', (
    updated_recipe["titre"],
    updated_recipe["temps_preparation"],
    updated_recipe["temps_cuisson"],
    updated_recipe["rendement"],
    ingredients_json,
    instructions_json,
    recipe_id
))

conn.commit()
conn.close()

print("La recette a été mise à jour avec succès.")
