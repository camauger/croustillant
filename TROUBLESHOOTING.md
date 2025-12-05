# 🔧 Guide de Dépannage - Erreur JSON "Function n..."

## Problème

Erreur lors du démarrage de `netlify dev` :
```
Erreur: Unexpected token 'F', "Function n"... is not valid JSON
```

## Causes Possibles

1. **Cache Netlify corrompu** - Fichiers de configuration corrompus dans `.netlify/`
2. **Problème de découverte des fonctions** - Netlify CLI ne peut pas parser la configuration des fonctions
3. **Conflit avec Edge Functions** - Netlify CLI essaie de configurer Edge Functions même si elles sont désactivées

## Solutions

### Solution 1: Nettoyer complètement le cache

```bash
# Nettoyer le cache Netlify
just clear-netlify-cache

# Nettoyer le cache Deno
just clear-deno-cache

# Supprimer manuellement si nécessaire
rm -rf .netlify
# ou sur Windows PowerShell:
Remove-Item -Recurse -Force .netlify
```

### Solution 2: Vérifier la configuration

```bash
# Vérifier la configuration des fonctions
just debug-functions

# Vérifier que netlify.toml est valide
# (il devrait être en TOML, pas JSON)
```

### Solution 3: Utiliser npx directement avec debug

```bash
# Tester avec npx et voir les logs détaillés
npx netlify-cli dev --debug

# Ou avec des logs encore plus détaillés
NETLIFY_DEBUG=true npx netlify-cli dev
```

### Solution 4: Vérifier les fichiers de fonctions

Assurez-vous que tous les fichiers Python ont:
- ✅ Fonction `handler(event, context)` définie
- ✅ Pas de caractères invisibles ou BOM
- ✅ Encodage UTF-8

```bash
# Vérifier les handlers
grep -l "def handler" netlify/functions/*.py

# Vérifier l'encodage (sur Linux/Mac)
file netlify/functions/*.py
```

### Solution 5: Tester avec une version spécifique de Netlify CLI

```bash
# Installer une version spécifique
npm install -g netlify-cli@12.0.0

# Ou utiliser npx avec une version spécifique
npx netlify-cli@12.0.0 dev
```

### Solution 6: Contourner l'erreur (temporaire)

Si l'erreur persiste mais que le serveur statique fonctionne:

1. Le serveur statique devrait être accessible sur `http://localhost:8888`
2. Les fonctions Python ne fonctionneront pas localement mais fonctionneront en production
3. Pour tester les fonctions, déployez sur Netlify

## Vérification de la Configuration

Votre configuration devrait avoir:

```toml
[build]
  functions = "netlify/functions"

[[redirects]]
  from = "/api/*"
  to = "/.netlify/functions/:splat"
  status = 200
```

Et dans `netlify/functions/`:
- ✅ `runtime.txt` avec `python-3.11`
- ✅ `requirements.txt` avec les dépendances
- ✅ Fichiers Python avec `handler(event, context)`

## Test de la Configuration

```bash
# 1. Vérifier les fonctions
just debug-functions

# 2. Nettoyer le cache
just clear-netlify-cache

# 3. Essayer de démarrer
just dev
```

## Si Rien Ne Fonctionne

1. **Déployer directement sur Netlify** - Les fonctions Python fonctionneront en production même si elles ne fonctionnent pas localement
2. **Utiliser le serveur statique uniquement** - Pour tester le frontend
3. **Contacter le support Netlify** - Avec les logs de `netlify dev --debug`

## Notes Importantes

- ⚠️ L'erreur Deno/Edge Functions n'empêche **pas** le serveur statique de fonctionner
- ✅ Les fonctions Python fonctionneront **toujours** en production sur Netlify
- 🔧 Le problème est spécifique à l'environnement de développement local sur Windows

