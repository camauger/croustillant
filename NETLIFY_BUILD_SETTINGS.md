# ⚙️ Configuration Netlify - Paramètres de Build

## 📋 Paramètres de Build à Configurer

Lorsque vous créez un nouveau site sur Netlify, configurez ces paramètres :

### 1. Build Settings

Dans la section **"Build settings"** :

| Paramètre | Valeur |
|-----------|--------|
| **Build command** | `echo "No build needed"` |
| **Publish directory** | `public` |
| **Functions directory** | `netlify/functions` |

**Note :** Ces valeurs correspondent à votre `netlify.toml`, donc Netlify les détectera automatiquement. Mais vous pouvez les vérifier/ajuster manuellement.

### 2. Variables d'Environnement

Dans **"Site settings" → "Environment variables"**, ajoutez :

| Variable | Valeur | Description |
|----------|--------|-------------|
| `NETLIFY_DATABASE_URL` | `postgresql://neondb_owner:npg_O9ZpGfCeihI3@ep-mute-water-aeo7lu3c-pooler.c-2.us-east-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require` | Votre chaîne de connexion Neon (remplacez par la vôtre si différente) |

**Note :** Le code supporte aussi `DATABASE_URL` comme alternative, mais `NETLIFY_DATABASE_URL` est utilisé en priorité.

**Important :**
- ⚠️ Remplacez la valeur ci-dessus par **votre vraie** chaîne de connexion Neon
- ✅ Utilisez la chaîne de connexion avec `-pooler` pour de meilleures performances
- ✅ Incluez `?sslmode=require` pour la sécurité

### 3. Python Runtime

Le runtime Python est automatiquement détecté depuis `netlify/functions/runtime.txt` :
- **Version** : `python-3.11`

**Pas besoin de configurer manuellement** - Netlify le détecte automatiquement.

### 4. Dependencies

Les dépendances Python sont installées automatiquement depuis `netlify/functions/requirements.txt` :
- `psycopg2-binary==2.9.9`
- `python-dotenv==1.0.0`

**Pas besoin de configurer manuellement** - Netlify les installe automatiquement.

## 🚀 Guide de Déploiement Étape par Étape

### Étape 1 : Préparer le Repository

```bash
# Vérifier que tout est commité
git status

# Si nécessaire, ajouter et commiter
git add .
git commit -m "Ready for Netlify deployment"
git push origin main
```

### Étape 2 : Créer le Site sur Netlify

