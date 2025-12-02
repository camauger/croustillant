# Croustillant - Project Documentation for Claude

## Project Overview
Croustillant is a modern serverless recipe management application. Users can view recipes, create new ones, select favorites, and generate intelligent shopping lists with unit conversion and categorization.

**Version**: 2.0 (Modernized Serverless)
**Previous Version**: Flask-based monolith (see legacy/ folder for old code)

## Tech Stack

### Current Architecture (v2.0)
- **Frontend**: Vanilla JavaScript (ES6+), HTML5, CSS3
- **Backend**: Netlify Functions (Python serverless)
- **Database**: Supabase (PostgreSQL)
- **Hosting**: Netlify (Static + Serverless)
- **Storage**: Browser LocalStorage (user preferences)

### Legacy Architecture (v1.0)
- **Backend**: Python 3.6+ with Flask
- **Database**: SQLite3
- **Frontend**: Jinja2 templates
- **Session**: Flask server-side sessions
- **Hosting**: Heroku

## Architecture

### System Architecture
```
┌─────────────────────────────────────────┐
│  Netlify CDN (Edge Network)             │
│  ├── Static Files (HTML/CSS/JS)         │
│  └── Global Caching                     │
└─────────────────┬───────────────────────┘
                  │ HTTPS
┌─────────────────┴───────────────────────┐
│  Netlify Functions (AWS Lambda)         │
│  ├── /api/recipes (List & Create)       │
│  ├── /api/recipe-detail/:id (CRUD)      │
│  └── /api/shopping-list (Generate)      │
└─────────────────┬───────────────────────┘
                  │ PostgreSQL Protocol
┌─────────────────┴───────────────────────┐
│  Supabase (Backend-as-a-Service)        │
│  ├── PostgreSQL Database (500MB free)   │
│  ├── Storage API (images)               │
│  ├── Real-time subscriptions            │
│  └── Authentication (future)            │
└─────────────────────────────────────────┘
```

### Database Schema (Supabase)

**recipes table (PostgreSQL)**:
- `id` (BIGSERIAL PRIMARY KEY) - Auto-incrementing ID
- `titre` (TEXT NOT NULL UNIQUE) - Recipe title
- `temps_preparation` (TEXT) - Preparation time
- `temps_cuisson` (TEXT) - Cooking time
- `rendement` (TEXT) - Yield/portions
- `ingredients` (JSONB NOT NULL) - Ingredients array (indexed)
- `instructions` (JSONB NOT NULL) - Instructions array
- `image_url` (TEXT) - Recipe image URL
- `category` (TEXT) - Recipe category (indexed)
- `tags` (TEXT[]) - Tags array (indexed with GIN)
- `created_at` (TIMESTAMP WITH TIME ZONE) - Creation timestamp
- `updated_at` (TIMESTAMP WITH TIME ZONE) - Last update (auto-updated)

**Indexes**:
- `idx_recipes_titre` - B-tree index on title for searches
- `idx_recipes_category` - B-tree index on category
- `idx_recipes_ingredients` - GIN index on JSONB ingredients
- `idx_recipes_tags` - GIN index on tags array

### Key Files

**Frontend (public/)**:
- `index.html` - Single-page application entry point
- `css/style.css` - Modern responsive styles
- `js/config.js` - Application configuration
- `js/api.js` - API client for backend communication
- `js/storage.js` - LocalStorage management
- `js/router.js` - Client-side routing (SPA)
- `js/app.js` - Main application initialization
- `js/components/` - Modular UI components
  - `recipes-list.js` - Recipe grid and search
  - `recipe-detail.js` - Recipe modal and detail view
  - `recipe-form.js` - Create/edit recipe form
  - `selection.js` - Selected recipes management
  - `shopping-list.js` - Smart shopping list with categories

**Backend (netlify/functions/)**:
- `recipes.py` - GET all recipes, POST create recipe
- `recipe-detail.py` - GET/PUT/DELETE single recipe
- `shopping-list.py` - POST generate smart shopping list
- `utils/db.py` - Supabase client and response formatting
- `utils/ingredients.py` - Unit conversion and categorization
- `requirements.txt` - Python dependencies (supabase==2.3.0)

**Infrastructure**:
- `netlify.toml` - Netlify deployment configuration
- `supabase-schema.sql` - Database schema and indexes
- `.env.example` - Environment variables template

