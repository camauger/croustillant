# 🍳 Croustillant - Modern Serverless Version

A modern, serverless recipe management application built with Netlify Functions and Supabase.

## ✨ Features

### Core Features
- 📖 **Recipe Management**: Create, view, edit, and delete recipes
- 🔍 **Smart Search**: Search recipes by title or ingredients
- ⭐ **Recipe Selection**: Build your meal plan by selecting recipes
- 🛒 **Smart Shopping Lists**: Automatically generate consolidated shopping lists
- 📱 **Responsive Design**: Works perfectly on desktop, tablet, and mobile

### Advanced Features
- 🔢 **Unit Conversion**: Automatically converts between metric/imperial units
- 🏷️ **Smart Categorization**: Ingredients grouped by category (produce, dairy, meat, etc.)
- ✅ **Checkable Items**: Check off items as you shop
- 📋 **Export Options**: Copy to clipboard or print shopping lists
- 🎯 **Pantry Exclusion**: Option to exclude common pantry items
- 📊 **Quantity Rounding**: Rounds to practical amounts (2.3 eggs → 3 eggs)

## 🏗️ Architecture

### Tech Stack
- **Frontend**: Vanilla JavaScript (ES6+), HTML5, CSS3
- **Backend**: Netlify Functions (Python)
- **Database**: Supabase (PostgreSQL)
- **Hosting**: Netlify (Static + Serverless)
- **Storage**: LocalStorage (user preferences)

### Architecture Diagram
```
┌─────────────────────────────────────────┐
│  Netlify CDN (Global)                   │
│  ├── Static Files (HTML/CSS/JS)         │
│  └── Edge Caching                       │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────┴───────────────────────┐
│  Netlify Functions (Serverless)         │
│  ├── /api/recipes (GET, POST)           │
│  ├── /api/recipe-detail/:id (CRUD)      │
│  └── /api/shopping-list (POST)          │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────┴───────────────────────┐
│  Supabase (Backend-as-a-Service)        │
│  ├── PostgreSQL Database                │
│  ├── Storage (for images)               │
│  └── Real-time subscriptions            │
└─────────────────────────────────────────┘
```

## 📁 Project Structure

```
croustillant/
├── public/                      # Frontend static files
│   ├── index.html              # Main HTML file
│   ├── css/
│   │   └── style.css           # Styles
│   └── js/
│       ├── config.js           # Configuration
│       ├── api.js              # API client
│       ├── storage.js          # LocalStorage management
│       ├── router.js           # Client-side router
│       ├── app.js              # Main application
│       └── components/         # UI components
│           ├── recipes-list.js
│           ├── recipe-detail.js
│           ├── recipe-form.js
│           ├── selection.js
│           └── shopping-list.js
│
├── netlify/
│   └── functions/              # Serverless API
│       ├── recipes.py          # Recipes list & create
│       ├── recipe-detail.py    # Single recipe CRUD
│       ├── shopping-list.py    # Shopping list generation
│       ├── requirements.txt    # Python dependencies
│       └── utils/
│           ├── db.py           # Database utilities
│           └── ingredients.py  # Ingredient processing
│
├── migration/                  # Migration tools
│   ├── migrate-to-supabase.py  # SQLite to Supabase
│   └── requirements.txt
│
├── netlify.toml                # Netlify configuration
├── supabase-schema.sql         # Database schema
├── .env.example                # Environment variables template
├── DEPLOYMENT.md               # Deployment guide
└── CLAUDE.MD                   # AI assistant documentation
```

## 🚀 Quick Start

### Local Development

#### 1. Clone and Install
```bash
git clone <your-repo-url>
cd croustillant
```

