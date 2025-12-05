# 🚀 Quick Start Guide - Croustillant Modern Version

Get your modernized Croustillant app running in 10 minutes!

## What You'll Need
- ✅ GitHub/GitLab account
- ✅ Netlify account (free)
- ✅ Neon account (free, no credit card required)
- ✅ 10 minutes

## Step 1: Set Up Neon DB (3 minutes)

### 1.1 Create Project
1. Go to [neon.tech](https://neon.tech) and sign up (free, no credit card)
2. Click **"Create Project"**
3. Enter:
   - **Name**: `croustillant`
   - **Region**: Choose closest to you (e.g., US East, EU West)
   - **PostgreSQL version**: 16 (latest)
4. Click **"Create"** and wait 30 seconds

### 1.2 Create Database Schema
1. Once project is ready, click **"SQL Editor"** in left sidebar
2. Open `neon-schema.sql` from your project
3. Copy entire contents
4. Paste into Neon SQL Editor
5. Click **"Run"**
6. You should see "Query executed successfully"

### 1.3 Get Connection String
1. Go to **"Dashboard"** in Neon
2. Click **"Connection Details"**
3. Copy the **Connection String**
4. It will look like: `postgresql://user:password@ep-xxxxx-xxxxx.region.aws.neon.tech/neondb?sslmode=require`
5. **Save this** - you'll need it for Netlify!

✅ **Neon DB is ready!**

## Step 2: Deploy to Netlify (5 minutes)

### 2.1 Push Code to GitHub
```bash
# If not already in a Git repo
git init
git add .
git commit -m "Initial commit - modernized version"

# Create repo on GitHub, then:
git remote add origin https://github.com/yourusername/croustillant.git
git push -u origin main
```

### 2.2 Connect to Netlify
1. Go to [netlify.com](https://netlify.com) and sign up
2. Click **"Add new site"** → **"Import an existing project"**
3. Choose **GitHub** (or your Git provider)
4. Select your `croustillant` repository
5. Configure build settings:
   - **Build command**: `echo 'No build needed'`
   - **Publish directory**: `public`
   - **Functions directory**: `netlify/functions`
6. Click **"Show advanced"** → **"New variable"**
7. Add environment variable:
   - **Key**: `DATABASE_URL`
   - **Value**: Your Neon connection string (from step 1.3)
8. Click **"Deploy site"**

### 2.3 Wait for Deployment
- Watch the deploy log (1-2 minutes)
- When complete, you'll see: **"Site is live"**
- Click the URL (like `https://random-name-12345.netlify.app`)

✅ **Your app is live!**

## Step 3: Test Your App (2 minutes)

### 3.1 Add Your First Recipe
1. Click **"Ajouter"** in navigation
2. Fill in the form:
   - **Titre**: `Pâtes Carbonara`
   - **Temps de préparation**: `10 minutes`
   - **Temps de cuisson**: `15 minutes`
   - **Rendement**: `4 portions`
3. Add ingredients:
   - `Spaghetti`, `400`, `g`
   - `Bacon`, `200`, `g`
   - `Oeufs`, `4`, (leave unit empty)
   - `Parmesan`, `100`, `g`
4. Add instructions:
   - `Cuire les pâtes al dente`
   - `Faire revenir le bacon`
   - `Mélanger avec les oeufs et le parmesan`
5. Click **"Créer la recette"**

### 3.2 Test Selection and Shopping List
1. Go to **"Recettes"** (home page)
2. Click **"+ Ajouter à ma sélection"** on your recipe
3. Click **"Ma sélection"** in navigation
4. Click **"📋 Générer la liste de courses"**
5. See your ingredients organized by category!

✅ **Everything works!**

## Optional: Migrate Existing Data

If you have recipes in the old SQLite database:

### Migration Steps
See [NEON_MIGRATION.md](NEON_MIGRATION.md) for detailed migration instructions from Supabase or SQLite to Neon DB.

For SQLite to Neon:
```bash
# 1. Create .env file in project root
echo "DATABASE_URL=your-neon-connection-string" > .env
echo "SQLITE_DB=recipes.db" >> .env

# 2. Use pg_dump or create a custom migration script
# See NEON_MIGRATION.md for detailed instructions
```

The migration process will:
- Read all recipes from SQLite
- Transform data to PostgreSQL format
- Insert into Neon database
- Report success/failures

✅ **Migration complete!**

## Customize Your Site

### Change Site Name
1. In Netlify dashboard
2. **Site settings** → **General** → **Site details**
3. Click **"Change site name"**
4. Enter new name (e.g., `my-recipes`)
5. Your URL becomes: `https://my-recipes.netlify.app`

### Add Custom Domain
1. In Netlify dashboard
2. **Domain settings** → **Add custom domain**
3. Follow instructions to configure DNS
4. Free SSL certificate included!

## What's Next?

### Learn More
- **Full deployment guide**: See [DEPLOYMENT.md](DEPLOYMENT.md)
- **Technical documentation**: See [README-MODERN.md](README-MODERN.md)
- **For developers**: See [CLAUDE.MD](CLAUDE.MD)

### Customize Your App
- Edit styles in `public/css/style.css`
- Modify colors by changing CSS variables at top of file
- Add more ingredient categories in `netlify/functions/utils/ingredients.py`

### Add Features
Check out planned features in README-MODERN.md:
- User authentication
- Recipe ratings
- Meal planning calendar
- Dark mode
- And more!

## Troubleshooting

### App shows "Loading..." forever
**Fix**: Check environment variables in Netlify
1. Netlify dashboard → **Site settings** → **Environment variables**
2. Verify `DATABASE_URL` is set correctly with your Neon connection string
3. Make sure it includes `?sslmode=require`
4. Click **"Deploy site"** to redeploy

### Can't create recipes
**Fix**: Check Neon database
1. Go to Neon dashboard
2. **SQL Editor** → Run `SELECT * FROM recipes LIMIT 1;` to verify table exists
3. If not, re-run `neon-schema.sql` in SQL Editor
4. Verify your `DATABASE_URL` is correct

### Functions returning errors
**Fix**: Check Netlify function logs
1. Netlify dashboard → **Functions** tab
2. Click on function name
3. View error logs
4. Common issues:
   - Missing environment variables
   - Python dependencies not installed (check `requirements.txt`)

### Shopping list not categorizing
**Check**: Ingredient names must match keywords
- Edit `netlify/functions/utils/ingredients.py`
- Add keywords to `INGREDIENT_CATEGORIES`
- Redeploy to Netlify

## Need Help?

- **Documentation Issues**: Check DEPLOYMENT.md
- **Technical Issues**: Check Netlify and Neon logs
- **Migration Help**: See NEON_MIGRATION.md
- **Feature Requests**: Open an issue on GitHub

## Success! 🎉

You now have a modern, scalable recipe app running on:
- ✅ Netlify (99.9% uptime)
- ✅ Neon DB (serverless PostgreSQL)
- ✅ Free tier (suitable for personal use)
- ✅ HTTPS enabled
- ✅ Global CDN
- ✅ Serverless architecture

**Enjoy your new recipe management app!**

---

**Total time**: ~10 minutes
**Cost**: $0 (free tier)
**Scaling**: Automatic
**Maintenance**: Minimal
