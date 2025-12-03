# 🔄 Migration Guide: Supabase to Neon DB

This guide will help you migrate your Croustillant application from Supabase to Neon DB.

## 📋 Prerequisites

- Existing Croustillant application using Supabase
- Access to your Supabase project dashboard
- A Neon account (free tier is sufficient)

## 🎯 Why Migrate to Neon DB?

### Advantages of Neon DB:
- ✅ **True Serverless PostgreSQL**: Pay only for what you use
- ✅ **Faster Cold Starts**: Database wakes up in <500ms
- ✅ **Branching**: Create database branches like Git
- ✅ **Generous Free Tier**: 0.5 GB storage, 100 compute hours/month
- ✅ **Autoscaling**: Automatically scales with your workload
- ✅ **Standard PostgreSQL**: No vendor lock-in, use standard tools

## 🚀 Migration Steps

### Step 1: Export Data from Supabase

#### Option A: Using Supabase Dashboard (Recommended for small datasets)

1. Go to your Supabase project dashboard
2. Click on **"SQL Editor"**
3. Run this query to export your recipes:

```sql
SELECT * FROM recipes ORDER BY id;
```

4. Click the **"Results"** section
5. Click **"Download as CSV"**
6. Save the file as `recipes_export.csv`

#### Option B: Using pg_dump (Recommended for larger datasets)

1. Get your Supabase connection string:
   - Go to **Project Settings** → **Database**
   - Copy the **Connection String** (Direct connection)

2. Export your data:

```bash
pg_dump "postgresql://postgres:[YOUR-PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres" \
  --table=recipes \
  --data-only \
  --column-inserts \
  > recipes_export.sql
```

### Step 2: Set Up Neon DB

