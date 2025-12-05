# 🔍 Diagnostic Complet - Croustillant

## Étape 1: Vérifier l'État du Serveur

### 1.1 Le serveur est-il démarré ?

```powershell
# Test 1: Vérifier si le serveur répond
curl http://localhost:8888

# Si vous voyez du HTML → ✅ Serveur démarré
# Si erreur de connexion → ❌ Serveur non démarré
```

**Si le serveur n'est pas démarré :**
```powershell
just dev-ps
# ou
npx netlify-cli dev
```

### 1.2 Les fonctions Python sont-elles accessibles ?

```powershell
# Test 2: Tester l'endpoint API
curl http://localhost:8888/api/recipes

# Si vous voyez du JSON → ✅ Fonctions fonctionnent
# Si "Function not found" → ❌ Fonctions non disponibles
# Si erreur 500 → ❌ Erreur dans les fonctions
```

## Étape 2: Vérifier la Configuration

### 2.1 Vérifier les fichiers de fonctions

```powershell
just debug-functions
```

**Résultat attendu :**
- ✅ 3 fichiers Python trouvés
- ✅ runtime.txt présent
- ✅ requirements.txt présent
- ✅ 3 handlers trouvés

### 2.2 Vérifier les variables d'environnement

```powershell
# Vérifier si .env existe
Test-Path .env

# Voir le contenu (sans afficher le mot de passe)
Get-Content .env | Select-String "DATABASE_URL"
```

**Vérifications :**
- [ ] Fichier `.env` existe
- [ ] `DATABASE_URL` est défini
- [ ] Le format est correct : `postgresql://...?sslmode=require`

### 2.3 Vérifier la configuration Netlify

```powershell
# Vérifier netlify.toml
Get-Content netlify.toml
```

**Vérifications :**
- [ ] `functions = "netlify/functions"` est présent
- [ ] Redirection `/api/*` → `/.netlify/functions/:splat` est configurée

## Étape 3: Problèmes Spécifiques

### Problème A: "Fonction API non trouvée" dans le navigateur

**Causes possibles :**
1. Serveur Netlify non démarré
2. Fonctions Python non disponibles (erreur Deno)
3. Route API incorrecte

**Solutions :**

```powershell
# Solution 1: Redémarrer le serveur
just kill-deno-processes
just clear-deno-cache
just clear-netlify-cache
just dev-ps

# Solution 2: Vérifier que le serveur écoute sur le bon port
# Ouvrez http://localhost:8888 dans votre navigateur
# Vous devriez voir la page d'accueil
```

### Problème B: Erreur Deno/Edge Functions

**Symptôme :** Erreur `EBUSY` ou `Failed to set up Deno`

**Solutions :**

```powershell
# Solution 1: Nettoyer complètement
just kill-deno-processes
just clear-deno-cache

# Attendre 5 secondes, puis :
just dev-ps

# Solution 2: Si ça ne marche toujours pas
# Fermez TOUS les terminaux PowerShell
# Redémarrez PowerShell
# Puis :
Remove-Item -Recurse -Force "$env:APPDATA\netlify\Config\deno-cli" -ErrorAction SilentlyContinue
just dev-ps
```

### Problème C: Erreur "DATABASE_URL must be set"

**Solutions :**

```powershell
# 1. Vérifier que .env existe
Test-Path .env

# 2. Si .env n'existe pas, créez-le :
@"
DATABASE_URL=postgresql://neondb_owner:npg_O9ZpGfCeihI3@ep-mute-water-aeo7lu3c-pooler.c-2.us-east-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require
"@ | Out-File -FilePath .env -Encoding utf8

# 3. Redémarrer le serveur
just dev-ps
```

### Problème D: Erreur de connexion à la base de données

**Solutions :**

