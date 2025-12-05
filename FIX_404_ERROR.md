# 🔧 Résoudre l'Erreur 404 sur /api/recipes

## 🔍 Diagnostic

Vous voyez cette erreur :
```
Failed to load resource: the server responded with a status of 404
Non-JSON response received: <!DOCTYPE html>...Page not found
```

## ✅ Solutions selon le Contexte

### Option A : Vous Testez LOCALEMENT (http://localhost:8888)

**C'est normal !** Les fonctions Python ne fonctionnent **pas** localement à cause du problème Deno sur Windows.

**Solutions :**
1. **Déployer sur Netlify** (Recommandé) - Les fonctions fonctionneront en production
2. **Continuer le développement frontend** - Le serveur statique fonctionne

### Option B : Vous Testez sur NETLIFY (https://votre-site.netlify.app)

Si vous voyez cette erreur sur Netlify, les fonctions ne sont pas encore déployées.

## 🚀 Solution : Vérifier et Déployer

### Étape 1 : Vérifier que les Changements sont Poussés

```bash
# Vérifier l'état
git status

# Si des changements ne sont pas poussés :
git push origin main
```

**Remplacez `main` par votre branche si nécessaire.**

### Étape 2 : Vérifier le Déploiement Netlify

1. **Allez sur Netlify Dashboard**
2. **Vérifiez "Deploys"** :
   - Y a-t-il un nouveau déploiement après votre dernier commit ?
   - Le déploiement a-t-il réussi (vert) ou échoué (rouge) ?

### Étape 3 : Vérifier les Logs de Déploiement

Dans les logs, cherchez :

**✅ Succès :**
```
Detected functions:
  - recipes
  - recipe-detail
  - shopping-list
```

**❌ Échec :**
```
No Functions were found in netlify/functions directory
```

### Étape 4 : Redéployer si Nécessaire

Si les fonctions ne sont pas détectées :

1. **Netlify Dashboard → Deploys**
2. **"Trigger deploy" → "Clear cache and deploy site"**
3. **Attendez 1-2 minutes**

### Étape 5 : Vérifier la Structure sur GitHub

Assurez-vous que la structure est correcte sur GitHub :

1. **Allez sur votre repository GitHub**
2. **Naviguez vers `netlify/functions/`**
3. **Vérifiez que vous voyez** :
   - `recipes/` (dossier)
   - `recipe-detail/` (dossier)
   - `shopping-list/` (dossier)
   - `utils/` (dossier)

**Pas** les anciens fichiers `.py` à la racine !

## 🔍 Vérifications Supplémentaires

### Vérifier netlify.toml

Assurez-vous que `netlify.toml` contient :

```toml
[build]
  functions = "netlify/functions"
```

### Vérifier les Build Settings

Dans Netlify Dashboard → Site settings → Build & deploy → Build settings :

- **Functions directory** : `netlify/functions` ✅
- **Base directory** : (vide) ✅
- **Package directory** : (vide) ✅

### Vérifier les Variables d'Environnement

Assurez-vous que `NETLIFY_DATABASE_URL` est défini :

1. **Netlify Dashboard → Site settings → Environment variables**
2. **Vérifiez que `NETLIFY_DATABASE_URL` existe**
3. **Si non, ajoutez-la** avec votre chaîne de connexion Neon

## 📝 Checklist de Déploiement

- [ ] Les nouveaux fichiers sont commités
- [ ] Les changements sont poussés sur GitHub (`git push`)
- [ ] Netlify a détecté le nouveau commit (déploiement automatique)
- [ ] Les logs montrent "Detected functions: recipes, recipe-detail, shopping-list"
- [ ] La variable `NETLIFY_DATABASE_URL` est définie
- [ ] Le déploiement est réussi (vert)
- [ ] Test sur `https://votre-site.netlify.app/api/recipes` fonctionne

## 🆘 Si Rien Ne Fonctionne

1. **Vérifiez sur GitHub** que la structure est correcte
2. **Redéployez avec cache clear** sur Netlify
3. **Vérifiez les logs de déploiement** pour des erreurs spécifiques
4. **Contactez le support Netlify** si le problème persiste

