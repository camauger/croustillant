# 🔧 Résoudre l'Erreur 404 "Function not found"

## 🔍 Diagnostic de l'Erreur

Vous voyez cette erreur :
```
Failed to load resource: the server responded with a status of 404 (Not Found)
Function not found...
```

## ❓ Question Importante : Où Testez-Vous ?

### Option A : Vous testez LOCALEMENT (http://localhost:8888)

**C'est normal !** Les fonctions Python ne fonctionnent **pas** localement à cause de l'erreur Deno sur Windows.

**Solutions :**

1. **Déployer sur Netlify** (Recommandé)
   - Les fonctions fonctionneront en production
   - Voir guide ci-dessous

2. **Continuer le développement frontend**
   - Le serveur statique fonctionne
   - Vous pouvez développer l'interface
   - Les fonctions fonctionneront en production

### Option B : Vous testez sur NETLIFY (https://your-site.netlify.app)

Si vous voyez cette erreur sur Netlify, il y a un problème de configuration.

## 🚀 Solution : Déployer sur Netlify

### Étape 1 : Vérifier que le Code est Prêt

```bash
# Vérifier l'état
git status

# Si nécessaire, ajouter et commiter
git add .
git commit -m "Support NETLIFY_DATABASE_URL, ready for deployment"
git push origin main
```

### Étape 2 : Déployer sur Netlify

1. **Allez sur [netlify.com](https://netlify.com)**
2. **"Add new site" → "Import an existing project"**
3. **Connectez votre repository GitHub**
4. **Configurez les Build Settings :**
   - Build command : `echo "No build needed"`
   - Publish directory : `public`
   - Functions directory : `netlify/functions`

5. **Ajoutez la Variable d'Environnement** (IMPORTANT) :
   - Cliquez "Show advanced" → "New variable"
   - **Key** : `NETLIFY_DATABASE_URL`
   - **Value** : Votre chaîne de connexion Neon complète
   - Cliquez "Add variable"

6. **Déployez** : Cliquez "Deploy site"

### Étape 3 : Vérifier le Déploiement

1. **Attendez 1-2 minutes** pour le déploiement
2. **Vérifiez les Functions** :
   - Dans Netlify Dashboard → "Functions"
   - Vous devriez voir : `recipes`, `recipe-detail`, `shopping-list`

3. **Testez l'URL Netlify** :
   - Visitez `https://your-site.netlify.app`
   - Les fonctions devraient fonctionner !

## 🔍 Vérifications si l'Erreur Persiste sur Netlify

### 1. Vérifier les Functions dans Netlify Dashboard

1. Allez dans **"Functions"** dans le dashboard Netlify
2. Vérifiez que vous voyez :
   - ✅ `recipes`
   - ✅ `recipe-detail`
   - ✅ `shopping-list`

**Si les functions ne sont pas listées :**
- Vérifiez que `netlify/functions/` contient les fichiers `.py`
- Vérifiez que `netlify.toml` a `functions = "netlify/functions"`

### 2. Vérifier les Logs

1. Dans Netlify Dashboard → **"Functions"**
2. Cliquez sur une fonction (ex: `recipes`)
3. Regardez les **logs** pour voir les erreurs

**Erreurs communes :**
- `DATABASE_URL must be set` → Variable d'environnement manquante
- `relation "recipes" does not exist` → Schéma non créé dans Neon
- `Module not found` → Dépendances Python non installées

### 3. Vérifier la Variable d'Environnement

1. Dans Netlify Dashboard → **"Site settings" → "Environment variables"**
2. Vérifiez que `NETLIFY_DATABASE_URL` est définie
3. Vérifiez que la valeur est correcte (copiez depuis Neon)

**Pour tester la connexion :**
- Allez dans Neon SQL Editor
- Testez : `SELECT COUNT(*) FROM recipes;`
- Si ça fonctionne, la connexion est OK

### 4. Redéployer

Si vous avez modifié les variables d'environnement :

1. Dans Netlify Dashboard → **"Deploys"**
2. Cliquez sur **"Trigger deploy" → "Clear cache and deploy site"**
3. Attendez le redéploiement

## 📋 Checklist de Débogage

- [ ] Code poussé vers GitHub
- [ ] Site déployé sur Netlify
- [ ] Variable `NETLIFY_DATABASE_URL` ajoutée dans Netlify
- [ ] Functions visibles dans Netlify Dashboard → Functions
- [ ] Schéma de base de données créé dans Neon
- [ ] Test de connexion réussi dans Neon SQL Editor
- [ ] Logs de functions vérifiés (pas d'erreurs)
- [ ] Site testé sur l'URL Netlify (pas localhost)

## 🎯 Résumé

**Si vous testez localement :**
- ✅ C'est normal que les fonctions ne fonctionnent pas
- ✅ Déployez sur Netlify pour tester les fonctions

**Si vous testez sur Netlify :**
- ✅ Vérifiez que `NETLIFY_DATABASE_URL` est définie
- ✅ Vérifiez les logs des functions
- ✅ Vérifiez que le schéma est créé dans Neon
- ✅ Redéployez si nécessaire

## 💡 Prochaine Étape

**Dites-moi :**
1. Testez-vous sur `localhost:8888` ou sur `https://your-site.netlify.app` ?
2. Avez-vous déjà déployé sur Netlify ?
3. Si oui, voyez-vous les functions dans le dashboard Netlify ?

Avec ces informations, je pourrai vous aider plus précisément ! 🔍

