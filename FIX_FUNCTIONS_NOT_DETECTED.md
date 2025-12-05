# 🔧 Functions Non Détectées sur Netlify

## 🔍 Problème

La section "Functions" n'apparaît pas dans le dashboard Netlify, ce qui signifie que les fonctions Python n'ont pas été détectées lors du déploiement.

## ✅ Solutions

### Solution 1 : Vérifier la Configuration

#### 1.1 Vérifier netlify.toml

Assurez-vous que `netlify.toml` contient :

```toml
[build]
  functions = "netlify/functions"
```

#### 1.2 Vérifier la Structure des Fichiers

Vérifiez que vous avez cette structure :

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

### Solution 2 : Vérifier les Build Settings dans Netlify

1. **Allez dans Netlify Dashboard**
2. **Sélectionnez votre site**
3. **"Site settings" → "Build & deploy" → "Build settings"**
4. **Vérifiez que :**
   - **Functions directory** : `netlify/functions`
   - Si ce champ est vide ou différent, **modifiez-le** et sauvegardez

### Solution 3 : Vérifier les Logs de Déploiement

1. **Dans Netlify Dashboard → "Deploys"**
2. **Cliquez sur le dernier déploiement**
3. **Regardez les logs** pour voir :
   - Si les fonctions sont détectées
   - S'il y a des erreurs

**Recherchez dans les logs :**
- `Functions directory: netlify/functions`
- `Detected functions:`
- `Installing dependencies`
- Erreurs liées aux fonctions

### Solution 4 : Redéployer avec Cache Clear

1. **Dans Netlify Dashboard → "Deploys"**
2. **Cliquez "Trigger deploy" → "Clear cache and deploy site"**
3. **Attendez le redéploiement complet**

### Solution 5 : Vérifier que les Fichiers sont dans le Repository

Assurez-vous que les fichiers de fonctions sont bien dans Git :

```bash
# Vérifier que les fichiers sont trackés
git ls-files netlify/functions/

# Vous devriez voir :
# netlify/functions/recipes.py
# netlify/functions/recipe-detail.py
# netlify/functions/shopping-list.py
# netlify/functions/runtime.txt
# netlify/functions/requirements.txt
```

Si des fichiers manquent :

```bash
git add netlify/functions/
git commit -m "Add Netlify functions"
git push origin main
```

### Solution 6 : Vérifier runtime.txt et requirements.txt

Assurez-vous que ces fichiers existent et sont corrects :

**netlify/functions/runtime.txt :**
```
python-3.11
```

**netlify/functions/requirements.txt :**
```
psycopg2-binary==2.9.9
python-dotenv==1.0.0
```

### Solution 7 : Vérifier le Format des Handlers

Assurez-vous que chaque fichier `.py` a une fonction `handler` :

**Exemple (recipes.py) :**
```python
def handler(event, context):
    # Votre code ici
    return format_response(200, {"success": True})
```

## 🔍 Diagnostic Détaillé

### Étape 1 : Vérifier le Déploiement

1. **Allez dans "Deploys"**
2. **Regardez le dernier déploiement**
3. **Vérifiez le statut** : Succès ou Échec ?

### Étape 2 : Vérifier les Logs

Dans les logs de déploiement, cherchez :

**Si vous voyez :**
```
Functions directory: netlify/functions
Detected functions:
  - recipes
  - recipe-detail
  - shopping-list
```
→ Les fonctions sont détectées, mais peut-être pas affichées dans le dashboard

**Si vous voyez :**
```
No functions directory found
```
→ Le répertoire n'est pas détecté

**Si vous voyez :**
```
Error installing dependencies
```
→ Problème avec requirements.txt

### Étape 3 : Vérifier la Structure du Repository

Assurez-vous que le repository contient bien :

```
croustillant/
  netlify/
    functions/
      *.py
      runtime.txt
      requirements.txt
  netlify.toml
  public/
  ...
```

## 🚀 Solution Rapide : Redéployer

1. **Vérifiez que tout est commité :**
   ```bash
   git status
   git add .
   git commit -m "Fix functions configuration"
   git push origin main
   ```

2. **Dans Netlify Dashboard :**
   - "Deploys" → "Trigger deploy" → "Clear cache and deploy site"

3. **Attendez le déploiement** (1-2 minutes)

4. **Vérifiez à nouveau** :
   - "Functions" devrait maintenant apparaître
   - Ou vérifiez les logs pour voir si les fonctions sont détectées

## 📋 Checklist de Vérification

- [ ] `netlify.toml` contient `functions = "netlify/functions"`
- [ ] Les fichiers `.py` existent dans `netlify/functions/`
- [ ] `runtime.txt` existe et contient `python-3.11`
- [ ] `requirements.txt` existe et contient les dépendances
- [ ] Tous les fichiers sont dans Git (pas dans .gitignore)
- [ ] Build settings dans Netlify : Functions directory = `netlify/functions`
- [ ] Déploiement réussi (pas d'erreurs dans les logs)
- [ ] Cache nettoyé et redéployé

## 💡 Note Importante

**Même si "Functions" n'apparaît pas dans le dashboard**, les fonctions peuvent quand même fonctionner si :
- Elles sont correctement configurées dans `netlify.toml`
- Les fichiers sont présents dans le repository
- Le déploiement est réussi

**Testez directement l'URL :**
```
https://your-site.netlify.app/api/recipes
```

Si vous recevez une réponse JSON (même une erreur), les fonctions fonctionnent !

## 🆘 Si Rien Ne Fonctionne

1. **Vérifiez les logs de déploiement** pour des erreurs spécifiques
2. **Vérifiez que le repository est bien connecté** à Netlify
3. **Essayez de créer un nouveau site** sur Netlify et reconnectez le repository
4. **Contactez le support Netlify** avec les logs de déploiement

## 📝 Prochaines Étapes

1. Vérifiez la configuration (netlify.toml, structure des fichiers)
2. Vérifiez les build settings dans Netlify
3. Redéployez avec cache clear
4. Testez l'URL `/api/recipes` directement
5. Vérifiez les logs pour des erreurs spécifiques

**Dites-moi ce que vous trouvez dans les logs de déploiement !** 🔍