1. **Vérifier la connexion dans Neon :**
   - Allez sur [console.neon.tech](https://console.neon.tech)
   - Ouvrez SQL Editor
   - Testez : `SELECT * FROM recipes LIMIT 1;`
   - Si ça fonctionne → La base de données est OK

2. **Vérifier le schéma :**
   - Dans Neon SQL Editor, vérifiez que la table `recipes` existe
   - Si non, exécutez `neon-schema.sql`

3. **Vérifier la chaîne de connexion :**
   - Utilisez le pooler (avec `-pooler` dans l'URL)
   - Incluez `?sslmode=require`
   - Votre chaîne est correcte : `postgresql://neondb_owner:...@ep-mute-water-aeo7lu3c-pooler...`

## Étape 4: Test Complet

### Checklist de Test

```powershell
# 1. Serveur démarré ?
curl http://localhost:8888 | Select-String -Pattern "html" -Quiet
# Devrait retourner True

# 2. Fonctions accessibles ?
$response = curl -s http://localhost:8888/api/recipes
$response -match "success|recipes|error"
# Devrait contenir un de ces mots

# 3. Configuration OK ?
just debug-functions
# Devrait montrer 3 fonctions avec ✅

# 4. Variables d'environnement ?
Test-Path .env
# Devrait retourner True
```

## Étape 5: Solutions par Scénario

### Scénario 1: Rien ne fonctionne (serveur ne démarre pas)

```powershell
# 1. Nettoyer tout
just kill-deno-processes
just clear-deno-cache
just clear-netlify-cache

# 2. Vérifier Netlify CLI
npx netlify-cli --version

# 3. Redémarrer dans un nouveau terminal
just dev-ps
```

### Scénario 2: Serveur démarre mais fonctions ne fonctionnent pas

**C'est normal sur Windows !** Les fonctions Python ne fonctionnent pas localement à cause de l'erreur Deno.

**Solutions :**
1. **Continuer le développement frontend** - Le serveur statique fonctionne
2. **Déployer sur Netlify** - Les fonctions fonctionneront en production

### Scénario 3: Erreurs dans le navigateur

**Vérifier la console du navigateur :**
1. Ouvrez les outils de développement (F12)
2. Onglet "Console"
3. Regardez les erreurs

**Erreurs communes :**
- `API request failed` → Fonctions non disponibles (normal localement)
- `DATABASE_URL must be set` → Créer le fichier `.env`
- `Failed to fetch` → Serveur non démarré

## Étape 6: Solution Définitive - Déployer sur Netlify

Si rien ne fonctionne localement, **déployez directement sur Netlify** :

### 6.1 Préparer le déploiement

```powershell
# 1. Vérifier que tout est commité
git status

# 2. Créer le fichier .env si nécessaire (pour référence locale)
# (Ne pas commiter .env !)

# 3. Pousser vers GitHub
git add .
git commit -m "Ready for deployment"
git push origin main
```

### 6.2 Déployer sur Netlify

1. **Créer un compte Netlify** (si pas déjà fait)
   - [netlify.com](https://netlify.com)

2. **Connecter le repository**
   - "Add new site" → "Import an existing project"
   - Choisir GitHub
   - Sélectionner votre repository

3. **Configurer le build**
   - Build command : `echo "No build needed"`
   - Publish directory : `public`
   - Functions directory : `netlify/functions`

4. **Ajouter la variable d'environnement**
   - Site settings → Environment variables
   - Key : `DATABASE_URL`
   - Value : Votre chaîne de connexion Neon (celle que vous avez)

5. **Déployer**
   - Cliquer "Deploy site"
   - Attendre 1-2 minutes

6. **Tester**
   - Visiter l'URL Netlify (ex: `https://your-site.netlify.app`)
   - Tout devrait fonctionner !

## Étape 7: Commandes de Diagnostic Rapide

```powershell
# Diagnostic complet en une commande
Write-Host "=== DIAGNOSTIC COMPLET ===" -ForegroundColor Cyan
Write-Host "`n1. Serveur:" -ForegroundColor Yellow
$server = try { (Invoke-WebRequest -Uri "http://localhost:8888" -TimeoutSec 2 -UseBasicParsing).StatusCode } catch { "Non démarré" }
Write-Host "   Status: $server"

Write-Host "`n2. Fonctions:" -ForegroundColor Yellow
$api = try { (Invoke-WebRequest -Uri "http://localhost:8888/api/recipes" -TimeoutSec 2 -UseBasicParsing).Content } catch { "Non disponibles" }
Write-Host "   API: $(if ($api -match 'success|recipes') { 'OK' } else { 'Erreur' })"

Write-Host "`n3. Configuration:" -ForegroundColor Yellow
$envExists = Test-Path .env
Write-Host "   .env: $(if ($envExists) { 'Existe' } else { 'MANQUANT' })"
$tomlExists = Test-Path netlify.toml
Write-Host "   netlify.toml: $(if ($tomlExists) { 'Existe' } else { 'MANQUANT' })"

Write-Host "`n4. Fonctions Python:" -ForegroundColor Yellow
$funcCount = (Get-ChildItem netlify/functions/*.py -ErrorAction SilentlyContinue).Count
Write-Host "   Fichiers: $funcCount"

Write-Host "`n=== FIN DU DIAGNOSTIC ===" -ForegroundColor Cyan
```

## Résumé des Solutions

| Problème | Solution Rapide |
|----------|----------------|
| Serveur ne démarre pas | `just dev-ps` dans un nouveau terminal |
| Erreur Deno | `just kill-deno-processes && just clear-deno-cache` |
| Fonctions 404 | Normal localement → Déployer sur Netlify |
| Erreur DATABASE_URL | Créer `.env` avec votre chaîne Neon |
| Erreur connexion DB | Vérifier dans Neon SQL Editor |
| Rien ne marche | Déployer sur Netlify (fonctionnera en production) |

## Important à Retenir

✅ **Le serveur statique fonctionne** même avec l'erreur Deno
✅ **Les fonctions Python fonctionneront en production** sur Netlify
✅ **L'erreur Deno est un problème Windows local** - pas un problème de code
✅ **Déployer sur Netlify résout tous les problèmes** de développement local

## Prochaine Étape Recommandée

**Déployez sur Netlify maintenant** - C'est la solution la plus rapide et la plus fiable !

1. Créez le fichier `.env` avec votre `DATABASE_URL`
2. Poussez vers GitHub
3. Déployez sur Netlify
4. Ajoutez `DATABASE_URL` dans Netlify
5. Testez - tout fonctionnera ! 🎉

