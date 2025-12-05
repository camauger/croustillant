# 🗄️ Créer le Schéma de Base de Données - Neon

## Problème

Vous avez reçu l'erreur :
```
ERROR: relation "recipes" does not exist
```

Cela signifie que la table `recipes` n'existe pas encore dans votre base de données Neon.

## Solution : Exécuter le Schéma SQL

### Étape 1 : Ouvrir Neon SQL Editor

1. Allez sur [console.neon.tech](https://console.neon.tech)
2. Connectez-vous
3. Sélectionnez votre projet `croustillant`
4. Cliquez sur **"SQL Editor"** dans le menu de gauche

### Étape 2 : Ouvrir le Fichier Schema

1. Ouvrez le fichier `neon-schema.sql` dans votre éditeur de code
2. **Copiez TOUT le contenu** du fichier

### Étape 3 : Exécuter dans Neon

1. Dans Neon SQL Editor, **collez** le contenu du fichier `neon-schema.sql`
2. Cliquez sur **"Run"** (ou appuyez sur `Ctrl+Enter`)
3. Vous devriez voir : **"Query executed successfully"**

### Étape 4 : Vérifier

Exécutez cette requête pour vérifier que la table existe :

```sql
SELECT COUNT(*) FROM recipes;
```

**Résultat attendu :** `0` (la table existe mais est vide)

## Si Vous Avez des Erreurs

### Erreur : "relation already exists"

Si vous voyez cette erreur, c'est que certaines tables existent déjà. C'est OK, continuez.

### Erreur : "permission denied"

Vérifiez que vous êtes connecté avec le bon compte et projet.

### Erreur : Syntaxe SQL

Assurez-vous d'avoir copié **tout** le contenu du fichier `neon-schema.sql`.

## Après la Création du Schéma

Une fois le schéma créé :

1. **La table `recipes` existera** (mais sera vide)
2. **Les fonctions Python fonctionneront** (une fois déployées sur Netlify)
3. **Vous pourrez ajouter des recettes** via l'interface web

## Ajouter des Recettes de Test

Après avoir créé le schéma, vous pouvez ajouter une recette de test :

```sql
INSERT INTO recipes (titre, temps_preparation, temps_cuisson, rendement, ingredients, instructions)
VALUES (
    'Pâtes Carbonara',
    '10 minutes',
    '15 minutes',
    '4 portions',
    '[
        {"nom": "Spaghetti", "quantite": 400, "unite": "g"},
        {"nom": "Bacon", "quantite": 200, "unite": "g"},
        {"nom": "Oeufs", "quantite": 4, "unite": ""},
        {"nom": "Parmesan", "quantite": 100, "unite": "g"}
    ]'::jsonb,
    '[
        "Cuire les pâtes al dente",
        "Faire revenir le bacon dans une poêle",
        "Mélanger les oeufs avec le parmesan râpé",
        "Ajouter les pâtes chaudes et mélanger rapidement"
    ]'::jsonb
);
```

## Résumé

1. ✅ Ouvrir Neon SQL Editor
2. ✅ Copier le contenu de `neon-schema.sql`
3. ✅ Coller et exécuter dans Neon
4. ✅ Vérifier avec `SELECT COUNT(*) FROM recipes;`
5. ✅ (Optionnel) Ajouter des recettes de test

**Une fois fait, dites-moi et on pourra tester !** 🚀

