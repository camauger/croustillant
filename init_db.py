import sqlite3

conn = sqlite3.connect('recipes.db')
c = conn.cursor()
c.execute('''
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
conn.close()
print("Base de données initialisée avec contrainte UNIQUE sur le titre.")