1. Allez sur [netlify.com](https://netlify.com)
2. Cliquez **"Add new site"** → **"Import an existing project"**
3. Choisissez votre provider Git (GitHub, GitLab, Bitbucket)
4. Autorisez Netlify à accéder à votre repository
5. Sélectionnez votre repository `croustillant`

### Étape 3 : Configurer les Build Settings

Netlify devrait **détecter automatiquement** les paramètres depuis `netlify.toml`, mais vérifiez :

1. Cliquez sur **"Show advanced"** pour voir tous les paramètres
2. Vérifiez que :
   - **Base directory** : (laisser vide)
   - **Build command** : `echo "No build needed"`
   - **Publish directory** : `public`
   - **Functions directory** : `netlify/functions`

### Étape 4 : Ajouter les Variables d'Environnement

**Avant de déployer**, ajoutez la variable d'environnement :

1. Cliquez sur **"Show advanced"** → **"New variable"**
2. Ajoutez :
   - **Key** : `NETLIFY_DATABASE_URL`
   - **Value** : Votre chaîne de connexion Neon complète
3. Cliquez **"Add variable"**

**Note :** Vous pouvez aussi utiliser `DATABASE_URL` si vous préférez, le code supporte les deux.

**Important :** Faites cela **avant** de cliquer "Deploy site" pour que le premier déploiement fonctionne.

### Étape 5 : Déployer

1. Cliquez **"Deploy site"**
2. Attendez 1-2 minutes
3. Vous verrez les logs de déploiement en temps réel

### Étape 6 : Vérifier le Déploiement

Une fois déployé :

1. **Vérifiez l'URL** : Votre site sera disponible sur `https://random-name-12345.netlify.app`
2. **Testez les fonctions** :
   - Visitez l'URL
   - Essayez d'ajouter une recette
   - Vérifiez que les recettes s'affichent

## 🔍 Vérification Post-Déploiement

### Vérifier les Functions

1. Dans Netlify Dashboard, allez dans **"Functions"**
2. Vous devriez voir :
   - `recipes` (GET, POST)
   - `recipe-detail` (GET, PUT, DELETE)
   - `shopping-list` (POST)

### Vérifier les Logs

1. Dans Netlify Dashboard, allez dans **"Functions"**
2. Cliquez sur une fonction
3. Vérifiez les logs pour des erreurs

### Tester l'API

```bash
# Tester l'endpoint recipes
curl https://your-site.netlify.app/api/recipes
```

Vous devriez recevoir une réponse JSON avec les recettes (même si la liste est vide).

## ⚙️ Paramètres Avancés (Optionnels)

### Branch Deploys

Dans **"Site settings" → "Build & deploy" → "Continuous Deployment"** :

- **Production branch** : `main` (ou `master`)
- **Branch deploys** : Activer si vous voulez déployer d'autres branches

### Build Hooks

Pour déclencher des déploiements manuels via API.

### Custom Domain

Dans **"Domain settings"** :
- Ajoutez votre domaine personnalisé
- Configurez le DNS selon les instructions Netlify
- SSL est automatique et gratuit

## 🐛 Dépannage

### Erreur : "Function not found"

**Cause :** Variable `NETLIFY_DATABASE_URL` (ou `DATABASE_URL`) manquante ou incorrecte

**Solution :**
1. Vérifiez que `NETLIFY_DATABASE_URL` est définie dans Environment variables
2. Vérifiez que la valeur est correcte (copiez depuis Neon)
3. Redéployez le site

### Erreur : "Module not found"

**Cause :** Dépendances Python non installées

**Solution :**
1. Vérifiez que `requirements.txt` existe dans `netlify/functions/`
2. Vérifiez les logs de build pour voir les erreurs d'installation
3. Vérifiez que `runtime.txt` existe et contient `python-3.11`

### Erreur : "Database connection failed"

**Cause :** `NETLIFY_DATABASE_URL` (ou `DATABASE_URL`) incorrecte ou base de données inaccessible

**Solution :**
1. Testez la connexion dans Neon SQL Editor
2. Vérifiez que la chaîne de connexion inclut `?sslmode=require`
3. Vérifiez que votre projet Neon est actif (non suspendu)
4. Vérifiez que la variable d'environnement est bien définie dans Netlify

## 📝 Checklist de Déploiement

- [ ] Repository poussé vers GitHub/GitLab
- [ ] Site créé sur Netlify
- [ ] Build settings configurés (ou détectés automatiquement)
- [ ] Variable `NETLIFY_DATABASE_URL` (ou `DATABASE_URL`) ajoutée
- [ ] Déploiement réussi
- [ ] Functions visibles dans le dashboard
- [ ] Site accessible et fonctionnel
- [ ] Test d'ajout de recette réussi

## 🎉 Une Fois Configuré

Après le premier déploiement :
- ✅ Les déploiements futurs seront automatiques (à chaque push)
- ✅ Les fonctions Python fonctionneront en production
- ✅ Vous pourrez ajouter/modifier des recettes
- ✅ Tout fonctionnera parfaitement !

## 💡 Astuce

**Pour tester rapidement :**
1. Déployez d'abord avec les paramètres de base
2. Vérifiez les logs si quelque chose ne fonctionne pas
3. Ajustez les variables d'environnement si nécessaire
4. Redéployez

**Tout est prêt !** 🚀

