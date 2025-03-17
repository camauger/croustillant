import os
import sqlite3
import json

# Chemin vers le dossier contenant les fichiers JSON de tes recettes
dossier_json = 'recettes_json'  # Assure-toi que ce dossier existe et contient tes fichiers .json

# Connexion à la base de données SQLite (la base doit être initialisée au préalable)
conn = sqlite3.connect('recipes.db')
cursor = conn.cursor()

# Parcours de tous les fichiers JSON dans le dossier
for fichier in os.listdir(dossier_json):
    if fichier.endswith('.json'):
        chemin_fichier = os.path.join(dossier_json, fichier)
        with open(chemin_fichier, 'r', encoding='utf-8') as f:
            recette = json.load(f)

        # Convertir les listes d'ingrédients et d'instructions en chaînes JSON
        ingredients_json = json.dumps(recette["ingrédients"], ensure_ascii=False)
        instructions_json = json.dumps(recette["instructions"], ensure_ascii=False)

        # Insertion de la recette dans la table 'recipes'
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
        print(f"Recette '{recette['titre']}' ajoutée depuis le fichier {fichier}.")

# Enregistrer toutes les modifications et fermer la connexion
conn.commit()
conn.close()
print("Toutes les recettes ont été ajoutées à la base de données.")
