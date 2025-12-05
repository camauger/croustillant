# 🔍 Diagnostic : "Fonction API non trouvée"

## ❓ Question Importante : Où Testez-Vous ?

### Option A : Vous Testez LOCALEMENT (http://localhost:8888)

**C'est normal que ça ne fonctionne pas !**

Les fonctions Python Netlify ne fonctionnent **PAS** localement sur Windows à cause d'un problème avec Deno/Edge Functions. C'est un problème connu de Netlify CLI sur Windows.

**Solutions :**
1. **Déployer sur Netlify** (Recommandé) - Les fonctions fonctionneront en production
2. **Continuer le développement frontend** - Le serveur statique fonctionne, vous pouvez développer l'interface

### Option B : Vous Testez sur NETLIFY (https://votre-site.netlify.app)

Si vous voyez cette erreur sur Netlify, il y a un problème de déploiement.

## 🔧 Diagnostic Étape par Étape

### Étape 1 : Vérifier que les Fichiers sont Commités

```bash
# Vérifier l'état Git
git status

# Si des fichiers ne sont pas commités :
git add netlify/functions/ netlify.toml
git commit -m "Fix functions structure"
git push origin main
```

### Étape 2 : Vérifier la Structure sur GitHub

1. Allez sur votre repository GitHub
2. Naviguez vers `netlify/functions/`
3. **Vérifiez que vous voyez** :
   - `recipes/` (dossier)
   - `recipe-detail/` (dossier)
   - `shopping-list/` (dossier)
   - `utils/` (dossier)

**Si vous ne voyez PAS ces dossiers sur GitHub**, ils ne sont pas dans le repository !

### Étape 3 : Vérifier le Déploiement Netlify

1. **Allez sur Netlify Dashboard**
2. **Sélectionnez votre site**
3. **Allez dans "Deploys"**
4. **Vérifiez le dernier déploiement** :
   - Est-il réussi (vert) ou échoué (rouge) ?
   - Y a-t-il un nouveau déploiement après votre dernier commit ?

### Étape 4 : Vérifier les Logs de Déploiement

Dans les logs de déploiement, cherchez :

**✅ Succès (ce que vous devriez voir) :**
```
Detected functions:
  - recipes
  - recipe-detail
  - shopping-list
```

**❌ Échec (ce qui indique un problème) :**
```
No Functions were found in netlify/functions directory
```

### Étape 5 : Vérifier la Configuration Netlify

Dans **Netlify Dashboard → Site settings → Build & deploy → Build settings** :

- **Functions directory** : `netlify/functions` ✅
- **Base directory** : (vide) ✅
- **Package directory** : (vide) ✅

### Étape 6 : Vérifier netlify.toml

Assurez-vous que `netlify.toml` contient :

```toml
[functions]
  directory = "netlify/functions"
```

**ET PAS** :
```toml
[build]
  functions = "netlify/functions"  # ❌ Ancienne syntaxe
```

### Étape 7 : Vérifier la Structure des Fonctions

Chaque fonction doit avoir cette structure :

```
netlify/functions/recipes/
  ├── handler.py          ✅ Doit exister
  ├── runtime.txt         ✅ Doit contenir "python-3.11" (sans ligne vide)
  └── requirements.txt    ✅ Doit contenir les dépendances
```

**Vérifiez que `runtime.txt` ne contient PAS de ligne vide à la fin !**

## 🚀 Solutions selon le Problème

### Problème 1 : Fichiers Non Commités

```bash
# Ajouter tous les fichiers
git add netlify/functions/
git add netlify.toml

# Commiter
git commit -m "Add Netlify functions with proper structure"

# Pousser
git push origin main

# Attendre le déploiement Netlify (1-2 minutes)
```

### Problème 2 : Fonctions Non Détectées

1. **Redéployer avec cache clear** :
   - Netlify Dashboard → Deploys → Trigger deploy → Clear cache and deploy site

2. **Vérifier que `runtime.txt` est correct** :
   - Ouvrir `netlify/functions/recipes/runtime.txt`
   - Doit contenir **uniquement** : `python-3.11`
   - **Pas de ligne vide à la fin !**

3. **Vérifier sur GitHub** que les fichiers sont bien là

### Problème 3 : Test Local (Windows)

Si vous testez localement sur Windows, **c'est normal que ça ne fonctionne pas**.

**Solutions :**
- Déployer sur Netlify pour tester
- Utiliser WSL (Windows Subsystem for Linux) pour tester localement
- Développer le frontend seulement (le serveur statique fonctionne)

## 📋 Checklist Complète

- [ ] Les fichiers sont commités et poussés sur GitHub
- [ ] La structure est visible sur GitHub (`netlify/functions/recipes/`, etc.)
- [ ] `netlify.toml` utilise `[functions] directory = "netlify/functions"`
- [ ] Chaque fonction a `handler.py`, `runtime.txt`, `requirements.txt`
- [ ] `runtime.txt` contient `python-3.11` (sans ligne vide)
- [ ] Le déploiement Netlify est réussi (vert)
- [ ] Les logs montrent "Detected functions: recipes, recipe-detail, shopping-list"
- [ ] La variable `DATABASE_URL` ou `NETLIFY_DATABASE_URL` est définie dans Netlify
- [ ] Vous testez sur Netlify (pas localement sur Windows)

## 🆘 Si Rien Ne Fonctionne

1. **Vérifiez sur GitHub** que tous les fichiers sont là
2. **Redéployez avec cache clear** sur Netlify
3. **Vérifiez les logs de déploiement** pour des erreurs spécifiques
4. **Contactez le support Netlify** si le problème persiste

## 💡 Astuce

Pour tester rapidement si les fonctions sont déployées :

1. Allez sur `https://votre-site.netlify.app/.netlify/functions/recipes`
2. Si vous voyez une réponse JSON (même une erreur), les fonctions sont déployées ✅
3. Si vous voyez "Function not found" ou 404, les fonctions ne sont pas déployées ❌

