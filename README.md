# 🍳 Croustillant - Modern Serverless Version

A modern, serverless recipe management application built with Netlify Functions and Neon DB.

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
- **Database**: Neon DB (Serverless PostgreSQL)
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
│  Neon DB (Serverless PostgreSQL)        │
│  ├── Automatic Scaling                  │
│  ├── Connection Pooling                 │
│  └── Generous Free Tier                 │
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
├── netlify.toml                # Netlify configuration
├── neon-schema.sql             # Database schema
├── .env.example                # Environment variables template
└── README.md                   # This file
```

## 🚀 Quick Start

### Local Development

#### 1. Clone and Install
```bash
git clone <your-repo-url>
cd croustillant
```

#### 2. Set Up Neon DB
1. Create a free account at [Neon](https://neon.tech)
2. Click **"Create Project"**
3. Choose a region close to your users
4. Once created, click **"SQL Editor"** in the sidebar
5. Open the `neon-schema.sql` file from your project
6. Copy the entire SQL content and paste it into the Neon SQL Editor
7. Click **"Run"** - you should see a success message
8. Get your connection string:
   - Go to **"Dashboard"**
   - Click **"Connection Details"**
   - Copy the **Connection String** (it includes everything you need)

#### 3. Configure Environment
Create `.env` file:
```env
DATABASE_URL=postgresql://user:password@ep-cool-darkness-123456.us-east-2.aws.neon.tech/neondb?sslmode=require
```

**Important**: Replace with your actual Neon connection string!

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

#### Quick Deployment to Netlify

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Migrate to Neon DB"
   git push origin main
   ```

2. **Connect to Netlify**
   - Go to [Netlify](https://netlify.com)
   - Click "Add new site" → "Import an existing project"
   - Connect your GitHub repository
   - Configure build settings:
     - **Build command**: `echo "No build needed"`
     - **Publish directory**: `public`
     - **Functions directory**: `netlify/functions`

3. **Set Environment Variables**
   - In Netlify dashboard, go to **Site settings** → **Environment variables**
   - Add `DATABASE_URL` with your Neon connection string

4. **Deploy!**
   - Click "Deploy site"
   - Your app will be live in ~30 seconds

## 🔧 Configuration

### Environment Variables

**Required**:
- `DATABASE_URL`: Your Neon PostgreSQL connection string

**Optional**:
- `ENABLE_AUTH`: Enable authentication (future feature)

### Neon DB Connection Pooling

Neon automatically handles connection pooling. For optimal performance in serverless environments:
- Use the connection string with `?sslmode=require`
- Connection pooling is managed by the psycopg2 pool in `utils/db.py`
- Default: min 1, max 10 connections per function instance

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

## 🔐 Security Features

### Improvements in This Version

- ✅ **SQL Injection Prevention**: All queries use parameterized statements
- ✅ **Input Validation**: Comprehensive validation on all endpoints
- ✅ **Error Handling**: Sanitized error messages (no internal details exposed)
- ✅ **Connection Pooling**: Efficient database connection management
- ✅ **CORS Headers**: Configured for API access

## 📈 Performance

### Optimizations
- Minimal JavaScript bundle (no frameworks)
- CSS optimized for fast rendering
- Database indexes on frequently queried fields
- JSONB for efficient ingredient queries
- Edge caching via Netlify CDN
- Connection pooling for database efficiency

### Neon DB Benefits
- **Serverless Autoscaling**: Automatically scales with traffic
- **Instant Cold Starts**: Database wakes up in <500ms
- **Generous Free Tier**: 0.5 GB storage, 100 hours compute/month
- **High Availability**: Built on AWS with automatic backups

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
- Verify DATABASE_URL is correct
- Check Neon project is active (not suspended)
- Test connection from Neon dashboard

**LocalStorage issues**
- Clear browser cache
- Check browser console for errors
- Verify LocalStorage is not disabled

## 💰 Cost Estimation

### Neon DB Free Tier
- **Storage**: 0.5 GB
- **Compute**: 100 hours/month
- **Branches**: 10 project branches
- **Data Transfer**: Included

For a personal recipe app: **$0/month** (within free tier)

### Netlify Free Tier
- **Bandwidth**: 100 GB/month
- **Build Minutes**: 300 minutes/month
- **Functions**: 125K requests/month, 100 hours runtime

For a personal recipe app: **$0/month** (within free tier)

**Total Cost**: **$0/month** for typical personal use! 🎉

## 📄 License

MIT License - See LICENSE file for details

## 🙏 Acknowledgments

- Built with [Netlify](https://netlify.com)
- Database powered by [Neon](https://neon.tech)
- Icons from emoji set

## 📞 Support

- Documentation: See this README
- Issues: GitHub Issues
- Discussions: GitHub Discussions

---

**Made with ❤️ and optimized for serverless**
