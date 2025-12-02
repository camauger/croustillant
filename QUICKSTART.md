# 🚀 Quick Start Guide - Croustillant Modern Version

Get your modernized Croustillant app running in 10 minutes!

## What You'll Need
- ✅ GitHub/GitLab account
- ✅ Netlify account (free)
- ✅ Supabase account (free)
- ✅ 10 minutes

## Step 1: Set Up Supabase (3 minutes)

### 1.1 Create Project
1. Go to [supabase.com](https://supabase.com) and sign up
2. Click **"New Project"**
3. Enter:
   - **Name**: `croustillant`
   - **Database Password**: Create a strong password (save it!)
   - **Region**: Choose closest to you
4. Click **"Create new project"** and wait 1-2 minutes

### 1.2 Create Database
1. Once project is ready, click **"SQL Editor"** in left sidebar
2. Open `supabase-schema.sql` from your project
3. Copy entire contents
4. Paste into SQL Editor
5. Click **"Run"**
6. You should see "Success. No rows returned"

### 1.3 Get API Keys
1. Go to **"Project Settings"** (gear icon in sidebar)
2. Click **"API"** tab
3. Copy these two values (you'll need them):
   - **Project URL**: `https://xxxxxxxxxxxxx.supabase.co`
   - **anon/public key**: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`

✅ **Supabase is ready!**

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
7. Add environment variables:
   - Variable 1:
     - **Key**: `SUPABASE_URL`
     - **Value**: Your Supabase Project URL
   - Variable 2:
     - **Key**: `SUPABASE_KEY`
     - **Value**: Your Supabase anon key
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
```bash
# 1. Create .env file in project root
echo "SUPABASE_URL=your-project-url" > .env
echo "SUPABASE_SERVICE_KEY=your-service-key" >> .env
echo "SQLITE_DB=recipes.db" >> .env

# 2. Install dependencies
cd migration
pip install -r requirements.txt

# 3. Run migration
python migrate-to-supabase.py
```

The script will:
- Read all recipes from SQLite
- Upload to Supabase
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
2. Verify `SUPABASE_URL` and `SUPABASE_KEY` are set correctly
3. Click **"Deploy site"** to redeploy

### Can't create recipes
**Fix**: Check Supabase database
1. Go to Supabase dashboard
2. **Table Editor** → Verify `recipes` table exists
3. If not, re-run `supabase-schema.sql` in SQL Editor

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
- **Technical Issues**: Check Netlify and Supabase logs
- **Feature Requests**: Open an issue on GitHub

## Success! 🎉

You now have a modern, scalable recipe app running on:
- ✅ Netlify (99.9% uptime)
- ✅ Supabase (managed PostgreSQL)
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
