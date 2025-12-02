# Deployment Guide - Croustillant on Netlify

## Overview
This guide will help you deploy the modernized Croustillant application to Netlify with Supabase as the database backend.

## Prerequisites
- Git repository (GitHub, GitLab, or Bitbucket)
- Netlify account (free tier available)
- Supabase account (free tier available)

## Step 1: Set Up Supabase Database

### 1.1 Create a Supabase Project
1. Go to [supabase.com](https://supabase.com)
2. Sign up or log in
3. Click "New Project"
4. Fill in project details:
   - Name: `croustillant`
   - Database password: (save this securely)
   - Region: Choose closest to your users
5. Wait for project creation (1-2 minutes)

### 1.2 Create Database Schema
1. In your Supabase dashboard, go to "SQL Editor"
2. Copy the contents of `supabase-schema.sql`
3. Paste and click "Run"
4. Verify tables are created in "Table Editor"

### 1.3 Get API Credentials
1. Go to "Project Settings" > "API"
2. Save these values:
   - **Project URL**: `https://xxxxx.supabase.co`
   - **Anon/Public Key**: `eyJhbGc...` (public key)
   - **Service Role Key**: `eyJhbGc...` (secret key - for migration only)

### 1.4 Configure Row Level Security (Optional)
For now, we'll allow public access. To enable later:
```sql
ALTER TABLE recipes ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Allow all operations" ON recipes FOR ALL USING (true);
```

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
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your-service-role-key
SQLITE_DB=recipes.db
```

### 2.3 Run Migration
```bash
python migration/migrate-to-supabase.py
```

The script will:
- Read all recipes from SQLite
- Transform data to Supabase format
- Insert into Supabase database
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

Add these variables:
```
SUPABASE_URL = https://your-project.supabase.co
SUPABASE_KEY = your-anon-public-key
```

**Important**: Use the **anon/public key**, NOT the service role key!

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
Supabase provides:
- Daily automatic backups (free tier: 7 days retention)
- Manual backups via dashboard

## Troubleshooting

### Functions Not Working
**Problem**: API calls return 404 or 500 errors

**Solutions**:
1. Check environment variables are set in Netlify
2. Verify function names match API routes
3. Check function logs for errors
4. Ensure `requirements.txt` is in `netlify/functions/`

### Database Connection Errors
**Problem**: "SUPABASE_URL must be set" error

**Solutions**:
1. Verify environment variables in Netlify
2. Check that variables don't have trailing spaces
3. Redeploy site after adding variables
4. Use anon key, not service role key

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
2. Consider using Supabase Storage for images
3. Check image URL format in database

### Migration Script Fails
**Problem**: Migration script encounters errors

**Solutions**:
1. Check SQLite database exists and is readable
2. Verify Supabase credentials in `.env`
3. Check Supabase table exists (run schema first)
4. Review error messages for specific issues

## Maintenance

### Regular Tasks
- Monitor function execution logs
- Check Supabase database size (500MB free tier limit)
- Review and optimize slow queries
- Update dependencies periodically

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

**Supabase Free**:
- 500MB database
- 1GB file storage
- 2GB bandwidth
- 50k monthly active users

### When to Upgrade
Upgrade if you exceed:
- Netlify: 100GB bandwidth or 125k API calls
- Supabase: 500MB data or 1GB files

Paid plans start at:
- Netlify: $19/month
- Supabase: $25/month

## Security Considerations

### Current Setup (Public Access)
- Anyone can view, create, edit, and delete recipes
- No authentication required
- Suitable for personal use or trusted groups

### Adding Authentication (Future)
To restrict access:
1. Enable Supabase Auth
2. Add login/signup UI
3. Update Netlify Functions to verify JWT tokens
4. Enable Row Level Security in Supabase
5. Create policies for authenticated users

## Performance Optimization

### Frontend
- Images are lazy-loaded
- Minimal JavaScript bundle
- CSS is optimized
- LocalStorage for user preferences

### Backend
- Database indexes on frequently queried fields
- Efficient JSONB queries
- Connection pooling via Supabase

### Future Improvements
- Add caching headers
- Implement service worker for offline support
- Use CDN for static assets
- Optimize database queries

## Support and Resources

- **Netlify Docs**: https://docs.netlify.com
- **Supabase Docs**: https://supabase.com/docs
- **Netlify Functions Guide**: https://docs.netlify.com/functions/overview/
- **Supabase Python Client**: https://github.com/supabase/supabase-py

## Next Steps

After successful deployment:
1. Share your app URL with users
2. Collect feedback
3. Plan feature enhancements
4. Consider adding authentication
5. Implement analytics
6. Add more recipe categories
7. Create mobile app (optional)
