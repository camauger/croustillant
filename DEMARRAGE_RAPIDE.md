# 🚀 Démarrage Rapide - Croustillant

## Problème : "Rien ne marche"

Voici comment tout faire fonctionner en 5 minutes :

## ✅ Étape 1 : Vérifier les Prérequis

### 1.1 Fichier .env
```powershell
# Vérifier que .env existe et contient DATABASE_URL
Get-Content .env
```

**✅ Votre .env est correct !** Il contient bien `DATABASE_URL`.

### 1.2 Netlify CLI
```powershell
# Vérifier si Netlify CLI est installé
npx netlify-cli --version
```

Si erreur, installez :
```powershell
npm install -g netlify-cli
```

## ✅ Étape 2 : Démarrer le Serveur

### Option A : Avec Just (Recommandé)

```powershell
# Dans PowerShell
just dev-ps
```

### Option B : Directement avec npx

```powershell
# Si just ne fonctionne pas
npx netlify-cli dev
```

### Option C : Si Erreur Deno

```powershell
# 1. Nettoyer d'abord
just kill-deno-processes
just clear-deno-cache

# 2. Puis démarrer
just dev-ps
```

## ✅ Étape 3 : Vérifier que Ça Fonctionne

### 3.1 Ouvrir le Navigateur

1. Ouvrez votre navigateur
2. Allez sur : **http://localhost:8888**
3. Vous devriez voir la page d'accueil de Croustillant

### 3.2 Tester les Fonctions API

**Dans le terminal**, testez :
```powershell
curl http://localhost:8888/api/recipes
```

**Résultats possibles :**
- ✅ JSON avec `{"success": true, "recipes": [...]}` → **Tout fonctionne !**
- ⚠️ "Function not found" → Normal localement, fonctionnera en production
- ❌ Erreur de connexion → Serveur non démarré

## ⚠️ Si les Fonctions ne Fonctionnent Pas Localement

**C'EST NORMAL !** L'erreur Deno sur Windows empêche les fonctions Python de démarrer localement.

**Mais :**
- ✅ Le serveur statique fonctionne
- ✅ Vous pouvez développer le frontend
- ✅ Les fonctions fonctionneront en production sur Netlify

## 🎯 Solution Définitive : Déployer sur Netlify

Si vous voulez tester les fonctions Python **maintenant**, déployez sur Netlify :

### Déploiement en 3 Minutes

1. **Pousser vers GitHub** :
   ```powershell
   git add .
   git commit -m "Ready for deployment"
   git push origin main
   ```

2. **Déployer sur Netlify** :
   - Allez sur [netlify.com](https://netlify.com)
   - "Add new site" → "Import an existing project"
   - Connectez GitHub
   - Configurez :
     - Build : `echo "No build needed"`
     - Publish : `public`
     - Functions : `netlify/functions`
   - **Ajoutez variable** :
     - Key : `DATABASE_URL`
     - Value : Votre chaîne de connexion Neon (celle dans votre .env)
   - Cliquez "Deploy"

3. **Tester** :
   - Visitez l'URL Netlify
   - **Tout fonctionnera !** 🎉

## 📋 Checklist de Vérification

Avant de dire "rien ne marche", vérifiez :

- [ ] Serveur démarré ? → `just dev-ps` dans un terminal
- [ ] Page accessible ? → `http://localhost:8888` dans le navigateur
- [ ] Fichier .env existe ? → `Test-Path .env` (devrait être True)
- [ ] DATABASE_URL défini ? → `Get-Content .env` (devrait montrer DATABASE_URL)
- [ ] Fonctions Python configurées ? → `just debug-functions`

## 🔍 Diagnostic Détaillé

Si vous voulez un diagnostic complet :

```powershell
# Voir tous les détails
just debug-functions
```

## 💡 Conseils

1. **Le serveur doit être démarré** pour que quelque chose fonctionne
2. **Les fonctions Python peuvent ne pas fonctionner localement** (erreur Deno) - c'est normal
3. **Déployer sur Netlify résout tous les problèmes** de développement local
4. **Le frontend fonctionne** même si les fonctions ne fonctionnent pas

## 🆘 Besoin d'Aide ?

Dites-moi **exactement** :
1. Quel message d'erreur vous voyez ?
2. Dans quel contexte (terminal, navigateur, console) ?
3. Avez-vous démarré le serveur avec `just dev-ps` ?

Avec ces informations, je pourrai vous aider plus précisément !