#### 2. Set Up Supabase
- Create account at [supabase.com](https://supabase.com)
- Create new project
- Run `supabase-schema.sql` in SQL Editor
- Get API credentials

#### 3. Configure Environment
Create `.env` file:
```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
```

#### 4. Install Netlify CLI
```bash
npm install -g netlify-cli
```

#### 5. Run Locally
```bash
netlify dev
```

Visit `http://localhost:8888`

### Production Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for complete deployment guide.

Quick steps:
1. Push code to GitHub/GitLab
2. Connect repository to Netlify
3. Set environment variables in Netlify
4. Deploy!

## 🔧 Configuration

### Environment Variables

**Required**:
- `SUPABASE_URL`: Your Supabase project URL
- `SUPABASE_KEY`: Supabase anon/public key

**Optional**:
- `ENABLE_AUTH`: Enable authentication (future feature)

### User Preferences

Stored in browser LocalStorage:
- `excludePantryItems`: Exclude common pantry items from shopping list
- Selected recipe IDs

## 📊 Database Schema

### recipes Table

| Column | Type | Description |
|--------|------|-------------|
| id | BIGSERIAL | Primary key |
| titre | TEXT | Recipe title (unique) |
| temps_preparation | TEXT | Preparation time |
| temps_cuisson | TEXT | Cooking time |
| rendement | TEXT | Yield/servings |
| ingredients | JSONB | Ingredients array |
| instructions | JSONB | Instructions array |
| image_url | TEXT | Recipe image URL |
| category | TEXT | Recipe category |
| tags | TEXT[] | Tags array |
| created_at | TIMESTAMP | Creation timestamp |
| updated_at | TIMESTAMP | Last update timestamp |

### Ingredients JSON Format
```json
[
  {
    "nom": "flour",
    "quantité": 2,
    "unité": "cups"
  },
  {
    "groupe": "Wet ingredients",
    "liste": [
      {
        "nom": "milk",
        "quantité": 1,
        "unité": "cup"
      }
    ]
  }
]
```

## 🎨 Features in Detail

### Smart Shopping List Generation

The shopping list generator includes:

1. **Unit Conversion**
   - Automatic conversion to base units (ml, grams)
   - Converts between metric and imperial
   - Supported units: cups, tbsp, tsp, oz, lb, ml, l, g, kg

2. **Smart Aggregation**
   - Combines identical ingredients across recipes
   - Handles different unit systems
   - Groups by category

3. **Categorization**
   - Dairy products
   - Meats and fish
   - Fruits and vegetables
   - Grains and breads
   - Condiments and spices
   - Canned goods
   - Frozen items
   - Other

4. **Practical Quantities**
   - Rounds to sensible amounts
   - Whole numbers for countable items
   - Decimal precision for measurements

### Recipe Search

- Full-text search on title and instructions
- Case-insensitive matching
- Real-time results

### Recipe Selection

- Stored in browser LocalStorage
- Persists between sessions
- Visual badge showing count
- Quick add/remove buttons

## 🔐 Security

### Current Setup
- Public access (no authentication)
- Read and write operations available to all
- Suitable for personal/trusted use

### Future Authentication
Plans to add:
- Supabase Auth integration
- User accounts
- Private recipe collections
- Row Level Security policies

## 📈 Performance

### Optimizations
- Minimal JavaScript bundle (no frameworks)
- CSS optimized for fast rendering
- Database indexes on frequently queried fields
- JSONB for efficient ingredient queries
- Edge caching via Netlify CDN

### Metrics (Target)
- First Contentful Paint: < 1s
- Time to Interactive: < 2s
- Function execution: < 500ms

## 🧪 Testing Locally

### Test API Endpoints
```bash
# List recipes
curl http://localhost:8888/api/recipes

# Get single recipe
curl http://localhost:8888/api/recipe-detail/1

# Create recipe
curl -X POST http://localhost:8888/api/recipes \
  -H "Content-Type: application/json" \
  -d '{"titre":"Test","ingredients":[],"instructions":[]}'

# Generate shopping list
curl -X POST http://localhost:8888/api/shopping-list \
  -H "Content-Type: application/json" \
  -d '{"recipe_ids":[1,2],"exclude_pantry":false}'
```

## 🐛 Troubleshooting

### Common Issues

**Functions return 404**
- Check environment variables are set
- Verify `netlify.toml` configuration
- Ensure Python dependencies are installed

**Database connection errors**
- Verify Supabase credentials
- Check database table exists
- Test connection from Supabase dashboard

**LocalStorage issues**
- Clear browser cache
- Check browser console for errors
- Verify LocalStorage is not disabled

## 🤝 Contributing

### Development Workflow
1. Create feature branch
2. Make changes
3. Test locally with `netlify dev`
4. Push to repository
5. Create pull request

### Code Style
- JavaScript: ES6+ features, async/await
- Python: PEP 8 style guide
- CSS: BEM-like naming convention

## 📝 Migration from Old Version

To migrate from Flask/SQLite version:

1. Run migration script:
```bash
cd migration
pip install -r requirements.txt
python migrate-to-supabase.py
```

2. Verify data in Supabase dashboard
3. Deploy new version
4. Update bookmarks/links

## 🔮 Future Enhancements

### Planned Features
- [ ] User authentication
- [ ] Recipe ratings and reviews
- [ ] Meal planning calendar
- [ ] Nutritional information
- [ ] Recipe sharing
- [ ] Mobile app (PWA)
- [ ] Offline support
- [ ] Recipe import from URLs
- [ ] Multi-language support
- [ ] Dark mode

### Community Requests
- Recipe collections/folders
- Collaborative meal planning
- Grocery store integration
- Recipe scaling
- Print-optimized views

## 📄 License

MIT License - See LICENSE file for details

## 🙏 Acknowledgments

- Built with [Netlify](https://netlify.com)
- Database powered by [Supabase](https://supabase.com)
- Icons from emoji set

## 📞 Support

- Documentation: See DEPLOYMENT.md and CLAUDE.MD
- Issues: GitHub Issues
- Discussions: GitHub Discussions

---

**Made with ❤️ and modernized for the cloud**