1. **Create a Neon Account**
   - Go to [https://neon.tech](https://neon.tech)
   - Sign up for free (no credit card required)

2. **Create a New Project**
   - Click **"Create Project"**
   - Name: `croustillant` (or your preferred name)
   - Region: Choose closest to your users (e.g., US East, EU West)
   - PostgreSQL version: 16 (latest)
   - Click **"Create"**

3. **Run the Schema**
   - Click **"SQL Editor"** in the left sidebar
   - Open your local `neon-schema.sql` file
   - Copy the entire content
   - Paste into the Neon SQL Editor
   - Click **"Run"**
   - You should see: "Query executed successfully"

4. **Get Your Connection String**
   - Go to **"Dashboard"**
   - Click **"Connection Details"**
   - Copy the **Connection String**
   - It will look like: `postgresql://user:password@ep-cool-darkness-123456.us-east-2.aws.neon.tech/neondb?sslmode=require`

### Step 3: Import Data to Neon

#### Option A: Using CSV Import

1. In Neon SQL Editor, use COPY command:

```sql
-- First, we need to handle the CSV properly
-- Create a temporary table for import
CREATE TEMP TABLE recipes_temp (
    id BIGINT,
    titre TEXT,
    temps_preparation TEXT,
    temps_cuisson TEXT,
    rendement TEXT,
    ingredients TEXT,  -- Will convert to JSONB
    instructions TEXT, -- Will convert to JSONB
    image_url TEXT,
    category TEXT,
    tags TEXT,         -- Will convert to array
    created_at TIMESTAMP WITH TIME ZONE,
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Note: You'll need to manually paste CSV data or use psql for file import
-- After importing, convert to proper types:

INSERT INTO recipes (
    id, titre, temps_preparation, temps_cuisson, rendement,
    ingredients, instructions, image_url, category, tags,
    created_at, updated_at
)
SELECT
    id,
    titre,
    temps_preparation,
    temps_cuisson,
    rendement,
    ingredients::jsonb,
    instructions::jsonb,
    image_url,
    category,
    string_to_array(tags, ',')::text[],
    created_at,
    updated_at
FROM recipes_temp;

-- Reset the sequence to avoid ID conflicts
SELECT setval('recipes_id_seq', (SELECT MAX(id) FROM recipes));
```

#### Option B: Using SQL File

If you exported using pg_dump:

```bash
# Using psql command line
psql "your-neon-connection-string" < recipes_export.sql

# Update the sequence
psql "your-neon-connection-string" -c "SELECT setval('recipes_id_seq', (SELECT MAX(id) FROM recipes));"
```

#### Option C: Manual Verification Query

After import, verify your data:

```sql
-- Check record count
SELECT COUNT(*) FROM recipes;

-- Check sample data
SELECT id, titre, category FROM recipes LIMIT 5;

-- Verify JSONB fields
SELECT
    id,
    titre,
    jsonb_array_length(ingredients) as ingredient_count,
    jsonb_array_length(instructions) as instruction_count
FROM recipes
LIMIT 5;
```

### Step 4: Update Your Application

1. **Update Environment Variables**

Update your `.env` file:

```env
# OLD - Remove these
# SUPABASE_URL=https://xxxxx.supabase.co
# SUPABASE_KEY=xxxxxx

# NEW - Add this
DATABASE_URL=postgresql://user:password@ep-cool-darkness-123456.us-east-2.aws.neon.tech/neondb?sslmode=require
```

2. **The Code is Already Updated!**

All the Python functions have been updated to use Neon DB:
- ✅ `netlify/functions/recipes.py`
- ✅ `netlify/functions/recipe-detail.py`
- ✅ `netlify/functions/shopping-list.py`
- ✅ `netlify/functions/utils/db.py`

3. **Update Netlify Environment Variables**

If deployed on Netlify:
- Go to **Site settings** → **Environment variables**
- Delete: `SUPABASE_URL` and `SUPABASE_KEY`
- Add: `DATABASE_URL` with your Neon connection string
- Click **"Save"**
- Redeploy your site

### Step 5: Test the Migration

1. **Test Locally**

```bash
# Install dependencies
cd netlify/functions
pip install -r requirements.txt

# Run local development server
netlify dev
```

2. **Test API Endpoints**

```bash
# List recipes
curl http://localhost:8888/api/recipes

# Get a specific recipe (replace 1 with an actual ID)
curl http://localhost:8888/api/recipe-detail/1

# Create a test recipe
curl -X POST http://localhost:8888/api/recipes \
  -H "Content-Type: application/json" \
  -d '{
    "titre": "Test Recipe",
    "ingredients": [{"nom": "test", "quantité": 1, "unité": "cup"}],
    "instructions": ["Step 1: Test"]
  }'
```

3. **Test in Browser**

- Open http://localhost:8888
- Browse recipes
- Create a new recipe
- Generate a shopping list
- Everything should work identically to before!

### Step 6: Deploy to Production

```bash
git add .
git commit -m "Migrate from Supabase to Neon DB"
git push origin main
```

Netlify will automatically deploy your changes.

## 🔍 Troubleshooting

### Issue: "relation 'recipes' does not exist"

**Solution**: The schema wasn't created properly.
- Re-run `neon-schema.sql` in Neon SQL Editor
- Verify the table exists: `SELECT * FROM recipes LIMIT 1;`

### Issue: "connection refused" or "timeout"

**Solution**: Connection string is incorrect.
- Verify your connection string has `?sslmode=require`
- Check that your Neon project is active (not suspended)
- Ensure there are no firewall issues

### Issue: "invalid input syntax for type json"

**Solution**: Data wasn't imported correctly.
- Check that JSONB columns contain valid JSON
- Use `::jsonb` cast when importing from text

### Issue: "sequence is out of sync"

**Solution**: Reset the sequence after import.

```sql
SELECT setval('recipes_id_seq', (SELECT MAX(id) FROM recipes));
```

## 📊 Comparison: Before vs After

| Feature | Supabase | Neon DB |
|---------|----------|---------|
| Database | PostgreSQL | PostgreSQL |
| Query Language | SQL | SQL |
| SDK Required | Yes (Supabase client) | No (Standard PostgreSQL) |
| Connection Pooling | Built-in | psycopg2 pool |
| Cold Start | ~1-2s | <500ms |
| Free Tier Storage | 500 MB | 512 MB |
| Free Tier Compute | Unlimited (throttled) | 100 hours/month |
| Branching | No | Yes (Git-like) |
| Time Travel | No | Yes (point-in-time recovery) |

## 🎉 Benefits You'll Notice

### Performance Improvements:
- ✅ **Faster cold starts**: Database wakes up faster
- ✅ **Better connection pooling**: More efficient resource usage
- ✅ **Parameterized queries**: Better security and performance

### Developer Experience:
- ✅ **Standard PostgreSQL**: No vendor-specific syntax
- ✅ **Database branching**: Test schema changes safely
- ✅ **Better debugging**: Direct SQL queries, no abstraction layer

### Security:
- ✅ **SQL injection protection**: All queries use parameters
- ✅ **No exposed API keys**: Connection string is server-side only
- ✅ **Input validation**: Comprehensive validation on all endpoints

## 🆘 Need Help?

If you encounter issues during migration:

1. **Check Neon Documentation**: [https://neon.tech/docs](https://neon.tech/docs)
2. **Verify Connection**: Use Neon's SQL Editor to test queries
3. **Check Logs**: Look at Netlify function logs for errors
4. **Create an Issue**: Open a GitHub issue with details

## 🔄 Rollback Plan

If you need to revert to Supabase:

1. Keep your old `.env` file backed up
2. Restore the old Supabase-based code:
   ```bash
   git checkout <commit-before-migration>
   ```
3. Update environment variables back to Supabase credentials
4. Redeploy

However, with the improved code quality and security, we recommend staying with Neon DB!

---

**Migration complete! Enjoy your improved Croustillant application! 🎉**
