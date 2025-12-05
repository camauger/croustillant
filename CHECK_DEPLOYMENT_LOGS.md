# 📋 Vérifier les Logs de Déploiement Netlify

## 🔍 Problème : Functions Non Visibles dans le Dashboard

Selon la [documentation Netlify](https://docs.netlify.com/build/functions/overview/), les fonctions peuvent ne pas s'afficher dans le dashboard mais être actives. Il faut vérifier les **logs de déploiement** pour confirmer.

## ✅ Étapes de Vérification

### Étape 1 : Vérifier les Logs de Déploiement

1. **Netlify Dashboard → "Deploys"**
2. **Cliquez sur le dernier déploiement**
3. **Regardez les logs** et cherchez :

#### ✅ Si les fonctions sont détectées, vous verrez :

```
Functions directory: netlify/functions
Detected functions:
  - recipes
  - recipe-detail
  - shopping-list
Installing dependencies...
```

#### ❌ Si les fonctions ne sont pas détectées, vous verrez :

```
No functions directory found
```

ou

```
Functions directory: netlify/functions
No functions detected
```

### Étape 2 : Vérifier la Structure dans les Logs

Dans les logs, cherchez des messages comme :

```
Detected build settings
  Functions directory: netlify/functions
  Publish directory: public
```

### Étape 3 : Vérifier l'Installation des Dépendances Python

Si les fonctions sont détectées, vous devriez voir :

```
Installing Python dependencies...
Successfully installed psycopg2-binary-2.9.9 python-dotenv-1.0.0
```

## 🎯 Test Direct des Functions

**Même si "Functions" n'apparaît pas dans le dashboard**, testez directement :

### Test 1 : Endpoint Recipes

```
https://your-site.netlify.app/api/recipes
```

**Résultats possibles :**
- ✅ **Réponse JSON** (même vide) → Functions fonctionnent !
- ❌ **404 Not Found** → Functions non détectées
- ❌ **500 Error** → Erreur dans le code (mais functions détectées)

### Test 2 : Vérifier les Headers de Réponse

Utilisez les outils de développement du navigateur (F12) :
- **Network tab** → Testez `/api/recipes`
- **Regardez les headers de réponse**
- Si vous voyez `Content-Type: application/json`, les functions fonctionnent

## 🔧 Solutions si les Functions ne sont Pas Détectées

### Solution 1 : Vérifier netlify.toml est dans Git

```bash
# Vérifier
git ls-files netlify.toml

# Si pas dans Git, ajoutez-le :
git add netlify.toml
git commit -m "Add netlify.toml configuration"
git push origin main
```

### Solution 2 : Vérifier la Structure des Fichiers

Assurez-vous que cette structure existe dans votre repository :

```
netlify/
  functions/
    recipes.py
    recipe-detail.py
    shopping-list.py
    runtime.txt
    requirements.txt
    utils/
      db.py
      ingredients.py
```

### Solution 3 : Vérifier Build Settings dans Netlify

1. **"Site settings" → "Build & deploy" → "Build settings"**
2. **Vérifiez "Functions directory"** :
   - Doit être : `netlify/functions`
   - Si différent, **modifiez-le manuellement**

### Solution 4 : Redéployer avec Cache Clear

1. **"Deploys" → "Trigger deploy" → "Clear cache and deploy site"**
2. **Attendez le déploiement complet**
3. **Vérifiez les logs à nouveau**

## 📊 Interprétation des Logs

### Logs Normaux (Functions Détectées)

```
1: Installing dependencies
2: Functions directory: netlify/functions
3: Detected functions:
4:   - recipes
5:   - recipe-detail
6:   - shopping-list
7: Installing Python dependencies...
8: Successfully installed...
```

### Logs avec Problème

```
1: Functions directory: netlify/functions
2: No functions detected
```

→ Vérifiez que les fichiers `.py` sont dans Git

```
1: Error: No runtime.txt found
```

→ Vérifiez que `runtime.txt` existe et contient `python-3.11`

```
1: Error installing dependencies
```

→ Vérifiez `requirements.txt`

## 💡 Note Importante sur Python

La [documentation Netlify](https://docs.netlify.com/build/functions/overview/) mentionne principalement JavaScript, TypeScript et Go, mais **Python est toujours supporté** via `runtime.txt`.

**Configuration requise pour Python :**
- ✅ `runtime.txt` avec `python-3.11` (ou autre version)
- ✅ `requirements.txt` avec les dépendances
- ✅ Fonction `handler(event, context)` dans chaque fichier `.py`

## 🎯 Action Immédiate

1. **Allez dans Netlify Dashboard → "Deploys"**
2. **Cliquez sur le dernier déploiement**
3. **Copiez les logs** (surtout les lignes concernant "Functions")
4. **Partagez-les** pour que je puisse vous aider plus précisément

**Ou testez directement :**
```
https://your-site.netlify.app/api/recipes
```

Si vous recevez une réponse JSON, **les functions fonctionnent**, même si elles n'apparaissent pas dans le dashboard ! 🎉

