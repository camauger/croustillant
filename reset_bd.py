import sqlite3

# Connexion à la base de données (le fichier recipes.db)
conn = sqlite3.connect('recipes.db')
c = conn.cursor()

# Supprimer la table existante si elle existe
c.execute('DROP TABLE IF EXISTS recipes')
conn.commit()

# Créer la table avec la contrainte UNIQUE sur le titre
c.execute('''
    CREATE TABLE recipes (
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
conn.close()

print("Base de données vidée et recréée avec contrainte UNIQUE sur le titre.")
