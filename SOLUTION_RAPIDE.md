# ⚡ Solution Rapide : "Fonction API non trouvée"

## 🎯 Réponse Rapide

**Si vous testez LOCALEMENT (http://localhost:8888) :**
- ❌ **C'est normal que ça ne fonctionne pas !**
- Les fonctions Python ne fonctionnent pas localement sur Windows
- **Solution** : Déployez sur Netlify pour tester

**Si vous testez sur NETLIFY (https://votre-site.netlify.app) :**
- Les fonctions ne sont pas déployées
- Suivez les étapes ci-dessous

## 🚀 Solution en 3 Étapes

### Étape 1 : Vérifier que Tout est Commité

```bash
# Vérifier l'état
git status

# Si des fichiers sont modifiés :
git add netlify/functions/ netlify.toml
git commit -m "Fix Netlify functions structure"
git push origin main
```

### Étape 2 : Vérifier sur GitHub

1. Allez sur votre repository GitHub
2. Cliquez sur `netlify/functions/`
3. **Vous devez voir** :
   - `recipes/` (dossier)
   - `recipe-detail/` (dossier)
   - `shopping-list/` (dossier)
   - `utils/` (dossier)

**Si vous ne voyez PAS ces dossiers**, ils ne sont pas dans Git !

### Étape 3 : Redéployer sur Netlify

1. **Netlify Dashboard → Deploys**
2. **"Trigger deploy" → "Clear cache and deploy site"**
3. **Attendez 1-2 minutes**
4. **Vérifiez les logs** :
   - Cherchez "Detected functions: recipes, recipe-detail, shopping-list"

## ✅ Test Rapide

Pour vérifier si les fonctions sont déployées :

1. Allez sur `https://votre-site.netlify.app/.netlify/functions/recipes`
2. **Si vous voyez du JSON** (même une erreur) → ✅ Fonctions déployées
3. **Si vous voyez 404** → ❌ Fonctions non déployées

## 🐛 Si Ça Ne Fonctionne Toujours Pas

### Vérifier netlify.toml

Le fichier doit contenir :
```toml
[functions]
  directory = "netlify/functions"
```

**PAS** :
```toml
[build]
  functions = "netlify/functions"  # ❌ Ancienne syntaxe
```

### Vérifier runtime.txt

Chaque fonction doit avoir `runtime.txt` avec :
```
python-3.11
```

**Sans ligne vide à la fin !**

### Vérifier les Build Settings

Dans Netlify Dashboard → Site settings → Build & deploy :

- **Functions directory** : `netlify/functions` ✅

## 📞 Besoin d'Aide ?

1. Dites-moi **où vous testez** (local ou Netlify)
2. Dites-moi si les fichiers sont **sur GitHub**
3. Dites-moi si le **déploiement Netlify est réussi**