**Migration**:
- `migration/migrate-to-supabase.py` - SQLite to Supabase migration
- `migration/requirements.txt` - Migration script dependencies

**Documentation**:
- `DEPLOYMENT.md` - Complete deployment guide
- `README-MODERN.md` - Modern version documentation
- `CLAUDE.MD` - This file (AI assistant guide)

## API Endpoints

### GET /api/recipes
List all recipes with optional filtering
**Query Parameters**:
- `search` - Search term (searches title and instructions)
- `category` - Filter by category
- `limit` - Number of results (default: 100)
- `offset` - Pagination offset (default: 0)

**Response**:
```json
{
  "success": true,
  "recipes": [...],
  "count": 42
}
```

### GET /api/recipe-detail/:id
Get single recipe by ID
**Response**:
```json
{
  "success": true,
  "recipe": {
    "id": 1,
    "titre": "Recipe Name",
    "ingredients": [...],
    "instructions": [...],
    ...
  }
}
```

### POST /api/recipes
Create new recipe
**Body**:
```json
{
  "titre": "Required",
  "temps_preparation": "Optional",
  "temps_cuisson": "Optional",
  "rendement": "Optional",
  "image_url": "Optional",
  "ingredients": [...],  // Required
  "instructions": [...], // Required
  "category": "Optional",
  "tags": []  // Optional
}
```

### PUT /api/recipe-detail/:id
Update existing recipe
**Body**: Same as POST (all fields optional except what you want to update)

### DELETE /api/recipe-detail/:id
Delete recipe by ID

### POST /api/shopping-list
Generate smart shopping list
**Body**:
```json
{
  "recipe_ids": [1, 2, 3],
  "exclude_pantry": false
}
```

**Response**:
```json
{
  "success": true,
  "shopping_list": {
    "Produits laitiers": [...],
    "Viandes et poissons": [...],
    "Fruits et légumes": [...]
  },
  "total_items": 15,
  "recipe_count": 3,
  "recipes": [...]
}
```

## Data Formats

### Recipe JSON Structure
```json
{
  "titre": "Recipe Name",
  "temps_preparation": "20 minutes",
  "temps_cuisson": "30 minutes",
  "rendement": "4 portions",
  "image_url": "https://...",
  "category": "Main Course",
  "tags": ["vegetarian", "quick"],
  "ingredients": [
    {
      "nom": "Flour",
      "quantité": 2,
      "unité": "cups"
    },
    {
      "groupe": "Wet Ingredients",
      "liste": [
        {
          "nom": "Milk",
          "quantité": 1,
          "unité": "cup"
        }
      ]
    }
  ],
  "instructions": [
    "Mix dry ingredients",
    "Add wet ingredients",
    "Bake at 350°F"
  ]
}
```

## Important Implementation Details

### Smart Shopping List Features

**Unit Conversion System**:
- Converts all quantities to base units (ml for volume, g for weight)
- Supports metric and imperial units
- Volume: ml, l, tasse, c. à soupe, c. à thé, cups
- Weight: g, kg, oz, lb
- Implementation: `netlify/functions/utils/ingredients.py`

**Ingredient Categorization**:
- Automatic categorization by keywords
- Categories: Dairy, Meat/Fish, Produce, Grains, Condiments, Canned, Frozen, Other
- Configurable category keywords
- Implementation: `INGREDIENT_CATEGORIES` in ingredients.py

**Smart Aggregation**:
- Combines ingredients with same name and compatible units
- Converts to common unit before aggregating
- Rounds to practical quantities (2.3 eggs → 3)
- Implementation: `aggregate_ingredients()` in ingredients.py

**Pantry Items Exclusion**:
- Optional exclusion of common pantry items (salt, pepper, oil, etc.)
- User preference stored in LocalStorage
- List configurable: `COMMON_PANTRY_ITEMS` in ingredients.py

### Frontend State Management

**LocalStorage Keys**:
- `croustillant_selected_recipes` - Array of selected recipe IDs
- `croustillant_preferences` - User preferences object

**Client-Side Routing**:
- Single-page application (SPA) architecture
- Routes: `/`, `/create`, `/selection`, `/shopping`
- No page reloads, smooth navigation
- Browser history API integration

### Deployment Configuration

**Netlify**:
- Publish directory: `public/`
- Functions directory: `netlify/functions/`
- Redirects: `/api/*` → `/.netlify/functions/:splat`
- CORS headers configured in `netlify.toml`

