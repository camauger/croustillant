# 🍳 Croustillant

A modern, serverless recipe management application built with Netlify Functions and Neon DB.

## ✨ Features

- 📖 **Recipe Management**: Create, view, edit, and delete recipes
- 🔍 **Smart Search**: Search recipes by title or ingredients
- ⭐ **Recipe Selection**: Build your meal plan by selecting recipes
- 🛒 **Smart Shopping Lists**: Automatically generate consolidated shopping lists with unit conversion
- 📱 **Responsive Design**: Works perfectly on desktop, tablet, and mobile

## 🏗️ Architecture

- **Frontend**: Vanilla JavaScript (ES6+), HTML5, CSS3
- **Backend**: Netlify Functions (Python 3.11)
- **Database**: Neon DB (Serverless PostgreSQL)
- **Hosting**: Netlify (Static + Serverless)

## 📁 Project Structure

```
croustillant/
├── public/                      # Frontend static files
│   ├── index.html
│   ├── css/style.css
│   └── js/
│       ├── api.js              # API client
│       ├── app.js              # Main application
│       ├── router.js           # Client-side routing
│       └── components/         # UI components
│
├── netlify/
│   └── functions/              # Serverless API
│       ├── recipes/            # Recipes endpoint
│       │   ├── handler.py
│       │   ├── runtime.txt
│       │   └── requirements.txt
│       ├── recipe-detail/      # Recipe CRUD endpoint
│       ├── shopping-list/      # Shopping list endpoint
│       └── utils/              # Shared utilities
│           ├── db.py           # Database connection
│           └── ingredients.py  # Ingredient processing
│
├── netlify.toml                # Netlify configuration
├── neon-schema.sql             # Database schema
└── README.md                   # This file
```

## 🚀 Quick Start

### 1. Set Up Neon DB

1. Create account at [neon.tech](https://neon.tech)
2. Create new project
3. Run `neon-schema.sql` in SQL Editor
4. Copy connection string from Dashboard

### 2. Local Development

```bash
# Install Netlify CLI
npm install -g netlify-cli

# Create .env file
echo "DATABASE_URL=postgresql://..." > .env

# Run development server
netlify dev
```

Visit `http://localhost:8888`

### 3. Deploy to Netlify

1. Push to GitHub
2. Connect repository to Netlify
3. Set environment variable: `DATABASE_URL`
4. Deploy!

**Build Settings:**
- Build command: `echo "No build needed"`
- Publish directory: `public`
- Functions directory: `netlify/functions`

## 🔧 Configuration

### Environment Variables

- `DATABASE_URL`: Neon PostgreSQL connection string
  - Format: `postgresql://user:password@ep-xxxxx.region.aws.neon.tech/neondb?sslmode=require`

### Netlify Configuration

The `netlify.toml` file is already configured with:
- Functions directory: `netlify/functions`
- Redirects: `/api/*` → `/.netlify/functions/:splat`
- CORS headers for API endpoints

## 📊 API Endpoints

- `GET /api/recipes` - List all recipes (with search, category, pagination)
- `POST /api/recipes` - Create new recipe
- `GET /api/recipe-detail/:id` - Get single recipe
- `PUT /api/recipe-detail/:id` - Update recipe
- `DELETE /api/recipe-detail/:id` - Delete recipe
- `POST /api/shopping-list` - Generate shopping list from selected recipes

## 🧪 Testing

```bash
# List recipes
curl http://localhost:8888/api/recipes

# Create recipe
curl -X POST http://localhost:8888/api/recipes \
  -H "Content-Type: application/json" \
  -d '{"titre":"Test","ingredients":[],"instructions":[]}'
```

## 🐛 Troubleshooting

**Functions return 404:**
- Verify `netlify.toml` has `[functions] directory = "netlify/functions"`
- Check environment variables are set in Netlify dashboard
- Ensure all function folders have `handler.py`, `runtime.txt`, and `requirements.txt`

**Database connection errors:**
- Verify `DATABASE_URL` is correct
- Check Neon project is active
- Test connection from Neon SQL Editor

## 📚 Documentation

- **Deployment Guide**: See `DEPLOYMENT.md`
- **Database Schema**: See `neon-schema.sql`
- **Project Details**: See `CLAUDE.MD` for AI assistant context

## 💰 Cost

**Free Tier:**
- Neon: 0.5 GB storage, 100 hours compute/month
- Netlify: 100 GB bandwidth, 125K function requests/month

**Total: $0/month** for typical personal use! 🎉

## 📄 License

MIT License

---

**Made with ❤️ and optimized for serverless**
