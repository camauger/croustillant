# ⚙️ Configuration Netlify - Base Directory et Package Directory

## 📋 Paramètres à Configurer

Dans **Netlify Dashboard → Site settings → Build & deploy → Build settings**, vous avez ces champs :

### ✅ Configuration Correcte pour Ce Projet

| Paramètre | Valeur | Explication |
|-----------|--------|-------------|
| **Base directory** | *(laisser vide)* | Tout est à la racine du repository |
| **Package directory** | *(laisser vide)* | Pas un monorepo, donc vide |
| **Build command** | `echo 'No build command needed'` | Défini dans `netlify.toml` |
| **Publish directory** | `public` | Défini dans `netlify.toml` |
| **Functions directory** | `netlify/functions` | Défini dans `netlify.toml` |

## 🔍 Pourquoi Ces Champs Sont Vides (C'est Normal !)

### Base Directory
- **Vide = racine du repository** (`.`)
- Utilisé pour les monorepos où le projet est dans un sous-dossier
- **Votre cas** : Tout est à la racine, donc **laisser vide** ✅

### Package Directory
- **Vide = pas de package directory spécifique**
- Utilisé pour les monorepos où `package.json` ou `netlify.toml` est dans un sous-dossier
- **Votre cas** : `netlify.toml` est à la racine, donc **laisser vide** ✅

## ⚠️ Si Netlify Ne Détecte Pas les Fonctions

Si les fonctions ne sont toujours pas détectées après avoir laissé ces champs vides, essayez :

### Option 1 : Définir Explicitement (Si Nécessaire)

Si Netlify a des problèmes, vous pouvez définir explicitement :

| Paramètre | Valeur |
|-----------|--------|
| **Base directory** | `.` |
| **Package directory** | `.` |

**Mais normalement, laisser vide devrait fonctionner !**

### Option 2 : Vérifier la Structure Git

Assurez-vous que `netlify.toml` est bien à la racine dans Git :

```bash
# Vérifier
git ls-files netlify.toml

# Devrait afficher : netlify.toml
```

### Option 3 : Vérifier les Logs de Déploiement

Dans les logs de déploiement, cherchez :

```
Detected build settings
  Base directory:
  Functions directory: netlify/functions
```

Si vous voyez une erreur comme :
```
No Functions were found in netlify/functions directory
```

Alors le problème n'est **pas** les paramètres Base/Package directory, mais plutôt :
1. Les fichiers ne sont pas dans Git
2. La structure des fonctions n'est pas correcte
3. `runtime.txt` a un problème de format

## 🚀 Actions Recommandées

1. **Laissez Base directory et Package directory vides** (c'est correct !)
2. **Vérifiez que Functions directory = `netlify/functions`**
3. **Assurez-vous que les nouvelles fonctions sont commitées** :
   ```bash
   git add netlify/functions/recipes/
   git add netlify/functions/recipe-detail/
   git add netlify/functions/shopping-list/
   git commit -m "Restructure functions into separate folders"
   git push origin main
   ```
4. **Redéployez avec cache clear** :
   - Netlify Dashboard → Deploys → Trigger deploy → Clear cache and deploy site

## 📝 Résumé

- ✅ **Base directory** : Vide (correct pour votre projet)
- ✅ **Package directory** : Vide (correct pour votre projet)
- ✅ **Functions directory** : `netlify/functions` (doit être défini)
- ✅ **Publish directory** : `public` (doit être défini)

Ces paramètres sont normalement détectés automatiquement depuis `netlify.toml`, mais vous pouvez les vérifier manuellement dans les Build settings.

