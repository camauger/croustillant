# Deployment Guide - Croustillant on Netlify

## Overview
This guide will help you deploy the modernized Croustillant application to Netlify with Neon DB as the database backend.

## Prerequisites
- Git repository (GitHub, GitLab, or Bitbucket)
- Netlify account (free tier available)
- Neon account (free tier available)

## Step 1: Set Up Neon DB Database

### 1.1 Create a Neon Project
1. Go to [neon.tech](https://neon.tech)
2. Sign up or log in (free, no credit card required)
3. Click "Create Project"
4. Fill in project details:
   - Name: `croustillant`
   - Region: Choose closest to your users (e.g., US East, EU West)
   - PostgreSQL version: 16 (latest)
5. Click "Create" and wait for project creation (30 seconds)

### 1.2 Create Database Schema
1. In your Neon dashboard, click "SQL Editor" in the left sidebar
2. Open your local `neon-schema.sql` file
3. Copy the entire content
4. Paste into the Neon SQL Editor
5. Click "Run"
6. You should see: "Query executed successfully"
7. Verify tables are created by running: `SELECT * FROM recipes LIMIT 1;`

### 1.3 Get Connection String
1. Go to "Dashboard" in Neon
2. Click "Connection Details"
3. Copy the **Connection String**
4. It will look like: `postgresql://user:password@ep-xxxxx-xxxxx.region.aws.neon.tech/neondb?sslmode=require`
5. **Important**: Use the connection string with `?sslmode=require` for secure connections

## Step 2: Migrate Existing Data (Optional)

If you have existing recipes in SQLite:

### 2.1 Install Migration Dependencies
```bash
cd migration
pip install -r requirements.txt
```

### 2.2 Configure Environment
Create `.env` file in the project root:
```env
DATABASE_URL=postgresql://user:password@ep-xxxxx-xxxxx.region.aws.neon.tech/neondb?sslmode=require
SQLITE_DB=recipes.db
```

**Note**: If you're migrating from Supabase, see [NEON_MIGRATION.md](NEON_MIGRATION.md) for detailed instructions.

### 2.3 Run Migration
```bash
# For SQLite to Neon migration, you'll need to create a custom script
# or use pg_dump/psql to export and import data
```

The migration process will:
- Read all recipes from SQLite
- Transform data to PostgreSQL format
- Insert into Neon database
- Report success/errors

## Step 3: Deploy to Netlify

### 3.1 Connect Repository to Netlify
1. Go to [netlify.com](https://netlify.com)
2. Sign up or log in
3. Click "Add new site" > "Import an existing project"
4. Choose your Git provider and repository
5. Configure build settings:
   - **Base directory**: (leave empty)
   - **Build command**: `echo 'No build needed'`
   - **Publish directory**: `public`
   - **Functions directory**: `netlify/functions`

### 3.2 Configure Environment Variables
In Netlify dashboard, go to "Site settings" > "Environment variables"

Add this variable:
```
DATABASE_URL = postgresql://user:password@ep-xxxxx-xxxxx.region.aws.neon.tech/neondb?sslmode=require
```

**Important**:
- Replace with your actual Neon connection string
- Make sure it includes `?sslmode=require` for secure connections
- Use the connection string from Neon dashboard (not a password reset)

### 3.3 Deploy
1. Click "Deploy site"
2. Wait for deployment (1-2 minutes)
3. Your site will be live at `https://random-name.netlify.app`

### 3.4 Configure Custom Domain (Optional)
1. Go to "Domain settings"
2. Add custom domain
3. Follow DNS configuration instructions

## Step 4: Verify Deployment

### 4.1 Test Basic Functionality
1. Visit your Netlify URL
2. Check that homepage loads
3. Try creating a recipe
4. Verify recipe appears in list

### 4.2 Test All Features
- ✅ View recipes list
- ✅ Create new recipe
- ✅ View recipe details
- ✅ Edit recipe
- ✅ Delete recipe
- ✅ Add recipe to selection
- ✅ Generate shopping list
- ✅ Export shopping list

### 4.3 Check Netlify Functions Logs
1. In Netlify dashboard, go to "Functions"
2. Check function execution logs
3. Look for any errors

## Step 5: Post-Deployment Configuration

### 5.1 Update CLAUDE.MD
Update the project documentation with:
- New architecture details
- Deployment URLs
- Environment variables

### 5.2 Set Up Monitoring (Optional)
Netlify provides:
- Analytics (requires paid plan)
- Function logs (free)
- Deploy notifications

### 5.3 Configure Backup (Recommended)
Neon provides:
- Automatic backups (point-in-time recovery)
- Manual backups via dashboard
- Database branching for safe testing

## Troubleshooting

### Functions Not Working
**Problem**: API calls return 404 or 500 errors

**Solutions**:
1. Check environment variables are set in Netlify
2. Verify function names match API routes
3. Check function logs for errors
4. Ensure `requirements.txt` is in `netlify/functions/`

### Database Connection Errors
**Problem**: "DATABASE_URL must be set" error

**Solutions**:
1. Verify `DATABASE_URL` is set in Netlify environment variables
2. Check that the connection string is correct and includes `?sslmode=require`
3. Verify your Neon project is active (not suspended)
4. Test the connection string in Neon SQL Editor
5. Redeploy site after adding/updating variables

### CORS Errors
**Problem**: Browser shows CORS policy errors

**Solutions**:
1. Verify `netlify.toml` includes CORS headers
2. Check API functions return proper headers
3. Clear browser cache

### Recipe Images Not Loading
**Problem**: Image URLs return 404

**Solutions**:
1. Use absolute URLs for images
2. Consider using a CDN or image hosting service (e.g., Cloudinary, Imgur)
3. Check image URL format in database
4. Ensure image URLs are publicly accessible

### Migration Script Fails
**Problem**: Migration script encounters errors

**Solutions**:
1. Check SQLite database exists and is readable
2. Verify `DATABASE_URL` in `.env` is correct
3. Check Neon table exists (run `neon-schema.sql` first)
4. Verify connection string includes `?sslmode=require`
5. Review error messages for specific issues

## Maintenance

### Regular Tasks
- Monitor function execution logs
- Check Neon database size (0.5 GB free tier limit)
- Review and optimize slow queries
- Update dependencies periodically
- Monitor Neon compute hours (100 hours/month free tier)

### Updating the Application
1. Make changes locally
2. Test thoroughly
3. Push to Git repository
4. Netlify auto-deploys from main branch
5. Monitor deployment logs

### Rollback Procedure
If deployment has issues:
1. Go to Netlify dashboard
2. "Deploys" tab
3. Find last working deploy
4. Click "Publish deploy"

## Cost Estimation

### Free Tier Limits
**Netlify Free**:
- 100GB bandwidth/month
- 300 build minutes/month
- Unlimited sites
- 125k serverless function requests/month

**Neon Free**:
- 0.5 GB database storage
- 100 compute hours/month
- 10 project branches
- Automatic backups

### When to Upgrade
Upgrade if you exceed:
- Netlify: 100GB bandwidth or 125k API calls
- Neon: 0.5 GB storage or 100 compute hours/month

Paid plans start at:
- Netlify: $19/month
- Neon: $19/month (Pro plan)

## Security Considerations

### Current Setup (Public Access)
- Anyone can view, create, edit, and delete recipes
- No authentication required
- Suitable for personal use or trusted groups

### Adding Authentication (Future)
To restrict access:
1. Implement authentication (e.g., Auth0, Clerk, or custom JWT)
2. Add login/signup UI
3. Update Netlify Functions to verify JWT tokens
4. Add user_id column to recipes table
5. Filter queries by authenticated user

## Performance Optimization

### Frontend
- Images are lazy-loaded
- Minimal JavaScript bundle
- CSS is optimized
- LocalStorage for user preferences

### Backend
- Database indexes on frequently queried fields
- Efficient JSONB queries
- Connection pooling via psycopg2 (min 1, max 10 connections)
- Parameterized queries for security

### Future Improvements
- Add caching headers
- Implement service worker for offline support
- Use CDN for static assets
- Optimize database queries

## Support and Resources

- **Netlify Docs**: https://docs.netlify.com
- **Neon Docs**: https://neon.tech/docs
- **Netlify Functions Guide**: https://docs.netlify.com/functions/overview/
- **psycopg2 Documentation**: https://www.psycopg.org/docs/
- **PostgreSQL Documentation**: https://www.postgresql.org/docs/

## Next Steps

After successful deployment:
1. Share your app URL with users
2. Collect feedback
3. Plan feature enhancements
4. Consider adding authentication
5. Implement analytics
6. Add more recipe categories
7. Create mobile app (optional)