**Environment Variables** (set in Netlify dashboard):
- `SUPABASE_URL` - Supabase project URL (required)
- `SUPABASE_KEY` - Supabase anon/public key (required)

## Development Workflow

### Local Development Setup
```bash
# 1. Install Netlify CLI
npm install -g netlify-cli

# 2. Set up environment variables
cp .env.example .env
# Edit .env with your Supabase credentials

# 3. Run development server
netlify dev

# Accesses:
# - Frontend: http://localhost:8888
# - Functions: http://localhost:8888/api/*
```

### Testing Functions Locally
```bash
# Test recipes endpoint
curl http://localhost:8888/api/recipes

# Test shopping list
curl -X POST http://localhost:8888/api/shopping-list \
  -H "Content-Type: application/json" \
  -d '{"recipe_ids":[1,2],"exclude_pantry":false}'
```

### Database Setup (Supabase)
1. Create account at supabase.com
2. Create new project
3. Go to SQL Editor
4. Run `supabase-schema.sql`
5. Copy API credentials to `.env`

### Migration from Old Version
```bash
cd migration
pip install -r requirements.txt
python migrate-to-supabase.py
```

## Coding Conventions

### JavaScript (Frontend)
- ES6+ features (arrow functions, async/await, destructuring)
- No framework dependencies (Vanilla JS)
- Modular component architecture
- Clear function names and comments
- French for UI text, English for code

### Python (Backend)
- PEP 8 style guide
- Type hints where beneficial
- Clear docstrings for functions
- Error handling with try/except
- JSON responses with consistent format

### CSS
- Custom properties (CSS variables) for theming
- Mobile-first responsive design
- BEM-like naming convention
- Organized by component

### Naming
- French: UI text, recipe fields, database columns
- English: Code, functions, variables, comments
- snake_case: Python, database fields
- camelCase: JavaScript variables/functions
- kebab-case: CSS classes, file names

## When Working on This Project

### Before Making Changes:
1. ✅ Check if database schema needs updating (run migration SQL)
2. ✅ Consider impact on API contracts (frontend expects certain formats)
3. ✅ Test with both grouped and ungrouped ingredients
4. ✅ Verify LocalStorage handling isn't broken
5. ✅ Test on mobile devices (responsive design)
6. ✅ Check Netlify function logs for errors

### Common Tasks:

**Adding a new API endpoint**:
1. Create function in `netlify/functions/`
2. Add to `netlify.toml` if needed
3. Update `js/api.js` with new method
4. Test locally with `netlify dev`

**Adding a new UI component**:
1. Create file in `public/js/components/`
2. Add rendering function
3. Register route in `js/app.js` if needed
4. Update navigation in `index.html`

**Modifying database schema**:
1. Update `supabase-schema.sql`
2. Run SQL in Supabase dashboard
3. Update API functions to handle new fields
4. Update frontend to display new data
5. Create migration if needed

**Improving shopping list logic**:
1. Edit `netlify/functions/utils/ingredients.py`
2. Add unit conversions or categories
3. Test with various ingredient combinations
4. Update documentation

### Testing Checklist:
- [ ] Recipe creation with all field types
- [ ] Recipe editing preserves data
- [ ] Recipe deletion removes from selection
- [ ] Search returns relevant results
- [ ] Shopping list aggregates correctly
- [ ] Unit conversion works (metric/imperial)
- [ ] Categorization is accurate
- [ ] Mobile responsiveness
- [ ] Browser back/forward buttons work
- [ ] LocalStorage persists correctly
- [ ] Print shopping list works
- [ ] Copy to clipboard works

## Security Considerations

### Current Setup (Public Access)
- ⚠️ **No authentication** - Anyone can access the app
- ⚠️ **No user accounts** - All users share the same data
- ⚠️ **Public database** - All recipes visible to everyone
- ✅ **No sensitive data** - Recipes are public information
- ✅ **HTTPS** - All traffic encrypted via Netlify
- ✅ **Environment variables** - Credentials not in code

**Suitable for**: Personal use, trusted groups, public recipe collections

### Future Authentication Implementation
To add user accounts:
1. Enable Supabase Authentication
2. Add login/signup UI in frontend
3. Verify JWT tokens in Netlify Functions
4. Enable Row Level Security (RLS) in Supabase
5. Create policies: `CREATE POLICY "Users see own recipes" ON recipes FOR SELECT USING (auth.uid() = user_id);`
6. Add `user_id` column to recipes table

