# 🔧 Correction du Fichier .env

## Problème Détecté

Le fichier `.env` existe mais `DATABASE_URL` n'est pas défini ou est incorrect.

## Solution Immédiate

### Option 1 : Créer/Corriger le fichier .env (PowerShell)

```powershell
# Créer le fichier .env avec votre chaîne de connexion Neon
@"
DATABASE_URL=postgresql://neondb_owner:npg_O9ZpGfCeihI3@ep-mute-water-aeo7lu3c-pooler.c-2.us-east-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require
"@ | Out-File -FilePath .env -Encoding utf8

# Vérifier que c'est bien créé
Get-Content .env
```

### Option 2 : Éditer Manuellement

1. Ouvrez le fichier `.env` dans votre éditeur
2. Ajoutez cette ligne (remplacez par votre vraie chaîne de connexion si différente) :

```env
DATABASE_URL=postgresql://neondb_owner:npg_O9ZpGfCeihI3@ep-mute-water-aeo7lu3c-pooler.c-2.us-east-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require
```

3. Sauvegardez le fichier

### Option 3 : Utiliser la Commande Just

```bash
# Si vous avez une commande setup dans justfile
just setup
```

## Vérification

Après avoir créé/corrigé le fichier `.env`, vérifiez :

```powershell
# Vérifier que DATABASE_URL est défini
Get-Content .env | Select-String "DATABASE_URL"
```

Vous devriez voir :
```
DATABASE_URL=postgresql://...
```

## Ensuite

1. **Redémarrer le serveur** :
   ```powershell
   just dev-ps
   ```

2. **Tester** :
   - Ouvrez `http://localhost:8888`
   - Les fonctions devraient maintenant fonctionner (si le serveur démarre correctement)

## Important

- ⚠️ Ne commitez **JAMAIS** le fichier `.env` dans Git
- ✅ Le fichier `.env` devrait être dans `.gitignore`
- ✅ Pour la production, ajoutez `DATABASE_URL` dans Netlify Dashboard

## Si Ça Ne Fonctionne Toujours Pas

1. Vérifiez que votre chaîne de connexion Neon est correcte
2. Testez la connexion dans Neon SQL Editor
3. Vérifiez que le schéma de base de données est créé (`neon-schema.sql`)
4. Déployez sur Netlify - ça fonctionnera en production !

