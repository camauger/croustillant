# 🔍 Vérifier vos Recettes - Guide

## Problème : "Je ne peux pas voir mes recettes"

Cela peut être dû à deux choses :
1. **Les fonctions Python ne fonctionnent pas localement** (erreur Deno - normal)
2. **Il n'y a pas de recettes dans la base de données**

## Solution 1 : Vérifier dans Neon DB

### Étape 1 : Ouvrir Neon SQL Editor

1. Allez sur [console.neon.tech](https://console.neon.tech)
2. Connectez-vous
3. Sélectionnez votre projet `croustillant`
4. Cliquez sur **"SQL Editor"** dans le menu de gauche

### Étape 2 : Vérifier les Recettes

Exécutez cette requête SQL :

```sql
SELECT COUNT(*) as total_recettes FROM recipes;
```

**Résultats possibles :**
- Si `total_recettes = 0` → Il n'y a pas de recettes dans la base de données
- Si `total_recettes > 0` → Il y a des recettes, mais elles ne sont pas accessibles localement

### Étape 3 : Voir les Recettes

Pour voir les recettes existantes :

```sql
SELECT id, titre, created_at
FROM recipes
ORDER BY created_at DESC
LIMIT 10;
```

## Solution 2 : Ajouter des Recettes de Test

Si la base de données est vide, ajoutez une recette de test :

### Option A : Via SQL (dans Neon SQL Editor)

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
        "Faire revenir le bacon",
        "Mélanger avec les oeufs et le parmesan"
    ]'::jsonb
);
```

### Option B : Via l'Interface (après déploiement)

Une fois déployé sur Netlify, vous pourrez ajouter des recettes via l'interface web.

## Solution 3 : Déployer sur Netlify (Recommandé)

**C'est la meilleure solution !** Les fonctions Python fonctionneront en production :

### Déploiement Rapide

1. **Vérifier que tout est prêt** :
   ```bash
   git status
   ```

2. **Pousser vers GitHub** :
   ```bash
   git add .
   git commit -m "Ready for deployment"
   git push origin main
   ```

3. **Déployer sur Netlify** :
   - Allez sur [netlify.com](https://netlify.com)
   - "Add new site" → "Import an existing project"
   - Connectez GitHub
   - Configurez :
     - Build command : `echo "No build needed"`
     - Publish directory : `public`
     - Functions directory : `netlify/functions`
   - **Ajoutez variable d'environnement** :
     - Key : `DATABASE_URL`
     - Value : Votre chaîne de connexion Neon (celle dans votre `.env`)
   - Cliquez "Deploy"

4. **Tester** :
   - Visitez l'URL Netlify
   - Les recettes devraient s'afficher !

## Solution 4 : Vérifier la Configuration Locale

Si vous voulez quand même essayer localement :

### Vérifier que .env est correct

```bash
# Vérifier le contenu de .env
cat .env
```

Assurez-vous que `DATABASE_URL` est défini et correct.

### Vérifier la Connexion

Dans Neon SQL Editor, testez la connexion :

```sql
SELECT version();
```

Si ça fonctionne, la connexion est OK.

## Diagnostic Complet

### Checklist

- [ ] Base de données a des recettes ? → Vérifier dans Neon SQL Editor
- [ ] `DATABASE_URL` est défini ? → Vérifier dans `.env`
- [ ] Serveur Netlify est démarré ? → `just dev-ps` ou `npx netlify-cli dev`
- [ ] Fonctions Python fonctionnent ? → Normalement non localement (erreur Deno)
- [ ] Déployé sur Netlify ? → Les fonctions fonctionneront en production

## Résumé

**Situation actuelle :**
- ✅ Serveur statique fonctionne
- ❌ Fonctions Python ne fonctionnent pas localement (normal)
- ❓ Recettes dans la base de données ? → Vérifier dans Neon

**Solution recommandée :**
1. Vérifier dans Neon si des recettes existent
2. Si oui → Déployer sur Netlify pour les voir
3. Si non → Ajouter des recettes via SQL ou après déploiement

## Prochaine Étape

**Vérifiez d'abord dans Neon SQL Editor** si des recettes existent :

```sql
SELECT COUNT(*) FROM recipes;
```

Puis dites-moi le résultat ! 🔍