## Performance Optimizations

### Frontend
- ✅ No framework overhead (Vanilla JS)
- ✅ Minimal CSS bundle
- ✅ LocalStorage for instant data access
- ✅ Client-side routing (no page reloads)
- ✅ Lazy loading for images (CSS)
- 🔄 Could add: Service worker for offline support

### Backend
- ✅ Serverless (scales automatically)
- ✅ Database indexes on frequently queried fields
- ✅ JSONB for efficient JSON queries
- ✅ Connection pooling via Supabase
- 🔄 Could add: Redis caching for frequent queries

### Network
- ✅ Netlify CDN (global edge caching)
- ✅ HTTPS/2 support
- ✅ Compression enabled
- 🔄 Could add: Image optimization/CDN

## Known Limitations

### Free Tier Limits
**Netlify Free**:
- 100GB bandwidth/month
- 125,000 function requests/month
- 300 build minutes/month

**Supabase Free**:
- 500MB database storage
- 1GB file storage
- 2GB bandwidth/month
- 50,000 monthly active users

### Technical Limitations
- No real-time collaboration (yet)
- No offline support (yet)
- No image optimization
- No recipe import from URLs
- No nutritional calculations
- Single language (French)

## Troubleshooting

### "Functions return 404"
- Check environment variables in Netlify dashboard
- Verify `netlify.toml` configuration
- Check function logs in Netlify dashboard
- Ensure Python dependencies installed

### "Database connection failed"
- Verify Supabase credentials in `.env`
- Check Supabase project is active
- Test connection from Supabase dashboard
- Use anon key (not service role key)

### "Shopping list categories wrong"
- Review `INGREDIENT_CATEGORIES` in ingredients.py
- Check ingredient names for typos
- Add missing keywords to categories
- Test with various ingredient combinations

### "LocalStorage not persisting"
- Check browser privacy settings
- Clear browser cache and try again
- Verify storage.js is loaded
- Check browser console for errors

## Future Enhancements

### High Priority
- [ ] User authentication and accounts
- [ ] Recipe ratings and reviews
- [ ] Mobile app (Progressive Web App)
- [ ] Recipe import from URLs
- [ ] Meal planning calendar

### Medium Priority
- [ ] Nutritional information
- [ ] Recipe scaling (adjust portions)
- [ ] Multi-language support
- [ ] Dark mode
- [ ] Recipe collections/folders

### Low Priority
- [ ] Recipe sharing via links
- [ ] Collaborative meal planning
- [ ] Integration with grocery delivery services
- [ ] Voice commands
- [ ] Recipe recommendations (AI)

## Migration Notes

### From Flask Version (v1.0)
Key differences:
- Server-side sessions → Client-side LocalStorage
- Jinja2 templates → JavaScript SPA
- SQLite → PostgreSQL (Supabase)
- Monolithic → Serverless functions
- Heroku → Netlify

Migration path:
1. Run `migration/migrate-to-supabase.py`
2. Deploy new version to Netlify
3. Update bookmarks/links
4. Keep old version running during transition
5. Verify all recipes migrated correctly

### Backward Compatibility
- JSON data format is compatible
- Recipe IDs preserved during migration
- Old JSON files can still be imported
- Shopping list logic improved but compatible

## Support and Resources

- **Deployment Guide**: See DEPLOYMENT.md
- **User Documentation**: See README-MODERN.md
- **Netlify Docs**: https://docs.netlify.com
- **Supabase Docs**: https://supabase.com/docs
- **Python Supabase Client**: https://github.com/supabase/supabase-py

## Summary for AI Assistants

When working on this project:
1. This is a **serverless** architecture (not Flask anymore)
2. Frontend is **Vanilla JavaScript** SPA (not Jinja2 templates)
3. Backend is **Netlify Functions** (Python serverless)
4. Database is **Supabase** PostgreSQL (not SQLite)
5. Deployment is on **Netlify** (not Heroku)
6. Focus on **unit conversion** and **categorization** for shopping lists
7. Maintain **mobile-first** responsive design
8. Keep **no authentication** for simplicity (future enhancement)
9. Test locally with `netlify dev`
10. Always check DEPLOYMENT.md for deployment procedures
